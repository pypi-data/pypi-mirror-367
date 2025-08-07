"""
Rexi API Client

Main module containing the RexiAPI class for interacting with the Rexi API.
"""

import os
import json
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
        return self._config.get('base_url', 'https://api.rexi.io/v1')
    
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
        
        # This is a placeholder for the actual implementation
        # In a real implementation, you would use a library like aiohttp or httpx
        # to make asynchronous HTTP requests
        
        # For now, we'll just return empty dictionaries as placeholders
        # In a real implementation, you would:
        # 1. Construct the full URL from base_url and endpoint
        # 2. Add headers including X-API-Key for authentication
        # 3. Make the actual HTTP request
        # 4. Parse and return the response
        
        # Example of what a real implementation might look like (pseudo-code):
        """
        import httpx
        
        headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}{endpoint}"
        
        async with httpx.AsyncClient() as client:
            if method.upper() == "GET":
                response = await client.get(url, headers=headers, params=params)
            elif method.upper() == "POST":
                response = await client.post(url, headers=headers, json=params)
            # Handle other methods...
            
            response.raise_for_status()
            return response.json()
        """
        
        # Placeholder response
        return {}
