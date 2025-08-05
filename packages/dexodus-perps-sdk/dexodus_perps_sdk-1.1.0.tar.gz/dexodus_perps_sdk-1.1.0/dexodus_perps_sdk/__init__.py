# dexodus_sdk/client.py
import subprocess
import json
import os
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Union

# Load environment variables from .env file
def load_env_file():
    """Load environment variables from .env file if it exists."""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

# Load .env file when module is imported
load_env_file()

# ##############################################################################
# Dexodus Python SDK (Wrapper)
#
# This SDK provides a native Python interface for the Dexodus perpetual futures
# trading platform. It acts as a wrapper, calling the core JavaScript SDK via
# a subprocess to handle all blockchain interactions.
#
# Features:
# - Position management (open, close, increase, decrease)
# - Real-time position data with PnL calculations
# - Limit orders (Take Profit & Stop Loss)
# - Market symbols enum for type safety
# - Debug mode support
# - Sponsored gas transactions
# ##############################################################################

# Market Symbols Enum (matches JavaScript MARKET_SYMBOLS)
class MarketSymbols:
    """Market symbols enum for IDE autocomplete and type safety."""
    BTC = "BTC"
    ETH = "ETH"
    BNB = "BNB"
    SOL = "SOL"
    XRP = "XRP"
    DOGE = "DOGE"
    ADA = "ADA"
    TRX = "TRX"
    AVAX = "AVAX"
    SUI = "SUI"

@dataclass
class TradeParams:
    """Parameters for position modification (legacy - use specific methods instead)."""
    collateral: float
    size: float
    is_long: bool
    is_increase: bool
    market: str
    slippage: float

@dataclass
class PositionParams:
    """Parameters for opening a position."""
    market: str
    size: float
    collateral: float
    slippage: float
    is_long: Optional[bool] = None  # For openPosition method

@dataclass
class ModifyPositionParams:
    """Parameters for modifying an existing position."""
    market: str
    is_long: bool
    size_delta: float
    slippage: float
    collateral_delta: Optional[float] = None

@dataclass
class LimitOrderParams:
    """Parameters for creating limit orders (TP/SL)."""
    market: str
    is_long: bool
    size_to_close: float
    limit_price: float
    slippage: float
    collateral_to_close: Optional[float] = 0

