"""
Solana Module

Provides Solana blockchain-specific functionality for the Rexi API.
This module is organized into multiple classes, each focusing on a specific category of the API.
"""

from typing import Dict, Any, Optional, List, Union, Callable


class MarketAnalytics:
    """
    Market Analytics API for Solana blockchain.
    Provides methods for retrieving market statistics and activity data.
    """
    
    def __init__(self, client):
        """
        Initialize the Market Analytics module.
        
        Args:
            client: The RexiAPI client instance
        """
        self._client = client
    
    async def get_market_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive market statistics including data for all trading platforms with timeframes.
        
        Returns:
            Dictionary containing market statistics like price, volume, etc.
        """
        return await self._client._request('GET', '/solana/market-stats')
    
    async def get_sol_market_data(self) -> Dict[str, Any]:
        """
        Get SOL market data including price, market cap, and fee statistics.
        
        Returns:
            Current SOL market information
        """
        return await self._client._request('GET', '/solana/sol/market-data')
    
    async def get_activity_types(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get available activity types for Solana transactions.
        
        Args:
            params: Dictionary with optional parameters:
                - activity_type: Activity type (transfer, nfttrading, dextrading, default: "transfer")
        
        Returns:
            Mapping of activity type keys to descriptions
        """
        return await self._client._request('GET', '/solana/activity/types', params=params)


