# Conditional Example
# if (x > 0) y = x + 1; else y = x - 1;

# Input: R1 = x
# Output: R2 = y

main:
    # Load x
    LI R1, 5           # x = 5 (test value)
    
    # Compare with 0
    BEQ R1, R0, else_branch
    
    # if-branch: y = x + 1
    ADDI R2, R1, 1
    JAL end_if
    
else_branch:
    # else-branch: y = x - 1
    ADDI R2, R1, -1
    
end_if:
    # Store result
    HALT
