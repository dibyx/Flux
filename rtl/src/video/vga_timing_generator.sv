// VGA Timing Generator
// Generates horizontal and vertical sync signals for 640x480 @ 60Hz
// Pixel clock: 25.175 MHz (standard VGA)

module vga_timing_generator (
    input  wire       clk,        // 25 MHz pixel clock
    input  wire       rst_n,
    output reg [9:0]  pixel_x,    // Current pixel X coordinate
    output reg [9:0]  pixel_y,    // Current pixel Y coordinate
    output reg        hsync,      // Horizontal sync
    output reg        vsync,      // Vertical sync
    output reg        display_en, // High when in visible area
    output reg        frame_start // Pulse at start of new frame
);

// VGA 640x480 @ 60Hz timing parameters
// Horizontal timing (pixels)
localparam H_DISPLAY    = 640;  // Visible area
localparam H_FRONT      = 16;   // Front porch
localparam H_SYNC       = 96;   // Sync pulse
localparam H_BACK       = 48;   // Back porch
localparam H_TOTAL      = H_DISPLAY + H_FRONT + H_SYNC + H_BACK; // 800

// Vertical timing (lines)
localparam V_DISPLAY    = 480;  // Visible area
localparam V_FRONT      = 10;   // Front porch
localparam V_SYNC       = 2;    // Sync pulse
localparam V_BACK       = 33;   // Back porch
localparam V_TOTAL      = V_DISPLAY + V_FRONT + V_SYNC + V_BACK; // 525

// Sync polarities (negative for VGA)
localparam H_SYNC_POL   = 1'b0; // Active low
localparam V_SYNC_POL   = 1'b0; // Active low

// Horizontal counter
reg [9:0] h_count;
reg [9:0] v_count;

// Horizontal timing
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        h_count <= 10'd0;
    end else begin
        if (h_count == H_TOTAL - 1) begin
            h_count <= 10'd0;
        end else begin
            h_count <= h_count + 10'd1;
        end
    end
end

// Vertical timing
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        v_count <= 10'd0;
    end else begin
        if (h_count == H_TOTAL - 1) begin
            if (v_count == V_TOTAL - 1) begin
                v_count <= 10'd0;
            end else begin
                v_count <= v_count + 10'd1;
            end
        end
    end
end

// Generate sync signals
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        hsync <= ~H_SYNC_POL;
        vsync <= ~V_SYNC_POL;
    end else begin
        // Horizontal sync
        if (h_count >= (H_DISPLAY + H_FRONT) && 
            h_count < (H_DISPLAY + H_FRONT + H_SYNC)) begin
            hsync <= H_SYNC_POL;
        end else begin
            hsync <= ~H_SYNC_POL;
        end
        
        // Vertical sync
        if (v_count >= (V_DISPLAY + V_FRONT) && 
            v_count < (V_DISPLAY + V_FRONT + V_SYNC)) begin
            vsync <= V_SYNC_POL;
        end else begin
            vsync <= ~V_SYNC_POL;
        end
    end
end

// Display enable (visible area)
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        display_en <= 1'b0;
    end else begin
        display_en <= (h_count < H_DISPLAY) && (v_count < V_DISPLAY);
    end
end

// Pixel coordinates (only valid when display_en is high)
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        pixel_x <= 10'd0;
        pixel_y <= 10'd0;
    end else begin
        if (h_count < H_DISPLAY) begin
            pixel_x <= h_count;
        end else begin
            pixel_x <= 10'd0;
        end
        
        if (v_count < V_DISPLAY) begin
            pixel_y <= v_count;
        end else begin
            pixel_y <= 10'd0;
        end
    end
end

// Frame start pulse (one clock cycle at start of frame)
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        frame_start <= 1'b0;
    end else begin
        frame_start <= (h_count == 10'd0) && (v_count == 10'd0);
    end
end

endmodule
