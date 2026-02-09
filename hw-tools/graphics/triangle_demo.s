# Triangle Demo - Assembly Program
# Draws a red triangle on the screen

# Triangle vertices
# V0: (100, 200)
# V1: (500, 200)  
# V2: (300, 400)
# Color: Red (0xFF0000)

.data
# Vertex coordinates
v0_x: .word 100
v0_y: .word 200
v1_x: .word 500  
v1_y: .word 200
v2_x: .word 300
v2_y: .word 400
color: .word 0xFF0000

.text
main:
    # Load vertex 0
    LI R10, 100      # V0 X
    LI R11, 200      # V0 Y
    
    # Load vertex 1
    LI R12, 500      # V1 X
    LI R13, 200      # V1 Y
    
    # Load vertex 2
    LI R14, 300      # V

2 X
    LI R15, 400      # V2 Y
    
    # Load color (red)
    LI R16, 0xFF0000
    
    # Write to rasterizer registers (memory-mapped)
    # Base address for graphics: 0x5000
    STORE R10, 0x5000    # V0 X
    STORE R11, 0x5004    # V0 Y
    STORE R12, 0x5008    # V1 X
    STORE R13, 0x500C    # V1 Y
    STORE R14, 0x5010    # V2 X
    STORE R15, 0x5014    # V2 Y
    STORE R16, 0x5018    # Color
    
    # Trigger rasterization (write 1 to start register)
    LI R20, 1
    STORE R20, 0x5020    # Start rasterization
    
    # Wait for completion (poll busy flag)
wait_loop:
    LOAD R21, 0x5024     # Read busy flag
    BNE R21, R0, wait_loop  # Loop while busy
    
    # Triangle drawn!
    HALT
