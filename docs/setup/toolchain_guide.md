# Complete Toolchain Setup Guide

This guide provides step-by-step instructions to set up a complete GPU development environment for the **flux** project.

## Overview

You'll install tools for:
- **HDL Simulation**: Verilator, Icarus Verilog
- **Verification**: Cocotb (Python-based testbenches)
- **FPGA Synthesis**: Yosys, nextpnr
- **ASIC Flow**: OpenLane, Magic, KLayout
- **Software**: LLVM, Mesa 3D, Vulkan SDK

**Estimated time**: 2-4 hours (depending on internet speed)

---

## Platform Support

| Tool | Windows | Linux | macOS |
|------|---------|-------|-------|
| Verilator | ✓ (WSL) | ✓ | ✓ |
| Yosys | ✓ (WSL) | ✓ | ✓ |
| OpenLane | Docker | ✓ | Docker |
| LLVM | ✓ | ✓ | ✓ |

**Recommendation**: Linux (Ubuntu 22.04 LTS) for best compatibility. Windows users should use WSL2.

---

## Part 1: HDL Simulation Tools

### 1.1 Verilator (Fast Cycle-Accurate Simulator)

**Linux (Ubuntu/Debian)**:
```bash
# Install dependencies
sudo apt-get install -y git make autoconf g++ flex bison ccache
sudo apt-get install -y libgoogle-perftools-dev numactl perl-doc
sudo apt-get install -y libfl2 libfl-dev zlib1g zlib1g-dev

# Clone and build Verilator
git clone https://github.com/verilator/verilator
cd verilator
git checkout v5.010
autoconf
./configure
make -j$(nproc)
sudo make install

# Verify installation
verilator --version
```

**Windows (WSL2)**:
- Enable WSL2: `wsl --install`
- Install Ubuntu 22.04 from Microsoft Store
- Follow Linux instructions above

**macOS**:
```bash
brew install verilator
```

### 1.2 Icarus Verilog (Alternative Simulator)

**Linux**:
```bash
sudo apt-get install iverilog gtkwave
```

**macOS**:
```bash
brew install icarus-verilog
```

**Test**:
```bash
# Create test file
echo 'module test; initial $display("Hello GPU!"); endmodule' > test.v
iverilog -o test test.v
vvp test
# Expected output: Hello GPU!
```

### 1.3 GTKWave (Waveform Viewer)

**Linux**:
```bash
sudo apt-get install gtkwave
```

**macOS**:
```bash
brew install gtkwave
```

