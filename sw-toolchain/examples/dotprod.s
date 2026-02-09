# Dot Product Example
# Computes dot = A[0]*B[0] + A[1]*B[1] + A[2]*B[2] + A[3]*B[3]

# Inputs:
# R10 = base address of A (4 floats)
# R11 = base address of B (4 floats)
# R12 = output address for result

main:
    # Load vectors
    LOAD R1, 0(R10)     # R1 = [A0, A1, A2, A3]
    LOAD R2, 0(R11)     # R2 = [B0, B1, B2, B3]
    
    # Element-wise multiply
    MUL R3, R1, R2      # R3 = [A0*B0, A1*B1, A2*B2, A3*B3]
    
    # Horizontal sum (manual reduction for now)
    # Extract and accumulate (simplified - assumes we can access individual lanes)
    # In real implementation, would need shuffle/reduce instructions
    
    # For now, store partial products
    STORE R3, 0(R12)
    
    HALT
