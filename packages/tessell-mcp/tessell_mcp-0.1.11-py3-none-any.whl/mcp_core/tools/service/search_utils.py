"""
Service search utilities for enhanced search functionality.
"""
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class ServiceSearchEngine:
    """Enhanced search engine for service discovery with intelligent matching."""
    
    def __init__(self):
        self.common_separators = ['-', '_', ' ', '.']
        self.common_suffixes = ['db', 'database', 'server', 'svc', 'service', 'prod', 'dev', 'test', 'stage', 'staging']
    
    def generate_variations(self, query: str) -> List[str]:
        """Generate variations of the search query."""
        variations = [query]
        normalized = query.lower()
        
        # Handle separators
        for sep in self.common_separators:
            if sep in normalized:
                # Replace with other separators
                for other_sep in self.common_separators:
                    if sep != other_sep:
                        variations.append(normalized.replace(sep, other_sep))
                # Also try without separator
                variations.append(normalized.replace(sep, ''))
        
        # Split by separators and add parts
        for sep in self.common_separators:
            if sep in normalized:
                parts = normalized.split(sep)
                # Add individual parts
                variations.extend(parts)
                # Add combinations without common suffixes
                for part in parts:
                    if part not in self.common_suffixes:
                        variations.append(part)
        
        # Also split by multiple separators using regex to handle cases like "dev-test_db"
        import re
        pattern = '|'.join(re.escape(sep) for sep in self.common_separators)
        all_parts = re.split(pattern, normalized)
        all_parts = [p.strip() for p in all_parts if p.strip()]
        variations.extend(all_parts)
        
        # Remove common suffixes
        for suffix in self.common_suffixes:
            for sep in ['', '-', '_']:
                suffix_pattern = sep + suffix
                if normalized.endswith(suffix_pattern) and len(normalized) > len(suffix_pattern):
                    base = normalized[:-len(suffix_pattern)]
                    variations.append(base)
        
        # Handle queries without separators (e.g., "salesdb" -> "sales-db", "sales_db")
        # Check if query ends with a common suffix without separator
        for suffix in self.common_suffixes:
            if normalized.endswith(suffix) and len(normalized) > len(suffix):
                # Check if there's no separator before the suffix
                base = normalized[:-len(suffix)]
                if base and not any(base.endswith(sep) for sep in self.common_separators):
                    # Generate variations with separators
                    for sep in self.common_separators:
                        variations.append(base + sep + suffix)
        
        # Remove duplicates and empty strings
        variations = list(set(v for v in variations if v))
        logger.debug(f"Generated variations for '{query}': {variations}")
        return variations
    
    def calculate_score(self, service_name: str, query: str, variations: List[str]) -> float:
        """Calculate relevance score for a service match."""
        service_lower = service_name.lower()
        query_lower = query.lower()
        
        # Exact match gets highest score
        if service_lower == query_lower:
            return 1.0
        
        # Check variations for exact match
        for i, variation in enumerate(variations):
            if service_lower == variation:
                # Slightly lower score for variations, decreasing by order
                return max(0.9 - (i * 0.05), 0.7)
        
        # Substring matches
        if query_lower in service_lower:
            # Score based on position and length ratio
            position = service_lower.find(query_lower)
            length_ratio = len(query) / len(service_name)
            position_score = 1.0 - (position / len(service_name))
            return 0.5 + (length_ratio * 0.2) + (position_score * 0.1)
        
        # Check if any variation is substring
        for i, variation in enumerate(variations):
            if variation in service_lower:
                # Lower score for variation substrings
                position = service_lower.find(variation)
                length_ratio = len(variation) / len(service_name)
                position_score = 1.0 - (position / len(service_name))
                base_score = 0.3 - (i * 0.02)
                return max(base_score + (length_ratio * 0.1) + (position_score * 0.05), 0.1)
        
        # Check for word-based matching (handles reordering and partial matches)
        word_score = self._calculate_word_match_score(service_name, query)
        if word_score > 0:
            return word_score
        
        return 0.0
    
    def _calculate_word_match_score(self, service_name: str, query: str) -> float:
        """
        Calculate score based on word matching, handling reordering and partial matches.
        E.g., "hr int db" matches "hr-int", "int hr db" matches "hr-int"
        """
        # Extract words from both service name and query
        service_words = self._extract_words(service_name.lower())
        query_words = self._extract_words(query.lower())
        
        if not query_words:
            return 0.0
        
        # Remove common suffixes from query words for matching
        query_words_cleaned = []
        for word in query_words:
            if word not in self.common_suffixes:
                query_words_cleaned.append(word)
        
        if not query_words_cleaned:
            query_words_cleaned = query_words
        
        # Count how many query words are found in service name
        matched_words = 0
        for query_word in query_words_cleaned:
            # Check exact word match
            if query_word in service_words:
                matched_words += 1
            else:
                # Check if query word is a substring of any service word
                for service_word in service_words:
                    if query_word in service_word or service_word in query_word:
                        matched_words += 0.8  # Partial match gets slightly lower score
                        break
        
        # Calculate score based on matched words ratio
        if matched_words > 0:
            match_ratio = matched_words / len(query_words_cleaned)
            # Base score of 0.2-0.4 for word matches
            return min(0.2 + (match_ratio * 0.2), 0.4)
        
        return 0.0
    
    def _extract_words(self, text: str) -> List[str]:
        """Extract meaningful words from text, splitting by separators."""
        words = []
        # Split by all common separators
        import re
        pattern = '|'.join(re.escape(sep) for sep in self.common_separators)
        parts = re.split(pattern, text)
        
        for part in parts:
            part = part.strip()
            if part and len(part) > 1:  # Ignore single character words
                words.append(part)
        
        return words
    
    def search_with_additional_terms(
        self, 
        services: List[Dict], 
        query: str, 
        additional_terms: List[str] = None,
        page_size: int = 20
    ) -> List[Dict]:
        """
        Enhanced search that uses additional terms to boost relevance.
        
        Args:
            services: List of service dictionaries
            query: Primary search query
            additional_terms: Additional terms to boost matching results
            page_size: Maximum results to return
            
        Returns:
            List of matched services with boosted scores
        """
        # First, get results for primary query (get extra to allow for re-ranking)
        primary_results = self.search(services, query, page_size * 3)
        
        if not additional_terms or not primary_results:
            return primary_results[:page_size]
        
        # Process additional terms - generate variations for each
        all_additional_variations = []
        for term in additional_terms:
            if term:  # Skip empty terms
                variations = self.generate_variations(term.lower())
                all_additional_variations.extend(variations)
        
        # Remove duplicates
        all_additional_variations = list(set(all_additional_variations))
        
        # Boost scores for results matching additional terms
        for result in primary_results:
            boost = 0
            service_name_lower = result["name"].lower()
            matched_additional = []
            
            for term_var in all_additional_variations:
                if term_var in service_name_lower:
                    boost += 0.05  # Small boost for each matching additional term
                    # Track which additional terms matched
                    for original_term in additional_terms:
                        if term_var in self.generate_variations(original_term.lower()):
                            matched_additional.append(original_term)
                            break
            
            # Apply boost (cap at reasonable limit)
            result["match_score"] = min(result["match_score"] + boost, 0.99)
            result["matched_additional_terms"] = list(set(matched_additional))
        
        # Re-sort by boosted scores
        primary_results.sort(key=lambda x: x["match_score"], reverse=True)
        
        # Also search for services that match additional terms but not primary query
        additional_matches = []
        for term in additional_terms:
            if term:
                term_results = self.search(services, term, page_size)
                for result in term_results:
                    # Only add if not already in primary results
                    if not any(r["id"] == result["id"] for r in primary_results):
                        # Lower base score for additional-only matches
                        result["match_score"] = result["match_score"] * 0.3
                        result["matched_on_additional"] = True
                        additional_matches.append(result)
        
        # Combine results, primary matches first
        all_results = primary_results + additional_matches
        
        # Remove duplicates by service id
        seen_ids = set()
        unique_results = []
        for result in all_results:
            if result["id"] not in seen_ids:
                seen_ids.add(result["id"])
                unique_results.append(result)
        
        return unique_results[:page_size]
    
    def get_matched_variation(self, service_name: str, query: str, variations: List[str]) -> str:
        """Determine which variation matched the service name."""
        service_lower = service_name.lower()
        query_lower = query.lower()
        
        if query_lower in service_lower:
            return query
        
        for variation in variations:
            if variation in service_lower:
                return variation
        
        return ""
    
    def search(self, services: List[Dict], query: str, page_size: int = 20) -> List[Dict]:
        """
        Enhanced search with variations and scoring.
        
        Args:
            services: List of service dictionaries
            query: Search query string
            page_size: Maximum number of results to return
            
        Returns:
            List of matched services with scores
        """
        if not query:
            return []
        
        variations = self.generate_variations(query)
        scored_results = []
        
        for service in services:
            if not isinstance(service, dict):
                continue
                
            service_name = service.get("name", "")
            if not service_name:
                continue
                
            score = self.calculate_score(service_name, query, variations)
            
            if score > 0:
                matched_variation = self.get_matched_variation(service_name, query, variations)
                scored_results.append({
                    "service": service,
                    "score": score,
                    "matched_variation": matched_variation
                })
        
        # Sort by score (highest first)
        scored_results.sort(key=lambda x: x["score"], reverse=True)
        
        # Log search results
        logger.info(f"Search for '{query}' found {len(scored_results)} matches")
        if scored_results:
            logger.debug(f"Top matches: {[(r['service']['name'], r['score']) for r in scored_results[:5]]}")
        
        # Return top results
        return [
            {
                "id": r["service"]["id"],
                "name": r["service"]["name"],
                "match_score": round(r["score"], 3),
                "matched_on": r["matched_variation"]
            }
            for r in scored_results[:page_size]
        ]