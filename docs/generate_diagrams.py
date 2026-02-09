#!/usr/bin/env python3
"""
Generate architecture diagrams for flux GPU documentation
Uses matplotlib to create professional diagrams
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch, Circle
import numpy as np

def create_logic_gates_to_alu():
    """Diagram 1: From Logic Gates to ALU"""
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle('From Logic Gates to GPU ALU', fontsize=20, fontweight='bold')
    
    # Panel 1: Basic Logic Gates
    ax = axes[0]
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 12)
    ax.axis('off')
    ax.set_title('1. Basic Logic Gates', fontsize=14, fontweight='bold')
    
    # AND gate
    and_gate = mpatches.FancyBboxPatch((1, 8), 3, 1.5, boxstyle="round,pad=0.1",
                                        edgecolor='black', facecolor='lightblue', linewidth=2)
    ax.add_patch(and_gate)
    ax.text(2.5, 8.75, 'AND', ha='center', va='center', fontsize=12, fontweight='bold')
    
    # OR gate
    or_gate = mpatches.FancyBboxPatch((1, 5.5), 3, 1.5, boxstyle="round,pad=0.1",
                                       edgecolor='black', facecolor='lightgreen', linewidth=2)
    ax.add_patch(or_gate)
    ax.text(2.5, 6.25, 'OR', ha='center', va='center', fontsize=12, fontweight='bold')
    
    # NOT gate
    not_gate = mpatches.FancyBboxPatch((1, 3), 3, 1.5, boxstyle="round,pad=0.1",
                                        edgecolor='black', facecolor='lightyellow', linewidth=2)
    ax.add_patch(not_gate)
    ax.text(2.5, 3.75, 'NOT', ha='center', va='center', fontsize=12, fontweight='bold')
    
    ax.text(5, 6, '→', fontsize=30, ha='center')
    
    # Panel 2: Building Blocks
    ax = axes[1]
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 12)
    ax.axis('off')
    ax.set_title('2. Building Blocks', fontsize=14, fontweight='bold')
    
    # Full Adder
    adder = mpatches.FancyBboxPatch((1, 7.5), 4, 3, boxstyle="round,pad=0.1",
                                     edgecolor='black', facecolor='lightcoral', linewidth=2)
    ax.add_patch(adder)
    ax.text(3, 9, 'Full Adder', ha='center', va='center', fontsize=12, fontweight='bold')
    ax.text(3, 8.2, '(AND, OR, XOR)', ha='center', va='center', fontsize=9)
    
    # Multiplexer
    mux = mpatches.FancyBboxPatch((1, 3.5), 4, 3, boxstyle="round,pad=0.1",
                                   edgecolor='black', facecolor='lightsteelblue', linewidth=2)
    ax.add_patch(mux)
    ax.text(3, 5, 'Multiplexer', ha='center', va='center', fontsize=12, fontweight='bold')
    ax.text(3, 4.2, '(AND, OR, NOT)', ha='center', va='center', fontsize=9)
    
    ax.text(6, 6, '→', fontsize=30, ha='center')
    
    # Panel 3: ALU
    ax = axes[2]
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 12)
    ax.axis('off')
    ax.set_title('3. Complete ALU', fontsize=14, fontweight='bold')
    
    # ALU box
    alu = mpatches.FancyBboxPatch((1, 3), 7, 6, boxstyle="round,pad=0.2",
                                   edgecolor='darkblue', facecolor='lavender', linewidth=3)
    ax.add_patch(alu)
    ax.text(4.5, 7.5, 'Arithmetic Logic Unit', ha='center', va='center',
            fontsize=14, fontweight='bold', color='darkblue')
    
    # Components
    ax.text(2.5, 6, '• Adders', ha='left', fontsize=10)
    ax.text(2.5, 5.3, '• Multipliers', ha='left', fontsize=10)
    ax.text(2.5, 4.6, '• Comparators', ha='left', fontsize=10)
    
    ax.text(5.5, 6, '• Shifters', ha='left', fontsize=10)
    ax.text(5.5, 5.3, '• Logic Ops', ha='left', fontsize=10)
    ax.text(5.5, 4.6, '• Muxes', ha='left', fontsize=10)
    
    # Inputs/Outputs
    ax.arrow(0.5, 8, 0.4, -2, head_width=0.2, head_length=0.2, fc='green', ec='green')
    ax.text(0.5, 8.5, 'Inputs', ha='center', fontsize=9, color='green', fontweight='bold')
    
    ax.arrow(8.5, 6, 0.8, 0, head_width=0.2, head_length=0.2, fc='red', ec='red')
    ax.text(9.5, 6.3, 'Result', ha='center', fontsize=9, color='red', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('logic_gates_to_alu.png', dpi=300, bbox_inches='tight')
    print("✓ Generated: logic_gates_to_alu.png")
    plt.close()

def create_gpu_architecture():
    """Diagram 2: Complete GPU Architecture"""
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 14)
    ax.axis('off')
    ax.set_title('flux GPU Complete Architecture', fontsize=22, fontweight='bold', pad=20)
    
    # Shader Core (center)
    shader = FancyBboxPatch((7, 5), 6, 5, boxstyle="round,pad=0.15",
                             edgecolor='darkblue', facecolor='lightblue', linewidth=3)
    ax.add_patch(shader)
    ax.text(10, 8.5, 'Shader Core', ha='center', fontsize=14, fontweight='bold')
    ax.text(10, 7.8, '(Compute Pipeline)', ha='center', fontsize=10)
    
    # Components inside shader
    ax.text(8, 7, '• SIMD ALU (4-wide)', ha='left', fontsize=9)
    ax.text(8, 6.5, '• Register File (32×32)', ha='left', fontsize=9)
    ax.text(8, 6, '• Instruction Decoder', ha='left', fontsize=9)
    
    # Graphics Pipeline (right)
    graphics = FancyBboxPatch((14.5, 5), 4.5, 5, boxstyle="round,pad=0.15",
                               edgecolor='darkgreen', facecolor='lightgreen', linewidth=3)
    ax.add_patch(graphics)
    ax.text(16.75, 8.5, 'Graphics', ha='center', fontsize=14, fontweight='bold')
    ax.text(16.75, 7.8, 'Pipeline', ha='center', fontsize=10)
    
    ax.text(15, 7, '• Rasterizer', ha='left', fontsize=9)
    ax.text(15, 6.5, '• Framebuffer', ha='left', fontsize=9)
    ax.text(15, 6, '• VGA Out', ha='left', fontsize=9)
    
    # Memory System (left)
    memory = FancyBboxPatch((1, 5), 4.5, 5, boxstyle="round,pad=0.15",
                             edgecolor='darkorange', facecolor='peachpuff', linewidth=3)
    ax.add_patch(memory)
    ax.text(3.25, 8.5, 'Memory', ha='center', fontsize=14, fontweight='bold')
    ax.text(3.25, 7.8, 'System', ha='center', fontsize=10)
    
    ax.text(1.5, 7, '• 64 KB RAM', ha='left', fontsize=9)
    ax.text(1.5, 6.5, '• Framebuffer', ha='left', fontsize=9)
    ax.text(1.5, 6, '• Memory Bus', ha='left', fontsize=9)
    
    # Control Unit (top)
    control = FancyBboxPatch((7, 11), 6, 2, boxstyle="round,pad=0.15",
                              edgecolor='purple', facecolor='thistle', linewidth=3)
    ax.add_patch(control)
    ax.text(10, 12.3, 'Control Unit', ha='center', fontsize=14, fontweight='bold')
    ax.text(10, 11.7, 'Instruction Fetch & Decode', ha='center', fontsize=9)
    
    # Memory Bus (bottom)
    bus = Rectangle((3, 3.5), 14, 0.8, edgecolor='gray', facecolor='lightgray', linewidth=2)
    ax.add_patch(bus)
    ax.text(10, 3.9, 'Memory Bus (128-bit)', ha='center', fontsize=10, fontweight='bold')
    
    # Connections
    # Control to Shader
    ax.arrow(10, 10.9, 0, -0.8, head_width=0.3, head_length=0.2, fc='purple', ec='purple', linewidth=2)
    
    # Shader to Memory
    ax.arrow(6.8, 7.5, -1.2, 0, head_width=0.3, head_length=0.2, fc='blue', ec='blue', linewidth=2)
    ax.arrow(5.7, 7, 1.2, 0, head_width=0.3, head_length=0.2, fc='blue', ec='blue', linewidth=2)
    
    # Shader to Graphics
    ax.arrow(13.2, 7.5, 1.2, 0, head_width=0.3, head_length=0.2, fc='green', ec='green', linewidth=2)
    
    # To bus
    ax.arrow(3.25, 4.9, 0, -0.9, head_width=0.2, head_length=0.15, fc='gray', ec='gray')
    ax.arrow(10, 4.9, 0, -0.9, head_width=0.2, head_length=0.15, fc='gray', ec='gray')
    ax.arrow(16.75, 4.9, 0, -0.9, head_width=0.2, head_length=0.15, fc='gray', ec='gray')
    
    # Output
    vga = FancyBboxPatch((17, 1), 2.5, 1.5, boxstyle="round,pad=0.1",
                          edgecolor='red', facecolor='lightcoral', linewidth=2)
    ax.add_patch(vga)
    ax.text(18.25, 1.75, 'VGA\nDisplay', ha='center', fontsize=10, fontweight='bold')
    
    ax.arrow(16.75, 4.3, 1.2, -2.5, head_width=0.3, head_length=0.2, fc='red', ec='red', linewidth=2)
    
    # Legend
    ax.text(1, 1.5, 'Color Legend:', fontsize=11, fontweight='bold')
    ax.text(1, 1, '■ Blue: Compute  ■ Green: Graphics  ■ Orange: Memory  ■ Purple: Control',
            fontsize=9, color='black')
    
    plt.tight_layout()
    plt.savefig('gpu_architecture.png', dpi=300, bbox_inches='tight')
    print("✓ Generated: gpu_architecture.png")
    plt.close()

def create_simd_visualization():
    """Diagram 3: SIMD 4-Wide Parallelism"""
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')
    ax.set_title('SIMD: Single Instruction, Multiple Data (4-Wide)', fontsize=18, fontweight='bold')
    
    # Instruction box
    instr = FancyBboxPatch((6, 8), 4, 1, boxstyle="round,pad=0.1",
                            edgecolor='darkblue', facecolor='lightblue', linewidth=2)
    ax.add_patch(instr)
    ax.text(8, 8.5, 'ADD R3, R1, R2', ha='center', fontsize=12, fontweight='bold')
    
    # Arrow down
    ax.arrow(8, 7.8, 0, -0.5, head_width=0.3, head_length=0.15, fc='black', ec='black', linewidth=2)
    
    # Four ALU lanes
    colors = ['#FFB6C1', '#98FB98', '#87CEEB', '#FFD700']
    lane_names = ['Lane 0', 'Lane 1', 'Lane 2', 'Lane 3']
    
    for i, (color, name) in enumerate(zip(colors, lane_names)):
        x = 2 + i * 3.2
        
        # Lane box
        lane = FancyBboxPatch((x, 3.5), 2.5, 3, boxstyle="round,pad=0.1",
                               edgecolor='darkblue', facecolor=color, linewidth=2)
        ax.add_patch(lane)
        ax.text(x + 1.25, 6, name, ha='center', fontsize=11, fontweight='bold')
        
        # Inputs
        ax.text(x + 0.5, 5.3, f'R1[{i}]', ha='center', fontsize=9)
        ax.text(x + 2, 5.3, f'R2[{i}]', ha='center', fontsize=9)
        
        # ALU symbol
        ax.text(x + 1.25, 4.7, '+', ha='center', fontsize=16, fontweight='bold')
        
        # Output
        ax.text(x + 1.25, 3.9, f'R3[{i}]', ha='center', fontsize=9, fontweight='bold')
        
        # Example values
        val1 = 1.0 + i
        val2 = 0.5 + i * 0.5
        result = val1 + val2
        
        ax.text(x + 0.5, 4.9, f'{val1}', ha='center', fontsize=8, color='blue')
        ax.text(x + 2, 4.9, f'{val2}', ha='center', fontsize=8, color='blue')
        ax.text(x + 1.25, 4.2, f'{result}', ha='center', fontsize=8, color='red', fontweight='bold')
    
    # Result combination
    result_box = FancyBboxPatch((5, 1), 6, 1.5, boxstyle="round,pad=0.1",
                                 edgecolor='darkgreen', facecolor='lightgreen', linewidth=2)
    ax.add_patch(result_box)
    ax.text(8, 1.75, '128-bit Result: [1.5, 3.0, 5.5, 8.0]', ha='center', fontsize=11, fontweight='bold')
    
    # Arrows to result
    for i in range(4):
        x = 3.25 + i * 3.2
        ax.arrow(x, 3.3, 0.5 + i * 0.5, -1.5, head_width=0.2, head_length=0.15,
                 fc='green', ec='green', linewidth=1.5, alpha=0.7)
    
    # Performance note
    ax.text(8, 0.3, '✓ 4× Faster: 4 additions in 1 clock cycle!', ha='center',
            fontsize=12, fontweight='bold', color='darkgreen',
            bbox=dict(boxstyle='round', facecolor='lightyellow', edgecolor='darkgreen', linewidth=2))
    
    plt.tight_layout()
    plt.savefig('simd_visualization.png', dpi=300, bbox_inches='tight')
    print("✓ Generated: simd_visualization.png")
    plt.close()

def create_chip_fabrication():
    """Diagram 4: From Silicon to Working Chip"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    fig.suptitle('Semiconductor Fabrication: Silicon → Working Chip', fontsize=18, fontweight='bold')
    
    # Panel 1: Silicon wafer
    ax = axes[0, 0]
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    ax.set_title('1. Silicon Wafer', fontsize=14, fontweight='bold')
    
    circle = Circle((5, 5), 4, edgecolor='darkgray', facecolor='silver', linewidth=3)
    ax.add_patch(circle)
    ax.text(5, 5, 'Pure Silicon\n(99.9999%)', ha='center', va='center',
            fontsize=12, fontweight='bold')
    ax.text(5, 1, '300mm diameter', ha='center', fontsize=10)
    
    # Panel 2: Transistor formation
    ax = axes[0, 1]
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    ax.set_title('2. Transistor Formation', fontsize=14, fontweight='bold')
    
    # Substrate
    substrate = Rectangle((1, 1), 8, 1, edgecolor='black', facecolor='gray', linewidth=2)
    ax.add_patch(substrate)
    ax.text(5, 1.5, 'Silicon Substrate', ha='center', fontsize=9, color='white', fontweight='bold')
    
    # NMOS transistor
    nmos_gate = Rectangle((3, 2), 1, 2, edgecolor='black', facecolor='gold', linewidth=2)
    ax.add_patch(nmos_gate)
    ax.text(3.5, 3, 'Gate', ha='center', fontsize=8, rotation=90)
    
    nmos_s = Rectangle((2, 2), 0.8, 0.8, edgecolor='black', facecolor='lightblue', linewidth=1)
    nmos_d = Rectangle((4.2, 2), 0.8, 0.8, edgecolor='black', facecolor='lightblue', linewidth=1)
    ax.add_patch(nmos_s)
    ax.add_patch(nmos_d)
    ax.text(2.4, 2.4, 'S', ha='center', fontsize=9, fontweight='bold')
    ax.text(4.6, 2.4, 'D', ha='center', fontsize=9, fontweight='bold')
    
    ax.text(3.5, 4.5, 'NMOS Transistor', ha='center', fontsize=10, fontweight='bold')
    
    # PMOS transistor
    pmos_gate = Rectangle((6, 2), 1, 2, edgecolor='black', facecolor='gold', linewidth=2)
    ax.add_patch(pmos_gate)
    
    pmos_s = Rectangle((5, 2), 0.8, 0.8, edgecolor='black', facecolor='lightcoral', linewidth=1)
    pmos_d = Rectangle((7.2, 2), 0.8, 0.8, edgecolor='black', facecolor='lightcoral', linewidth=1)
    ax.add_patch(pmos_s)
    ax.add_patch(pmos_d)
    
    ax.text(6.5, 4.5, 'PMOS Transistor', ha='center', fontsize=10, fontweight='bold')
    
    ax.text(5, 5.5, 'Billions of transistors\nformed on wafer', ha='center', fontsize=9)
    
    # Panel 3: Metal layers
    ax = axes[1, 0]
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    ax.set_title('3. Metal Interconnect', fontsize=14, fontweight='bold')
    
    # Layer stack
    layers = [
        ('Metal 5', 8, 'gold'),
        ('Insulator', 7, 'lightblue'),
        ('Metal 4', 6, 'gold'),
        ('Insulator', 5, 'lightblue'),
        ('Metal 3', 4, 'gold'),
        ('Insulator', 3, 'lightblue'),
        ('Metal 2', 2, 'gold'),
    ]
    
    for name, y, color in layers:
        layer = Rectangle((2, y), 6, 0.6, edgecolor='black', facecolor=color, linewidth=1)
        ax.add_patch(layer)
        ax.text(1.2, y + 0.3, name, ha='right', fontsize=9)
    
    ax.text(5, 0.5, 'Up to 10+ metal layers\nfor routing signals', ha='center', fontsize=9)
    
    # Panel 4: Final chip
    ax = axes[1, 1]
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    ax.set_title('4. Packaged Chip', fontsize=14, fontweight='bold')
    
    # Package
    package = FancyBboxPatch((2, 3), 6, 4, boxstyle="round,pad=0.2",
                              edgecolor='black', facecolor='darkgray', linewidth=3)
    ax.add_patch(package)
    
    # Die
    die = Rectangle((3.5, 4.5), 3, 2, edgecolor='gold', facecolor='silver', linewidth=2)
    ax.add_patch(die)
    ax.text(5, 5.5, 'Silicon Die\n(flux GPU)', ha='center', fontsize=10, fontweight='bold')
    
    # Pins
    for i in range(8):
        pin = Rectangle((2.2 + i * 0.7, 2.5), 0.3, 0.5, edgecolor='black',
                        facecolor='gold', linewidth=1)
        ax.add_patch(pin)
    
    ax.text(5, 1.5, 'Bond wires connect\ndie to package pins', ha='center', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('chip_fabrication.png', dpi=300, bbox_inches='tight')
    print("✓ Generated: chip_fabrication.png")
    plt.close()

def main():
    """Generate all diagrams"""
    print("="*60)
    print("flux GPU - Generating Architecture Diagrams")
    print("="*60)
    print("\nCreating diagrams...")
    
    create_logic_gates_to_alu()
    create_gpu_architecture()
    create_simd_visualization()
    create_chip_fabrication()
    
    print("\n" + "="*60)
    print("✓ All diagrams generated successfully!")
    print("="*60)
    print("\nGenerated files:")
    print("  1. logic_gates_to_alu.png - Building blocks progression")
    print("  2. gpu_architecture.png - Complete system overview")
    print("  3. simd_visualization.png - Parallelism explanation")
    print("  4. chip_fabrication.png - Silicon to chip process")
    print("\nMove these to docs/images/ for repository use.")

if __name__ == "__main__":
    main()
