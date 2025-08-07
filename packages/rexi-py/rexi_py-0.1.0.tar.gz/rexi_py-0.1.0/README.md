<div align="center">
  <img src="rexi_logo.png" alt="Rexi Logo" width="300"/>
  <h1>Rexi Python API Client</h1>
  <p>A powerful, modern Python library for interacting with the Rexi API services</p>
  
  [![PyPI version](https://img.shields.io/pypi/v/rexi-py.svg)](https://pypi.org/project/rexi-py/)
  [![Python Versions](https://img.shields.io/pypi/pyversions/rexi-py.svg)](https://pypi.org/project/rexi-py/)
  [![License](https://img.shields.io/github/license/rexi-api/rexi-py.svg)](https://github.com/rexi-api/rexi-py/blob/main/LICENSE)
  [![Build Status](https://img.shields.io/github/workflow/status/rexi-api/rexi-py/CI)](https://github.com/rexi-api/rexi-py/actions)
  [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
</div>

## Overview

Rexi Python API Client is a comprehensive toolkit for interacting with the Rexi API services, with a focus on Solana blockchain operations. Built with modern Python practices, the library offers a clean, intuitive async interface to access all Rexi API endpoints.

## Installation

```bash
# Once published to PyPI, you can install with:
# pip install rexi-py

# For now, install directly from the source:
# pip install git+https://github.com/yourusername/rexi-py.git
```

## Features

- Simple and intuitive async API
- Complete coverage of Rexi API endpoints
- Organized into logical modules for different API categories
- Built-in support for Solana blockchain operations
- Typed interface with Python type hints
- WebSocket support for real-time data

## Basic Usage

```python
import os
import asyncio
from rexi_py import RexiAPI

async def example():
    # Initialize Rexi API client
    rexi = RexiAPI({
        'api_key': os.environ.get('REXI_API_KEY')
    })
    
    # Get market statistics
    market_stats = await rexi.solana.get_market_stats()
    
    # Monitor wallet activity
    wallet_activity = await rexi.solana.monitor_wallet({
        'address': 'So11111111111111111111111111111111111111112',
        'timeout': 30
    })
    
    # Get token information
    token_info = await rexi.solana.get_token_info({
        'address': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'
    })
    
    print({
        'market_stats': market_stats,
        'wallet_activity': wallet_activity,
        'token_info': token_info
    })

# Run the async function
asyncio.run(example())
```

## API Reference

For detailed API documentation, please see the [documentation directory](docs/README.md), which contains comprehensive information about all available endpoints organized by functionality:

- [Market Analytics](docs/market-analytics.md)
- [Token Information](docs/token-information.md)
- [KOL Calls and Alerts](docs/kol-calls-alerts.md)
- [Wallet Monitoring](docs/wallet-monitoring.md)
- [Blockchain Data](docs/blockchain-data.md)
- [Real-time Data Streams](docs/realtime-data.md)

### RexiAPI

The main client class for interacting with the Rexi API.

```python
rexi = RexiAPI({
    'api_key': 'your_api_key_here'
})
```

Or use an environment variable:

```python
# Set REXI_API_KEY environment variable
import os
os.environ['REXI_API_KEY'] = 'your_api_key_here'

# Initialize without explicitly providing the key
rexi = RexiAPI()
```

For complete usage examples, see the `example.py` file in the project root.

## Complete Example

See the `example.py` file for a complete demonstration of all API endpoints.

## License

[MIT](LICENSE)