class TokenInformation:
    """
    Token Information API for Solana blockchain.
    Provides methods for retrieving detailed information about tokens.
    """
    
    def __init__(self, client):
        """
        Initialize the Token Information module.
        
        Args:
            client: The RexiAPI client instance
        """
        self._client = client
    
    async def get_token_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get comprehensive token information by contract address.
        
        Args:
            params: Dictionary with the following keys:
                - address: Token contract address (required)
        
        Returns:
            Token information
        """
        if 'address' not in params:
            raise ValueError("Token contract address is required")
            
        contract_address = params.get('address')
        return await self._client._request('GET', '/solana/token/info/{contract_address}', 
                                         path_params={'contract_address': contract_address})
    
    async def get_holder_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get top 100 holders data for a token.
        
        Args:
            params: Dictionary with the following keys:
                - address: Token contract address (required)
                - tracked_only: Return only tracked wallets (optional, default: False)
        
        Returns:
            Holder data for the token
        """
        if 'address' not in params:
            raise ValueError("Token contract address is required")
            
        contract_address = params.pop('address')
        return await self._client._request('GET', '/solana/token/holder-data/{contract_address}', 
                                         params=params,
                                         path_params={'contract_address': contract_address})
    
    async def get_top_traders(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get top 100 traders for a token.
        
        Args:
            params: Dictionary with the following keys:
                - address: Token contract address (required)
        
        Returns:
            Top traders data for the token
        """
        if 'address' not in params:
            raise ValueError("Token contract address is required")
            
        contract_address = params.pop('address')
        return await self._client._request('GET', '/solana/token/top-traders/{contract_address}', 
                                         path_params={'contract_address': contract_address})
    
    async def get_token_details(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get detailed information about a specific token by mint address.
        
        Args:
            params: Dictionary with the following keys:
                - address: Token mint address (required)
        
        Returns:
            Detailed token information
        """
        if 'address' not in params:
            raise ValueError("Token mint address is required")
            
        mint_address = params.pop('address')
        return await self._client._request('GET', '/solana/radar/token/{mint_address}', 
                                         path_params={'mint_address': mint_address})


class KOLCallsAlerts:
    """
    KOL (Key Opinion Leaders) Calls and Alerts API for Solana blockchain.
    Provides methods for retrieving token calls, alerts, and caller information.
    """
    
    def __init__(self, client):
        """
        Initialize the KOL Calls and Alerts module.
        
        Args:
            client: The RexiAPI client instance
        """
        self._client = client
    
    async def get_new_calls(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get new token calls and alerts from monitoring systems.
        
        Args:
            params: Dictionary with optional parameters:
                - page: Page number (≥1, default: 1)
                - limit: Number of results per page (1-100, default: 20)
        
        Returns:
            Latest token calls and alerts
        """
        return await self._client._request('GET', '/solana/radar/calls/new', params=params)
    
    async def get_most_called(self, timeframe: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get most called tokens by timeframe from monitoring systems.
        
        Args:
            timeframe: Valid timeframes (1h, 6h, 24h, 7d, 30d)
            params: Dictionary with optional parameters:
                - page: Page number (≥1, default: 1)
                - limit: Number of results per page (1-100, default: 20)
        
        Returns:
            Most called tokens for the specified timeframe
        """
        if timeframe not in ['1h', '6h', '24h', '7d', '30d']:
            raise ValueError("Invalid timeframe. Must be one of: 1h, 6h, 24h, 7d, 30d")
            
        return await self._client._request('GET', '/solana/radar/calls/most/{timeframe}', 
                                         params=params,
                                         path_params={'timeframe': timeframe})
    
    async def get_caller_profile(self, caller_id: str) -> Dict[str, Any]:
        """
        Get detailed profile information for a specific caller by their ID.
        
        Args:
            caller_id: Caller ID
        
        Returns:
            Full caller profile including Telegram/Twitter info and performance metrics
        """
        return await self._client._request('GET', '/solana/radar/caller/{caller_id}', 
                                         path_params={'caller_id': caller_id})
    
    async def get_caller_calls(self, caller_id: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get all calls made by a specific caller.
        
        Args:
            caller_id: Caller ID
            params: Dictionary with optional parameters:
                - sort: Sort order (newest, oldest, default: newest)
                - page: Page number (≥1, default: 1)
                - limit: Number of results per page (1-100, default: 20)
                - q: Optional search query to filter calls
        
        Returns:
            Call history for the specified caller
        """
        return await self._client._request('GET', '/solana/radar/caller/{caller_id}/calls', 
                                         params=params,
                                         path_params={'caller_id': caller_id})
    
    async def get_caller_performance(self, caller_id: str) -> Dict[str, Any]:
        """
        Get performance statistics for a specific caller by their ID.
        
        Args:
            caller_id: Caller ID
        
        Returns:
            Caller stats including win rate, average gain, and analyzed calls
        """
        return await self._client._request('GET', '/solana/radar/caller/{caller_id}/performance', 
                                         path_params={'caller_id': caller_id})
    
    async def get_top_callers(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get top performing callers based on recent call data.
        
        Args:
            params: Dictionary with optional parameters:
                - limit: Number of top callers to return (1-50, default: 20)
        
        Returns:
            Callers ranked by performance score
        """
        return await self._client._request('GET', '/solana/radar/callers/top', params=params)


class WalletMonitoring:
    """
    Wallet Monitoring API for Solana blockchain.
    Provides methods for monitoring wallet activity and retrieving transaction data.
    """
    
    def __init__(self, client):
        """
        Initialize the Wallet Monitoring module.
        
        Args:
            client: The RexiAPI client instance
        """
        self._client = client
    
    async def get_wallet_trading_calls(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get Solana trading calls for a specific wallet address with monitoring capabilities.
        
        Args:
            params: Dictionary with the following keys:
                - address: Wallet address to monitor (required)
                - timeout: Maximum seconds to wait for calls (1-120, default: 30)
                - realtime: Boolean indicating if real-time updates are desired (optional)
        
        Returns:
            Trading calls data for the specified address
        """
        if 'address' not in params:
            raise ValueError("Wallet address is required")
            
        return await self._client._request('GET', '/solana/monitor/getcalls', params=params)
    
    async def get_latest_trading_calls(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get latest Solana trading calls from the Scan API.
        
        Args:
            params: Dictionary with optional parameters:
                - page: Page number (≥1, default: 1)
                - limit: Number of results per page (1-10000, default: 50)
        
        Returns:
            Latest trading calls data
        """
        return await self._client._request('GET', '/solana/monitor/getlatestcalls', params=params)


class BlockchainData:
    """
    Blockchain Data API for Solana blockchain.
    Provides methods for retrieving account, token, and transaction data.
    """
    
    def __init__(self, client):
        """
        Initialize the Blockchain Data module.
        
        Args:
            client: The RexiAPI client instance
        """
        self._client = client
    
    async def get_account_tokens(self, address: str) -> Dict[str, Any]:
        """
        Get tokens held by an account address.
        
        Args:
            address: Account address
        
        Returns:
            All tokens held by the specified account with balances and USD values
        """
        return await self._client._request('GET', '/solana/account/{address}/tokens', 
                                         path_params={'address': address})
    
    async def get_account_funding_source(self, address: str) -> Dict[str, Any]:
        """
        Get the funding source for an account address.
        
        Args:
            address: Account address
        
        Returns:
            Information about which address funded this account
        """
        return await self._client._request('GET', '/solana/account/{address}/funded-by', 
                                         path_params={'address': address})
    
    async def get_token_accounts(self, address: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get token accounts for a wallet address with pagination support.
        
        Args:
            address: Account address
            params: Dictionary with optional parameters:
                - page: Page number (≥1, default: 1)
                - page_size: Number of results per page (1-100, default: 100)
                - token_type: Type of tokens to return (default: "token")
                - hide_zero: Hide accounts with zero balance (default: True)
        
        Returns:
            Detailed token account information
        """
        return await self._client._request('GET', '/solana/account/{address}/token-accounts', 
                                         params=params,
                                         path_params={'address': address})
    
    async def get_account_domains(self, address: str) -> Dict[str, Any]:
        """
        Get domain information associated with an account address.
        
        Args:
            address: Account address
        
        Returns:
            Domain names associated with the account address
        """
        return await self._client._request('GET', '/solana/account/{address}/domains', 
                                         path_params={'address': address})
    
    async def get_account_transactions(self, address: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get transactions for an account address with paging support.
        
        Args:
            address: Account address
            params: Dictionary with optional parameters:
                - page: Page number (≥1, default: 1)
                - page_size: Number of results per page (1-100, default: 10)
                - before: Transaction signature to paginate before (optional)
        
        Returns:
            Transaction history with detailed information
        """
        return await self._client._request('GET', '/solana/account/{address}/transactions', 
                                         params=params,
                                         path_params={'address': address})
    
    async def get_account_transfers(self, address: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get token transfers for an account address.
        
        Args:
            address: Account address
            params: Dictionary with optional parameters:
                - page: Page number (≥1, default: 1)
                - page_size: Number of results per page (1-100, default: 10)
                - remove_spam: Filter out spam tokens (default: True)
                - exclude_amount_zero: Exclude zero amount transfers (default: True)
        
        Returns:
            Transfer history with filtering options
        """
        return await self._client._request('GET', '/solana/account/{address}/transfers', 
                                         params=params,
                                         path_params={'address': address})
    
    async def get_account_transfers_total(self, address: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get total count of token transfers for an account address.
        
        Args:
            address: Account address
            params: Dictionary with optional parameters:
                - remove_spam: Filter out spam tokens (default: True)
                - exclude_amount_zero: Exclude zero amount transfers (default: True)
        
        Returns:
            Total number of transfers with filtering options
        """
        return await self._client._request('GET', '/solana/account/{address}/transfers/total', 
                                         params=params,
                                         path_params={'address': address})
    
    async def get_account_dex_trading_total(self, address: str) -> Dict[str, Any]:
        """
        Get total count of DEX trading activities for an account address.
        
        Args:
            address: Account address
        
        Returns:
            Total number of DEX trading activities
        """
        return await self._client._request('GET', '/solana/account/{address}/dex-trading/total', 
                                         path_params={'address': address})
    
    async def get_account_nft_total(self, address: str) -> Dict[str, Any]:
        """
        Get total count of NFT activities for an account address.
        
        Args:
            address: Account address
        
        Returns:
            Total number of NFT activities
        """
        return await self._client._request('GET', '/solana/account/{address}/nft/total', 
                                         path_params={'address': address})


class RealtimeData:
    """
    Real-time Data Streams API for Solana blockchain.
    Provides methods for accessing WebSocket endpoints and real-time data.
    """
    
    def __init__(self, client):
        """
        Initialize the Real-time Data module.
        
        Args:
            client: The RexiAPI client instance
        """
        self._client = client
    
    def get_websocket_url(self) -> str:
        """
        Get the WebSocket URL for live calls.
        
        Returns:
            WebSocket URL for connecting to the live calls endpoint
        """
        return f"{self._client.base_url.replace('http', 'ws')}/solana/monitor/livecalls"
    
    # Note: WebSocket implementation would require additional code
    # to handle WebSocket connections, which is beyond the scope of this simple client.
    # In a real implementation, you might use a library like websockets or asyncio
