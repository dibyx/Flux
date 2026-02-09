# flux Repository Manifest

This file describes the intended structure of the `flux` project and the purpose of each directory.

.
├── meta/                   # Project governance, legal, and planning
│   ├── LEGAL.md            # License and export control info
│   └── roadmap.md          # Implementation timeline
├── rtl/                    # SystemVerilog Source Code
│   ├── src/                # Synthesizable RTL
│   │   └── gpu_top.sv      # Top-level module stub
│   └── test/               # Verification
│       └── test_gpu_top.py # Cocotb testbench
├── docs/                   # Documentation
│   └── notebooks/          # Interactive visualizations
│       ├── pipeline_trace.md       # Observable spec
│       └── memory_heatmap.ipynb    # Jupyter notebook
├── hw-tools/               # FPGA/ASIC build scripts (Placeholder)
├── sw-toolchain/           # Compiler & Runtime (Placeholder)
└── demos/                  # Example applications (Placeholder)
