`default_nettype none

// Shader Core Top Module for flux GPU
// Integrates: Instruction Decoder + ALU + Register File

module shader_core (
    input  wire clk,
    input  wire rst_n,
    input  wire enable,
    
    // Instruction memory interface
    input  wire [31:0] instruction,
    
    // Current thread ID (0-31)
    input  wire [4:0]  thread_id,
    
    // Memory interface (simplified)
    output wire [31:0] mem_addr,
    output wire [127:0] mem_wr_data,
    output wire        mem_wr_enable,
    input  wire [127:0] mem_rd_data,
    output wire        mem_rd_enable,
    
    // Status
    output wire        halted
);

    // Decoded instruction fields
    wire [6:0]  opcode;
    wire [4:0]  rd, rs1, rs2;
    wire [2:0]  funct3;
    wire [6:0]  funct7;
    wire [31:0] immediate;
    
    // Control signals
    wire alu_enable;
    wire [3:0] alu_op;
    wire mem_read, mem_write, reg_write, use_immediate, is_branch;
    
    // Instruction decoder
    instruction_decoder decoder (
        .instruction(instruction),
        .opcode(opcode),
        .rd(rd), .rs1(rs1), .rs2(rs2),
        .funct3(funct3), .funct7(funct7),
        .immediate(immediate),
        .alu_enable(alu_enable),
        .alu_op(alu_op),
        .mem_read(mem_read),
        .mem_write(mem_write),
        .reg_write(reg_write),
        .use_immediate(use_immediate),
        .is_branch(is_branch),
        .is_halt(halted)
    );
    
    // Register file
    wire [127:0] rf_rd_data_a, rf_rd_data_b;
    wire [127:0] rf_wr_data;
    wire rf_wr_enable;
    
    register_file #(
        .NUM_THREADS(32),
        .NUM_REGS(32),
        .DATA_WIDTH(128)
    ) regfile (
        .clk(clk),
        .rst_n(rst_n),
        .rd_thread_id_a(thread_id),
        .rd_addr_a(rs1),
        .rd_data_a(rf_rd_data_a),
        .rd_thread_id_b(thread_id),
        .rd_addr_b(rs2),
        .rd_data_b(rf_rd_data_b),
        .wr_thread_id(thread_id),
        .wr_addr(rd),
        .wr_data(rf_wr_data),
        .wr_enable(rf_wr_enable)
    );
    
    // ALU
    wire [127:0] alu_operand_a, alu_operand_b, alu_result;
    wire alu_valid;
    
    // Operand selection (immediate vs register)
    assign alu_operand_a = rf_rd_data_a;
    assign alu_operand_b = use_immediate ? {4{immediate}} : rf_rd_data_b;  // Broadcast imm to all lanes
    
    simd_alu alu (
        .clk(clk),
        .rst_n(rst_n),
        .enable(alu_enable && enable),
        .alu_op(alu_op),
        .operand_a(alu_operand_a),
        .operand_b(alu_operand_b),
        .result(alu_result),
        .valid(alu_valid)
    );
    
    // Register write-back
    assign rf_wr_data = mem_read ? mem_rd_data : alu_result;
    assign rf_wr_enable = (reg_write && alu_valid) || mem_read;
    
    // Memory interface
    assign mem_addr = alu_result[31:0];  // Address from ALU (rs1 + offset)
    assign mem_wr_data = rf_rd_data_b;   // Data from rs2
    assign mem_wr_enable = mem_write && enable;
    assign mem_rd_enable = mem_read && enable;

endmodule
