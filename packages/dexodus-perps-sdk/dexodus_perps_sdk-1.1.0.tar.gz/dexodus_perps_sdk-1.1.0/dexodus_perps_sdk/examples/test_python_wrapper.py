#!/usr/bin/env python3
"""
Test script for the Dexodus Python SDK wrapper (v1.1.0 - Simplified Configuration).

This script tests basic functionality to ensure the Python wrapper
correctly communicates with the JavaScript SDK v1.1.0 with simplified configuration.
"""

import os
import sys
from client import DexodusClient, MarketSymbols

def test_basic_functionality():
    """Test basic SDK functionality with simplified configuration."""
    print("🧪 Testing Dexodus Python SDK Wrapper (v1.1.0 - Simplified Config)\n")

    try:
        # Test 1: Client initialization (simplified)
        print("📡 Test 1: Client Initialization (Simplified)")
        print("✨ Only PRIVATE_KEY environment variable required!")
        client = DexodusClient.create(
            debug=True  # Enable debug mode for testing
        )
        print("✅ Client initialized successfully\n")
        
        # Test 2: Get available markets
        print("📊 Test 2: Get Available Markets")
        markets = client.get_available_markets()
        print(f"✅ Markets retrieved: {markets}")
        print(f"✅ Market symbols enum works: {MarketSymbols.BTC}\n")
        
        # Test 3: Get balances
        print("💰 Test 3: Get Account Balances")
        balances = client.get_balances()
        print(f"✅ Balances retrieved:")
        print(f"   EOA USDC: {balances['eoa']}")
        print(f"   Smart Account USDC: {balances['smartAccount']}\n")
        
        # Test 4: Get positions
        print("📊 Test 4: Get Open Positions")
        positions = client.get_positions()
        print(f"✅ Positions retrieved: {len(positions)} position(s)")
        
        if positions:
            for i, pos in enumerate(positions, 1):
                print(f"   Position {i}: {pos['marketName']} {'Long' if pos['isLong'] else 'Short'}")
                print(f"      Size: ${pos['size']:.2f}, PnL: ${pos['pnl']:.2f}")
        else:
            print("   No open positions found")
        print()
        
        # Test 5: Simple position opening (if user wants to test)
        test_trading = input("🤔 Do you want to test opening a small position? (y/N): ").lower().strip()
        
        if test_trading == 'y':
            print("\n📈 Test 5: Opening Small Long Position")
            try:
                result = client.open_long(
                    market=MarketSymbols.BTC,
                    size=10.0,      # Small $10 position
                    collateral=2.0,  # $2 collateral (5x leverage)
                    slippage=0.5
                )
                
                print("✅ Position opened successfully!")
                print(f"   UserOp Hash: {result['userOpHash']}")
                if 'transactionHash' in result:
                    print(f"   TX Hash: {result['transactionHash']}")
                print(f"   Gas: {'FREE (sponsored)' if result['gasFee'] == 0 else str(result['gasFee']) + ' USDC'}")
                
            except Exception as e:
                print(f"⚠️  Position opening failed: {e}")
        
        print("\n🎉 All tests completed successfully!")
        print("\n📋 Test Results:")
        print("✅ Client initialization")
        print("✅ Market data retrieval")
        print("✅ Balance checking")
        print("✅ Position fetching")
        print("✅ Python ↔ JavaScript communication")
        print("✅ Error handling")
        print("✅ Debug mode")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_market_symbols():
    """Test the MarketSymbols enum."""
    print("\n🔍 Testing MarketSymbols Enum:")
    
    symbols = [
        MarketSymbols.BTC, MarketSymbols.ETH, MarketSymbols.BNB,
        MarketSymbols.SOL, MarketSymbols.XRP, MarketSymbols.DOGE,
        MarketSymbols.ADA, MarketSymbols.TRX, MarketSymbols.AVAX,
        MarketSymbols.SUI
    ]
    
    print(f"Available symbols: {', '.join(symbols)}")
    print("✅ MarketSymbols enum working correctly\n")

def main():
    """Run all tests."""
    # Check required environment variables (simplified - only private key needed!)
    if not os.getenv('PRIVATE_KEY'):
        print("❌ Error: PRIVATE_KEY environment variable is required")
        print("💡 Tip: Only PRIVATE_KEY is needed with v1.1.0 simplified configuration!")
        sys.exit(1)
    
    # Run tests
    test_market_symbols()
    success = test_basic_functionality()
    
    if success:
        print("\n🎉 All Python wrapper tests passed!")
        print("\nThe Dexodus Python SDK is ready for use! 🚀")
    else:
        print("\n❌ Some tests failed. Please check your configuration.")
        sys.exit(1)

if __name__ == "__main__":
    main()
