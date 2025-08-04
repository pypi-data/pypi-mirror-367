#!/usr/bin/env python3

# Copyright © 2020-2025, Meheret Tesfaye Batu <meherett.batu@gmail.com>
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit

from typing import Union

from ..exceptions import MnemonicError
from ..mnemonics import (
    IMnemonic, MoneroMnemonic
)
from .iseed import ISeed


class MoneroSeed(ISeed):
    """
    This class generates a root extended private key from a given seed using the
    Monero standard. The Monero standard defines a method for generating mnemonic
    phrases and converting them into a binary seed used for hierarchical
    deterministic wallets.

    .. note::
        This class inherits from the ``ISeed`` class, thereby ensuring that all functions are accessible.
    """

    length = 32

    @classmethod
    def name(cls) -> str:
        """
        Get the name of the seeds class.

        :return: The name of the seeds class.
        :rtype: str
        """

        return "Monero"

    @classmethod
    def from_mnemonic(cls, mnemonic: Union[str, IMnemonic], **kwargs) -> str:
        """
        Converts a mnemonic phrase to its corresponding seed.

        :param mnemonic: The mnemonic phrase to be decoded. Can be a string or an instance of `IMnemonic`.
        :type mnemonic: Union[str, IMnemonic]

        :return: The decoded entropy as a string.
        :rtype: str
        """
        mnemonic = (
            mnemonic.mnemonic() if isinstance(mnemonic, IMnemonic) else mnemonic
        )
        if not MoneroMnemonic.is_valid(mnemonic=mnemonic):
            raise MnemonicError(f"Invalid {cls.name()} mnemonic words")

        return MoneroMnemonic.decode(mnemonic=mnemonic)
