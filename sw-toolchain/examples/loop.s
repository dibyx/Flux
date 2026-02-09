# Loop Example
# for (i = 0; i < 4; i++) C[i] = A[i] + B[i]
# Processes 4 iterations

# Setup
    LI R10, 0          # i = 0
    LI R11, 4          # loop limit
    LI R20, 0x1000     # Base address A
    LI R21, 0x2000     # Base address B
    LI R22, 0x3000     # Base address C

loop:
    # Load A[i]
    LOAD R1, 0(R20)
    
    # Load B[i]
    LOAD R2, 0(R21)
    
    # Add
    ADD R3, R1, R2
    
    # Store C[i]
    STORE R3, 0(R22)
    
    # Increment pointers (4 elements * 4 bytes = 16)
    ADDI R20, R20, 16
    ADDI R21, R21, 16
    ADDI R22, R22, 16
    
    # Increment counter
    ADDI R10, R10, 4
    
    # Check if done
    BNE R10, R11, loop
    
    HALT
