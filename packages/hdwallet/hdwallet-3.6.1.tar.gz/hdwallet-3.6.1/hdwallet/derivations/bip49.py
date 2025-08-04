#!/usr/bin/env python3

# Copyright © 2020-2024, Meheret Tesfaye Batu <meherett.batu@gmail.com>
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit

from typing import Tuple

from .bip44 import BIP44Derivation


class BIP49Derivation(BIP44Derivation):  # https://github.com/bitcoin/bips/blob/master/bip-0049.mediawiki
    """
    This class implements the BIP49 standard for hierarchical deterministic wallets.
    BIP49 defines a specific path structure for deriving keys from a master seed.

    .. note::
        This class inherits from the ``BIP44Derivation`` class, thereby ensuring that all functions are accessible.
    """

    _purpose: Tuple[int, bool] = (49, True)

    @classmethod
    def name(cls) -> str:
        """
        Get the name of the derivation class.

        :return: The name of the derivation class.
        :rtype: str
        """

        return "BIP49"
