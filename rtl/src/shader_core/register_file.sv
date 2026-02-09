`default_nettype none

// Multi-threaded Register File for flux GPU
// Supports 32 threads × 32 registers × 128-bit (4×FP32) per register

module register_file #(
    parameter NUM_THREADS = 32,
    parameter NUM_REGS    = 32,
    parameter DATA_WIDTH  = 128  // 4× FP32
)(
    input  wire clk,
    input  wire rst_n,
    
    // Read port 1
    input  wire [$clog2(NUM_THREADS)-1:0] rd_thread_id_a,
    input  wire [4:0]                     rd_addr_a,
    output wire [DATA_WIDTH-1:0]          rd_data_a,
    
    // Read port 2
    input  wire [$clog2(NUM_THREADS)-1:0] rd_thread_id_b,
    input  wire [4:0]                     rd_addr_b,
    output wire [DATA_WIDTH-1:0]          rd_data_b,
    
    // Write port
    input  wire [$clog2(NUM_THREADS)-1:0] wr_thread_id,
    input  wire [4:0]                     wr_addr,
    input  wire [DATA_WIDTH-1:0]          wr_data,
    input  wire                           wr_enable
);

    // Register storage: 32 threads × 32 registers × 128 bits
    // Total: 131,072 bits = 16 KB
    reg [DATA_WIDTH-1:0] registers [0:NUM_THREADS*NUM_REGS-1];
    
    // Compute flat addresses
    wire [$clog2(NUM_THREADS*NUM_REGS)-1:0] addr_a = {rd_thread_id_a, rd_addr_a};
    wire [$clog2(NUM_THREADS*NUM_REGS)-1:0] addr_b = {rd_thread_id_b, rd_addr_b};
    wire [$clog2(NUM_THREADS*NUM_REGS)-1:0] addr_w = {wr_thread_id, wr_addr};
    
    // Read ports (combinational)
    // R0 is hardwired to 0
    assign rd_data_a = (rd_addr_a == 5'h0) ? {DATA_WIDTH{1'b0}} : registers[addr_a];
    assign rd_data_b = (rd_addr_b == 5'h0) ? {DATA_WIDTH{1'b0}} : registers[addr_b];
    
    // Write port (synchronous)
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            // Reset all registers to 0
            integer i;
            for (i = 0; i < NUM_THREADS*NUM_REGS; i = i + 1) begin
                registers[i] <= {DATA_WIDTH{1'b0}};
            end
        end else if (wr_enable && wr_addr != 5'h0) begin
            // Write (R0 is hardwired, ignore writes)
            registers[addr_w] <= wr_data;
        end
    end

endmodule
