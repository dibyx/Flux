# Vector Addition Example
# Computes C[i] = A[i] + B[i] for 4 elements

# Assume:
# R10 = base address of A
# R11 = base address of B
# R12 = base address of C

main:
    # Load A[0:3] into R1
    LOAD R1, 0(R10)
    
    # Load B[0:3] into R2
    LOAD R2, 0(R11)
    
    # Compute C = A + B (SIMD across all 4 lanes)
    ADD R3, R1, R2
    
    # Store result C[0:3]
    STORE R3, 0(R12)
    
    HALT
