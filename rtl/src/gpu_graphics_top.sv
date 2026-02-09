// GPU Graphics Top Module
// Integrates rasterizer, framebuffer, and VGA controller
// Provides simple interface for drawing triangles

module gpu_graphics_top (
    input  wire        clk_sys,    // System clock (50 MHz)
    input  wire        clk_vga,    // VGA pixel clock (25 MHz)
    input  wire        rst_n,
    
    // Triangle drawing interface
    input  wire [9:0]  tri_v0_x,
    input  wire [9:0]  tri_v0_y,
    input  wire [9:0]  tri_v1_x,
    input  wire [9:0]  tri_v1_y,
    input  wire [9:0]  tri_v2_x,
    input  wire [9:0]  tri_v2_y,
    input  wire [23:0] tri_color,
    input  wire        tri_draw,    // Start drawing triangle
    output wire        tri_busy,    // Rasterizer is working
    output wire        tri_done,    // Triangle complete
    
    // Clear screen interface
    input  wire        clear_screen,
    input  wire [23:0] clear_color,
    output wire        clear_busy,
    output wire        clear_done,
    
    // VGA output
    output wire        hsync,
    output wire        vsync,
    output wire [7:0]  vga_r,
    output wire [7:0]  vga_g,
    output wire [7:0]  vga_b
);

// Framebuffer interface signals
wire [18:0] fb_wr_addr;
wire [23:0] fb_wr_data;
wire        fb_wr_enable;
wire [18:0] fb_rd_addr;
wire [23:0] fb_rd_data;

// Rasterizer instantiation
rasterizer rast (
    .clk        (clk_sys),
    .rst_n      (rst_n),
    .v0_x       (tri_v0_x),
    .v0_y       (tri_v0_y),
    .v1_x       (tri_v1_x),
    .v1_y       (tri_v1_y),
    .v2_x       (tri_v2_x),
    .v2_y       (tri_v2_y),
    .color      (tri_color),
    .start      (tri_draw),
    .busy       (tri_busy),
    .done       (tri_done),
    .fb_addr    (fb_wr_addr),
    .fb_data    (fb_wr_data),
    .fb_write   (fb_wr_enable)
);

// Framebuffer instantiation
framebuffer fb (
    .clk        (clk_sys),  // Use system clock for write
    .rst_n      (rst_n),
    .wr_addr    (fb_wr_addr),
    .wr_data    (fb_wr_data),
    .wr_enable  (fb_wr_enable),
    .rd_addr    (fb_rd_addr),
    .rd_data    (fb_rd_data)
);

// VGA controller instantiation
vga_controller vga (
    .clk        (clk_vga),      // 25 MHz VGA clock
    .rst_n      (rst_n),
    .fb_rd_addr (fb_rd_addr),
    .fb_rd_data (fb_rd_data),
    .hsync      (hsync),
    .vsync      (vsync),
    .vga_r      (vga_r),
    .vga_g      (vga_g),
    .vga_b      (vga_b)
);

// Clear screen logic (simple state machine)
reg [2:0] clear_state;
reg [18:0] clear_addr;

localparam CLR_IDLE  = 3'd0;
localparam CLR_RUN   = 3'd1;
localparam CLR_DONE  = 3'd2;

assign clear_busy = (clear_state == CLR_RUN);
assign clear_done = (clear_state == CLR_DONE);

always @(posedge clk_sys or negedge rst_n) begin
    if (!rst_n) begin
        clear_state <= CLR_IDLE;
        clear_addr <= 19'd0;
    end else begin
        case (clear_state)
            CLR_IDLE: begin
                if (clear_screen) begin
                    clear_state <= CLR_RUN;
                    clear_addr <= 19'd0;
                end
            end
            
            CLR_RUN: begin
                clear_addr <= clear_addr + 19'd1;
                if (clear_addr == 19'd307199) begin  // 640*480-1
                    clear_state <= CLR_DONE;
                end
            end
            
            CLR_DONE: begin
                clear_state <= CLR_IDLE;
            end
            
            default: clear_state <= CLR_IDLE;
        endcase
    end
end

endmodule
