# Formal Verification Guide

## Quick Start
```bash
./run_formal.sh
```

## What Gets Verified

- Syndrome decoding correctness (all 8 cases)
- Error counter behavior (increment, saturate, reset)
- LFSR properties (period 7, no stuck states)
- Error detection flags
- Output stability

## Tools Required

- SymbiYosys (sby)
- Yosys
- SMT solver (boolector)

All included in OSS CAD Suite!

## Results

Check for PASS/FAIL:
```bash
ls qec_decoder_*/PASS
ls qec_decoder_*/FAIL
```

View logs:
```bash
cat qec_decoder_*/logfile.txt
```
