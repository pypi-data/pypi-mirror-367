export const AutomationOrdersABI = [
  {
    type: "constructor",
    inputs: [],
    stateMutability: "nonpayable",
  },
  {
    type: "fallback",
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
    name: "checkOrder",
    inputs: [
      {
        name: "markPrice",
        type: "uint256",
        internalType: "uint256",
      },
      {
        name: "_price",
        type: "uint256",
        internalType: "uint256",
      },
      {
        name: "_long",
        type: "bool",
        internalType: "bool",
      },
      {
        name: "_orderType",
        type: "uint256",
        internalType: "uint256",
      },
    ],
    outputs: [
      {
        name: "",
        type: "bool",
        internalType: "bool",
      },
    ],
    stateMutability: "view",
  },
  {
    type: "function",
    name: "deleteAllOrdersRelated",
    inputs: [
      {
        name: "positionKey",
        type: "bytes32",
        internalType: "bytes32",
      },
    ],
    outputs: [],
    stateMutability: "nonpayable",
  },
  {
    type: "function",
    name: "deleteOrder",
    inputs: [
      {
        name: "_orderId",
        type: "uint256",
        internalType: "uint256",
      },
      {
        name: "marketKey",
        type: "bytes32",
        internalType: "bytes32",
      },
    ],
    outputs: [],
    stateMutability: "nonpayable",
  },
  {
    type: "function",
    name: "editOrder",
    inputs: [
      {
        name: "order",
        type: "tuple",
        internalType: "struct AutomationOrdersV3.Order",
        components: [
          {
            name: "orderId",
            type: "uint256",
            internalType: "uint256",
          },
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
            name: "slippage",
            type: "uint256",
            internalType: "uint256",
          },
          {
            name: "oType",
            type: "uint256",
            internalType: "uint256",
          },
          {
            name: "long",
            type: "bool",
            internalType: "bool",
          },
        ],
      },
      {
        name: "marketKey",
        type: "bytes32",
        internalType: "bytes32",
      },
    ],
    outputs: [],
    stateMutability: "nonpayable",
  },
  {
    type: "function",
    name: "executeOrder",
    inputs: [
      {
        name: "_orderIds",
        type: "uint256[]",
        internalType: "uint256[]",
      },
      {
        name: "_currentPrice",
        type: "uint256",
        internalType: "uint256",
      },
      {
        name: "orderType",
        type: "uint256",
        internalType: "uint256",
      },
      {
        name: "marketKey",
        type: "bytes32",
        internalType: "bytes32",
      },
      {
        name: "isIncrease",
        type: "bool",
        internalType: "bool",
      },
    ],
    outputs: [],
    stateMutability: "nonpayable",
  },
  {
    type: "function",
    name: "futuresCore",
    inputs: [],
    outputs: [
      {
        name: "",
        type: "address",
        internalType: "address payable",
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
    name: "getOrder",
    inputs: [
      {
        name: "_id",
        type: "uint256",
        internalType: "uint256",
      },
    ],
    outputs: [
      {
        name: "",
        type: "tuple",
        internalType: "struct AutomationOrdersV3.Order",
        components: [
          {
            name: "orderId",
            type: "uint256",
            internalType: "uint256",
          },
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
            name: "slippage",
            type: "uint256",
            internalType: "uint256",
          },
          {
            name: "oType",
            type: "uint256",
            internalType: "uint256",
          },
          {
            name: "long",
            type: "bool",
            internalType: "bool",
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
        name: "_futuresCore",
        type: "address",
        internalType: "address",
      },
    ],
    outputs: [],
    stateMutability: "nonpayable",
  },
  {
    type: "function",
    name: "order",
    inputs: [
      {
        name: "_size",
        type: "uint256",
        internalType: "uint256",
      },
      {
        name: "_collateral",
        type: "uint256",
        internalType: "uint256",
      },
      {
        name: "_price",
        type: "uint256",
        internalType: "uint256",
      },
      {
        name: "_slippage",
        type: "uint256",
        internalType: "uint256",
      },
      {
        name: "_long",
        type: "bool",
        internalType: "bool",
      },
      {
        name: "orderType",
        type: "uint256",
        internalType: "uint256",
      },
      {
        name: "marketKey",
        type: "bytes32",
        internalType: "bytes32",
      },
    ],
    outputs: [],
    stateMutability: "nonpayable",
  },
  {
    type: "function",
    name: "orderCounter",
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
    name: "s_orders",
    inputs: [
      {
        name: "",
        type: "uint256",
        internalType: "uint256",
      },
    ],
    outputs: [
      {
        name: "orderId",
        type: "uint256",
        internalType: "uint256",
      },
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
        name: "slippage",
        type: "uint256",
        internalType: "uint256",
      },
      {
        name: "oType",
        type: "uint256",
        internalType: "uint256",
      },
      {
        name: "long",
        type: "bool",
        internalType: "bool",
      },
    ],
    stateMutability: "view",
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
    name: "OrderCreated",
    inputs: [
      {
        name: "orderId",
        type: "uint256",
        indexed: true,
        internalType: "uint256",
      },
      {
        name: "key",
        type: "bytes32",
        indexed: true,
        internalType: "bytes32",
      },
      {
        name: "positionKey",
        type: "bytes32",
        indexed: true,
        internalType: "bytes32",
      },
      {
        name: "trader",
        type: "address",
        indexed: false,
        internalType: "address",
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
        name: "slippage",
        type: "uint256",
        indexed: false,
        internalType: "uint256",
      },
      {
        name: "oType",
        type: "uint256",
        indexed: false,
        internalType: "uint256",
      },
      {
        name: "long",
        type: "bool",
        indexed: false,
        internalType: "bool",
      },
      {
        name: "eoa",
        type: "address",
        indexed: false,
        internalType: "address",
      },
    ],
    anonymous: false,
  },
  {
    type: "event",
    name: "OrderDeleted",
    inputs: [
      {
        name: "orderId",
        type: "uint256",
        indexed: true,
        internalType: "uint256",
      },
      {
        name: "key",
        type: "bytes32",
        indexed: true,
        internalType: "bytes32",
      },
      {
        name: "positionKey",
        type: "bytes32",
        indexed: true,
        internalType: "bytes32",
      },
      {
        name: "trader",
        type: "address",
        indexed: false,
        internalType: "address",
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
        name: "slippage",
        type: "uint256",
        indexed: false,
        internalType: "uint256",
      },
      {
        name: "oType",
        type: "uint256",
        indexed: false,
        internalType: "uint256",
      },
      {
        name: "long",
        type: "bool",
        indexed: false,
        internalType: "bool",
      },
      {
        name: "eoa",
        type: "address",
        indexed: false,
        internalType: "address",
      },
    ],
    anonymous: false,
  },
  {
    type: "event",
    name: "OrderEdited",
    inputs: [
      {
        name: "orderId",
        type: "uint256",
        indexed: true,
        internalType: "uint256",
      },
      {
        name: "key",
        type: "bytes32",
        indexed: true,
        internalType: "bytes32",
      },
      {
        name: "positionKey",
        type: "bytes32",
        indexed: true,
        internalType: "bytes32",
      },
      {
        name: "trader",
        type: "address",
        indexed: false,
        internalType: "address",
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
        name: "slippage",
        type: "uint256",
        indexed: false,
        internalType: "uint256",
      },
      {
        name: "oType",
        type: "uint256",
        indexed: false,
        internalType: "uint256",
      },
      {
        name: "long",
        type: "bool",
        indexed: false,
        internalType: "bool",
      },
      {
        name: "eoa",
        type: "address",
        indexed: false,
        internalType: "address",
      },
    ],
    anonymous: false,
  },
  {
    type: "event",
    name: "OrderExecuted",
    inputs: [
      {
        name: "orderId",
        type: "uint256",
        indexed: true,
        internalType: "uint256",
      },
      {
        name: "key",
        type: "bytes32",
        indexed: true,
        internalType: "bytes32",
      },
      {
        name: "positionKey",
        type: "bytes32",
        indexed: true,
        internalType: "bytes32",
      },
      {
        name: "trader",
        type: "address",
        indexed: false,
        internalType: "address",
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
        name: "slippage",
        type: "uint256",
        indexed: false,
        internalType: "uint256",
      },
      {
        name: "oType",
        type: "uint256",
        indexed: false,
        internalType: "uint256",
      },
      {
        name: "long",
        type: "bool",
        indexed: false,
        internalType: "bool",
      },
      {
        name: "eoa",
        type: "address",
        indexed: false,
        internalType: "address",
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
