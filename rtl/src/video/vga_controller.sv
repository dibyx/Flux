// VGA Controller
// Top-level VGA output controller with framebuffer interface
// Supports 640x480 @ 60Hz with RGB888 color

module vga_controller (
    input  wire        clk,        // 25 MHz pixel clock
    input  wire        rst_n,
    
    // Framebuffer read interface
    output wire [18:0] fb_rd_addr, // 640*480 = 307,200 addresses
    input  wire [23:0] fb_rd_data, // RGB888 pixel data
    
    // VGA output signals
    output wire        hsync,
    output wire        vsync,
    output reg  [7:0]  vga_r,
    output reg  [7:0]  vga_g,
    output reg  [7:0]  vga_b
);

// Internal signals from timing generator
wire [9:0] pixel_x;
wire [9:0] pixel_y;
wire       display_en;
wire       frame_start;

// Instantiate timing generator
vga_timing_generator timing_gen (
    .clk         (clk),
    .rst_n       (rst_n),
    .pixel_x     (pixel_x),
    .pixel_y     (pixel_y),
    .hsync       (hsync),
    .vsync       (vsync),
    .display_en  (display_en),
    .frame_start (frame_start)
);

// Calculate framebuffer address
// Address = y * 640 + x
// Using shift and add: y * 640 = y * 512 + y * 128 = (y << 9) + (y << 7)
wire [18:0] addr_y_512 = {pixel_y, 9'b0};        // y * 512
wire [18:0] addr_y_128 = {2'b0, pixel_y, 7'b0};  // y * 128
wire [18:0] addr_calc  = addr_y_512 + addr_y_128 + {9'b0, pixel_x};

// Register the address for timing
reg [18:0] fb_addr_reg;
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        fb_addr_reg <= 19'd0;
    end else if (display_en) begin
        fb_addr_reg <= addr_calc;
    end else begin
        fb_addr_reg <= 19'd0;
    end
end

assign fb_rd_addr = fb_addr_reg;

// Output pixel data with blanking
// Register pixel data for better timing
reg [23:0] pixel_data_reg;
reg        display_en_reg;

always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        pixel_data_reg <= 24'd0;
        display_en_reg <= 1'b0;
    end else begin
        pixel_data_reg <= fb_rd_data;
        display_en_reg <= display_en;
    end
end

// Output RGB with blanking
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        vga_r <= 8'h00;
        vga_g <= 8'h00;
        vga_b <= 8'h00;
    end else if (display_en_reg) begin
        // Output pixel data from framebuffer
        vga_r <= pixel_data_reg[23:16];  // Red channel
        vga_g <= pixel_data_reg[15:8];   // Green channel
        vga_b <= pixel_data_reg[7:0];    // Blue channel
    end else begin
        // Blanking period - output black
        vga_r <= 8'h00;
        vga_g <= 8'h00;
        vga_b <= 8'h00;
    end
end

endmodule
