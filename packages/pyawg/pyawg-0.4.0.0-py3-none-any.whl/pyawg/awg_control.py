# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 Abhishek Bawkar
# -*- coding: utf-8 -*-

from __future__ import annotations

# from .base import AWG
from typing import Union


from .rigol import RigolDG1000Z
from .siglent import SiglentSDG1000X
import logging
import re

import vxi11


def awg_control(ip_address: str) -> Union [RigolDG1000Z, SiglentSDG1000X]:
    """
    Factory function to create AWG instances based on device identification.
        Args:
            ip_address (str): The IP address of the AWG device.

        Returns:
            AWG: An instance of a specific AWG subclass based on the identified model.

        Raises:
            ValueError: If the AWG device model is unsupported.
            Exception: If there is an error in identifying the AWG device.

        Example:
            awg = awg_control("192.168.1.100")
    """
    try:
        # Create a generic AWG instance to identify the device
        temp_awg = vxi11.Instrument(ip_address)
        manufacturer, model, serial_number, fw_version = (
            temp_awg.ask("*IDN?").strip().split(",")
        )
        temp_awg.close()  # Close the temporary connection

        if re.match("^(DG10[36]2Z)$", model):
            return RigolDG1000Z(ip_address)
        elif re.match("^(SDG10[36]2X( Plus)?)$", model):
            return SiglentSDG1000X(ip_address)
        else:
            raise ValueError(f"Unsupported AWG device: {model}")
    except Exception as e:
        logging.error(f"Failed to identify AWG at {ip_address}: {e}")
        raise
