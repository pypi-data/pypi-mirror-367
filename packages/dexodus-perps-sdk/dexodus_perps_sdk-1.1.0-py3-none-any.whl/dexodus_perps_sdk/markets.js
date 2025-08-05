// markets.js
// Market configuration with PriceIDs and MarketKeys from Dexodus

export const MARKETS = {
  "BTC": {
    symbol: "BTC",
    priceID: "0xe62df6c8b4a85fe1a67db44dc12de5db330f7ac66b72dc658afedf0f4a415b43",
    marketKey: "0x95d7f9d6571969d9bf39c6a4e1bb32ecc252f07309c0a1cfd23b49366414833c"
  },
  "ETH": {
    symbol: "ETH",
    priceID: "0xff61491a931112ddf1bd8147cd1b641375f79f5825126d665480874634fd0ace",
    marketKey: "0xbaf2dfadf73bb5597dae55258a19b57d5117bbb6753b578ae11715c86cfda1ef"
  },
  "BNB": {
    symbol: "BNB",
    priceID: "0x2f95862b045670cd22bee3114c39763a4a08beeb663b145d283c31d7d1101c4f",
    marketKey: "0xae5674792f03dfe286ef266c2a4322889ecbd78560830d45ea5efcc0c885efae"
  },
  "SOL": {
    symbol: "SOL",
    priceID: "0xef0d8b6fda2ceba41da15d4095d1da392a0d2f8ed0c6c7bc0f4cfac8c280b56d",
    marketKey: "0x9158501b03398cc0f46a14f42021b5c14c0b5e2adf1484c6ef8ff13804b17074"
  },
  "XRP": {
    symbol: "XRP",
    priceID: "0xec5d399846a9209f3fe5881d70aae9268c94339ff9817e8d18ff19fa05eea1c8",
    marketKey: "0xb02a59a8a0e660ce110041ca6c80197ac46ad136792ccf841570b529f5495a6b"
  },
  "DOGE": {
    symbol: "DOGE",
    priceID: "0xdcef50dd0a4cd2dcc17e45df1676dcb336a11a61c69df7a0299b0150c672d25c",
    marketKey: "0x0658a0a8f38327ffdd8b2c7e5ba3d846eb9fa58a5486e840327fe12c1aa3e09e"
  },
  "ADA": {
    symbol: "ADA",
    priceID: "0x2a01deaec9e51a579277b34b122399984d0bbf57e2458a7e42fecd2829867a0d",
    marketKey: "0xaa761a33f84add5dc31f02775d8f0fbf09f5744a730b37e7cc32e5cb36e7d321"
  },
  "TRX": {
    symbol: "TRX",
    priceID: "0x67aed5a24fdad045475e7195c98a98aea119c763f272d4523f5bac93a4f33c2b",
    marketKey: "0x1a2b04405959e7a468a79d322aec290d2d6ddcca871caef896dce16299afb7ce"
  },
  "AVAX": {
    symbol: "AVAX",
    priceID: "0x93da3352f9f1d105fdfe4971cfa80e9dd777bfc5d0f683ebb6e1294b92137bb7",
    marketKey: "0x514527389b8ba61371ea82f40500c2f2b9668e7bc37e46553292d964d95d02a9"
  },
  "SUI": {
    symbol: "SUI",
    priceID: "0x23d7315113f5b1d3ba7a83604c44b94d79f4fd69af77f804fc7f920a6dc65744",
    marketKey: "0xb26a6f11ffbaf9549b08a25d613a29f21ca7b3cc559b2cb55e4916c277861ddd"
  }
};

// Helper function to get market by symbol
export function getMarket(symbol) {
  const market = MARKETS[symbol.toUpperCase()];
  if (!market) {
    throw new Error(`Market ${symbol} not found. Available markets: ${Object.keys(MARKETS).join(', ')}`);
  }
  return market;
}

// Helper function to get all available markets
export function getAvailableMarkets() {
  return Object.keys(MARKETS);
}

// Helper function to generate market key from symbol (like frontend does)
export async function generateMarketKey(symbol) {
  const { keccak256, encodeAbiParameters } = await import('viem');
  return keccak256(encodeAbiParameters([{ type: "string" }], [symbol]));
}

// Helper function to convert float to BigInt with specified decimals (like frontend floatToBigInt)
export function floatToBigInt(value, decimals = 6) {
  return BigInt(Math.round(value * Math.pow(10, decimals)));
}

// Market symbols enum for IDE autocomplete and type safety
export const MARKET_SYMBOLS = {
  BTC: "BTC",
  ETH: "ETH",
  BNB: "BNB",
  SOL: "SOL",
  XRP: "XRP",
  DOGE: "DOGE",
  ADA: "ADA",
  TRX: "TRX",
  AVAX: "AVAX",
  SUI: "SUI"
};

// Freeze the object to prevent modifications
Object.freeze(MARKET_SYMBOLS);
