"""
Rexi API Client

Main module containing the RexiAPI class for interacting with the Rexi API.
"""

import os
import json
import aiohttp
from typing import Dict, Any, Optional, List, Union

# Import all submodules
from .solana import (
    MarketAnalytics,
    TokenInformation,
    KOLCallsAlerts,
    WalletMonitoring,
    BlockchainData,
    RealtimeData
)


class RexiAPI:
    """
    Rexi API Client for interacting with the Rexi API service.
    
    Provides access to various blockchain services including Solana.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Rexi API client.
        
        Args:
            config: Configuration dictionary which may include:
                - api_key: Your Rexi API key
                - base_url: Base URL for the API (optional)
        """
        self._config = config or {}
        
        # Get API key from config or environment variable
        self._api_key = self._config.get('api_key') or os.environ.get('REXI_API_KEY')
        if not self._api_key:
            raise ValueError("API key is required. Provide it in the constructor or set REXI_API_KEY environment variable.")
        
        # Initialize Solana service modules
        self._init_solana_modules()
    
    def _init_solana_modules(self):
        """Initialize all Solana modules with references to this client."""
        # Create the main Solana namespace
        self.solana = type('Solana', (), {})()
        
        # Initialize all submodules
        self.solana.market = MarketAnalytics(self)
        self.solana.token = TokenInformation(self)
        self.solana.radar = KOLCallsAlerts(self)
        self.solana.monitor = WalletMonitoring(self)
        self.solana.account = BlockchainData(self)
        self.solana.realtime = RealtimeData(self)
        
        # Add shorthand methods to the main Solana namespace
        self._add_shorthand_methods()
    
    def _add_shorthand_methods(self):
        """Add shorthand methods to the main Solana namespace for convenience."""
        # Map common methods from submodules to the main Solana namespace
        self.solana.get_market_stats = self.solana.market.get_market_stats
        self.solana.get_token_info = self.solana.token.get_token_info
        self.solana.monitor_wallet = self.solana.monitor.get_wallet_trading_calls
    
    @property
    def api_key(self) -> str:
        """Get the API key."""
        return self._api_key
    
    @property
    def base_url(self) -> str:
        """Get the base URL for the API."""
        return self._config.get('base_url', 'https://api.rexi.sh')
    
    async def _request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None,
                      path_params: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Make a request to the Rexi API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint template
            params: Query parameters or request body
            path_params: Parameters to substitute in the endpoint path
            
        Returns:
            API response as a dictionary
        """
        # Substitute path parameters if provided
        if path_params:
            for key, value in path_params.items():
                placeholder = f"{{{key}}}"
                if placeholder in endpoint:
                    endpoint = endpoint.replace(placeholder, str(value))
        
        # Construct the full URL from base_url and endpoint
        url = f"{self.base_url}{endpoint}"
        
        # Debug information
        print(f"Making {method} request to: {url}")
        
        # Set up headers with API key for authentication
        headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
            "User-Agent": "Rexi-Python-Client/0.1.5"
        }
        
        try:
            # Create a client session and make the request
            async with aiohttp.ClientSession() as session:
                if method.upper() == "GET":
                    async with session.get(url, headers=headers, params=params) as response:
                        response.raise_for_status()
                        return await response.json()
                        
                elif method.upper() == "POST":
                    async with session.post(url, headers=headers, json=params) as response:
                        response.raise_for_status()
                        return await response.json()
                        
                elif method.upper() == "PUT":
                    async with session.put(url, headers=headers, json=params) as response:
                        response.raise_for_status()
                        return await response.json()
                        
                elif method.upper() == "DELETE":
                    async with session.delete(url, headers=headers, params=params) as response:
                        response.raise_for_status()
                        return await response.json()
                        
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                    
        except aiohttp.ClientResponseError as e:
            # Handle HTTP errors from the API
            error_msg = f"API request failed with status {e.status}: {e.message}"
            print(f"Error: {error_msg}")
            return {"error": error_msg, "status": e.status}
            
        except aiohttp.ClientError as e:
            # Handle connection errors
            error_msg = f"Connection error: {str(e)}"
            print(f"Error: {error_msg}")
            return {"error": error_msg}
            
        except Exception as e:
            # Handle any other exceptions
            error_msg = f"Unexpected error during API request: {str(e)}"
            print(f"Error: {error_msg}")
            return {"error": error_msg}
