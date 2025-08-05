// dexodus-sdk-js/index.js

import { JsonRpcProvider, Wallet, AbiCoder, keccak256 } from "ethers";
import { createSmartAccountClient } from "@biconomy/account";
import { PaymasterMode } from "@biconomy/account";
import { HermesClient } from "@pythnetwork/hermes-client";
import dotenv from "dotenv";

dotenv.config();

// Import the Dexodus contract ABI from external file
import { DEXODUS_ABI } from "./dexodusAbi.js";
import { AutomationOrdersABI } from "./automationOrdersAbi.js";
import { getMarket, floatToBigInt, getAvailableMarkets, MARKET_SYMBOLS } from "./markets.js";

// Re-export market symbols for easy access
export { MARKET_SYMBOLS };

// Hardcoded configuration constants for simplified setup
const CHAIN_ID = 8453; // Base mainnet
const RPC_URL = "https://base-mainnet.g.alchemy.com/v2/R3MdlNixdW5-SXS419br4OjvQ-pzbLpd";
const BICONOMY_PAYMASTER_API_KEY = "xSulX287S.6bff9b2d-61a2-4fa3-b6e0-0d4a08ea8857";
const BUNDLER_URL = "https://bundler.biconomy.io/api/v2/8453/01945ec7-4878-747a-a547-22a71e096667";

// Contract addresses (same for all users on Base mainnet)
const CONTRACT_ADDRESSES = {
  DEXODUS: "0xA62C31A48aD402245eAa8B9D3a5D2f1e61e74e06",
  USDC: "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
  AUTOMATION_ORDERS: "0x89DBAfa4af7d25e78160aAA10a5EDdc7A98baA6e"
};

// USDC ABI (minimal for approve/transfer)
const USDC_ABI = [
  "function approve(address spender, uint256 amount) external returns (bool)",
  "function transfer(address to, uint256 amount) external returns (bool)",
  "function balanceOf(address owner) view returns (uint256)",
  "function decimals() view returns (uint8)",
];

export class DexodusClient {
  #smartAccount;
  #dexodusContract;
  #usdcContract;
  #automationOrdersContract;
  #provider;
  #signer;
  #biconomyAddress;
  #debug;

  /**
   * Initializes the DexodusClient with simplified configuration.
   * @param {object} config - The configuration object.
   * @param {string} config.privateKey - The user's EOA private key (required).
   * @param {boolean} config.debug - Enable debug logging (default: false).
   */
  static async create(config = {}) {
    // Simplified config - only privateKey is required, everything else is hardcoded
    const finalConfig = {
      privateKey: process.env.PRIVATE_KEY || config.privateKey,
      chainId: CHAIN_ID,
      biconomyPaymasterApiKey: BICONOMY_PAYMASTER_API_KEY,
      bundlerUrl: BUNDLER_URL,
      rpcUrl: RPC_URL,
      debug: config.debug || process.env.DEBUG === 'true' || false,
      // Use hardcoded contract addresses (same for all users)
      dexodusContractAddress: CONTRACT_ADDRESSES.DEXODUS,
      dexodusContractAbi: DEXODUS_ABI,
      usdcAddress: CONTRACT_ADDRESSES.USDC,
      automationOrdersAddress: CONTRACT_ADDRESSES.AUTOMATION_ORDERS,
      automationOrdersAbi: AutomationOrdersABI,
    };

    if (!finalConfig.privateKey) {
      throw new Error("Private key is required. Provide it via config.privateKey or PRIVATE_KEY environment variable.");
    }
    const client = new DexodusClient();
    await client._init(finalConfig);
    return client;
  }

  /**
   * Debug logging - only logs when debug mode is enabled
   * @private
   */
  _debugLog(...args) {
    if (this.#debug) {
      console.log('[DEBUG]', ...args);
    }
  }

  /**
   * Info logging - always logs important user-facing messages
   * @private
   */
  _infoLog(...args) {
    console.log(...args);
  }

  /**
   * Error logging - always logs errors
   * @private
   */
  _errorLog(...args) {
    console.error(...args);
  }

