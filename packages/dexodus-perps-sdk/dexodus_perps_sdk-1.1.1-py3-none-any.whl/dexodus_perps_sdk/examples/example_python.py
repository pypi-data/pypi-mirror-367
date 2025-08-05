#!/usr/bin/env python3
"""
Dexodus Python SDK Example (v1.1.0 - Simplified Configuration)

This example demonstrates all the features of the Dexodus Python SDK with
simplified configuration - only private key required!

Features demonstrated:
- Simplified client initialization (only PRIVATE_KEY needed)
- Position management with sponsored gas
- Real-time data with PnL calculations
- Limit orders (Take Profit & Stop Loss)
- Fund management
"""

import os
import sys
from client import DexodusClient, MarketSymbols, create_client_from_env

def main():
    print("🚀 Dexodus Python SDK - Complete Example\n")
    
    try:
        # =================================================================
        # 1. INITIALIZE CLIENT (SIMPLIFIED v1.1.0)
        # =================================================================
        print("📡 Initializing Dexodus Client...")
        print("✨ Using simplified configuration - only private key required!")

        # Option 1: Create client from environment variables (recommended)
        client = create_client_from_env(debug=False)

        # Option 2: Create client with explicit private key
        # client = DexodusClient.create(
        #     private_key="your_private_key_here",
        #     debug=False  # Set to True for verbose logging
        # )
        
        print("✅ Client initialized successfully\n")
        
        # =================================================================
        # 2. CHECK AVAILABLE MARKETS
        # =================================================================
        print("📊 Available Markets:")
        markets = client.get_available_markets()
        print(f"Markets: {', '.join(markets)}")
        print(f"Using MarketSymbols enum: {MarketSymbols.BTC}, {MarketSymbols.ETH}")
        print()
        
        # =================================================================
        # 3. CHECK ACCOUNT BALANCES
        # =================================================================
        print("💰 Account Balances:")
        balances = client.get_balances()
        print(f"EOA USDC: {balances['eoa']}")
        print(f"Smart Account USDC: {balances['smartAccount']}")
        print()
        
        # =================================================================
        # 4. OPEN POSITIONS
        # =================================================================
        print("📈 Opening Long Position on BTC...")
        long_result = client.open_long(
            market=MarketSymbols.BTC,
            size=50.0,      # $50 position
            collateral=10.0, # $10 collateral (5x leverage)
            slippage=0.5    # 0.5% slippage
        )
        
        print(f"✅ Long position opened!")
        print(f"UserOp Hash: {long_result['userOpHash']}")
        if 'transactionHash' in long_result:
            print(f"TX Hash: {long_result['transactionHash']}")
            print(f"Success: {long_result['success']}")
        print(f"Gas Fee: {'FREE (sponsored)' if long_result['gasFee'] == 0 else str(long_result['gasFee']) + ' USDC'}")
        print()
        
        print("📉 Opening Short Position on ETH...")
        short_result = client.open_short(
            market=MarketSymbols.ETH,
            size=30.0,      # $30 position
            collateral=10.0, # $10 collateral (3x leverage)
            slippage=0.5
        )
        
        print(f"✅ Short position opened!")
        print(f"UserOp Hash: {short_result['userOpHash']}")
        print()
        
        # =================================================================
        # 5. GET POSITIONS WITH REAL-TIME DATA
        # =================================================================
        print("📊 Fetching Open Positions...")
        positions = client.get_positions()
        
        if positions:
            print(f"✅ Found {len(positions)} open position(s)")
            print()
            
            for i, position in enumerate(positions, 1):
                print(f"Position {i}: {position['marketName']} {'Long' if position['isLong'] else 'Short'}")
                print(f"  Size: ${position['size']:.2f}")
                print(f"  Collateral: ${position['collateral']:.2f}")
                print(f"  Leverage: {position['leverage']:.1f}x")
                print(f"  Entry Price: ${position['entryPrice']:.2f}")
                print(f"  Current Price: ${position['currentPrice']:.2f}")
                print(f"  PnL: ${position['pnl']:.2f} ({position['roe']:.2f}%)")
                if position['liquidationPrice']:
                    print(f"  Liquidation Price: ${position['liquidationPrice']:.2f}")
                print()
        else:
            print("📭 No open positions found")
            print()
        
        # =================================================================
        # 6. CREATE LIMIT ORDERS
        # =================================================================
        if positions:
            first_position = positions[0]
            print(f"🎯 Creating Take Profit order for {first_position['marketName']}...")
            
            # Calculate TP price (10% profit target)
            if first_position['isLong']:
                tp_price = first_position['entryPrice'] * 1.10  # 10% above entry
            else:
                tp_price = first_position['entryPrice'] * 0.90  # 10% below entry
            
            tp_result = client.create_take_profit(
                market=first_position['marketId'],
                is_long=first_position['isLong'],
                size_to_close=first_position['size'] / 2,  # Close half position
                limit_price=tp_price,
                slippage=0.5
            )
            
            print(f"✅ Take Profit order created!")
            print(f"UserOp Hash: {tp_result['userOpHash']}")
            print(f"Trigger Price: ${tp_price:.2f}")
            print()
            
            print(f"🛡️  Creating Stop Loss order for {first_position['marketName']}...")
            
            # Calculate SL price (5% loss limit)
            if first_position['isLong']:
                sl_price = first_position['entryPrice'] * 0.95  # 5% below entry
            else:
                sl_price = first_position['entryPrice'] * 1.05  # 5% above entry
            
            sl_result = client.create_stop_loss(
                market=first_position['marketId'],
                is_long=first_position['isLong'],
                size_to_close=first_position['size'],  # Close full position
                limit_price=sl_price,
                slippage=0.5
            )
            
            print(f"✅ Stop Loss order created!")
            print(f"UserOp Hash: {sl_result['userOpHash']}")
            print(f"Trigger Price: ${sl_price:.2f}")
            print()
        
        # =================================================================
        # 7. POSITION MODIFICATION EXAMPLE
        # =================================================================
        if positions:
            first_position = positions[0]
            print(f"📊 Increasing {first_position['marketName']} position...")
            
            increase_result = client.increase_position(
                market=first_position['marketId'],
                is_long=first_position['isLong'],
                size_delta=25.0,     # Add $25 to position
                collateral_delta=5.0, # Add $5 collateral
                slippage=0.5
            )
            
            print(f"✅ Position increased!")
            print(f"UserOp Hash: {increase_result['userOpHash']}")
            print()
        
        # =================================================================
        # 8. FINAL BALANCES
        # =================================================================
        print("💰 Final Account Balances:")
        final_balances = client.get_balances()
        print(f"EOA USDC: {final_balances['eoa']}")
        print(f"Smart Account USDC: {final_balances['smartAccount']}")
        print()
        
        print("🎉 Python SDK example completed successfully!")
        print()
        print("📋 Features Demonstrated:")
        print("✅ Client initialization with simplified config")
        print("✅ Position opening (long/short) with sponsored gas")
        print("✅ Real-time position data with PnL calculations")
        print("✅ Limit orders (Take Profit & Stop Loss)")
        print("✅ Position modification (increase/decrease)")
        print("✅ Balance management")
        print("✅ Market symbols enum for type safety")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
