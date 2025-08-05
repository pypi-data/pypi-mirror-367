export const DEXODUS_ABI = [
  {
    type: "constructor",
    inputs: [],
    stateMutability: "nonpayable",
  },
  {
    type: "receive",
    stateMutability: "payable",
  },
  {
    type: "function",
    name: "UPGRADE_INTERFACE_VERSION",
    inputs: [],
    outputs: [
      {
        name: "",
        type: "string",
        internalType: "string",
      },
    ],
    stateMutability: "view",
  },
  {
    type: "function",
    name: "acceptOwnership",
    inputs: [],
    outputs: [],
    stateMutability: "nonpayable",
  },
  {
    type: "function",
    name: "calcLiquidationPrice",
    inputs: [
      {
        name: "positionKey",
        type: "bytes32",
        internalType: "bytes32",
      },
      {
        name: "key",
        type: "bytes32",
        internalType: "bytes32",
      },
      {
        name: "indexPrice",
        type: "uint256",
        internalType: "uint256",
      },
      {
        name: "long",
        type: "bool",
        internalType: "bool",
      },
    ],
    outputs: [
      {
        name: "liqPrice",
        type: "uint256",
        internalType: "uint256",
      },
      {
        name: "markPrice",
        type: "uint256",
        internalType: "uint256",
      },
      {
        name: "liquidate",
        type: "bool",
        internalType: "bool",
      },
      {
        name: "collateral",
        type: "uint256",
        internalType: "uint256",
      },
      {
        name: "size",
        type: "uint256",
        internalType: "uint256",
      },
    ],
    stateMutability: "view",
  },
  {
    type: "function",
    name: "chargeMakerFeeFromOrder",
    inputs: [
      {
        name: "trader",
        type: "address",
        internalType: "address",
      },
      {
        name: "key",
        type: "bytes32",
        internalType: "bytes32",
      },
      {
        name: "size",
        type: "uint256",
        internalType: "uint256",
      },
    ],
    outputs: [],
    stateMutability: "nonpayable",
  },
  {
    type: "function",
    name: "feedIds",
    inputs: [
      {
        name: "",
        type: "bytes32",
        internalType: "bytes32",
      },
    ],
    outputs: [
      {
        name: "",
        type: "bytes32",
        internalType: "bytes32",
      },
    ],
    stateMutability: "view",
  },
  {
    type: "function",
    name: "getEOAaddress",
    inputs: [
      {
        name: "_smartAccount",
        type: "address",
        internalType: "address",
      },
    ],
    outputs: [
      {
        name: "",
        type: "address",
        internalType: "address",
      },
    ],
    stateMutability: "view",
  },
  {
    type: "function",
    name: "getMarkPrice",
    inputs: [
      {
        name: "key",
        type: "bytes32",
        internalType: "bytes32",
      },
      {
        name: "indexPrice",
        type: "uint256",
        internalType: "uint256",
      },
    ],
    outputs: [
      {
        name: "markPrice",
        type: "uint256",
        internalType: "uint256",
      },
    ],
    stateMutability: "view",
  },
  {
    type: "function",
    name: "getMarketFundingRate",
    inputs: [
      {
        name: "key",
        type: "bytes32",
        internalType: "bytes32",
      },
      {
        name: "indexPrice",
        type: "uint256",
        internalType: "uint256",
      },
    ],
    outputs: [
      {
        name: "fundingRate",
        type: "int256",
        internalType: "int256",
      },
    ],
    stateMutability: "view",
  },
  {
    type: "function",
    name: "getMarketOI",
    inputs: [
      {
        name: "key",
        type: "bytes32",
        internalType: "bytes32",
      },
    ],
    outputs: [
      {
        name: "marketOI",
        type: "uint256",
        internalType: "uint256",
      },
      {
        name: "longOI",
        type: "uint256",
        internalType: "uint256",
      },
      {
        name: "shortOI",
        type: "uint256",
        internalType: "uint256",
      },
    ],
    stateMutability: "view",
  },
  {
    type: "function",
    name: "getPerpetualPrice",
    inputs: [
      {
        name: "key",
        type: "bytes32",
        internalType: "bytes32",
      },
      {
        name: "indexPrice",
        type: "uint256",
        internalType: "uint256",
      },
    ],
    outputs: [
      {
        name: "",
        type: "uint256",
        internalType: "uint256",
      },
    ],
    stateMutability: "view",
  },
  {
    type: "function",
    name: "getPerpetualPriceForPosition",
    inputs: [
      {
        name: "key",
        type: "bytes32",
        internalType: "bytes32",
      },
      {
        name: "indexPrice",
        type: "uint256",
        internalType: "uint256",
      },
      {
        name: "size",
        type: "int256",
        internalType: "int256",
      },
      {
        name: "long",
        type: "bool",
        internalType: "bool",
      },
    ],
    outputs: [
      {
        name: "",
        type: "uint256",
        internalType: "uint256",
      },
    ],
    stateMutability: "view",
  },
  {
    type: "function",
    name: "getPositionsData",
    inputs: [
      {
        name: "positionsKey",
        type: "bytes32[]",
        internalType: "bytes32[]",
      },
    ],
    outputs: [
      {
        name: "",
        type: "tuple[]",
        internalType: "struct Position.Data[]",
        components: [
          {
            name: "positionId",
            type: "uint256",
            internalType: "uint256",
          },
          {
            name: "size",
            type: "uint256",
            internalType: "uint256",
          },
          {
            name: "collateral",
            type: "uint256",
            internalType: "uint256",
          },
          {
            name: "price",
            type: "uint256",
            internalType: "uint256",
          },
          {
            name: "fundingFeeGrowthLongLast",
            type: "uint256",
            internalType: "uint256",
          },
          {
            name: "fundingFeeGrowthShortLast",
            type: "uint256",
            internalType: "uint256",
          },
          {
            name: "fundingFeeGrowthExtraLongLast",
            type: "uint256",
            internalType: "uint256",
          },
          {
            name: "fundingFeeGrowthExtraShortLast",
            type: "uint256",
            internalType: "uint256",
          },
          {
            name: "fundingFeeToReceiveLongLast",
            type: "uint256",
            internalType: "uint256",
          },
          {
            name: "fundingFeeToReceiveShortLast",
            type: "uint256",
            internalType: "uint256",
          },
        ],
      },
    ],
    stateMutability: "view",
  },
  {
    type: "function",
    name: "initialize",
    inputs: [
      {
        name: "liqPool",
        type: "address",
        internalType: "address",
      },
      {
        name: "t",
        type: "address",
        internalType: "address",
      },
      {
        name: "usdc",
        type: "address",
        internalType: "address",
      },
      {
        name: "_users",
        type: "address",
        internalType: "address",
      },
      {
        name: "pythContract",
        type: "address",
        internalType: "address",
      },
      {
        name: "_automationLiquidationsV3",
        type: "address",
        internalType: "address",
      },
      {
        name: "_automationOrdersV3",
        type: "address",
        internalType: "address",
      },
    ],
    outputs: [],
    stateMutability: "nonpayable",
  },
  {
    type: "function",
    name: "initializeMarket",
    inputs: [
      {
        name: "key",
        type: "bytes32",
        internalType: "bytes32",
      },
      {
        name: "weight",
        type: "uint256",
        internalType: "uint256",
      },
      {
        name: "makerFeeMultiplier",
        type: "uint256",
        internalType: "uint256",
      },
      {
        name: "takerFeeMultiplier",
        type: "uint256",
        internalType: "uint256",
      },
      {
        name: "tradingFeeToLPs",
        type: "uint256",
        internalType: "uint256",
      },
      {
        name: "tradingFeeToTreasury",
        type: "uint256",
        internalType: "uint256",
      },
      {
        name: "fundingFeeToLPs",
        type: "uint256",
        internalType: "uint256",
      },
      {
        name: "fundingFeeToTreasury",
        type: "uint256",
        internalType: "uint256",
      },
      {
        name: "allowedLeverage",
        type: "uint256",
        internalType: "uint256",
      },
      {
        name: "chillFactor",
        type: "uint256",
        internalType: "uint256",
      },
    ],
    outputs: [],
    stateMutability: "nonpayable",
  },
  {
    type: "function",
    name: "liquidatePosition",
    inputs: [
      {
        name: "owner",
        type: "address",
        internalType: "address",
      },
      {
        name: "isLong",
        type: "bool",
        internalType: "bool",
      },
      {
        name: "indexPrice",
        type: "uint256",
        internalType: "uint256",
      },
      {
        name: "key",
        type: "bytes32",
        internalType: "bytes32",
      },
    ],
    outputs: [],
    stateMutability: "nonpayable",
  },
  {
    type: "function",
    name: "modifyPosition",
    inputs: [
      {
        name: "collateral",
        type: "uint256",
        internalType: "uint256",
      },
      {
        name: "size",
        type: "uint256",
        internalType: "uint256",
      },
      {
        name: "isLong",
        type: "bool",
        internalType: "bool",
      },
      {
        name: "isIncrease",
        type: "bool",
        internalType: "bool",
      },
      {
        name: "key",
        type: "bytes32",
        internalType: "bytes32",
      },
      {
        name: "price",
        type: "uint256",
        internalType: "uint256",
      },
      {
        name: "slippage",
        type: "uint256",
        internalType: "uint256",
      },
      {
        name: "priceUpdate",
        type: "bytes[]",
        internalType: "bytes[]",
      },
    ],
    outputs: [],
    stateMutability: "nonpayable",
  },
  {
    type: "function",
    name: "modifyPositionFromOrders",
    inputs: [
      {
        name: "owner",
        type: "address",
        internalType: "address",
      },
      {
        name: "collateral",
        type: "uint256",
        internalType: "uint256",
      },
      {
        name: "size",
        type: "uint256",
        internalType: "uint256",
      },
      {
        name: "indexPrice",
        type: "uint256",
        internalType: "uint256",
      },
      {
        name: "isLong",
        type: "bool",
        internalType: "bool",
      },
      {
        name: "isIncrease",
        type: "bool",
        internalType: "bool",
      },
      {
        name: "key",
        type: "bytes32",
        internalType: "bytes32",
      },
      {
        name: "price",
        type: "uint256",
        internalType: "uint256",
      },
      {
        name: "slippage",
        type: "uint256",
        internalType: "uint256",
      },
      {
        name: "checkSlippage",
        type: "bool",
        internalType: "bool",
      },
    ],
    outputs: [],
    stateMutability: "nonpayable",
  },
  {
    type: "function",
    name: "owner",
    inputs: [],
    outputs: [
      {
        name: "",
        type: "address",
        internalType: "address",
      },
    ],
    stateMutability: "view",
  },
  {
    type: "function",
    name: "ownershipRegistry",
    inputs: [],
    outputs: [
      {
        name: "",
        type: "address",
        internalType: "contract IOwnershipRegistryModule",
      },
    ],
    stateMutability: "view",
  },
  {
    type: "function",
    name: "pendingOwner",
    inputs: [],
    outputs: [
      {
        name: "",
        type: "address",
        internalType: "address",
      },
    ],
    stateMutability: "view",
  },
  {
    type: "function",
    name: "proxiableUUID",
    inputs: [],
    outputs: [
      {
        name: "",
        type: "bytes32",
        internalType: "bytes32",
      },
    ],
    stateMutability: "view",
  },
  {
    type: "function",
    name: "renounceOwnership",
    inputs: [],
    outputs: [],
    stateMutability: "nonpayable",
  },
  {
    type: "function",
    name: "setLiquidityPool",
    inputs: [
      {
        name: "_liquidityPool",
        type: "address",
        internalType: "address",
      },
    ],
    outputs: [],
    stateMutability: "nonpayable",
  },
  {
    type: "function",
    name: "setOperator",
    inputs: [
      {
        name: "_operator",
        type: "address",
        internalType: "address",
      },
    ],
    outputs: [],
    stateMutability: "nonpayable",
  },
  {
    type: "function",
    name: "setOperatorPnL",
    inputs: [
      {
        name: "_operator",
        type: "address",
        internalType: "address",
      },
    ],
    outputs: [],
    stateMutability: "nonpayable",
  },
  {
    type: "function",
    name: "setTreasury",
    inputs: [
      {
        name: "_treasury",
        type: "address",
        internalType: "address",
      },
    ],
    outputs: [],
    stateMutability: "nonpayable",
  },
  {
    type: "function",
    name: "setUsers",
    inputs: [
      {
        name: "_users",
        type: "address",
        internalType: "address",
      },
    ],
    outputs: [],
    stateMutability: "nonpayable",
  },
  {
    type: "function",
    name: "totalWeights",
    inputs: [],
    outputs: [
      {
        name: "",
        type: "uint256",
        internalType: "uint256",
      },
    ],
    stateMutability: "view",
  },
  {
    type: "function",
    name: "transferOwnership",
    inputs: [
      {
        name: "newOwner",
        type: "address",
        internalType: "address",
      },
    ],
    outputs: [],
    stateMutability: "nonpayable",
  },
  {
    type: "function",
    name: "unrealizedPnL",
    inputs: [],
    outputs: [
      {
        name: "",
        type: "int256",
        internalType: "int256",
      },
    ],
    stateMutability: "view",
  },
  {
    type: "function",
    name: "updateFeedIds",
    inputs: [
      {
        name: "_marketKeys",
        type: "bytes32[]",
        internalType: "bytes32[]",
      },
      {
        name: "_feedIds",
        type: "bytes32[]",
        internalType: "bytes32[]",
      },
    ],
    outputs: [],
    stateMutability: "nonpayable",
  },
  {
    type: "function",
    name: "updateFundingFeeGrowth",
    inputs: [
      {
        name: "marketUpdate",
        type: "tuple[]",
        internalType: "struct FeeManager.MarketUpdate[]",
        components: [
          {
            name: "key",
            type: "bytes32",
            internalType: "bytes32",
          },
          {
            name: "indexPrice",
            type: "uint256",
            internalType: "uint256",
          },
        ],
      },
    ],
    outputs: [],
    stateMutability: "nonpayable",
  },
  {
    type: "function",
    name: "updateUnrealizedPnL",
    inputs: [
      {
        name: "marketUpdate",
        type: "tuple[]",
        internalType: "struct FeeManager.MarketUpdate[]",
        components: [
          {
            name: "key",
            type: "bytes32",
            internalType: "bytes32",
          },
          {
            name: "indexPrice",
            type: "uint256",
            internalType: "uint256",
          },
        ],
      },
    ],
    outputs: [],
    stateMutability: "nonpayable",
  },
  {
    type: "function",
    name: "upgradeToAndCall",
    inputs: [
      {
        name: "newImplementation",
        type: "address",
        internalType: "address",
      },
      {
        name: "data",
        type: "bytes",
        internalType: "bytes",
      },
    ],
    outputs: [],
    stateMutability: "payable",
  },
  {
    type: "function",
    name: "version",
    inputs: [],
    outputs: [
      {
        name: "",
        type: "uint256",
        internalType: "uint256",
      },
    ],
    stateMutability: "pure",
  },
  {
    type: "event",
    name: "Initialized",
    inputs: [
      {
        name: "version",
        type: "uint64",
        indexed: false,
        internalType: "uint64",
      },
    ],
    anonymous: false,
  },
  {
    type: "event",
    name: "InitiateTrade",
    inputs: [
      {
        name: "msgSender",
        type: "address",
        indexed: false,
        internalType: "address",
      },
      {
        name: "collateral",
        type: "uint256",
        indexed: false,
        internalType: "uint256",
      },
      {
        name: "size",
        type: "uint256",
        indexed: false,
        internalType: "uint256",
      },
      {
        name: "isLong",
        type: "bool",
        indexed: false,
        internalType: "bool",
      },
      {
        name: "isIncrease",
        type: "bool",
        indexed: false,
        internalType: "bool",
      },
      {
        name: "key",
        type: "bytes32",
        indexed: false,
        internalType: "bytes32",
      },
      {
        name: "price",
        type: "uint256",
        indexed: false,
        internalType: "uint256",
      },
      {
        name: "slippage",
        type: "uint256",
        indexed: false,
        internalType: "uint256",
      },
    ],
    anonymous: false,
  },
  {
    type: "event",
    name: "ModifiedPosition",
    inputs: [
      {
        name: "positionId",
        type: "uint256",
        indexed: true,
        internalType: "uint256",
      },
      {
        name: "owner",
        type: "address",
        indexed: true,
        internalType: "address",
      },
      {
        name: "positionKey",
        type: "bytes32",
        indexed: true,
        internalType: "bytes32",
      },
      {
        name: "marketKey",
        type: "bytes32",
        indexed: false,
        internalType: "bytes32",
      },
      {
        name: "isLong",
        type: "bool",
        indexed: false,
        internalType: "bool",
      },
      {
        name: "size",
        type: "uint256",
        indexed: false,
        internalType: "uint256",
      },
      {
        name: "collateral",
        type: "uint256",
        indexed: false,
        internalType: "uint256",
      },
      {
        name: "price",
        type: "uint256",
        indexed: false,
        internalType: "uint256",
      },
      {
        name: "perpetualPrice",
        type: "uint256",
        indexed: false,
        internalType: "uint256",
      },
      {
        name: "txType",
        type: "uint256",
        indexed: false,
        internalType: "uint256",
      },
      {
        name: "eoa",
        type: "address",
        indexed: false,
        internalType: "address",
      },
      {
        name: "badDebt",
        type: "uint256",
        indexed: false,
        internalType: "uint256",
      },
      {
        name: "trackingFundingFee",
        type: "int256",
        indexed: false,
        internalType: "int256",
      },
    ],
    anonymous: false,
  },
  {
    type: "event",
    name: "OwnershipTransferStarted",
    inputs: [
      {
        name: "previousOwner",
        type: "address",
        indexed: true,
        internalType: "address",
      },
      {
        name: "newOwner",
        type: "address",
        indexed: true,
        internalType: "address",
      },
    ],
    anonymous: false,
  },
  {
    type: "event",
    name: "OwnershipTransferred",
    inputs: [
      {
        name: "previousOwner",
        type: "address",
        indexed: true,
        internalType: "address",
      },
      {
        name: "newOwner",
        type: "address",
        indexed: true,
        internalType: "address",
      },
    ],
    anonymous: false,
  },
  {
    type: "event",
    name: "PositionLiquidated",
    inputs: [
      {
        name: "positionId",
        type: "uint256",
        indexed: true,
        internalType: "uint256",
      },
      {
        name: "owner",
        type: "address",
        indexed: true,
        internalType: "address",
      },
      {
        name: "positionKey",
        type: "bytes32",
        indexed: true,
        internalType: "bytes32",
      },
      {
        name: "marketKey",
        type: "bytes32",
        indexed: false,
        internalType: "bytes32",
      },
      {
        name: "perpetualPrice",
        type: "uint256",
        indexed: false,
        internalType: "uint256",
      },
      {
        name: "liqPrice",
        type: "uint256",
        indexed: false,
        internalType: "uint256",
      },
      {
        name: "trackingFundingFee",
        type: "int256",
        indexed: false,
        internalType: "int256",
      },
    ],
    anonymous: false,
  },
  {
    type: "event",
    name: "TradingFees",
    inputs: [
      {
        name: "marketKey",
        type: "bytes32",
        indexed: false,
        internalType: "bytes32",
      },
      {
        name: "eoa",
        type: "address",
        indexed: false,
        internalType: "address",
      },
      {
        name: "trader",
        type: "address",
        indexed: false,
        internalType: "address",
      },
      {
        name: "feeType",
        type: "uint256",
        indexed: false,
        internalType: "uint256",
      },
      {
        name: "toLP",
        type: "bool",
        indexed: false,
        internalType: "bool",
      },
      {
        name: "usdcAmount",
        type: "uint256",
        indexed: false,
        internalType: "uint256",
      },
    ],
    anonymous: false,
  },
  {
    type: "event",
    name: "UpdatedFundingFeeGrowth",
    inputs: [
      {
        name: "perpetualPrice",
        type: "uint256",
        indexed: false,
        internalType: "uint256",
      },
      {
        name: "fundingFeeToLPs",
        type: "uint256",
        indexed: false,
        internalType: "uint256",
      },
    ],
    anonymous: false,
  },
  {
    type: "event",
    name: "Upgraded",
    inputs: [
      {
        name: "implementation",
        type: "address",
        indexed: true,
        internalType: "address",
      },
    ],
    anonymous: false,
  },
  {
    type: "error",
    name: "AddressEmptyCode",
    inputs: [
      {
        name: "target",
        type: "address",
        internalType: "address",
      },
    ],
  },
  {
    type: "error",
    name: "AddressInsufficientBalance",
    inputs: [
      {
        name: "account",
        type: "address",
        internalType: "address",
      },
    ],
  },
  {
    type: "error",
    name: "ERC1967InvalidImplementation",
    inputs: [
      {
        name: "implementation",
        type: "address",
        internalType: "address",
      },
    ],
  },
  {
    type: "error",
    name: "ERC1967NonPayable",
    inputs: [],
  },
  {
    type: "error",
    name: "FailedInnerCall",
    inputs: [],
  },
  {
    type: "error",
    name: "InvalidInitialization",
    inputs: [],
  },
  {
    type: "error",
    name: "NotInitializing",
    inputs: [],
  },
  {
    type: "error",
    name: "OwnableInvalidOwner",
    inputs: [
      {
        name: "owner",
        type: "address",
        internalType: "address",
      },
    ],
  },
  {
    type: "error",
    name: "OwnableUnauthorizedAccount",
    inputs: [
      {
        name: "account",
        type: "address",
        internalType: "address",
      },
    ],
  },
  {
    type: "error",
    name: "SafeERC20FailedOperation",
    inputs: [
      {
        name: "token",
        type: "address",
        internalType: "address",
      },
    ],
  },
  {
    type: "error",
    name: "UUPSUnauthorizedCallContext",
    inputs: [],
  },
  {
    type: "error",
    name: "UUPSUnsupportedProxiableUUID",
    inputs: [
      {
        name: "slot",
        type: "bytes32",
        internalType: "bytes32",
      },
    ],
  },
];
