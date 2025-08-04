#!/usr/bin/env python3

# Copyright © 2020-2025, Meheret Tesfaye Batu <meherett.batu@gmail.com>
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit

from ..slip44 import CoinTypes
from ..eccs import SLIP10Secp256k1ECC
from ..consts import (
    Info, Entropies, Mnemonics, Seeds, HDs, Addresses, Networks, XPrivateKeyVersions, XPublicKeyVersions
)
from .icryptocurrency import (
    ICryptocurrency, INetwork
)


class Mainnet(INetwork):

    NAME = "mainnet"
    PUBLIC_KEY_ADDRESS_PREFIX = 0x1e
    SCRIPT_ADDRESS_PREFIX = 0xd
    XPRIVATE_KEY_VERSIONS = XPrivateKeyVersions({
        "P2PKH": 0x221312b,
        "P2SH": 0x221312b
    })
    XPUBLIC_KEY_VERSIONS = XPublicKeyVersions({
        "P2PKH": 0x22d2533,
        "P2SH": 0x22d2533
    })
    MESSAGE_PREFIX = None
    WIF_PREFIX = 0xd4


class Testnet(INetwork):

    NAME = "testnet"
    PUBLIC_KEY_ADDRESS_PREFIX = 0x8b
    SCRIPT_ADDRESS_PREFIX = 0x13
    XPRIVATE_KEY_VERSIONS = XPrivateKeyVersions({
        "P2PKH": 0x3a805837,
        "P2SH": 0x3a805837
    })
    XPUBLIC_KEY_VERSIONS = XPublicKeyVersions({
        "P2PKH": 0x3a8061a0,
        "P2SH": 0x3a8061a0
    })
    MESSAGE_PREFIX = None
    WIF_PREFIX = 0xef


class Pivx(ICryptocurrency):

    NAME = "Pivx"
    SYMBOL = "PIVX"
    INFO = Info({
        "SOURCE_CODE": "https://github.com/PIVX-Project/PIVX",
        "WHITEPAPER": "https://pivx.org/whitepaper",
        "WEBSITES": [
            "https://pivx.org"
        ]
    })
    ECC = SLIP10Secp256k1ECC
    COIN_TYPE = CoinTypes.Pivx
    SUPPORT_BIP38 = True
    NETWORKS = Networks({
        "MAINNET": Mainnet, "TESTNET": Testnet
    })
    DEFAULT_NETWORK = NETWORKS.MAINNET
    ENTROPIES = Entropies({
        "BIP39"
    })
    MNEMONICS = Mnemonics({
        "BIP39"
    })
    SEEDS = Seeds({
        "BIP39"
    })
    HDS = HDs({
        "BIP32", "BIP44"
    })
    DEFAULT_HD = HDS.BIP44
    DEFAULT_PATH = f"m/44'/{COIN_TYPE}'/0'/0/0"
    ADDRESSES = Addresses((
        "P2PKH", "P2SH"
    ))
    DEFAULT_ADDRESS = ADDRESSES.P2PKH
    SEMANTICS = [
        "p2pkh", "p2sh"
    ]
    DEFAULT_SEMANTIC = "p2pkh"
