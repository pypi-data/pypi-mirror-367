# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 Abhishek Bawkar
# -*- coding: utf-8 -*-

from __future__ import annotations


class PyAWGException(Exception):
    """
    Base exception class for all exceptions raised by the PyAWG library.

    This exception can be used to catch all errors specific to PyAWG.
    """

    pass


class InvalidChannelNumber(PyAWGException):
    """
    Exception raised for errors in the input channel number.

    Attributes:
        channel -- input channel number which caused the error

    Methods:
        __init__(self, channel) -- initializes the exception with the given channel number
    """

    def __init__(self: InvalidChannelNumber, channel) -> None:
        """
        Initializes the InvalidChannelNumber exception with a custom error message.

        Args:
            channel: The channel number that caused the exception. This can be of any type, but it is recommended to check the datatype and its value.

        Returns:
            None
        """
        super().__init__(
            f"Invalid Channel Number: {channel}; please check the datatype and/or its value"
        )
