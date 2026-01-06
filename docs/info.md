# Quantum Error Correction Syndrome Decoder

A hardware implementation of a 3-qubit quantum error correction syndrome decoder.

## Overview

This ASIC implements a real-time syndrome decoder for 3-qubit stabilizer codes, supporting both bit-flip and phase-flip error correction with integrated error statistics.

## Features

- **Dual-mode**: Bit-flip (X) and phase-flip (Z) codes
- **Real-time decoding**: Combinational logic for instant correction decisions
- **Error tracking**: 4-bit counter for correctable errors
- **Test mode**: Built-in LFSR pattern generator
- **Error detection**: Flags for correctable and uncorrectable errors

## Specifications

- **Technology**: SKY130 (130nm)
- **Frequency**: 50 MHz
- **Area**: 922 µm² (92 standard cells)
- **Power**: 70.8 µW @ 50 MHz
- **Utilization**: 71.8%

## Syndrome Mapping

| Syndrome | Error Location | Correction |
|----------|----------------|------------|
| 000 | None | 00 |
| 001 | Qubit 2 | 11 |
| 010 | Qubit 1 | 10 |
| 011 | Qubit 0 | 01 |
| 100 | Qubit 0 | 01 |
| 101 | Qubit 1 | 10 |
| 110 | Qubit 2 | 11 |
| 111 | Multiple | Flag |

## Pin Assignments

**Inputs (ui_in[7:0]):**
- [2:0] Syndrome bits
- [3] Mode select (0=bit-flip, 1=phase-flip)
- [4] Test mode enable
- [5] Clear statistics

**Outputs (uo_out[7:0]):**
- [1:0] Correction decision
- [2] Error detected flag
- [3] Uncorrectable error flag
- [7:4] Error count

## Verification

- Comprehensive cocotb testbench (100% pass rate)
- Gate-level simulation verified
- All timing constraints met @ 50 MHz
- DRC/LVS clean

## Author

Thomas Gilbert (thomasgilbert481)