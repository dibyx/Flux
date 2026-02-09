`default_nettype none

// Instruction Decoder for flux GPU
// Decodes 32-bit instructions into control signals

module instruction_decoder (
    input  wire [31:0] instruction,
    
    // Decoded fields
    output wire [6:0]  opcode,
    output wire [4:0]  rd,
    output wire [4:0]  rs1,
    output wire [4:0]  rs2,
    output wire [2:0]  funct3,
    output wire [6:0]  funct7,
    output wire [31:0] immediate,
    
    // Control signals
    output wire        alu_enable,
    output wire [3:0]  alu_op,
    output wire        mem_read,
    output wire        mem_write,
    output wire        reg_write,
    output wire        use_immediate,
    output wire        is_branch,
    output wire        is_halt
);

    // Extract instruction fields
    assign opcode = instruction[6:0];
    assign rd     = instruction[11:7];
    assign rs1    = instruction[19:15];
    assign rs2    = instruction[24:20];
    assign funct3 = instruction[14:12];
    assign funct7 = instruction[31:25];
    
    // Immediate generation (sign-extended)
    wire [31:0] imm_i = {{20{instruction[31]}}, instruction[31:20]};
    wire [31:0] imm_s = {{20{instruction[31]}}, instruction[31:25], instruction[11:7]};
    wire [31:0] imm_b = {{19{instruction[31]}}, instruction[31], instruction[7], instruction[30:25], instruction[11:8], 1'b0};
    
    reg [31:0] imm_mux;
    always @(*) begin
        case (opcode)
            7'b0010011: imm_mux = imm_i;  // I-type (ADDI)
            7'b0100011: imm_mux = imm_s;  // S-type (STORE)
            7'b1100011: imm_mux = imm_b;  // B-type (BEQ, BNE)
            default:    imm_mux = 32'h0;
        endcase
    end
    assign immediate = imm_mux;
    
    // ALU operation encoding
    localparam ALU_ADD  = 4'h0;
    localparam ALU_SUB  = 4'h1;
    localparam ALU_MUL  = 4'h2;
    localparam ALU_DIV  = 4'h3;
    localparam ALU_PASS = 4'hF;
    
    // Decode control signals
    reg alu_en_r, mem_rd_r, mem_wr_r, reg_wr_r, use_imm_r, branch_r, halt_r;
    reg [3:0] alu_op_r;
    
    always @(*) begin
        // Defaults
        alu_en_r  = 1'b0;
        mem_rd_r  = 1'b0;
        mem_wr_r  = 1'b0;
        reg_wr_r  = 1'b0;
        use_imm_r = 1'b0;
        branch_r  = 1'b0;
        halt_r    = 1'b0;
        alu_op_r  = ALU_PASS;
        
        case (opcode)
            7'b0110011: begin  // R-type (ADD, SUB, MUL)
                alu_en_r = 1'b1;
                reg_wr_r = 1'b1;
                case ({funct7, funct3})
                    {7'h00, 3'b000}: alu_op_r = ALU_ADD;  // ADD
                    {7'h20, 3'b000}: alu_op_r = ALU_SUB;  // SUB
                    {7'h01, 3'b000}: alu_op_r = ALU_MUL;  // MUL
                    {7'h01, 3'b100}: alu_op_r = ALU_DIV;  // DIV
                    default:         alu_op_r = ALU_PASS;
                endcase
            end
            
            7'b0010011: begin  // I-type (ADDI)
                alu_en_r  = 1'b1;
                reg_wr_r  = 1'b1;
                use_imm_r = 1'b1;
                alu_op_r  = ALU_ADD;
            end
            
            7'b0000011: begin  // LOAD
                mem_rd_r  = 1'b1;
                reg_wr_r  = 1'b1;
                use_imm_r = 1'b1;
                alu_op_r  = ALU_ADD;  // Address calculation
            end
            
            7'b0100011: begin  // STORE
                mem_wr_r  = 1'b1;
                use_imm_r = 1'b1;
                alu_op_r  = ALU_ADD;  // Address calculation
            end
            
            7'b1100011: begin  // Branch (BEQ, BNE)
                branch_r = 1'b1;
                alu_en_r = 1'b1;
                alu_op_r = ALU_SUB;  // Compare via subtraction
            end
            
            7'b1111111: begin  // HALT
                halt_r = 1'b1;
            end
            
            default: begin
                // NOP or unknown instruction
            end
        endcase
    end
    
    assign alu_enable    = alu_en_r;
    assign alu_op        = alu_op_r;
    assign mem_read      = mem_rd_r;
    assign mem_write     = mem_wr_r;
    assign reg_write     = reg_wr_r;
    assign use_immediate = use_imm_r;
    assign is_branch     = branch_r;
    assign is_halt       = halt_r;

endmodule
