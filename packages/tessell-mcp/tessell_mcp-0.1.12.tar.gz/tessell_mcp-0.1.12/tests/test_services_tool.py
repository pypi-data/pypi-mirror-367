import os
import pytest
import logging
from mcp_core.tools.service.services import *

# Import shared configuration from conftest.py
from conftest import TEST_SERVICE_ID

def test_list_services():
    result = list_services()
    assert result["status_code"] == 200
    assert "content" in result
    assert isinstance(result["content"], str)

def test_get_service_details():
    result = get_service_details(TEST_SERVICE_ID)
    assert result["status_code"] == 200
    assert "service_details" in result
    assert isinstance(result["service_details"], dict)

def test_list_databases():
    result = list_databases(TEST_SERVICE_ID)
    assert result["status_code"] == 200
    assert "databases" in result
    logging.info(f"Databases for service {TEST_SERVICE_ID}: {result['databases']}")
    assert isinstance(result["databases"], list)


def test_search_services_by_name():
    # Use a substring of TEST_SERVICE_ID or a known service name for the query
    query = "mysql"  # Set to a valid substring or name for your environment
    result = search_services(query)
    assert result["status_code"] == 200
    logging.info(f"Search results for query '{query}': {result}")
    assert "matches" in result
    assert isinstance(result["matches"], list)

def test_enhanced_search_variations():
    """Test that enhanced search handles variations correctly."""
    # Test with a hyphenated query
    result1 = search_services("test-db")
    assert result1["status_code"] == 200
    assert "matches" in result1
    
    # If there are matches, check the structure
    if result1["matches"]:
        match = result1["matches"][0]
        assert "id" in match
        assert "name" in match
        assert "match_score" in match
        assert "matched_on" in match
        logging.info(f"Enhanced search result structure: {match}")
    
    # Test with underscore version
    result2 = search_services("test_db")
    assert result2["status_code"] == 200
    
    # Log the differences
    logging.info(f"Search with 'test-db': {len(result1.get('matches', []))} matches")
    logging.info(f"Search with 'test_db': {len(result2.get('matches', []))} matches")

def test_search_ranking():
    """Test that enhanced search results are ranked by relevance."""
    # Search for a common term
    result = search_services("prod")
    assert result["status_code"] == 200
    
    if len(result.get("matches", [])) > 1:
        # Check that match scores are in descending order
        scores = [m.get("match_score", 0) for m in result["matches"]]
        assert scores == sorted(scores, reverse=True), "Results should be sorted by match score"
        
        # Log top matches for debugging
        logging.info("Top 5 matches for 'prod':")
        for i, match in enumerate(result["matches"][:5]):
            logging.info(f"  {i+1}. {match['name']} (score: {match['match_score']}, matched: {match.get('matched_on', '')})")

def test_search_suffix_removal():
    """Test that common suffixes are handled properly."""
    # Search with a suffix
    result_with_suffix = search_services("mysql-database")
    assert result_with_suffix["status_code"] == 200
    
    # The search should also find services with just "mysql" due to suffix removal
    if result_with_suffix.get("matches"):
        names = [m["name"].lower() for m in result_with_suffix["matches"]]
        logging.info(f"Matches for 'mysql-database': {names[:5]}")
        
        # Check if any matches contain 'mysql' but not necessarily 'database'
        mysql_matches = [n for n in names if "mysql" in n]
        assert len(mysql_matches) > 0, "Should find services containing 'mysql'"

def test_ai_assisted_search():
    """Test AI-assisted search with additional terms."""
    # Simulate AI extracting terms from "I need the production mysql database"
    result = search_services("mysql", additional_terms=["production", "prod", "database"])
    assert result["status_code"] == 200
    
    if result.get("matches"):
        # Log results to see the effect of additional terms
        logging.info("AI-assisted search results for 'mysql' + ['production', 'prod', 'database']:")
        for i, match in enumerate(result["matches"][:5]):
            additional = match.get("matched_additional_terms", [])
            logging.info(f"  {i+1}. {match['name']} (score: {match.get('match_score', 0)}, additional: {additional})")
        
        # Check that results have proper structure
        first_match = result["matches"][0]
        assert "id" in first_match
        assert "name" in first_match
        assert "match_score" in first_match
        
        # If there are prod/production services, they should rank higher
        prod_matches = [m for m in result["matches"] if any(term in m["name"].lower() for term in ["prod", "production"])]
        if prod_matches and len(result["matches"]) > 1:
            # Check if any prod match is in top results
            top_names = [m["name"] for m in result["matches"][:3]]
            has_prod_in_top = any(any(term in name.lower() for term in ["prod", "production"]) for name in top_names)
            logging.info(f"Production services in top 3: {has_prod_in_top}")

def test_search_with_empty_additional_terms():
    """Test that empty additional terms don't break the search."""
    result = search_services("mysql", additional_terms=[])
    assert result["status_code"] == 200
    
    # Should work same as without additional terms
    result2 = search_services("mysql")
    assert result["status_code"] == result2["status_code"]

def test_service_action_invalid():
    result = manage_service(TEST_SERVICE_ID, "invalid_action")
    assert result["status_code"] == 400
    assert "error" in result

def test_service_action_start_stop():
    """Test starting and stopping a service based on its current status."""
    details_result = get_service_details(TEST_SERVICE_ID)
    assert details_result["status_code"] == 200
    details = details_result["service_details"]
    status = details.get("status")
    assert status in ("READY", "STOPPED", "STOPPING"), f"Unexpected service status: {status}"

    if status == "READY":
        stop_result = manage_service(TEST_SERVICE_ID, "stop", "Stopping for test")
        assert stop_result["status_code"] in (200, 202), f"Stop failed: {stop_result}"
    elif status == "STOPPED":
        start_result = manage_service(TEST_SERVICE_ID, "start", "Starting for test")
        assert start_result["status_code"] in (200, 202), f"Start failed: {start_result}"
    elif status == "STOPPING":
        pytest.skip("Service is stopping, not performing start/stop action.")
    else:
        pytest.fail(f"Unhandled service status: {status}")
