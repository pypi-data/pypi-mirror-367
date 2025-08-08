# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 Abhishek Bawkar
# -*- coding: utf-8 -*-

from __future__ import annotations

import json
import logging
import time
from typing import Union

import vxi11
from abc import ABC, abstractmethod

from .enums import (
    AmplitudeUnit,
    BurstModeRigol,
    BurstModeSiglent,
    BurstTriggerSource,
    FrequencyUnit,
    OutputLoad,
    PulseWidthUnit,
    WaveformType,
)
from .exceptions import *


class AWG(ABC):
    """
    An Abstract Base Class to represent an Arbitrary Waveform Generator (AWG) device.

    Attributes:
        ip_addr : str
            The IP address of the AWG device.
        device : Union[vxi11.Instrument, None]
            The VXI-11 instrument instance representing the AWG device.
        manufacturer : str
            The manufacturer of the AWG device.
        model : str
            The model of the AWG device.
        serial_number : str
            The serial number of the AWG device.
        fw_version : str
            The firmware version of the AWG device.

    Methods:
        __init__(self, ip_addr: str):
            Initializes the AWG device with the given IP address.
        __str__(self):
            Returns a JSON string representation of the AWG device details.
        close(self):
            Closes the connection to the AWG device.
        get_id(self) -> str:
            Queries the AWG device for its identification string.
        query(self, command):
            Sends a query command to the AWG device and returns the response.
        write(self, command):
            Sends a command to the AWG device.

    """

    ip_addr: str
    device: Union[vxi11.Instrument, None]
    manufacturer: str
    model: str
    serial_number: str
    fw_version: str
    MAX_CHANNELS: int
    MAX_FREQUENCY: Union[float, int]
    MIN_FREQUENCY: Union[float, int]
    MAX_AMPLITUDE: Union[float, int]
    MIN_AMPLITUDE: Union[float, int]

    def __init__(self: AWG, ip_addr: str):
        """
        Initialize the Arbitrary Waveform Generator (AWG) with the given IP address.

        Args:
            ip_addr (str): The IP address of the AWG device.

        Attributes:
            ip_addr (str): The IP address of the AWG device.
            device (vxi11.Instrument or None): The instrument object representing the AWG device.
            manufacturer (str): The manufacturer of the AWG device.
            model (str): The model of the AWG device.
            serial_number (str): The serial number of the AWG device.
            fw_version (str): The firmware version of the AWG device.

        Raises:
            Exception: If the connection to the AWG device fails.

        """
        self.ip_addr = ip_addr
        self.device = None
        try:
            self.device = vxi11.Instrument(ip_addr)
            self.device.clear()
            logging.debug(f"Connected to AWG at {ip_addr}")

            self.manufacturer, self.model, self.serial_number, self.fw_version = (
                self.get_id().strip().split(",")
            )
        except Exception as e:
            logging.error(f"Failed to connect to AWG at {ip_addr}: {e}")
            raise

    def __str__(self: AWG) -> str:
        """
        Returns a JSON string representation of the object with the following attributes:

        - manufacturer: The manufacturer of the device.
        - model: The model of the device.
        - serial_number: The serial number of the device.
        - fw_version: The firmware version of the device.

        The JSON string is formatted with an indentation of 2 spaces.

        Returns:
            str: A JSON string representation of the object.
        """
        return json.dumps(
            dict(
                manufacturer=self.manufacturer,
                model=self.model,
                serial_number=self.serial_number,
                fw_version=self.fw_version,
            ),
            indent=2,
        )

    def _validate_amplitude(self: AWG, amplitude: Union[float, int]) -> None:
        """
        Validates the amplitude value to ensure it is within the supported range.

        Args:
            amplitude (float or int): The amplitude value to be validated.

        Raises:
            TypeError: If the amplitude value is not of valid datatype (float or int).
            ValueError: If the amplitude value is not within the supported range.
        """
        if (type(amplitude) is not int) and (type(amplitude) is not float):
            raise TypeError(
                f"'amplitude' must be float or int; received {type(amplitude)}"
            )
        if not self.MIN_AMPLITUDE <= amplitude <= self.MAX_AMPLITUDE:
            raise ValueError(f"'amplitude' must be between -/+ 10")

    def _validate_channel(self: AWG, channel: int) -> None:
        """
        Validates the channel number to ensure it is within the supported range.

        Args:
            channel (int): The channel number to be validated.

        Raises:
            InvalidChannelNumber: If the channel number is not valid or not within the supported range.
        """
        if (type(channel) is not int) or (not 1 <= channel <= self.MAX_CHANNELS):
            raise InvalidChannelNumber(channel)

    def _validate_frequency(self: AWG, frequency: Union[float, int]) -> None:
        """
        Validates the frequency value to ensure it is within the supported range.

        Args:
            frequency (float or int): The frequency value to be validated.

        Raises:
            TypeError: If the frequency value is not of valid datatype (float or int).
            ValueError: If the frequency value is not within the supported range.
        """
        if (type(frequency) is not int) and (type(frequency) is not float):
            raise TypeError(
                f"'frequency' must be float or int; received {type(frequency)}"
            )
        if not self.MIN_FREQUENCY <= frequency <= self.MAX_FREQUENCY:
            raise ValueError(
                f"'frequency' must be between {self.MIN_FREQUENCY} and {self.MAX_FREQUENCY}"
            )

    def close(self: AWG) -> None:
        """
        Closes the connection to the AWG device.

        This method attempts to close the connection to the Arbitrary Waveform Generator (AWG) device.
        If the connection is successfully closed, a debug message is logged. If an error occurs during
        the process, an error message is logged with the exception details.

        Raises:
            Exception: If there is an issue closing the connection to the AWG device.
        """
        try:
            self.device.close()
            logging.debug("Disconnected from AWG")
        except Exception as e:
            logging.error(f"Failed to disconnect from AWG: {e}")

    def get_id(self: AWG) -> str:
        """
        Retrieves the identification string of the device.

        Returns:
            str: The identification string of the device.
        """
        return self.query("*IDN?")

    def query(self: AWG, command: str) -> str:
        """
        Sends a query command to the device and returns the response.

        Args:
            command (str): The command to be sent to the device.

        Returns:
            str: The response received from the device.

        Raises:
            Exception: If there is an error in sending the query or receiving the response.
        """
        try:
            response = self.device.ask(command)
            logging.debug(f"Sent query: {command}, Received: {response}")
            return response
        except Exception as e:
            logging.error(f"Failed to query command: {e}")
            raise

    def reset(self: AWG) -> None:
        """
        Sends a query command to the device and returns the response.

        Raises:
            Exception: If there is an error in sending the query or receiving the response.
        """
        try:
            response = self.device.write("*RST")
        except Exception as e:
            logging.error(f"Failed to reset the instrument: {e}")
            raise

    @abstractmethod
    def set_amplitude(
        self: AWG, channel, amplitude: float, unit: AmplitudeUnit = AmplitudeUnit.VPP
    ) -> None:
        """Sets the amplitude for the specified channel."""
        raise NotImplementedError

    @abstractmethod
    def set_burst_delay(self: AWG, channel: int, delay: Union[float, int]) -> None:
        """Sets the burst dealy for the specified channel."""
        raise NotImplementedError

    @abstractmethod
    def set_burst_mode(
        self: AWG, channel: int, mode: Union[BurstModeRigol, BurstModeSiglent]
    ) -> None:
        """Sets the burst mode for the specified channel."""
        raise NotImplementedError

    @abstractmethod
    def set_burst_period(self: AWG, channel: int, period: Union[float, int]) -> None:
        """Sets the burst period for the specified channel."""
        raise NotImplementedError

    @abstractmethod
    def set_burst_state(self: AWG, channel: int, state: bool) -> None:
        """Sets the state for the specified channel."""
        raise NotImplementedError

    @abstractmethod
    def set_burst_trigger_source(
        self: AWG, channel: int, trigger_source: BurstTriggerSource
    ) -> None:
        """Sets the burst trigger source for the specified channel."""
        raise NotImplementedError

    @abstractmethod
    def set_duty_cycle(self: AWG, channel: int, duty_cycle: Union[float, int]) -> None:
        """Sets the duty cycle for the specified channel."""
        raise NotImplementedError

    @abstractmethod
    def set_frequency(
        self: AWG,
        channel: int,
        frequency: float,
        unit: FrequencyUnit = FrequencyUnit.HZ,
    ) -> None:
        """Sets the frequency for the specified channel."""
        raise NotImplementedError

    @abstractmethod
    def set_offset(self: AWG, channel: int, offset_voltage: Union[float, int]) -> None:
        """Sets the offset voltage for the specified channel."""
        raise NotImplementedError

    @abstractmethod
    def set_output(self: AWG, channel: int, state: bool) -> None:
        """Sets the output state of the specified channel."""
        raise NotImplementedError

    @abstractmethod
    def set_output_load(
        self: AWG, channel: int, load: Union[float, int, OutputLoad]
    ) -> None:
        """Sets the output load for the specified channel."""
        raise NotImplementedError

    @abstractmethod
    def set_phase(self: AWG, channel: int, phase: Union[float, int]) -> None:
        """Sets the phase for the specified channel."""
        raise NotImplementedError

    @abstractmethod
    def set_pulse_width(
        self: AWG, channel: int, pulse_width: Union[float, int], unit: PulseWidthUnit
    ) -> None:
        """Sets the pulse width for the specified channel."""
        raise NotImplementedError

    @abstractmethod
    def set_waveform(self: AWG, channel: int, waveform_type: WaveformType) -> None:
        """Sets the waveform type for the specified channel."""
        raise NotImplementedError

    @abstractmethod
    def sync_phase(self: AWG, channel: int) -> None:
        """Synchronizes the phase of the specified channel with the other channel."""
        raise NotImplementedError

    @abstractmethod
    def trigger_burst(self: AWG, channel: int) -> None:
        """Triggers a burst on the specified channel."""
        raise NotImplementedError

    def write(self: AWG, command: str) -> None:
        """
        Sends a command to the device.

        Args:
            command (str): The command string to be sent to the device.

        Raises:
            Exception: If there is an error while writing the command to the device.
        """
        try:
            self.device.write(command)
            logging.debug(f"Sent command: {command}")
            time.sleep(0.25)
        except Exception as e:
            logging.error(f"Failed to write command: {e}")
            raise
