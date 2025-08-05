// dexodus_sdk/runner.js

// This script is NOT meant to be used directly. It's a command-line interface
// called by the Python wrapper to execute the core JS SDK.
//
// Supports all Dexodus SDK functionality including:
// - Position management (open, close, increase, decrease)
// - Real-time position data with PnL calculations
// - Limit orders (Take Profit & Stop Loss)
// - Fund management (deposit, withdraw, balances)
// - Market data and utilities

import { DexodusClient, MARKET_SYMBOLS } from './index.js';

async function main() {
    // process.argv contains the command-line arguments:
    // argv[0] = 'node'
    // argv[1] = 'runner.js'
    // argv[2] = command (e.g., 'openLong')
    // argv[3] = config JSON string
    // argv[4] = params JSON string
    const [,, command, configStr, paramsStr] = process.argv;

    if (!command || !configStr) {
        console.error("Usage: node runner.js <command> <configJson> [paramsJson]");
        process.exit(1);
    }

    try {
        const config = JSON.parse(configStr);
        const params = paramsStr ? JSON.parse(paramsStr) : {};

        // Override console.log to redirect debug output to stderr when in Python wrapper mode
        const originalConsoleLog = console.log;
        console.log = (...args) => {
            // Only redirect if it looks like debug output
            if (args[0] && (args[0].includes('[DEBUG]') || args[0].includes('Creating') || args[0].includes('Contract'))) {
                console.error(...args);
            } else {
                originalConsoleLog(...args);
            }
        };

        // Initialize the core DexodusClient
        const client = await DexodusClient.create(config);

        let result;
        switch (command) {
            // =================================================================
            // POSITION MANAGEMENT COMMANDS
            // =================================================================
            case 'openLong':
                result = await client.openLong(params);
                break;
            case 'openShort':
                result = await client.openShort(params);
                break;
            case 'openPosition':
                result = await client.openPosition(params);
                break;
            case 'increasePosition':
                result = await client.increasePosition(params);
                break;
            case 'decreasePosition':
                result = await client.decreasePosition(params);
                break;
            case 'getPositions':
                result = await client.getPositions();
                break;

            // =================================================================
            // LIMIT ORDER COMMANDS
            // =================================================================
            case 'createTakeProfit':
                result = await client.createTakeProfit(params);
                break;
            case 'createStopLoss':
                result = await client.createStopLoss(params);
                break;

            // =================================================================
            // FUND MANAGEMENT COMMANDS
            // =================================================================
            case 'deposit':
                result = await client.deposit(params.amount);
                break;
            case 'withdraw':
                result = await client.withdraw(params.amount);
                break;
            case 'getBalances':
                result = await client.getBalances();
                break;

            // =================================================================
            // UTILITY COMMANDS
            // =================================================================
            case 'getAvailableMarkets':
                result = client.getAvailableMarkets();
                break;

            // =================================================================
            // LEGACY COMMANDS (for backward compatibility)
            // =================================================================
            case 'modifyPosition':
                result = await client.modifyPosition(params);
                break;

            default:
                throw new Error(`Unknown command: ${command}`);
        }

        // The most important step: Print the final result as a JSON string to stdout.
        // The Python wrapper will capture and parse this output.
        console.log(JSON.stringify(result));

    } catch (error) {
        // If any error occurs, print it to stderr and exit with a non-zero code.
        // The Python wrapper will capture this and raise an exception.
        console.error(error.message);
        process.exit(1);
    }
}

main();
