# Quantum Error Correction Syndrome Decoder

[![test](https://github.com/TinyTapeout/tt-qec-decoder/actions/workflows/test.yaml/badge.svg)](https://github.com/TinyTapeout/tt-qec-decoder/actions/workflows/test.yaml)
[![gds](https://github.com/TinyTapeout/tt-qec-decoder/actions/workflows/gds.yaml/badge.svg)](https://github.com/TinyTapeout/tt-qec-decoder/actions/workflows/gds.yaml)
[![docs](https://github.com/TinyTapeout/tt-qec-decoder/actions/workflows/docs.yaml/badge.svg)](https://github.com/TinyTapeout/tt-qec-decoder/actions/workflows/docs.yaml)

A hardware implementation of a real-time 3-qubit quantum error correction syndrome decoder for Tiny Tapeout.

## Overview

This ASIC implements a syndrome decoder for 3-qubit stabilizer codes, supporting both bit-flip (X) and phase-flip (Z) error correction with integrated error statistics and analysis capabilities.

## Features

- **Dual-Mode Error Correction**: Supports both bit-flip and phase-flip quantum error codes
- **Real-Time Decoding**: Combinational logic for instant correction decisions
- **Advanced Statistics**:
  - 16-bit total error counter (with saturation)
  - Per-qubit error classification (8-bit counters)
  - Uncorrectable error tracking
  - 8-entry syndrome history buffer
- **Test Mode**: Built-in 16-bit maximal-length LFSR pattern generator
- **Error Detection**: Flags for correctable and uncorrectable errors

## Specifications

| Parameter | Value |
|-----------|-------|
| **Technology** | SKY130A (130nm) |
| **Target Frequency** | 50 MHz |
| **Total Cells** | 505 (excluding fill/tap) |
| **Utilization** | 29.1% |
| **Wire Length** | 9,744 µm |
| **Clock Period** | 20 ns |

### Cell Breakdown
- Combinational Logic: 159 cells
- Flip-Flops: 91 cells
- Buffers: 41 cells
- AND/NAND/OR/NOR: 111 cells
- Multiplexers: 18 cells

## Syndrome Mapping

| Syndrome | Error Location | Correction | Flags |
|----------|----------------|------------|-------|
| `000` | None | `00` | No error |
| `001` | Qubit 2 | `11` | Error detected |
| `010` | Qubit 1 | `10` | Error detected |
| `011` | Qubit 0 | `01` | Error detected |
| `100` | Qubit 0 | `01` | Error detected |
| `101` | Qubit 1 | `10` | Error detected |
| `110` | Qubit 2 | `11` | Error detected |
| `111` | Multiple errors | `00` | Error + Uncorrectable |

## Pin Assignments

### Dedicated Inputs (`ui_in[7:0]`)
| Bits | Function |
|------|----------|
| `[2:0]` | Syndrome bits |
| `[3]` | Mode select (0=bit-flip, 1=phase-flip) |
| `[4]` | Test mode enable (LFSR) |
| `[5]` | Clear statistics counters |
| `[7:6]` | Reserved |

### Dedicated Outputs (`uo_out[7:0]`)
| Bits | Function |
|------|----------|
| `[1:0]` | Correction decision |
| `[2]` | Error detected flag |
| `[3]` | Uncorrectable error flag |
| `[7:4]` | Error count (low nibble) |

### Bidirectional I/O (`uio_in[7:0]` / `uio_out[7:0]`)
| Bits | Input Function | Output Function (selected by `uio_in[1:0]`) |
|------|----------------|---------------------------------------------|
| `[1:0]` | Statistics selector | - |
| `[7:2]` | Reserved | Extended statistics data |

**Statistics Selector Values:**
- `00`: Error count high byte (bits 15:8)
- `01`: Qubit 0 error count
- `10`: Qubit 1 error count
- `11`: Qubit 2 + syndrome history + uncorrectable count

## Getting Started

### Prerequisites

- [OSS CAD Suite](https://github.com/YosysHQ/oss-cad-suite-build) (includes Yosys, iverilog, cocotb)
- Python 3.11+
- Make

### Running Tests

**RTL Simulation:**
```bash
cd test
make clean
make
```

**Gate-Level Simulation:**
```bash
cd test
make clean
make GATES=yes
```

**Formal Verification:**
```bash
cd formal
./run_formal.sh
```

### Viewing Waveforms
```bash
# Using GTKWave
gtkwave test/tb.fst test/tb.gtkw

# Using Surfer
surfer test/tb.fst
```

## Verification Status

✅ **RTL Tests**: 14/14 cocotb tests passing
- Basic syndrome decoding (all 8 cases)
- Error flag behavior
- 16-bit LFSR operation
- Error counter saturation
- Mode switching
- Statistics clearing
- Per-qubit error classification
- Reset behavior
- Output stability

✅ **Formal Verification**: All assertions proven
- Syndrome decoding correctness
- Error flag logic
- Interface constraints
- Coverage of all cases

✅ **Gate-Level Tests**: 3/3 passing
- Basic syndrome decoding
- Reset behavior
- Error flag functionality

## Project Structure
```
.
├── src/
│   ├── tt_um_qec_decoder.v      # Main RTL design
│   └── config.json              # OpenLane configuration
├── test/
│   ├── test.py                  # Cocotb RTL testbench
│   ├── test_gl.py              # Gate-level testbench
│   └── Makefile
├── formal/
│   ├── tt_um_qec_decoder_formal.sv  # Formal properties
│   ├── qec_decoder.sby          # SymbiYosys configuration
│   └── run_formal.sh            # Verification script
├── docs/
│   └── info.md                  # Project documentation
└── .github/workflows/           # CI/CD workflows
```

## Development

### Using the DevContainer

This project includes a VSCode DevContainer with all tools pre-installed:

1. Open in VSCode
2. Click "Reopen in Container" when prompted
3. Tools available: iverilog, cocotb, Verilator, Verible, LibreLane

### Linting & Formatting
```bash
# Verilog linting (Verilator)
verilator --lint-only src/tt_um_qec_decoder.v

# Format Verilog code
verible-verilog-format --inplace src/tt_um_qec_decoder.v
```

## Building the GDS

The design is built using OpenLane (SKY130 PDK):
```bash
# Runs automatically via GitHub Actions
# Or manually with:
docker run -v $(pwd):/work tinytapeout/tt-gds-action
```

## Author

**Thomas Gilbert** ([@thomasgilbert481](https://github.com/thomasgilbert481))

Enhanced Version: January 2026

## Acknowledgments

- [Tiny Tapeout](https://tinytapeout.com) - Open-source silicon project
- [SkyWater SKY130](https://github.com/google/skywater-pdk) - 130nm PDK
- [OpenLane](https://github.com/efabless/openlane) - RTL-to-GDS flow

## License

This project is submitted to Tiny Tapeout and follows their submission guidelines.

---

**Note**: This is a educational implementation of quantum error correction concepts in hardware. For production quantum computing applications, more sophisticated codes (Surface codes, LDPC, etc.) are typically used.