class DexodusClient:
    """
    A Python wrapper client for the Dexodus JavaScript SDK.

    Provides a native Python interface for perpetual futures trading on the
    Dexodus platform with sponsored gas transactions and real-time data.
    """

    def __init__(self, private_key: str = None, debug: bool = False):
        """
        Initialize the Dexodus client with simplified configuration.

        Args:
            private_key (str): Your EOA private key (optional, can use PRIVATE_KEY env var)
            debug (bool): Enable debug logging (default: False)
        """
        # Use environment variable if private_key not provided
        if private_key is None:
            private_key = os.getenv('PRIVATE_KEY')
            if not private_key:
                raise ValueError("Private key is required. Provide it via private_key parameter or PRIVATE_KEY environment variable.")

        self.config = {
            "privateKey": private_key,
            "debug": debug
        }

        # Find the path to the bundled JS runner script
        self.js_runner_path = os.path.join(os.path.dirname(__file__), 'runner.js')
        if not os.path.exists(self.js_runner_path):
            raise FileNotFoundError("Could not find the bundled JavaScript runner script.")

    @classmethod
    def create(cls, private_key: str = None, debug: bool = False):
        """
        Create a DexodusClient instance with simplified configuration (matches JavaScript SDK v1.1.0).

        Args:
            private_key (str): Your EOA private key (optional, can use PRIVATE_KEY env var)
            debug (bool): Enable debug logging (default: False)

        Returns:
            DexodusClient: Initialized client instance
        """
        return cls(private_key, debug)

    def _run_js_command(self, command: str, params: dict = None) -> dict:
        """
        A private helper to execute the JavaScript runner script.

        Args:
            command (str): The command for the runner to execute.
            params (dict): The parameters for the command (optional).

        Returns:
            dict: The JSON response from the JavaScript script.
        """
        # Serialize all configuration and parameters to JSON strings
        config_str = json.dumps(self.config)
        params_str = json.dumps(params or {})

        # Construct the command to execute with Node.js
        node_command = [
            'node',
            self.js_runner_path,
            command,
            config_str,
            params_str
        ]

        if self.config.get('debug', False):
            print(f"[DEBUG] Executing JS command: {command}")
            print(f"[DEBUG] Parameters: {params}")

        try:
            # Execute the command, capture stdout, and check for errors on stderr
            result = subprocess.run(
                node_command,
                capture_output=True,
                text=True,
                check=True,
                encoding='utf-8'
            )

            # The JS script prints its final result as a JSON string to stdout
            # Extract the JSON from the output (it's usually the last line)
            stdout_lines = result.stdout.strip().split('\n')
            json_line = stdout_lines[-1]  # Last line should be the JSON result

            if self.config.get('debug', False):
                print(f"[DEBUG] Raw stdout: {result.stdout}")
                print(f"[DEBUG] Extracted JSON: {json_line}")

            return json.loads(json_line)

        except subprocess.CalledProcessError as e:
            # If the JS script throws an error, it will be captured here
            error_msg = f"JavaScript SDK execution failed: {e.stderr}"
            if self.config.get('debug', False):
                print("Error executing JavaScript runner:")
                print("STDOUT:", e.stdout)
                print("STDERR:", e.stderr)
            raise Exception(error_msg)
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to decode JSON response from JavaScript SDK: {e}")

    # =============================================================================
    # POSITION MANAGEMENT METHODS
    # =============================================================================

    def open_long(self, market: str, size: float, collateral: float, slippage: float = 0.5) -> dict:
        """
        Open a long position (buy).

        Args:
            market (str): Market symbol (e.g., MarketSymbols.BTC or "BTC")
            size (float): Position size in USDC
            collateral (float): Collateral amount in USDC
            slippage (float): Slippage percentage (default: 0.5%)

        Returns:
            dict: Transaction result with userOpHash, transactionHash, success, gasFee
        """
        params = {
            "market": market,
            "size": size,
            "collateral": collateral,
            "slippage": slippage
        }
        return self._run_js_command('openLong', params)

    def open_short(self, market: str, size: float, collateral: float, slippage: float = 0.5) -> dict:
        """
        Open a short position (sell).

        Args:
            market (str): Market symbol (e.g., MarketSymbols.ETH or "ETH")
            size (float): Position size in USDC
            collateral (float): Collateral amount in USDC
            slippage (float): Slippage percentage (default: 0.5%)

        Returns:
            dict: Transaction result with userOpHash, transactionHash, success, gasFee
        """
        params = {
            "market": market,
            "size": size,
            "collateral": collateral,
            "slippage": slippage
        }
        return self._run_js_command('openShort', params)

    def open_position(self, market: str, is_long: bool, size: float, collateral: float, slippage: float = 0.5) -> dict:
        """
        Open a position (long or short).

        Args:
            market (str): Market symbol
            is_long (bool): True for long, False for short
            size (float): Position size in USDC
            collateral (float): Collateral amount in USDC
            slippage (float): Slippage percentage (default: 0.5%)

        Returns:
            dict: Transaction result
        """
        params = {
            "market": market,
            "isLong": is_long,
            "size": size,
            "collateral": collateral,
            "slippage": slippage
        }
        return self._run_js_command('openPosition', params)

    def increase_position(self, market: str, is_long: bool, size_delta: float,
                         collateral_delta: float = 0, slippage: float = 0.5) -> dict:
        """
        Increase an existing position size and/or collateral.

        Args:
            market (str): Market symbol
            is_long (bool): Position direction
            size_delta (float): Additional position size in USDC
            collateral_delta (float): Additional collateral in USDC (default: 0)
            slippage (float): Slippage percentage (default: 0.5%)

        Returns:
            dict: Transaction result
        """
        params = {
            "market": market,
            "isLong": is_long,
            "sizeDelta": size_delta,
            "collateralDelta": collateral_delta,
            "slippage": slippage
        }
        return self._run_js_command('increasePosition', params)

    def decrease_position(self, market: str, is_long: bool, size_delta: float, slippage: float = 0.5) -> dict:
        """
        Decrease an existing position size (partial close).

        Args:
            market (str): Market symbol
            is_long (bool): Position direction
            size_delta (float): Amount to reduce position size in USDC
            slippage (float): Slippage percentage (default: 0.5%)

        Returns:
            dict: Transaction result
        """
        params = {
            "market": market,
            "isLong": is_long,
            "sizeDelta": size_delta,
            "slippage": slippage
        }
        return self._run_js_command('decreasePosition', params)

    def get_positions(self) -> List[dict]:
        """
        Get all open positions with real-time data including PnL, ROE, and liquidation prices.

        Returns:
            List[dict]: List of position objects with the following structure:
                {
                    "positionId": str,           # Unique position identifier
                    "marketId": str,             # Market symbol (e.g., "BTC")
                    "marketName": str,           # Human-readable market name
                    "isLong": bool,              # Position direction
                    "size": float,               # Position size in USDC
                    "collateral": float,         # Collateral amount in USDC
                    "leverage": float,           # Calculated leverage
                    "entryPrice": float,         # Entry price
                    "currentPrice": float,       # Current market price
                    "liquidationPrice": float,   # Liquidation price
                    "pnl": float,               # Unrealized PnL in USDC
                    "roe": float,               # Return on equity in percentage
                    "trader": str               # Trader address
                }
        """
        return self._run_js_command('getPositions')

    # =============================================================================
    # LIMIT ORDER METHODS (Take Profit & Stop Loss)
    # =============================================================================

    def create_take_profit(self, market: str, is_long: bool, size_to_close: float,
                          limit_price: float, slippage: float = 0.5,
                          collateral_to_close: float = 0) -> dict:
        """
        Create a Take Profit order that automatically closes a position at a profit target.

        Args:
            market (str): Market symbol
            is_long (bool): Position direction
            size_to_close (float): Size to close when triggered (USDC)
            limit_price (float): Price to trigger TP
            slippage (float): Slippage percentage (default: 0.5%)
            collateral_to_close (float): Collateral to close (default: 0)

        Returns:
            dict: Transaction result
        """
        params = {
            "market": market,
            "isLong": is_long,
            "sizeToClose": size_to_close,
            "limitPrice": limit_price,
            "slippage": slippage,
            "collateralToClose": collateral_to_close
        }
        return self._run_js_command('createTakeProfit', params)

    def create_stop_loss(self, market: str, is_long: bool, size_to_close: float,
                        limit_price: float, slippage: float = 0.5,
                        collateral_to_close: float = 0) -> dict:
        """
        Create a Stop Loss order that automatically closes a position to limit losses.

        Args:
            market (str): Market symbol
            is_long (bool): Position direction
            size_to_close (float): Size to close when triggered (USDC)
            limit_price (float): Price to trigger SL
            slippage (float): Slippage percentage (default: 0.5%)
            collateral_to_close (float): Collateral to close (default: 0)

        Returns:
            dict: Transaction result
        """
        params = {
            "market": market,
            "isLong": is_long,
            "sizeToClose": size_to_close,
            "limitPrice": limit_price,
            "slippage": slippage,
            "collateralToClose": collateral_to_close
        }
        return self._run_js_command('createStopLoss', params)

    # =============================================================================
    # FUND MANAGEMENT METHODS
    # =============================================================================

    def deposit(self, amount: float) -> dict:
        """
        Transfer USDC from EOA to Smart Account.

        Args:
            amount (float): Amount of USDC to deposit

        Returns:
            dict: Transaction result with txHash
        """
        params = {"amount": amount}
        return self._run_js_command('deposit', params)

    def withdraw(self, amount: float) -> dict:
        """
        Transfer USDC from Smart Account to EOA. Gas paid in USDC via paymaster.

        Args:
            amount (float): Amount of USDC to withdraw

        Returns:
            dict: Transaction result with adjustedAmount and gasFee
        """
        params = {"amount": amount}
        return self._run_js_command('withdraw', params)

    def get_balances(self) -> dict:
        """
        Get USDC balances for both EOA and Smart Account.

        Returns:
            dict: Balance information with structure:
                {
                    "eoa": float,           # EOA USDC balance
                    "smartAccount": float   # Smart Account USDC balance
                }
        """
        return self._run_js_command('getBalances')

    # =============================================================================
    # UTILITY METHODS
    # =============================================================================

    def get_available_markets(self) -> List[str]:
        """
        Get list of supported trading markets.

        Returns:
            List[str]: List of market symbols (e.g., ["BTC", "ETH", "SOL", ...])
        """
        return self._run_js_command('getAvailableMarkets')

    # =============================================================================
    # LEGACY METHODS (for backward compatibility)
    # =============================================================================

    def modify_position(self, params: TradeParams) -> dict:
        """
        Legacy method for position modification (use specific methods instead).

        Args:
            params (TradeParams): Trade parameters

        Returns:
            dict: Transaction result
        """
        return self._run_js_command('modifyPosition', asdict(params))


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def create_client_from_env(debug: bool = False) -> DexodusClient:
    """
    Create a DexodusClient using environment variables (simplified configuration).

    Required environment variables:
    - PRIVATE_KEY: Your EOA private key

    Optional environment variables:
    - DEBUG: Debug mode (optional, default: False)

    Args:
        debug (bool): Override debug mode (default: False)

    Returns:
        DexodusClient: Initialized client instance
    """
    env_debug = os.getenv('DEBUG', 'false').lower() == 'true'

    return DexodusClient.create(
        debug=debug or env_debug
    )


# =============================================================================
# PACKAGE EXPORTS
# =============================================================================

__all__ = [
    'DexodusClient',
    'MarketSymbols',
    'TradeParams',
    'PositionParams',
    'ModifyPositionParams',
    'LimitOrderParams',
    'create_client_from_env'
]
