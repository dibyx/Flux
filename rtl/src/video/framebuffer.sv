// Framebuffer Module
// Dual-port RAM for VGA display
// 640x480 pixels, RGB888 (24-bit color)
// Port A: Write (from rasterizer)
// Port B: Read (to VGA controller)

module framebuffer (
    input  wire        clk,
    input  wire        rst_n,
    
    // Port A: Write interface (rasterizer)
    input  wire [18:0] wr_addr,   // 19 bits for 307,200 pixels
    input  wire [23:0] wr_data,   // RGB888
    input  wire        wr_enable,
    
    // Port B: Read interface (VGA)
    input  wire [18:0] rd_addr,
    output reg  [23:0] rd_data
);

// Framebuffer memory
// 307,200 pixels × 24 bits = 7,372,800 bits = ~900 KB
// For FPGA: Use BRAM (will be inferred as block RAM)
reg [23:0] mem [0:307199];  // 640 * 480 = 307,200

// Write port (Port A)
always @(posedge clk) begin
    if (wr_enable) begin
        mem[wr_addr] <= wr_data;
    end
end

// Read port (Port B) - registered output for better timing
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        rd_data <= 24'd0;
    end else begin
        rd_data <= mem[rd_addr];
    end
end

// Optional: Clear screen functionality
// (Can be triggered by external clear signal if needed)
integer i;
initial begin
    for (i = 0; i < 307200; i = i + 1) begin
        mem[i] = 24'h000000;  // Initialize to black
    end
end

endmodule
