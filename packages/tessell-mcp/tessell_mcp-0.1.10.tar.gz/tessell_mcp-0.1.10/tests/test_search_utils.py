"""
Unit tests for service search utilities.
"""
from mcp_core.tools.service.search_utils import ServiceSearchEngine


class TestServiceSearchEngine:
    """Test cases for ServiceSearchEngine."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.search_engine = ServiceSearchEngine()
        self.mock_services = [
            {"id": "1", "name": "sales-db"},
            {"id": "2", "name": "sales_db_prod"},
            {"id": "3", "name": "salesdb"},
            {"id": "4", "name": "sales-database"},
            {"id": "5", "name": "marketing-db"},
            {"id": "6", "name": "prod_sales_server"},
            {"id": "7", "name": "test.sales.db"},
            {"id": "8", "name": "sales"},
            {"id": "9", "name": "hr_database"},
            {"id": "10", "name": "sales-staging-db"},
        ]
    
    def test_generate_variations(self):
        """Test query variation generation."""
        # Test hyphen variations
        variations = self.search_engine.generate_variations("sales-db")
        assert "sales-db" in variations
        assert "sales_db" in variations
        assert "salesdb" in variations
        assert "sales db" in variations
        assert "sales" in variations
        assert "db" in variations
        
        # Test no-separator query (e.g., "salesdb")
        variations = self.search_engine.generate_variations("salesdb")
        assert "salesdb" in variations
        assert "sales" in variations
        assert "sales-db" in variations  # Should generate hyphenated version
        assert "sales_db" in variations  # Should generate underscore version
        assert "sales db" in variations  # Should generate space version
        
        # Test underscore variations
        variations = self.search_engine.generate_variations("prod_database")
        assert "prod_database" in variations
        assert "prod-database" in variations
        assert "proddatabase" in variations
        assert "prod database" in variations
        assert "prod" in variations
        
        # Test dot variations
        variations = self.search_engine.generate_variations("test.server")
        assert "test.server" in variations
        assert "test-server" in variations
        assert "test_server" in variations
        assert "test server" in variations
        assert "testserver" in variations
        assert "test" in variations
        
        # Test with multiple separators
        variations = self.search_engine.generate_variations("dev-test_db")
        assert "dev" in variations
        assert "test" in variations
        assert "db" in variations
    
    def test_calculate_score(self):
        """Test relevance scoring."""
        # Exact match should get highest score
        score = self.search_engine.calculate_score("sales-db", "sales-db", [])
        assert score == 1.0
        
        # Variation match should get high score
        variations = ["sales_db", "salesdb", "sales"]
        score = self.search_engine.calculate_score("sales_db", "sales-db", variations)
        assert 0.7 <= score < 1.0
        
        # Substring match should get medium score
        score = self.search_engine.calculate_score("sales-database", "sales", [])
        assert 0.5 <= score < 0.9
        
        # No match should get zero score
        score = self.search_engine.calculate_score("marketing-db", "sales", [])
        assert score == 0.0
        
        # Variation substring match should get lower score
        variations = ["sales_db", "sales"]
        score = self.search_engine.calculate_score("prod_sales_server", "sales-db", variations)
        assert 0.1 <= score < 0.5
    
    def test_get_matched_variation(self):
        """Test matched variation detection."""
        variations = ["sales_db", "salesdb", "sales"]
        
        # Direct query match
        matched = self.search_engine.get_matched_variation("sales-db-prod", "sales-db", variations)
        assert matched == "sales-db"
        
        # Variation match
        matched = self.search_engine.get_matched_variation("sales_db_prod", "sales-db", variations)
        assert matched == "sales_db"
        
        # No match
        matched = self.search_engine.get_matched_variation("marketing", "sales-db", variations)
        assert matched == ""
    
    def test_search_basic(self):
        """Test basic search functionality."""
        # Search for exact match
        results = self.search_engine.search(self.mock_services, "sales-db")
        assert len(results) > 0
        assert results[0]["name"] == "sales-db"
        assert results[0]["match_score"] == 1.0
        
        # Search should find variations
        assert any(r["name"] == "sales_db_prod" for r in results)
        assert any(r["name"] == "salesdb" for r in results)
        assert any(r["name"] == "sales-database" for r in results)
    
    def test_search_variations(self):
        """Test that different query formats find same results."""
        # Search with hyphen
        results1 = self.search_engine.search(self.mock_services, "sales-db")
        names1 = {r["name"] for r in results1}
        
        # Search with underscore
        results2 = self.search_engine.search(self.mock_services, "sales_db")
        names2 = {r["name"] for r in results2}
        
        # Should find similar results
        common_results = names1.intersection(names2)
        assert len(common_results) >= 3  # At least some overlap
    
    def test_search_ranking(self):
        """Test that results are properly ranked by relevance."""
        results = self.search_engine.search(self.mock_services, "sales")
        
        # Check that scores are in descending order
        scores = [r["match_score"] for r in results]
        assert scores == sorted(scores, reverse=True)
        
        # Exact match "sales" should be first
        assert results[0]["name"] == "sales"
        assert results[0]["match_score"] > results[1]["match_score"]
    
    def test_search_with_suffix_removal(self):
        """Test that common suffixes are removed for broader matching."""
        # Search for "hr_database" should also find "hr" if it exists
        results = self.search_engine.search(self.mock_services, "hr_database")
        assert len(results) > 0
        assert results[0]["name"] == "hr_database"
        
        # Search for "sales-staging-db" should find various sales services
        results = self.search_engine.search(self.mock_services, "sales-staging-db")
        assert any(r["name"] == "sales-staging-db" for r in results)
    
    def test_search_page_size(self):
        """Test that page size limit is respected."""
        results = self.search_engine.search(self.mock_services, "sales", page_size=3)
        assert len(results) <= 3
    
    def test_search_empty_query(self):
        """Test handling of empty query."""
        results = self.search_engine.search(self.mock_services, "")
        assert len(results) == 0
    
    def test_search_no_matches(self):
        """Test search with no matches."""
        results = self.search_engine.search(self.mock_services, "nonexistent")
        assert len(results) == 0
    
    def test_matched_on_field(self):
        """Test that matched_on field is populated correctly."""
        results = self.search_engine.search(self.mock_services, "sales-db")
        
        for result in results:
            assert "matched_on" in result
            # The matched variation should be in the service name
            if result["matched_on"]:
                assert result["matched_on"].lower() in result["name"].lower()
    
    def test_word_reordering(self):
        """Test that word reordering is handled correctly."""
        # Add test services
        test_services = [
            {"id": "1", "name": "hr-int"},
            {"id": "2", "name": "hr-int-db"},
            {"id": "3", "name": "marketing-prod"},
            {"id": "4", "name": "sanitized-clone-cm-test"},
            {"id": "5", "name": "test-sanitized-db"},
        ]
        
        # Test "hr int db" should find "hr-int" and "hr-int-db"
        results = self.search_engine.search(test_services, "hr int db")
        names = [r["name"] for r in results]
        assert "hr-int" in names
        assert "hr-int-db" in names
        
        # Test "int hr db" (reordered) should also find them
        results = self.search_engine.search(test_services, "int hr db")
        names = [r["name"] for r in results]
        assert "hr-int" in names
        assert "hr-int-db" in names
        
        # Test partial word matching: "sanitized test db" should find "sanitized-clone-cm-test"
        results = self.search_engine.search(test_services, "sanitized test db")
        names = [r["name"] for r in results]
        assert "sanitized-clone-cm-test" in names
        assert "test-sanitized-db" in names
    
    def test_complex_word_matching(self):
        """Test complex word matching scenarios."""
        test_services = [
            {"id": "1", "name": "prod-analytics-db-v2"},
            {"id": "2", "name": "analytics-prod-database"},
            {"id": "3", "name": "dev-analytics-service"},
            {"id": "4", "name": "analytics"},
        ]
        
        # Search for "analytics prod" in any order
        results = self.search_engine.search(test_services, "analytics prod")
        names = [r["name"] for r in results]
        assert "prod-analytics-db-v2" in names
        assert "analytics-prod-database" in names
        
        # Search for "prod analytics database" 
        results = self.search_engine.search(test_services, "prod analytics database")
        names = [r["name"] for r in results]
        assert "analytics-prod-database" in names
        assert "prod-analytics-db-v2" in names  # Should match even without exact "database"
    
    def test_partial_word_matching(self):
        """Test partial word matching."""
        test_services = [
            {"id": "1", "name": "customer-service-db"},
            {"id": "2", "name": "cust-svc-database"},
            {"id": "3", "name": "customer-api"},
        ]
        
        # "cust service" should match both "customer-service-db" and "cust-svc-database"
        results = self.search_engine.search(test_services, "cust service")
        names = [r["name"] for r in results]
        assert "customer-service-db" in names
        assert "cust-svc-database" in names
    
    def test_search_with_additional_terms(self):
        """Test search with additional terms for AI-assisted search."""
        test_services = [
            {"id": "1", "name": "sales-db-prod"},
            {"id": "2", "name": "sales-db-dev"},
            {"id": "3", "name": "sales-api-prod"},
            {"id": "4", "name": "marketing-db-prod"},
            {"id": "5", "name": "hr-db-staging"},
        ]
        
        # Search for "sales" with additional term "prod"
        results = self.search_engine.search_with_additional_terms(
            test_services, "sales", ["prod", "production"]
        )
        
        # Should find all sales services, but prod ones should rank higher
        names = [r["name"] for r in results]
        assert "sales-db-prod" in names
        assert "sales-api-prod" in names
        assert "sales-db-dev" in names
        
        # Prod services should rank higher due to additional terms
        assert results[0]["name"] in ["sales-db-prod", "sales-api-prod"]
        assert results[0]["match_score"] > results[2]["match_score"]  # prod > dev
        
        # Check that matched additional terms are tracked
        prod_results = [r for r in results if "prod" in r["name"]]
        for result in prod_results:
            if "matched_additional_terms" in result:
                assert "prod" in result["matched_additional_terms"] or "production" in result["matched_additional_terms"]
    
    def test_search_with_multiple_additional_terms(self):
        """Test with multiple additional terms for complex queries."""
        test_services = [
            {"id": "1", "name": "hr-integration-test-db"},
            {"id": "2", "name": "hr-prod-database"},
            {"id": "3", "name": "hr-api"},
            {"id": "4", "name": "sales-integration-db"},
            {"id": "5", "name": "hr-staging"},
        ]
        
        # User wants "hr system for integration testing"
        results = self.search_engine.search_with_additional_terms(
            test_services, "hr", ["integration", "int", "test", "testing"]
        )
        
        # hr-integration-test-db should rank highest
        assert results[0]["name"] == "hr-integration-test-db"
        assert results[0]["match_score"] > results[1]["match_score"]
        
        # Should also find other hr services
        names = [r["name"] for r in results]
        assert "hr-prod-database" in names
        assert "hr-api" in names
    
    def test_additional_terms_with_variations(self):
        """Test that additional terms also use variation generation."""
        test_services = [
            {"id": "1", "name": "sales_prod_db"},  # underscore version
            {"id": "2", "name": "sales-dev-database"},
            {"id": "3", "name": "marketing-production"},
        ]
        
        # Search with "prod" as additional term should match "production" and "prod_"
        results = self.search_engine.search_with_additional_terms(
            test_services, "sales", ["prod"]
        )
        
        # Should boost sales_prod_db due to "prod" variation matching
        assert results[0]["name"] == "sales_prod_db"
        
        # Should also find services with only additional terms
        results = self.search_engine.search_with_additional_terms(
            test_services, "database", ["production"]
        )
        names = [r["name"] for r in results]
        assert "sales-dev-database" in names  # Matches primary term
        assert "marketing-production" in names  # Matches additional term