  async _init(config) {
    // Initialize debug mode
    this.#debug = config.debug;

    this._debugLog('Initializing DexodusClient with config:', {
      chainId: config.chainId,
      debug: config.debug,
      bundlerUrl: config.bundlerUrl
    });

    // 1. Set up the Ethers provider and signer
    this.#provider = new JsonRpcProvider(config.rpcUrl);
    this.#signer = new Wallet(config.privateKey, this.#provider);
    this._debugLog('Provider and signer created');

    // 2. Create the Biconomy Smart Account using the new API
    this.#smartAccount = await createSmartAccountClient({
      signer: this.#signer,
      bundlerUrl: config.bundlerUrl,
      biconomyPaymasterApiKey: config.biconomyPaymasterApiKey,
    });
    this.#biconomyAddress = await this.#smartAccount.getAccountAddress();
    this._debugLog('Smart Account created, address:', this.#biconomyAddress);

    // 3. Create contract instances
    const { Contract } = await import("ethers");
    this._debugLog('Creating contracts...');
    this._debugLog('Contract addresses:', {
      dexodus: config.dexodusContractAddress,
      usdc: config.usdcAddress,
      automationOrders: config.automationOrdersAddress
    });

    try {
      this.#dexodusContract = new Contract(
        config.dexodusContractAddress,
        config.dexodusContractAbi,
        this.#provider
      );
      this._debugLog('Dexodus Contract created successfully');
    } catch (error) {
      this._errorLog('Error creating Dexodus contract:', error);
      throw error;
    }

    try {
      this.#usdcContract = new Contract(
        config.usdcAddress,
        USDC_ABI,
        this.#provider
      );
      this._debugLog('USDC Contract created successfully');
    } catch (error) {
      this._errorLog('Error creating USDC contract:', error);
      throw error;
    }

    try {
      this.#automationOrdersContract = new Contract(
        config.automationOrdersAddress,
        config.automationOrdersAbi,
        this.#provider
      );
      this._debugLog('AutomationOrders Contract created successfully');
    } catch (error) {
      this._errorLog('Error creating AutomationOrders contract:', error);
      throw error;
    }

  }

  /**
   * Modifies a perpetual position on the Dexodus exchange.
   * @param {object} params - The trade parameters.
   * @param {number} params.collateral - The collateral amount.
   * @param {number} params.size - The position size.
   * @param {boolean} params.isLong - True for a long position, false for short.
   * @param {boolean} params.isIncrease - True to open/increase, false to close/reduce.
   * @param {string} params.market - The market symbol (e.g., "BTC", "ETH").
   * @param {number} params.slippage - Slippage percentage (e.g., 0.5 for 0.5%).
   * @returns {Promise<object>} The response from the Biconomy Bundler.
   */
  async modifyPosition(params) {
    if (!this.#smartAccount || !this.#dexodusContract) {
      throw new Error("SDK not initialized. Please use DexodusClient.create()");
    }

    this._debugLog('Position modification params:', params);

    // Get market configuration
    const market = getMarket(params.market);
    this._debugLog('Using market:', market);

    // Initialize Hermes client and fetch current price
    const hermesClient = new HermesClient("https://hermes.pyth.network", {});
    this._debugLog('Fetching latest price from Hermes...');

    const priceUpdates = await hermesClient.getLatestPriceUpdates([market.priceID]);

    let updatesToSend = [];
    if (priceUpdates.binary.data) {
      // Loop each priceUpdate and append "0x" at the start
      updatesToSend = priceUpdates.binary.data.map((update) => {
        return "0x" + update;
      });
    }

    // Get current price from the price update
    const currentPrice = priceUpdates.parsed?.[0]?.price?.price;
    if (!currentPrice) {
      throw new Error(`Failed to fetch current price for ${params.market}`);
    }

    // Convert price to the correct format (Pyth prices are in different exponents)
    const priceExponent = priceUpdates.parsed[0].price.expo;
    const formattedPrice = currentPrice * Math.pow(10, priceExponent);

    this._debugLog(`Current ${params.market} price: $${formattedPrice}`);
    this._debugLog('Price updates to send:', updatesToSend.length);

    // Convert amounts to proper format using floatToBigInt (6 decimals for USDC)
    const collateralBigInt = floatToBigInt(params.collateral, 6);
    const sizeBigInt = floatToBigInt(params.size, 6);
    const priceBigInt = floatToBigInt(formattedPrice, 6);
    const slippageBasisPoints = Math.round((params.slippage / 100) * 10000);

    this._debugLog('Transaction parameters:', {
      collateral: `${collateralBigInt.toString()} (${params.collateral} USDC)`,
      size: `${sizeBigInt.toString()} (${params.size} USDC)`,
      price: `${priceBigInt.toString()} ($${formattedPrice})`,
      slippage: `${slippageBasisPoints} basis points (${params.slippage}%)`,
      marketKey: market.marketKey
    });

    // 1. Encode the calldata for the smart contract function using interface
    const txData = this.#dexodusContract.interface.encodeFunctionData('modifyPosition', [
      collateralBigInt,
      sizeBigInt,
      params.isLong,
      params.isIncrease,
      market.marketKey,
      priceBigInt,
      slippageBasisPoints,
      updatesToSend
    ]);

    const tx = {
      to: this.#dexodusContract.target,
      data: txData
    };

    try {
      // Send transaction with sponsored gas (gas tank) - no user payment required
      this._debugLog('Sending position modification transaction with sponsored gas...');
      const userOpResponse = await this.#smartAccount.sendTransaction(tx, {
        paymasterServiceData: { mode: PaymasterMode.SPONSORED },
      });

      this._debugLog('UserOp submitted with hash:', userOpResponse.userOpHash);
      this._debugLog('Waiting for transaction confirmation...');

      try {
        const transactionDetails = await userOpResponse.wait();

        return {
          userOpHash: userOpResponse.userOpHash,
          transactionHash: transactionDetails.receipt.transactionHash,
          gasFee: 0, // Gas is sponsored, no cost to user
          success: transactionDetails.success === "true"
        };
      } catch (waitError) {
        if (waitError.message.includes('Exceeded maximum duration')) {
          console.log('⚠️  Transaction is taking longer than expected to confirm.');
          console.log('UserOp Hash:', userOpResponse.userOpHash);
          console.log('You can check the transaction status manually using the userOp hash.');

          return {
            userOpHash: userOpResponse.userOpHash,
            transactionHash: null,
            gasFee: 0, // Gas is sponsored, no cost to user
            success: null,
            pending: true,
            message: 'Transaction submitted but confirmation timed out. Check status manually.'
          };
        }
        throw waitError;
      }

    } catch (error) {
      console.error('Error in modifyPosition:', error);
      throw error;
    }
  }

  /**
   * Deposit USDC from EOA to Smart Account
   * @param {number|string} amount - Amount in USDC (decimals will be handled)
   */
  async deposit(amount) {
    const decimals = Number(await this.#usdcContract.decimals());
    const value = BigInt(Math.round(Number(amount) * 10 ** decimals));
    // Approve and transfer USDC to smart account
    const tx = await this.#usdcContract
      .connect(this.#signer)
      .transfer(this.#biconomyAddress, value);
    await tx.wait();
    return { txHash: tx.hash };
  }

  /**
   * Withdraw USDC from Smart Account to EOA using paymaster (gas paid in USDC)
   * @param {number|string} amount - Amount in USDC (decimals will be handled)
   */
  async withdraw(amount) {
    if (!this.#usdcContract) {
      throw new Error('USDC contract not initialized. Please check your USDC_ADDRESS in .env');
    }

    const decimals = Number(await this.#usdcContract.decimals());
    let value = BigInt(Math.round(Number(amount) * 10 ** decimals));

    // Build initial transaction for USDC transfer
    const txData = this.#usdcContract.interface.encodeFunctionData('transfer', [
      this.#signer.address,
      value
    ]);

    const tx = {
      to: this.#usdcContract.target,
      data: txData
    };

    try {
      // Get fee quotes using ERC20 paymaster mode
      console.log('Getting fee quotes for withdrawal...');
      const feeQuotesResponse = await this.#smartAccount.getTokenFees(tx, {
        paymasterServiceData: { mode: PaymasterMode.ERC20 },
      });

      // Find USDC fee quote
      const usdcFeeQuote = feeQuotesResponse.feeQuotes?.find(
        (quote) => quote.symbol === "USDC"
      );

      if (!usdcFeeQuote) {
        throw new Error('USDC fee quote not available from paymaster');
      }

      console.log('USDC fee quote:', usdcFeeQuote);

      // Get current smart account USDC balance
      const smartAccountBalance = await this.#usdcContract.balanceOf(this.#biconomyAddress);
      const smartAccountBalanceFormatted = Number(smartAccountBalance) / (10 ** decimals);

      // Adjust withdrawal amount to account for gas fees
      let adjustedQuantity = Number(amount);
      const maxGasFee = parseFloat(usdcFeeQuote.maxGasFee);

      if (maxGasFee > smartAccountBalanceFormatted - adjustedQuantity) {
        adjustedQuantity = smartAccountBalanceFormatted - maxGasFee;
        if (adjustedQuantity <= 0) {
          throw new Error("Insufficient balance to cover gas fees");
        }
        console.log(`Adjusted withdrawal amount to ${adjustedQuantity} USDC to cover gas fees`);
      }

      // Update transaction with adjusted amount
      const adjustedValue = BigInt(Math.round(adjustedQuantity * 10 ** decimals));
      const updatedTxData = this.#usdcContract.interface.encodeFunctionData('transfer', [
        this.#signer.address,
        adjustedValue
      ]);

      const updatedTx = {
        to: this.#usdcContract.target,
        data: updatedTxData
      };

      // Send transaction with paymaster
      console.log('Sending withdrawal transaction with paymaster...');
      const userOpResponse = await this.#smartAccount.sendTransaction(updatedTx, {
        paymasterServiceData: {
          mode: PaymasterMode.ERC20,
          feeQuote: usdcFeeQuote,
          spender: feeQuotesResponse.tokenPaymasterAddress,
          maxApproval: true,
        },
      });

      console.log('UserOp submitted with hash:', userOpResponse.userOpHash);
      console.log('Waiting for transaction confirmation...');

      try {
        const transactionDetails = await userOpResponse.wait();

        return {
          userOpHash: userOpResponse.userOpHash,
          transactionHash: transactionDetails.receipt.transactionHash,
          adjustedAmount: adjustedQuantity,
          gasFee: maxGasFee,
          success: transactionDetails.success === "true"
        };
      } catch (waitError) {
        if (waitError.message.includes('Exceeded maximum duration')) {
          console.log('⚠️  Transaction is taking longer than expected to confirm.');
          console.log('UserOp Hash:', userOpResponse.userOpHash);
          console.log('You can check the transaction status manually using the userOp hash.');

          return {
            userOpHash: userOpResponse.userOpHash,
            transactionHash: null,
            adjustedAmount: adjustedQuantity,
            gasFee: maxGasFee,
            success: null,
            pending: true,
            message: 'Transaction submitted but confirmation timed out. Check status manually.'
          };
        }
        throw waitError;
      }

    } catch (error) {
      if (error.message.includes("Insufficient balance to cover gas fees")) {
        throw new Error("Insufficient USDC balance to cover gas fees for withdrawal");
      }
      throw error;
    }
  }

  /**
   * Get USDC balances for EOA and Smart Account
   */
  async getBalances() {
    const decimals = Number(await this.#usdcContract.decimals());
    const eoaBal = await this.#usdcContract.balanceOf(this.#signer.address);
    const smartBal = await this.#usdcContract.balanceOf(this.#biconomyAddress);
    return {
      eoa: Number(eoaBal) / (10 ** decimals),
      smartAccount: Number(smartBal) / (10 ** decimals),
    };
  }

  /**
   * Get the smart account address
   */
  async getSmartAccountAddress() {
    return this.#biconomyAddress;
  }

  /**
   * Get ETH balance of the smart account
   */
  async getETHBalance() {
    const balance = await this.#provider.getBalance(this.#biconomyAddress);
    return Number(balance) / 10 ** 18; // Convert from wei to ETH
  }

  /**
   * Get available markets for trading
   */
  getAvailableMarkets() {
    return getAvailableMarkets();
  }

  /**
   * Get market information by symbol
   */
  getMarketInfo(symbol) {
    return getMarket(symbol);
  }

  // =============================================================================
  // POSITION MANAGEMENT FUNCTIONS
  // =============================================================================

  /**
   * Get all open positions for the connected account
   * @returns {Promise<Array>} Array of position objects with calculated PnL, leverage, etc.
   */
  async getPositions() {
    if (!this.#smartAccount || !this.#dexodusContract) {
      throw new Error("SDK not initialized. Please use DexodusClient.create()");
    }

    try {
      this._debugLog('Fetching positions for account:', this.#biconomyAddress);

      // Get all available markets to check positions for
      const availableMarkets = getAvailableMarkets();
      const markets = availableMarkets.map(symbol => getMarket(symbol));

      // Create position keys for both long and short positions for each market
      const positionKeys = [];
      markets.forEach((market) => {
        positionKeys.push(this._encodePositionKey(this.#biconomyAddress, market.marketKey, true));  // Long
        positionKeys.push(this._encodePositionKey(this.#biconomyAddress, market.marketKey, false)); // Short
      });

      this._debugLog('Checking positions for', positionKeys.length, 'position keys...');

      // Call the smart contract to get positions data
      const positionsData = await this.#dexodusContract.getPositionsData(positionKeys);

      // Process the raw positions data
      const positions = [];
      positionsData.forEach((positionData, index) => {
        const marketIndex = Math.floor(index / 2);
        const isLong = index % 2 === 0;
        const market = markets[marketIndex];

        // Only include positions with collateral > 0 (active positions)
        const collateral = Number(positionData.collateral) / 1e6; // Convert from 6 decimals
        if (collateral > 0) {
          const size = Number(positionData.size) / 1e6;
          const entryPrice = Number(positionData.price) / 1e6;

          positions.push({
            positionId: positionKeys[index],
            marketId: market.symbol,
            marketKey: market.marketKey,
            marketName: market.symbol,
            isLong: isLong,
            size: size,
            collateral: collateral,
            leverage: size / collateral,
            entryPrice: entryPrice,
            trader: this.#biconomyAddress
          });
        }
      });

      this._debugLog(`Found ${positions.length} open positions`);

      // Enhance positions with current prices and PnL calculations
      const enhancedPositions = await this._enhancePositionsWithPrices(positions);

      return enhancedPositions;

    } catch (error) {
      this._errorLog('Error fetching positions:', error);
      throw error;
    }
  }

  // =============================================================================
  // USER-FRIENDLY WRAPPER FUNCTIONS
  //
  // These wrapper functions provide a much better developer experience by:
  // 1. Using intuitive action names (openPosition, closePosition, etc.)
  // 2. Hiding complex boolean flags (isIncrease, isLong combinations)
  // 3. Providing clear parameter names (sizeDelta vs size)
  // 4. Offering convenience methods for common actions (openLong, openShort)
  // =============================================================================

  /**
   * Open a new position (long or short)
   * @param {object} params - The position parameters
   * @param {string} params.market - Market symbol (e.g., "BTC", "ETH")
   * @param {boolean} params.isLong - True for long, false for short
   * @param {number} params.size - Position size in USDC
   * @param {number} params.collateral - Collateral amount in USDC
   * @param {number} params.slippage - Slippage percentage (e.g., 0.5 for 0.5%)
   * @returns {Promise<object>} Transaction result
   */
  async openPosition(params) {
    return this.modifyPosition({
      market: params.market,
      isLong: params.isLong,
      size: params.size,
      collateral: params.collateral,
      slippage: params.slippage,
      isIncrease: true
    });
  }

  /**
   * Close an existing position (requires fetching current position data)
   * @param {object} params - The close parameters
   * @param {string} params.market - Market symbol (e.g., "BTC", "ETH")
   * @param {boolean} params.isLong - True for long, false for short
   * @param {number} params.slippage - Slippage percentage (e.g., 0.5 for 0.5%)
   * @returns {Promise<object>} Transaction result
   */
  async closePosition(params) {
    // Note: In a full implementation, you would fetch the current position size
    // For now, we'll require the user to provide the size or implement position fetching
    throw new Error("closePosition requires position fetching implementation. Use modifyPosition with isIncrease: false and the full position size for now.");
  }

  /**
   * Increase an existing position
   * @param {object} params - The increase parameters
   * @param {string} params.market - Market symbol (e.g., "BTC", "ETH")
   * @param {boolean} params.isLong - True for long, false for short
   * @param {number} params.sizeDelta - Additional position size in USDC
   * @param {number} params.collateralDelta - Additional collateral in USDC
   * @param {number} params.slippage - Slippage percentage (e.g., 0.5 for 0.5%)
   * @returns {Promise<object>} Transaction result
   */
  async increasePosition(params) {
    return this.modifyPosition({
      market: params.market,
      isLong: params.isLong,
      size: params.sizeDelta,
      collateral: params.collateralDelta,
      slippage: params.slippage,
      isIncrease: true
    });
  }

  /**
   * Decrease an existing position
   * @param {object} params - The decrease parameters
   * @param {string} params.market - Market symbol (e.g., "BTC", "ETH")
   * @param {boolean} params.isLong - True for long, false for short
   * @param {number} params.sizeDelta - Amount to decrease position size in USDC
   * @param {number} params.slippage - Slippage percentage (e.g., 0.5 for 0.5%)
   * @returns {Promise<object>} Transaction result
   */
  async decreasePosition(params) {
    return this.modifyPosition({
      market: params.market,
      isLong: params.isLong,
      size: params.sizeDelta,
      collateral: 0, // No collateral change when decreasing
      slippage: params.slippage,
      isIncrease: false
    });
  }

  // =============================================================================
  // CONVENIENCE METHODS FOR COMMON ACTIONS
  // =============================================================================

  /**
   * Open a long position
   * @param {object} params - Position parameters
   * @param {string} params.market - Market symbol
   * @param {number} params.size - Position size in USDC
   * @param {number} params.collateral - Collateral amount in USDC
   * @param {number} params.slippage - Slippage percentage
   */
  async openLong(params) {
    return this.openPosition({ ...params, isLong: true });
  }

  /**
   * Open a short position
   * @param {object} params - Position parameters
   * @param {string} params.market - Market symbol
   * @param {number} params.size - Position size in USDC
   * @param {number} params.collateral - Collateral amount in USDC
   * @param {number} params.slippage - Slippage percentage
   */
  async openShort(params) {
    return this.openPosition({ ...params, isLong: false });
  }

  /**
   * Close a long position
   * @param {object} params - Close parameters
   * @param {string} params.market - Market symbol
   * @param {number} params.slippage - Slippage percentage
   */
  async closeLong(params) {
    return this.closePosition({ ...params, isLong: true });
  }

  /**
   * Close a short position
   * @param {object} params - Close parameters
   * @param {string} params.market - Market symbol
   * @param {number} params.slippage - Slippage percentage
   */
  async closeShort(params) {
    return this.closePosition({ ...params, isLong: false });
  }

  // =============================================================================
  // POSITION HELPER FUNCTIONS
  // =============================================================================

  /**
   * Encode a position key for smart contract calls
   * @private
   */
  _encodePositionKey(owner, marketKey, isLong) {
    // This exactly matches the frontend's encodePositionKey function
    // Encode the parameters using ABI encoding, then hash to get bytes32
    const abiCoder = AbiCoder.defaultAbiCoder();
    const encodedParams = abiCoder.encode(
      ["address", "bytes32", "bool"],
      [owner, marketKey, isLong]
    );

    // Hash the encoded parameters to get a bytes32 position key
    return keccak256(encodedParams);
  }

  /**
   * Enhance positions with current prices and calculated values
   * @private
   */
  async _enhancePositionsWithPrices(positions) {
    if (positions.length === 0) return positions;

    // Get current prices for all markets
    const { HermesClient } = await import('@pythnetwork/hermes-client');
    const hermesClient = new HermesClient("https://hermes.pyth.network", {});

    // Get unique markets from positions
    const uniqueMarkets = [...new Set(positions.map(p => p.marketId))];
    const marketConfigs = uniqueMarkets.map(symbol => getMarket(symbol));
    const priceIds = marketConfigs.map(market => market.priceID);

    this._debugLog('Fetching current prices for markets:', uniqueMarkets);

    try {
      const priceUpdates = await hermesClient.getLatestPriceUpdates(priceIds);
      const currentPrices = {};

      // Parse prices from Hermes response
      priceUpdates.parsed?.forEach((priceData, index) => {
        const marketSymbol = uniqueMarkets[index];
        const price = priceData.price.price;
        const expo = priceData.price.expo;
        currentPrices[marketSymbol] = price * Math.pow(10, expo);
      });

      // Enhance each position with current price and calculations
      const enhancedPositions = await Promise.all(positions.map(async (position) => {
        const currentPrice = currentPrices[position.marketId] || 0;

        // Calculate PnL
        const pnl = this._calculatePnL(position, currentPrice);
        const roe = (pnl / position.collateral) * 100;

        // Get liquidation price
        const liquidationPrice = await this._getLiquidationPrice(position);

        return {
          ...position,
          currentPrice,
          pnl,
          roe,
          liquidationPrice
        };
      }));

      return enhancedPositions;

    } catch (error) {
      this._debugLog('Error fetching current prices:', error.message);
      // Return positions without price data if price fetching fails
      return positions.map(position => ({
        ...position,
        currentPrice: 0,
        pnl: 0,
        roe: 0,
        liquidationPrice: null
      }));
    }
  }

  /**
   * Calculate PnL for a position
   * @private
   */
  _calculatePnL(position, currentPrice) {
    if (!currentPrice || currentPrice === 0) return 0;

    const priceChange = currentPrice - position.entryPrice;
    const pnl = position.isLong
      ? (priceChange / position.entryPrice) * position.size
      : (-priceChange / position.entryPrice) * position.size;

    return pnl;
  }

  /**
   * Get liquidation price for a position
   * @private
   */
  async _getLiquidationPrice(position) {
    try {
      const data = await this.#dexodusContract.calcLiquidationPrice(
        position.positionId,
        position.marketKey,
        0,
        position.isLong
      );

      // Return the liquidation price (first element, converted from 6 decimals)
      return Number(data[0]) / 1e6;

    } catch (error) {
      this._debugLog('Error calculating liquidation price for position:', position.positionId, error.message);
      return null;
    }
  }

  // =============================================================================
  // LIMIT ORDER FUNCTIONS (Take Profit & Stop Loss)
  // =============================================================================

  /**
   * Create a Take Profit order for an existing position
   * @param {object} params - Take profit parameters
   * @param {string} params.market - Market symbol (e.g., "BTC", "ETH")
   * @param {boolean} params.isLong - Position direction (true for long, false for short)
   * @param {number} params.sizeToClose - Size to close when TP is triggered (USDC)
   * @param {number} params.collateralToClose - Collateral to close (USDC, usually 0 for TP)
   * @param {number} params.limitPrice - Price at which to trigger the TP
   * @param {number} params.slippage - Slippage percentage (e.g., 0.5 for 0.5%)
   * @returns {Promise<object>} Transaction result
   */
  async createTakeProfit(params) {
    return this._createLimitOrder({
      ...params,
      orderType: 'tp'
    });
  }

  /**
   * Create a Stop Loss order for an existing position
   * @param {object} params - Stop loss parameters
   * @param {string} params.market - Market symbol (e.g., "BTC", "ETH")
   * @param {boolean} params.isLong - Position direction (true for long, false for short)
   * @param {number} params.sizeToClose - Size to close when SL is triggered (USDC)
   * @param {number} params.collateralToClose - Collateral to close (USDC, usually 0 for SL)
   * @param {number} params.limitPrice - Price at which to trigger the SL
   * @param {number} params.slippage - Slippage percentage (e.g., 0.5 for 0.5%)
   * @returns {Promise<object>} Transaction result
   */
  async createStopLoss(params) {
    return this._createLimitOrder({
      ...params,
      orderType: 'sl'
    });
  }

  /**
   * Internal function to create limit orders (TP/SL)
   * @private
   */
  async _createLimitOrder(params) {
    const { market, isLong, sizeToClose, collateralToClose = 0, limitPrice, slippage, orderType } = params;

    if (!this.#smartAccount || !this.#dexodusContract) {
      throw new Error("SDK not initialized. Please use DexodusClient.create()");
    }

    // Validate parameters
    if (!market || typeof isLong !== 'boolean' || !sizeToClose || !limitPrice || !slippage) {
      throw new Error("Missing required parameters for limit order");
    }

    if (!['tp', 'sl'].includes(orderType)) {
      throw new Error("Order type must be 'tp' (take profit) or 'sl' (stop loss)");
    }

    try {
      this._debugLog(`Creating ${orderType.toUpperCase()} order with params:`, {
        market,
        isLong,
        sizeToClose,
        collateralToClose,
        limitPrice,
        slippage,
        orderType
      });

      // Get market configuration
      const marketConfig = getMarket(market);
      if (!marketConfig) {
        throw new Error(`Market ${market} not found`);
      }

      // Get current market price for validation
      const { HermesClient } = await import('@pythnetwork/hermes-client');
      const hermesClient = new HermesClient("https://hermes.pyth.network", {});
      const priceUpdates = await hermesClient.getLatestPriceUpdates([marketConfig.priceID]);

      let currentPrice = 0;
      if (priceUpdates.parsed && priceUpdates.parsed.length > 0) {
        const priceData = priceUpdates.parsed[0];
        const price = priceData.price.price;
        const expo = priceData.price.expo;
        currentPrice = price * Math.pow(10, expo);
      }

      // Validate limit price against current market price
      const priceValidation = this._validateLimitPrice(limitPrice, currentPrice, isLong, orderType);
      if (priceValidation !== 'ok') {
        throw new Error(priceValidation);
      }

      this._debugLog(`Current ${market} price: $${currentPrice}`);
      this._debugLog(`${orderType.toUpperCase()} trigger price: $${limitPrice}`);

      // Prepare transaction data for AutomationOrders.order()
      const orderTypeValue = orderType === 'tp' ? 1 : 2; // 1 = TP, 2 = SL
      const slippageBasisPoints = Math.round((slippage / 100) * 10000); // Convert to basis points

      // Encode the function call
      const { Contract } = await import("ethers");
      const automationOrdersInterface = new Contract(
        "0x0000000000000000000000000000000000000000", // Dummy address for interface
        AutomationOrdersABI
      ).interface;

      const orderCallData = automationOrdersInterface.encodeFunctionData("order", [
        floatToBigInt(sizeToClose, 6),      // _size (6 decimals for USDC)
        floatToBigInt(collateralToClose, 6), // _collateral (6 decimals for USDC)
        floatToBigInt(limitPrice, 6),       // _price (6 decimals for USDC)
        slippageBasisPoints,                // _slippage (basis points)
        isLong,                            // _long
        orderTypeValue,                    // orderType (1=TP, 2=SL)
        marketConfig.marketKey             // marketKey
      ]);

      this._debugLog('Transaction parameters:', {
        sizeToClose: `${sizeToClose} USDC`,
        collateralToClose: `${collateralToClose} USDC`,
        triggerPrice: `${limitPrice} USDC`,
        slippage: `${slippageBasisPoints} basis points`,
        orderType: `${orderTypeValue} (${orderType.toUpperCase()})`,
        marketKey: marketConfig.marketKey
      });

      // Create transaction object
      const transaction = {
        to: CONTRACT_ADDRESSES.AUTOMATION_ORDERS,
        data: orderCallData,
      };

      this._debugLog(`Sending ${orderType.toUpperCase()} order transaction with sponsored gas...`);

      // Send transaction using Biconomy smart account (sponsored gas)
      const userOpResponse = await this.#smartAccount.sendTransaction(transaction, {
        paymasterServiceData: { mode: PaymasterMode.SPONSORED },
      });

      this._debugLog('UserOp submitted with hash:', userOpResponse.userOpHash);
      this._debugLog('Waiting for transaction confirmation...');

      // Wait for the transaction to be confirmed
      const transactionDetails = await userOpResponse.wait();

      return {
        userOpHash: userOpResponse.userOpHash,
        transactionHash: transactionDetails.transactionHash,
        success: transactionDetails.success,
        gasFee: 0, // Sponsored gas
        pending: false
      };

    } catch (error) {
      this._errorLog('Error creating limit order:', error);
      throw error;
    }
  }

  /**
   * Validate limit price based on current market price and order type
   * @private
   */
  _validateLimitPrice(limitPrice, currentPrice, isLong, orderType) {
    if (!currentPrice || currentPrice === 0) {
      return 'Unable to validate limit price - current market price unavailable';
    }

    // Validate limit price logic based on position direction and order type
    if (isLong && orderType === 'tp') {
      // Long Take Profit: limit price should be above current price
      if (limitPrice <= currentPrice) {
        return 'Take Profit price must be above current market price for long positions';
      }
    } else if (isLong && orderType === 'sl') {
      // Long Stop Loss: limit price should be below current price
      if (limitPrice >= currentPrice) {
        return 'Stop Loss price must be below current market price for long positions';
      }
    } else if (!isLong && orderType === 'tp') {
      // Short Take Profit: limit price should be below current price
      if (limitPrice >= currentPrice) {
        return 'Take Profit price must be below current market price for short positions';
      }
    } else if (!isLong && orderType === 'sl') {
      // Short Stop Loss: limit price should be above current price
      if (limitPrice <= currentPrice) {
        return 'Stop Loss price must be above current market price for short positions';
      }
    }

    return 'ok';
  }
}
