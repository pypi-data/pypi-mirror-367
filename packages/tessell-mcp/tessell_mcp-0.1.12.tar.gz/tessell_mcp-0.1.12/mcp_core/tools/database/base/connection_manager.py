"""
Connection manager for database connections.
Handles credential lookup and injection into connection strings.
"""

import os
import json
import logging
import re
from typing import Dict, Optional, Any
from urllib.parse import urlparse, parse_qs, quote
import threading

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages database connections and connection strings."""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or os.getenv("DATABASE_CONFIG_PATH")
        self._credentials_cache = None
        self._lock = threading.Lock()
        
    def build_connection_string_from_service(
        self,
        service_id: str,
        database_name: str
    ) -> str:
        """
        Build connection string by fetching service details from Tessell API and injecting credentials.
        Uses service name (not ID) for credential lookup to make config management easier.
        
        Args:
            service_id: Tessell service ID (UUID)
            database_name: Name of the database
        
        Returns:
            Complete connection string with credentials
        
        Raises:
            Exception: If service details cannot be fetched or credentials are missing
        """
        # Import here to avoid circular dependency
        from mcp_core.tools.service.services import get_service_details
        
        # Get service details from Tessell API
        service_response = get_service_details(service_id)
        
        if service_response.get("status_code") != 200:
            error_msg = service_response.get('error', 'Unknown error')
            raise Exception(f"Failed to get service details for {service_id}: {error_msg}")
        
        service_details = service_response.get("service_details", {})
        
        # Extract service name for credential lookup
        service_name = service_details.get("name")
        if not service_name:
            raise Exception(f"No service name found in service details for {service_id}")
        
        # Extract connection string template
        service_connectivity = service_details.get("serviceConnectivity", {})
        connect_strings = service_connectivity.get("connectStrings", [])
        
        if not connect_strings:
            raise Exception(f"No connection strings found for service {service_name} ({service_id})")
        
        # Get the default connection string (first one)
        default_conn = connect_strings[0]
        conn_template = default_conn.get("connectDescriptor")
        master_user = default_conn.get("masterUser")
        
        if not conn_template:
            raise Exception(f"No connection descriptor found for service {service_name} ({service_id})")
        
        # Replace database_name placeholder
        conn_str = conn_template.replace("<database_name>", database_name)
        
        # Get credentials from config using service_name[database_name]
        credentials = self.get_database_credentials(service_name, database_name)
        
        if not credentials:
            raise Exception(f"No credentials configured for service '{service_name}', database '{database_name}'. " +
                          f"Please add credentials in the config file under '{service_name}' -> '{database_name}'")
        
        # Extract username and password
        username = credentials.get("username", master_user)
        password = credentials.get("password")
        
        if not password:
            raise Exception(f"No password found in credentials for service '{service_name}', database '{database_name}'")
        
        # Replace password placeholder
        conn_str = conn_str.replace("<password>", quote(password, safe=''))
        
        # If username is different from master, update it in the connection string
        if username != master_user:
            # Replace the username in the connection string
            conn_str = conn_str.replace(f"//{master_user}:", f"//{username}:")
        
        return conn_str
    
    def get_database_credentials(
        self,
        service_name: str,
        database_name: str
    ) -> Optional[Dict[str, str]]:
        """
        Get credentials for service_name[database_name] from JSON config file.
        
        Args:
            service_name: Tessell service name (e.g., "postgres_ha_test")
            database_name: Database name
            
        Returns:
            Dict with 'username' and 'password', or None
        """
        if not self.config_path:
            logger.warning("No DATABASE_CONFIG_PATH set")
            return None
        
        # Load and cache credentials from JSON file
        if self._credentials_cache is None:
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    self._credentials_cache = config.get('database_credentials', {})
            except (FileNotFoundError, json.JSONDecodeError) as e:
                logger.error(f"Error loading credentials from {self.config_path}: {e}")
                return None
        
        # Look up service_name[database_name]
        service_creds = self._credentials_cache.get(service_name, {})
        return service_creds.get(database_name)
    
    
    
    
    def parse_connection_string(self, connection_string: str) -> Dict[str, Any]:
        """
        Parse a connection string into its components.
        
        Args:
            connection_string: Database connection string
            
        Returns:
            Dictionary containing parsed connection components
        """
        try:
            parsed = urlparse(connection_string)
            query_params = parse_qs(parsed.query)
            
            # Extract username and password
            username = password = None
            if parsed.username:
                username = parsed.username
            if parsed.password:
                password = parsed.password
            
            # Extract database name
            database = parsed.path.lstrip('/') if parsed.path else None
            
            # Parse query parameters
            params = {}
            for key, values in query_params.items():
                params[key] = values[0] if values else None
            
            return {
                "scheme": parsed.scheme,
                "host": parsed.hostname,
                "port": parsed.port,
                "username": username,
                "password": password,
                "database": database,
                "params": params
            }
            
        except Exception as e:
            logger.error(f"Error parsing connection string: {e}")
            return {}
    
    def validate_connection_string(self, connection_string: str) -> bool:
        """
        Validate a connection string format.
        
        Args:
            connection_string: Connection string to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            parsed = self.parse_connection_string(connection_string)
            required_fields = ["scheme", "host"]
            
            # Check required fields
            for field in required_fields:
                if not parsed.get(field):
                    logger.error(f"Missing required field in connection string: {field}")
                    return False
            
            # Validate scheme
            valid_schemes = ["postgresql", "postgres", "mysql", "oracle", "mssql"]
            if parsed["scheme"] not in valid_schemes:
                logger.error(f"Invalid database scheme: {parsed['scheme']}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Connection string validation error: {e}")
            return False
    
    
    def _mask_connection_string(self, connection_string: str) -> str:
        """
        Mask sensitive information in connection string.
        
        Args:
            connection_string: Original connection string
            
        Returns:
            Masked connection string
        """
        try:
            parsed = urlparse(connection_string)
            if parsed.password:
                # Replace password with asterisks
                netloc = parsed.netloc.replace(f":{parsed.password}@", ":***@")
                return connection_string.replace(parsed.netloc, netloc)
        except Exception:
            pass
        
        return connection_string
    



# Global connection manager instance
connection_manager = ConnectionManager() 