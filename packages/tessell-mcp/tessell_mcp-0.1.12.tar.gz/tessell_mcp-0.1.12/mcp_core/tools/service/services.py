from mcp_core.mcp_server import mcp
from mcp_core.tools.client_factory import get_tessell_api_client
from mcp_core.tools.service.search_utils import ServiceSearchEngine
import logging
import json

logger = logging.getLogger(__name__)

@mcp.tool()
def list_services(page_size: int = 10):
    """
    Retrieve a detailed list of all services (also called servers in Tessell) in the Tessell environment.

    Note: In Tessell, 'service' and 'server' are interchangeable terms. Agents should treat them as synonyms when interpreting user queries.

    Args:
        page_size (int, optional): The number of services to return per page. Defaults to 10.

    Returns:
        dict: A dictionary containing the HTTP status code and the raw JSON response text from the Tessell API. The response includes a list of service objects, each with fields such as ID, name, status, and availability machine ID.

    Example response:
        {
            "status_code": 200,
            "content": '[{"id": "svc-123", "name": "ServiceA", "status": "ACTIVE", "availability_machine_id": "am-456"}, ...]'
        }
    """
    client = get_tessell_api_client()
    logger.info(f"Listing services with page_size={page_size}")
    resp = client.get_services(page_size=page_size)
    return {"status_code": resp.status_code, "content": resp.text}

@mcp.tool()
def get_service_details(service_id: str):
    """
    Retrieve the full details for a given service ID (also called server ID in Tessell) using the Tessell API client.

    Args:
        service_id (str): The ID of the service.
    Returns:
        dict: {"status_code": int, "service_details": dict} or error message.
    """
    client = get_tessell_api_client()
    resp = client.get_service_details(service_id)
    logger.info(f"Fetching full service details for service_id={service_id}, status_code={resp.status_code}")
    if resp.status_code != 200:
        logger.error(f"Failed to fetch service details: {resp.text}")
        return {"status_code": resp.status_code, "error": resp.text}
    try:
        details = resp.json()
        return {"status_code": 200, "service_details": details}
    except Exception as e:
        logger.exception("Failed to parse service details JSON.")
        return {"status_code": 500, "error": str(e)}
    
@mcp.tool()
def list_databases(service_id: str):
    """
    List databases for a given service (server) by service_id by fetching service details and extracting the 'databases' field.

    Returns:
        dict: {"status_code": int, "databases": list}
    """
    client = get_tessell_api_client()
    logger.info(f"Listing databases for service_id={service_id} via service details")
    resp = client.get_service_details(service_id)
    if resp.status_code == 200:
        try:
            details = resp.json()
            databases = details.get("databases", [])
            return {"status_code": 200, "databases": databases}
        except Exception as e:
            logger.exception("Failed to parse service details JSON for databases.")
            return {"status_code": 500, "error": str(e)}
    else:
        logger.error(f"Failed to fetch service details for databases: {resp.text}")
        return {"status_code": resp.status_code, "error": resp.text}

@mcp.tool()
def search_services(query: str, additional_terms: list = None, page_size: int = 20):
    """
    Search services by name with intelligent matching and context-aware ranking.
    
    Core Features:
    - Format variations: 'sales-db' finds 'sales_db', 'salesdb', 'sales db'
    - Suffix removal: 'sales-db' also searches 'sales'  
    - Case insensitive matching
    - Separator handling: -, _, space, .
    - Relevance scoring (1.0=exact, 0.7-0.9=variations, 0.3-0.6=partial)
    - Relevance scoring with additional_terms boost
    
    Usage Patterns:
    1. Basic: search_services("sales")
    2. Environment: search_services("sales", ["prod", "production"])
       → 'sales-prod-db' scores higher than 'sales-dev-db' 
    3. Service type: search_services("analytics", ["sanitized", "test"])
       → 'sanitized-analytics-test' ranks #1
    
    How additional_terms work:
    - Services matching query AND additional_terms get score boost (+0.05 per term)
    - Services matching only query keep their normal score (no penalty)
    - Services matching only additional_terms appear at bottom (score * 0.3)
    - More context = better ranking accuracy
    
    For AI agents: Extract most likely service name as query (fix typos), add environment/context as additional_terms

    Args:
        query (str): Primary search term - the most specific identifier
        additional_terms (list, optional): Additional context terms to boost relevance
        page_size (int): Maximum results to return (default: 20)

    Returns:
        dict: {"status_code": int, "matches": [{"id": str, "name": str, "match_score": float, "matched_on": str, "matched_additional_terms": list}, ...]}
    """
    client = get_tessell_api_client()
    logger.info(f"Searching services: query={query}, additional_terms={additional_terms}, page_size={page_size}")
    
    resp = client.get_services(page_size=1000)
    if resp.status_code != 200:
        logger.error(f"Failed to search services: {resp.text}")
        return {"status_code": resp.status_code, "error": resp.text}
    
    # Parse response
    services_obj = resp.json()
    if isinstance(services_obj, str):
        try:
            services_obj = json.loads(services_obj)
        except Exception as e:
            logger.error(f"Failed to parse services response: {e}")
            return {"status_code": 500, "error": str(e)}
    
    services_list = services_obj.get("response", [])
    
    # Always use enhanced search with variations and scoring
    search_engine = ServiceSearchEngine()
    
    # Use additional terms if provided
    if additional_terms:
        results = search_engine.search_with_additional_terms(services_list, query, additional_terms, page_size)
    else:
        results = search_engine.search(services_list, query, page_size)
        
    return {"status_code": 200, "matches": results}

@mcp.tool()
def manage_service(service_id: str, action: str, comment: str = ""):
    """
    Start or stop a database service (server) by service_id.

    Note: In Tessell, 'service' and 'server' are interchangeable terms. Agents should treat them as synonyms when interpreting user queries.

    Args:
        service_id (str): The ID of the service to act on.
        action (str): Either 'start' or 'stop'.
        comment (str, optional): Comment for the action. Used for both start and stop.
    Returns:
        dict: {"status_code": int, "result": str}
    """
    client = get_tessell_api_client()
    logger.info(f"Performing action '{action}' on service_id={service_id}")
    if action == "start":
        resp = client.start_service(service_id, comment=comment)
    elif action == "stop":
        resp = client.stop_service(service_id, comment=comment)
    else:
        logger.error(f"Invalid action: {action}")
        return {"status_code": 400, "error": "Invalid action. Use 'start' or 'stop'."}
    if resp.status_code in (200, 202):
        logger.info(f"Service {action}ed successfully for service_id={service_id}")
        return {"status_code": resp.status_code, "result": f"Service {action}ed successfully."}
    else:
        logger.error(f"Failed to {action} service: {resp.text}")
        return {"status_code": resp.status_code, "error": resp.text}

