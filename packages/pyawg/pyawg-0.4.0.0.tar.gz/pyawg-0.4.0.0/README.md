# PyAWG

A simple (unofficial) python library to control some functions of Arbitrary Waveform Generators (aka Function / Signal Generators) from various manufacturers.

Currently following function generators are supported. Volunteers are welcome to extend it to support other models keeping the basic functions same.

## Siglent
- [Siglent SDG1000X Series Arbitrary Waveform Generator](https://www.siglenteu.com/download/8715/?tmstv=1740404771) 
  - SDG1032X
  - SDG1032X Plus
  - SDG1062X
  - SDG1062X Plus

## Rigol
- [Rigol DG1000Z Series Arbitrary Waveform Generator](https://www.batronix.com/pdf/Rigol/ProgrammingGuide/DG1000Z_ProgrammingGuide_EN.pdf)
  - DG1032Z
  - DG1062Z

## System Requirements

- Python (>=3.8,<4.0)

## Installation

Installation of the library is very simple via `pip` command as shown below.

```python
>>> pip install pyawg
```

## Functions

Following functions are implemented in the library. In case, any other command needs to be sent to the AWG, the `write()` and `query()` functions can be used to send any command 
to the AWG. The library will automatically add the required line terminator to the command. All bugs and new implementations/extensions are welcome via Github issues and/or pull 
requests.

| Functionality            | Function                     | Implemented | Tested | Description                                                                                                                          | 
|--------------------------|------------------------------|-------------|--------|--------------------------------------------------------------------------------------------------------------------------------------|
| Identify                 | `get_id()`                   | Yes         | Yes    | Get the ID of the connected AWG.                                                                                                     |
| Reset                    | `reset()`                    | Yes         | Yes    | Reset the AWG to system defaults.                                                                                                    |
| Close                    | `close()`                    | Yes         | Yes    | Close the connection to the AWG.                                                                                                     |
| Set Output               | `set_output()`               | Yes         | Yes    | Enables or disables the output.                                                                                                      |
| Set Output Load          | `set_output_load()`          | Yes         |        | Set the output load impedance.                                                                                                       |
| Set Waveform             | `set_waveform()`             | Yes         | Yes    | Set the waveform type.                                                                                                               |
| Set Frequency            | `set_frequency()`            | Yes         | Yes    | Set the frequency of the waveform in Hz, KHz, MHz.                                                                                   |
| Set Amplitude            | `set_amplitude()`            | Yes         | Yes    | Set the amplitude of the waveform in Vpp.                                                                                            |
| Set Offset               | `set_offset()`               | Yes         | Yes    | Set the offset voltage in Vdc.                                                                                                       |
| Set Duty Cycle           | `set_duty_cycle()`           | Yes         | Yes    | Set the duty cycle of the waveform in percentage.                                                                                    |
| Set Pulse Width          | `set_pulse_width()`          | Yes         |        | Set the pulse width of the waveform in seconds.                                                                                      |
| Set Phase                | `set_phase()`                | Yes         | Yes    | Set the phase shift in degrees.                                                                                                      |
| Synchronize Phase        | `sync_phase()`               | Yes         | Yes    | Synchronize the phase of the channels.                                                                                               |
| Enable Burst Mode        | `enable_burst_mode()`        | Yes         |        | Enable or disable burst mode.                                                                                                        |
| Set Burst Delay          | `set_burst_delay()`          | Yes         |        | Set the burst delay.                                                                                                                 |
| Set Burst Mode           | `set_burst_mode()`           | Yes         |        | Set the burst mode.                                                                                                                  |
| Set Burst Period         | `set_burst_period()`         | Yes         |        | Set the period of the burst.                                                                                                         |
| Set Burst State          | `set_burst_state()`          | Yes         |        | Turns the burst mode ON or OFF.                                                                                                      |
| Set Burst Trigger Source | `set_burst_trigger_source()` | Yes         |        | Set the trigger source for burst mode.                                                                                               |
| Trigger Burst            | `trigger_burst()`            | Yes         |        | Trigger the burst.                                                                                                                   |
| Write                    | `write()`                    | Yes         | Yes    | Write any documented command to the AWG. Please refer official programming guide for your instrument.                                |
| Query                    | `query()`                    | Yes         | Yes    | Query any documented command and retrieve the information from the AWG. Please refer official programming guide for your instrument. |


## Usage

Here is an exmaple with Rigol DG1032Z Arbitrary Waveform Generator. For the variants from other manufacturers, the `DEBUG` logs would be printed slightly different based on their 
respective syntax. 

```python
>>> from pyawg import awg_control, AmplitudeUnit, FrequencyUnit, WaveformType

>>> # Example for Square Wave of 10KHz, 5VPP with offset of 2.5V and phase shift of 90°

>>> awg = awg_control('192.168.1.100')
[2025.03.06 21:12:46][DEBUG] Connected to AWG at 192.168.1.100
[2025.03.06 21:12:46][DEBUG] Sent query: *IDN?, Received: Rigol Technologies,DG1032Z,DG1ZA2012604407,03.01.12  
[2025.03.06 21:12:46][DEBUG] RigolDG1000Z instance created.

>>> awg.set_waveform(1, WaveformType.SQUARE)
[2025.03.06 21:15:51][DEBUG] Sent command: SOUR1:FUNC SQU
[2025.03.06 21:15:51][DEBUG] Channel 1 waveform set to SQU

>>> awg.set_frequency(1, 10, FrequencyUnit.KHZ)
[2025.03.06 21:16:41][DEBUG] Sent command: SOUR1:FREQ 10KHZ
[2025.03.06 21:16:41][DEBUG] Channel 1 frequency set to 10KHZ

>>> awg.set_amplitude(1, 5, AmplitudeUnit.VPP)
[2025.03.06 21:18:19][DEBUG] Sent command: SOUR1:VOLT 5VPP
[2025.03.06 21:18:19][DEBUG] Channel 1 amplitude set to 5VPP

>>> awg.set_offset(1, 2.5)
[2025.03.06 21:20:02][DEBUG] Sent command: SOUR1:VOLT:OFFS 2.5
[2025.03.06 21:20:02][DEBUG] Channel 1 offset voltage set to 2.5 Vdc

>>> awg.set_phase(1, 90)
[2025.03.06 21:25:08][DEBUG] Sent command: SOUR1:PHAS 90
[2025.03.06 21:25:08][DEBUG] Channel 1 phase set to 90°

>>> awg.set_output(1, True)
[2025.03.06 21:25:34][DEBUG] Sent command: OUTP1 ON
[2025.03.06 21:25:34][DEBUG] Channel 1 output has been set to ON

>>> awg.close()
[2025.03.06 21:35:13][DEBUG] Disconnected from AWG
```


## Exceptions 

The library raises following exceptions in case of any error.

* InvalidChannelNumber : This exception is raised when the channel number is invalid. The valid channel numbers are 1 and 2.
* TypeError : This exception is raised when the datatype of an argument passed while calling a method is not valid. For example, if the frequency is passed as a string instead of a float.
* ValueError : This exception is raised when the value of an argument passed while calling a method is not valid. For example, if the frequency is passed as a negative number.
* Exception : This exception is raised when there is an error in the communication with the AWG. For example, if the AWG is not connected or if the command sent to the AWG is not valid.


## Cyber Resilience Act (CRA) Compliance Statement (applicable for the usage of this library in the EU countries)

The `pyawg` library is an open-source Python tool released under the GPLv3 license. It is designed for internal use in test automation environments, specifically to control arbitrary waveform generators (AWGs) over the VXI-11 protocol. 

Its primary usage is intended to be used **only as an internal tool for development and testing** of embedded hardware, firmware and software products.
It is **not meant to be part of any embedded software, firmware, or product delivered to customers**.

As such:
- The library is not incorporated into any commercial product.
- It is not distributed to end users or external third parties.
- It does not include cryptographic functionality or secure communication features.
- It does not collect, transmit, or store data outside the local test environment.
- It operates entirely within a controlled internal network or lab setup.

Given its limited scope and internal-only use, this library does not fall within the applicability of the EU Cyber Resilience Act (CRA), which focuses on digital products made available on the EU market. The use of `pyawg` aligns with current industry practices for open-source internal tooling and presents no known cybersecurity exposure in its intended context.

For a full breakdown of dependencies and software structure, please refer to the [Software Bill of Materials (SBOM)](https://github.com/abhishekbawkar/pyawg/blob/master/SBOM.md).


## Ownership and Contribution

This library was created and is maintained by Abhishek Bawkar as an independent open-source project.

The project is made available in good faith as a productivity aid for internal use. While it is not an official company product, collaboration and private forking for internal deployment is welcome and encouraged under the terms of the GPLv3 license.

All source code and documentation reflect the author’s original work unless stated otherwise.

Please refer to the [Contributor Guidelines](https://github.com/abhishekbawkar/pyawg/blob/master/CONTRIBUTING.md) for details on how to extend or modify this library responsibly.