# dexodus-perps-sdk

Python SDK for Dexodus perpetual futures trading platform on Base.

## Features

- **Position Management**: Open, close, increase, and decrease positions
- **Real-Time Data**: Get positions with live PnL, ROE, and liquidation prices
- **Limit Orders**: Create Take Profit and Stop Loss orders
- **Sponsored Gas**: Free transactions for position management
- **Market Symbols Enum**: Type-safe market selection with IDE autocomplete
- **Debug Mode**: Verbose logging for development and troubleshooting
- **Streamlined Setup**: Minimal configuration required

## Installation

### Prerequisites

This package requires **Node.js 16+** to be installed on your system, as it uses the JavaScript SDK internally.

**Install Node.js:**
- **macOS**: `brew install node` or download from [nodejs.org](https://nodejs.org/)
- **Ubuntu/Debian**: `sudo apt install nodejs npm`
- **Windows**: Download from [nodejs.org](https://nodejs.org/)

**Install Node.js dependencies:**
```bash
npm install @pythnetwork/hermes-client @biconomy/account ethers dotenv
```

### Install Python Package

```bash
pip install dexodus-perps-sdk
```

## Quick Start

```python
from dexodus_perps_sdk import DexodusClient, MarketSymbols

# Initialize client (only private key required!)
client = DexodusClient.create(
    debug=False  # Optional: Set to True for verbose logging
)

# Open a long position
result = client.open_long(
    market=MarketSymbols.BTC,
    size=50.0,        # $50 position
    collateral=10.0,  # $10 collateral (5x leverage)
    slippage=0.5      # 0.5% slippage
)

print(f"Position opened! TX: {result['transactionHash']}")
```

## Configuration

The SDK requires only your private key for authentication. All network and contract configurations are pre-configured for the Base mainnet.

Set up your environment variables in a `.env` file:

```bash
# Required
PRIVATE_KEY=your_private_key_here

# Optional
DEBUG=false
```

**Network Configuration:**
- Network: Base mainnet (Chain ID: 8453)
- Gas Sponsorship: Enabled for position operations
- Contract Integration: Fully configured for Dexodus protocol

## API Reference

### Client Initialization

```python
# Initialize with private key
client = DexodusClient.create(
    private_key="your_private_key",  # Optional: uses PRIVATE_KEY env var if not provided
    debug=False  # Optional: Enable verbose logging
)

# Initialize using environment variable
client = DexodusClient.create()  # Uses PRIVATE_KEY from .env
```

### Position Management

```python
# Open positions
client.open_long(market=MarketSymbols.BTC, size=50, collateral=10, slippage=0.5)
client.open_short(market=MarketSymbols.ETH, size=30, collateral=10, slippage=0.5)

# Modify positions
client.increase_position(market=MarketSymbols.BTC, is_long=True, size_delta=25, slippage=0.5)
client.decrease_position(market=MarketSymbols.BTC, is_long=True, size_delta=30, slippage=0.5)

# Get positions with real-time data
positions = client.get_positions()
for pos in positions:
    print(f"{pos['marketName']} {pos['isLong'] and 'Long' or 'Short'}: ${pos['pnl']:.2f} PnL")
```

### Limit Orders

```python
# Take Profit
client.create_take_profit(
    market=MarketSymbols.BTC,
    is_long=True,
    size_to_close=25.0,
    limit_price=50000.0,
    slippage=0.5
)

# Stop Loss
client.create_stop_loss(
    market=MarketSymbols.BTC,
    is_long=True,
    size_to_close=50.0,
    limit_price=40000.0,
    slippage=0.5
)
```

### Fund Management

```python
# Deposit/withdraw USDC
client.deposit(100.0)  # Deposit $100 USDC
client.withdraw(50.0)  # Withdraw $50 USDC

# Check balances
balances = client.get_balances()
print(f"Smart Account: ${balances['smartAccount']} USDC")
```

## Market Symbols

Use the `MarketSymbols` class for type safety:

```python
from dexodus_perps_sdk import MarketSymbols

# Available markets
MarketSymbols.BTC    # "BTC"
MarketSymbols.ETH    # "ETH"
MarketSymbols.SOL    # "SOL"
# ... and more
```

## Gas Fees

- **Position Operations**: FREE (sponsored by protocol)
- **Withdrawals**: Paid in USDC (deducted from withdrawal amount)
- **Deposits**: Standard ETH gas fees

## Testing

Test your installation:

```bash
# Run the built-in test
dexodus-perps-test

# Or in Python
python -c "from dexodus_perps_sdk import MarketSymbols; print('SDK installed correctly!')"
```

## Requirements

- **Python**: 3.7+
- **Node.js**: 16+ (required for JavaScript SDK)
- **Network**: Base network access
- **Funds**: USDC for trading

## Support

- **Documentation**: https://docs.dexodus.com/sdk
- **Issues**: https://github.com/dexodus/perps-sdk-python/issues
- **Discord**: https://discord.gg/dexodus
- **JavaScript SDK**: https://www.npmjs.com/package/dexodus-perps-sdk

## License

MIT