**Windows**: Download installer from [gtkwave.sourceforge.net](http://gtkwave.sourceforge.net/)

---

## Part 2: Verification Tools

### 2.1 Cocotb (Python Testbenches)

**Prerequisites**: Python 3.7+

```bash
# Install Python dependencies
pip3 install cocotb pytest cocotb-test

# Verify
python3 -c "import cocotb; print(cocotb.__version__)"
```

**Create a test (example)**:
```python
# test_example.py
import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def simple_test(dut):
    await Timer(1, units='ns')
    assert dut.output == 0
```

---

## Part 3: FPGA Synthesis Tools

### 3.1 Yosys (Open-Source Synthesis)

**Linux**:
```bash
# Install from package manager
sudo apt-get install yosys

# Or build from source for latest version
git clone https://github.com/YosysHQ/yosys.git
cd yosys
make -j$(nproc)
sudo make install
```

**macOS**:
```bash
brew install yosys
```

**Test**:
```bash
yosys -p "read_verilog test.v; synth; write_json output.json"
```

### 3.2 nextpnr (Place & Route)

**Linux**:
```bash
# Install dependencies
sudo apt-get install cmake libboost-all-dev libeigen3-dev

# Clone and build for ECP5 (example)
git clone https://github.com/YosysHQ/nextpnr
cd nextpnr
cmake -DARCH=ecp5 .
make -j$(nproc)
sudo make install
```

**Supported Architectures**:
- `ARCH=ice40` → Lattice iCE40 (UPduino, iCEstick)
- `ARCH=ecp5` → Lattice ECP5 (ULX3S)
- `ARCH=nexus` → Lattice Nexus

### 3.3 Project IceStorm / Trellis (Bitstream Tools)

**For iCE40**:
```bash
git clone https://github.com/YosysHQ/icestorm.git
cd icestorm
make -j$(nproc)
sudo make install
```

**For ECP5**:
```bash
git clone https://github.com/YosysHQ/prjtrellis
cd prjtrellis/libtrellis
cmake .
make
sudo make install
```

---

## Part 4: ASIC Tools (OpenLane Flow)

### 4.1 Docker Setup

**Linux**:
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
# Log out and back in

# Verify
docker run hello-world
```

### 4.2 OpenLane Installation

```bash
# Clone OpenLane
git clone https://github.com/The-OpenROAD-Project/OpenLane.git
cd OpenLane
git checkout 2023.12.10

# Pull Docker image (this takes time, ~10GB download)
make pull-openlane

# Test installation
make test
```

### 4.3 SkyWater PDK

The Process Design Kit is included in OpenLane Docker image. To access locally:

```bash
export PDK_ROOT=$HOME/pdk
make pdk
```

### 4.4 Magic (Layout Viewer)

**Linux**:
```bash
sudo apt-get install magic
```

**Usage**:
```bash
magic -T ~/.volare/sky130A/libs.tech/magic/sky130A.tech layout.mag
```

---

## Part 5: Software Toolchain

### 5.1 LLVM (Compiler Infrastructure)

**Linux**:
```bash
# Install prebuilt binaries
sudo apt-get install llvm-15 clang-15

# Or build from source
git clone https://github.com/llvm/llvm-project.git
cd llvm-project
mkdir build && cd build
cmake -DLLVM_ENABLE_PROJECTS="clang;lld" -DCMAKE_BUILD_TYPE=Release ../llvm
make -j$(nproc)
sudo make install
```

### 5.2 SPIRV-Tools

```bash
# Install SPIR-V ecosystem
sudo apt-get install spirv-tools spirv-headers

# Or from source
git clone https://github.com/KhronosGroup/SPIRV-Tools.git
cd SPIRV-Tools
mkdir build && cd build
cmake ..
make -j$(nproc)
sudo make install
```

### 5.3 Vulkan SDK

**Linux**:
```bash
# Download from lunarg.com/vulkan-sdk
wget -qO- https://packages.lunarg.com/lunarg-signing-key-pub.asc | sudo tee /etc/apt/trusted.gpg.d/lunarg.asc
sudo wget -qO /etc/apt/sources.list.d/lunarg-vulkan-jammy.list http://packages.lunarg.com/vulkan/lunarg-vulkan-jammy.list
sudo apt update
sudo apt install vulkan-sdk
```

**Verify**:
```bash
vulkaninfo | head -20
```

### 5.4 Mesa 3D (Driver Framework)

**For development (Linux)**:
```bash
# Install build dependencies
sudo apt-get install meson ninja-build libdrm-dev libx11-xcb-dev \
    libxcb-dri2-0-dev libxcb-dri3-dev libxcb-present-dev \
    libxshmfence-dev libwayland-dev

# Clone Mesa
git clone https://gitlab.freedesktop.org/mesa/mesa.git
cd mesa

# Configure (minimal build for flux driver)
meson setup build -Dgallium-drivers=flux -Dvulkan-drivers= -Dplatforms=x11
ninja -C build
```

---

## Part 6: Auxiliary Tools

### 6.1 KiCad (PCB Design)

For designing custom FPGA breakout boards:

```bash
# Linux
sudo apt-get install kicad

# macOS
brew install --cask kicad
```

### 6.2 Visual Studio Code Extensions

Recommended extensions for HDL development:

```bash
# Install VS Code
# Then install extensions:
# - "Verilog-HDL/SystemVerilog" by mshr-h
# - "WaveTrace" for waveform viewing
# - "TerosHDL" for linting and docs
```

---

## Verification Checklist

Run these commands to verify your installation:

```bash
# HDL Tools
verilator --version          # Should show v5.0+
yosys -V                     # Should show Yosys version
nextpnr-ecp5 --version       # Should show nextpnr

# Python environment
python3 -c "import cocotb"   # No error

# ASIC tools
cd OpenLane && make test     # Should pass

# Software stack
llvm-config --version        # Should show LLVM version
spirv-as --version           # Should show SPIRV version
```

---

## Quick Start Test

Let's run the flux GPU top-level testbench:

```bash
cd flux/rtl/test

# Create Makefile for cocotb
cat > Makefile << 'EOF'
SIM = verilator
TOPLEVEL_LANG = verilog
VERILOG_SOURCES = ../src/gpu_top.sv
TOPLEVEL = gpu_top
MODULE = test_gpu_top

include $(shell cocotb-config --makefiles)/Makefile.sim
EOF

# Run test
make
```

**Expected output**: `test_gpu_top.py::test_gpu_top_sanity PASSED`

---

## Troubleshooting

### Issue: Verilator compile errors

**Solution**: Ensure C++14 or later:
```bash
g++ --version  # Should be 7.0+
```

### Issue: Cocotb import error

**Solution**:
```bash
pip3 install --upgrade cocotb
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

### Issue: OpenLane Docker permission denied

**Solution**:
```bash
sudo usermod -aG docker $USER
# Log out and back in
```

---

## Next Steps

1. **Explore the RTL**: Navigate to `flux/rtl/src/` and examine `gpu_top.sv`
2. **Run simulations**: Modify `test_gpu_top.py` to test new features
3. **Synthesize for FPGA**: See `flux/hw-tools/fpga/README.md` for board-specific instructions
4. **Read theory docs**: Return to [GPU Fundamentals](../theory/gpu_fundamentals.md)

---

## Resource Links

- [Verilator Manual](https://verilator.org/guide/latest/)
- [Cocotb Documentation](https://docs.cocotb.org/)
- [Yosys Manual](https://yosyshq.readthedocs.io/)
- [OpenLane Documentation](https://openlane.readthedocs.io/)
- [SkyWater PDK](https://skywater-pdk.readthedocs.io/)
- [Vulkan Tutorial](https://vulkan-tutorial.com/)

**Community**:
- Reddit: r/FPGA, r/chipdesign
- Discord: ZipCPU FPGA server, OpenROAD Discord
- Forum: 1BitSquared (FPGA), Google Open Source Silicon (ASIC)
