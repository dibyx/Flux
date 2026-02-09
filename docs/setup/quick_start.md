# Quick Start Guide

Get up and running with **flux** in 15 minutes.

## Prerequisites

- Linux (Ubuntu 22.04+) or macOS
- 8GB RAM minimum
- 20GB free disk space
- Basic command-line familiarity

---

## Option 1: Simulation Only (Fastest)

**Goal**: Run the flux GPU testbench in simulation.

### Step 1: Install Verilator & Python

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y verilator python3-pip gtkwave

# macOS
brew install verilator python3

# Install cocotb
pip3 install cocotb pytest
```

### Step 2: Clone flux Repository

```bash
git clone https://github.com/your-org/flux.git
cd flux
```

### Step 3: Run Testbench

```bash
cd rtl/test

# Create Makefile
cat > Makefile << 'EOF'
SIM = verilator
TOPLEVEL_LANG = verilog
VERILOG_SOURCES = ../src/gpu_top.sv
TOPLEVEL = gpu_top
MODULE = test_gpu_top
include $(shell cocotb-config --makefiles)/Makefile.sim
EOF

# Run simulation
make

# View waveform (if VCD dump enabled)
gtkwave dump.vcd
```

**Expected**: Test passes, waveform shows clock toggling and register write.

---

## Option 2: FPGA Prototype (ULX3S Board)

**Goal**: Synthesize flux for a Lattice ECP5 FPGA.

### Step 1: Install FPGA Toolchain

```bash
# Install Yosys, nextpnr, Trellis
sudo apt-get install yosys nextpnr-ecp5 libecp5-dev

# Or build from source (see toolchain_guide.md)
```

### Step 2: Synthesize

```bash
cd flux/hw-tools/fpga/ulx3s

# Run synthesis and place-and-route
make bitstream

# Expected output: gpu_top.bit
```

### Step 3: Program FPGA

```bash
# Install programmer
sudo apt-get install fujprog

# Upload bitstream
fujprog gpu_top.bit
```

**Expected**: FPGA programmed. If connected to HDMI monitor, you should see video output (test pattern).

---

## Option 3: ASIC Flow (Educational)

**Goal**: Generate GDSII layout using SkyWater 130nm PDK.

### Step 1: Install Docker

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
# Log out and back in
```

### Step 2: Install OpenLane

```bash
git clone https://github.com/The-OpenROAD-Project/OpenLane.git
cd OpenLane
make pull-openlane  # Large download (~10GB)
```

### Step 3: Prepare flux for Hardening

```bash
cd flux/hw-tools/asic

# Copy RTL to OpenLane design folder
cp ../../rtl/src/gpu_top.sv OpenLane/designs/flux/src/

# Run flow
make openlane DESIGN=flux
```

**Expected**: GDSII file generated after ~30-60 minutes. View with Magic:

```bash
magic -T ~/.volare/sky130A/libs.tech/magic/sky130A.tech \
      OpenLane/designs/flux/runs/RUN_*/results/final/gds/flux.gds
```

---

## Learning Path

### Week 1: Theory
- Read [GPU Fundamentals](../theory/gpu_fundamentals.md)
- Study [Pipeline Explained](../theory/pipeline_explained.md)
- Review [Memory Systems](../theory/memory_systems.md)

### Week 2: Simulation
- Modify `gpu_top.sv` to add a simple accumulator register
- Write cocotb test to verify accumulator behavior
- Debug using GTKWave waveforms

### Week 3: Synthesis
- Synthesize modified design for FPGA
- Measure resource usage (LUTs, FFs, BRAMs)
- Optimize for area/speed

### Week 4: Toolchain
- Set up LLVM for shader compilation
- Write a simple shader in GLSL
- Compile to SPIR-V

---

## Common Issues

### Error: "cocotb module not found"

**Solution**:
```bash
pip3 install --user cocotb
export PYTHONPATH=$HOME/.local/lib/python3.x/site-packages
```

### Error: Verilator compile fails

**Solution**: Check GCC version (need 7.0+):
```bash
g++ --version
sudo apt-get install g++-11
export CXX=g++-11
```

### FPGA bitstream doesn't work

**Solution**: Verify board connection and programmer:
```bash
# List USB devices
lsusb | grep FTDI

# Check permissions
sudo chmod 666 /dev/ttyUSB0
```

---

## Next Steps

Depending on your interest:

**Hardware Designer** → Read [shader_core.sv Design Doc](../../rtl/docs/shader_core.md)  
**Software Engineer** → Read [Compiler Architecture](../../sw-toolchain/README.md)  
**Both** → Continue through the [Roadmap](../../meta/roadmap.md)

---

## Getting Help

- **GitHub Issues**: [your-org/flux/issues](https://github.com/your-org/flux/issues)
- **Discord**: [Join flux community](https://discord.gg/yourlink)
- **Documentation**: [Full Docs](../../README.md)

Happy GPU building! 🚀
