# FPGA Build Guide for flux GPU

## Overview

This guide shows how to synthesize the flux GPU for the **ULX3S FPGA board** (ECP5 LFE5U-85F).

---

## Hardware Requirements

### Recommended Board
- **ULX3S** - LFE5U-85F (85k LUTs)
  - Available from: Radiona, CrowdSupply
  - Price: ~$150-200
  - Features: 85k LUTs, 208KB BRAM, DSP slices, HDMI, USB

### Alternatives
- **OrangeCrab** - ECP5-25F (smaller, may not fit entire design)
- **Colorlight i5** - ECP5-25F (cheap, no peripherals)

---

## Software Setup

Install the open-source ECP5 toolchain:

### Linux (Ubuntu/Debian)
```bash
# Install Yosys (synthesis)
sudo apt install yosys

# Install nextpnr-ecp5 (place & route)
sudo apt install nextpnr-ecp5

# Install Project Trellis tools
sudo apt install fpga-icestorm libtrellis1

# Install OpenOCD (programming)
sudo apt install openocd
```

### macOS
```bash
brew install yosys nextpnr-ecp5 ecppack openocd
```

### Windows (WSL2)
Use Ubuntu WSL2 and follow Linux instructions.

---

## Build Process

### Step 1: Navigate to FPGA directory
```bash
cd flux/hw-tools/fpga
```

### Step 2: Run synthesis
```bash
make all
```

This will:
1. **Yosys**: Synthesize RTL → netlist (`gpu_top.json`)
2. **nextpnr-ecp5**: Place & Route → configuration (`gpu_top.config`)
3. **ecppack**: Generate bitstream (`build/gpu_top.bit`)

**Expected time**: 5-15 minutes

### Step 3: Check resource usage
```bash
make report
```

**Expected output** (approximate):
```
Number of LUTs:       8,000 / 85,000   (9%)
Number of FFs:       12,000 / 85,000  (14%)
Number of BRAMs:         32 / 208     (15%)
```

### Step 4: Check timing
```bash
make timing
```

**Target frequency**: 50 MHz  
**Expected**: Should meet timing at 50 MHz

---

## Programming the FPGA

### Connect ULX3S
1. Connect ULX3S via USB-C cable
2. Ensure FPGA power switch is ON

### Program bitstream
```bash
make prog
```

### Verify
- LEDs should light up showing status
- VGA output should show test pattern (if connected)

---

## Expected Resource Usage

### Shader Core Alone
- **LUTs**: ~6,000 (register file + ALU + decoder)
- **FFs**: ~10,000 (registers + pipeline stages)
- **BRAMs**: 16 KB register file = 32× 18Kb BRAM tiles

### With GPU Top
- **LUTs**: ~8,000
- **FFs**: ~12,000
- **BRAMs**: ~32 tiles

**Note**: FP32 operations use DSP slices if available, otherwise LUTs.

---

## Troubleshooting

### Synthesis fails with "undefined module"
- Check that all `.sv` files are listed in `synth.ys`
- Verify file paths are correct

### Timing not met
- Reduce target frequency in `Makefile`: `--freq 40`
- Check critical path in `build/pnr.log`
- Add pipeline stages if needed

### Programming fails
- Check USB connection
- Verify OpenOCD is installed: `openocd --version`
- Try manual programming: `ujprog build/gpu_top.bit` (ULX3S specific)

### BRAM usage too high
- Reduce `NUM_THREADS` in `register_file.sv` (e.g., 16 instead of 32)
- Use distributed RAM instead of BRAM for small memories

---

## Next Steps

### Test on Hardware
1. Monitor LED outputs (should blink if alive)
2. Connect UART for debugging
3. Display test pattern via VGA

### Optimize
1. Area: Reduce register file size
2. Timing: Add pipeline stages in ALU
3. Power: Clock gating for unused modules

### Expand
1. Add instruction memory (BRAM)
2. Implement warp scheduler
3. Add memory controller for external SDRAM

---

## Build Commands Reference

| Command | Description |
|---------|-------------|
| `make all` | Synthesize + P&R + bitstream |
| `make prog` | Program FPGA |
| `make report` | Resource utilization |
| `make timing` | Timing summary |
| `make clean` | Remove build artifacts |

---

## Resource Links

- **ULX3S Documentation**: https://ulx3s.github.io/
- **Project Trellis**: https://github.com/YosysHQ/prjtrellis
- **nextpnr-ecp5**: https://github.com/YosysHQ/nextpnr
- **Yosys Manual**: https://yosyshq.net/yosys/

---

**Last Updated**: 2026-02-08
