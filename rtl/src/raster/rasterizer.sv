// Triangle Rasterizer
// Converts triangle vertices to pixels using edge function algorithm
// Fills triangles with solid color

module rasterizer (
    input  wire        clk,
    input  wire        rst_n,
    
    // Triangle vertices (screen coordinates)
    input  wire [9:0]  v0_x,
    input  wire [9:0]  v0_y,
    input  wire [9:0]  v1_x,
    input  wire [9:0]  v1_y,
    input  wire [9:0]  v2_x,
    input  wire [9:0]  v2_y,
    
    // Triangle color
    input  wire [23:0] color,
    
    // Control
    input  wire        start,      // Start rasterization
    output reg         busy,       // Rasterizer is working
    output reg         done,       // Rasterization complete
    
    // Framebuffer write interface
    output reg  [18:0] fb_addr,
    output reg  [23:0] fb_data,
    output reg         fb_write
);

// State machine
localparam IDLE       = 3'd0;
localparam CALC_BBOX  = 3'd1;
localparam RASTER     = 3'd2;
localparam WRITE_PIX  = 3'd3;
localparam DONE_STATE = 3'd4;

reg [2:0] state;

// Bounding box
reg [9:0] min_x, max_x;
reg [9:0] min_y, max_y;
reg [9:0] curr_x, curr_y;

// Edge function results
wire signed [21:0] e0, e1, e2;
wire inside;

// Convert vertices to signed for edge function
wire signed [10:0] sv0_x = {1'b0, v0_x};
wire signed [10:0] sv0_y = {1'b0, v0_y};
wire signed [10:0] sv1_x = {1'b0, v1_x};
wire signed [10:0] sv1_y = {1'b0, v1_y};
wire signed [10:0] sv2_x = {1'b0, v2_x};
wire signed [10:0] sv2_y = {1'b0, v2_y};
wire signed [10:0] scurr_x = {1'b0, curr_x};
wire signed [10:0] scurr_y = {1'b0, curr_y};

// Edge functions for three edges
edge_function edge0 (
    .v0_x(sv0_x), .v0_y(sv0_y),
    .v1_x(sv1_x), .v1_y(sv1_y),
    .px(scurr_x), .py(scurr_y),
    .result(e0)
);

edge_function edge1 (
    .v0_x(sv1_x), .v0_y(sv1_y),
    .v1_x(sv2_x), .v1_y(sv2_y),
    .px(scurr_x), .py(scurr_y),
    .result(e1)
);

edge_function edge2 (
    .v0_x(sv2_x), .v0_y(sv2_y),
    .v1_x(sv0_x), .v1_y(sv0_y),
    .px(scurr_x), .py(scurr_y),
    .result(e2)
);

// Point is inside if all edge functions have same sign
assign inside = ((e0 >= 0) && (e1 >= 0) && (e2 >= 0)) ||
                ((e0 <= 0) && (e1 <= 0) && (e2 <= 0));

// Helper functions for min/max
function [9:0] min3;
    input [9:0] a, b, c;
    begin
        min3 = (a < b) ? ((a < c) ? a : c) : ((b < c) ? b : c);
    end
endfunction

function [9:0] max3;
    input [9:0] a, b, c;
    begin
        max3 = (a > b) ? ((a > c) ? a : c) : ((b > c) ? b : c);
    end
endfunction

// State machine
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        state    <= IDLE;
        busy     <= 1'b0;
        done     <= 1'b0;
        fb_write <= 1'b0;
        curr_x   <= 10'd0;
        curr_y   <= 10'd0;
        min_x    <= 10'd0;
        max_x    <= 10'd0;
        min_y    <= 10'd0;
        max_y    <= 10'd0;
        fb_addr  <= 19'd0;
        fb_data  <= 24'd0;
    end else begin
        case (state)
            IDLE: begin
                done <= 1'b0;
                fb_write <= 1'b0;
                if (start) begin
                    busy <= 1'b1;
                    state <= CALC_BBOX;
                end
            end
            
            CALC_BBOX: begin
                // Calculate bounding box
                min_x <= min3(v0_x, v1_x, v2_x);
                max_x <= max3(v0_x, v1_x, v2_x);
                min_y <= min3(v0_y, v1_y, v2_y);
                max_y <= max3(v0_y, v1_y, v2_y);
                
                // Clamp to screen bounds (640x480)
                if (min_x > 10'd639) min_x <= 10'd639;
                if (max_x > 10'd639) max_x <= 10'd639;
                if (min_y > 10'd479) min_y <= 10'd479;
                if (max_y > 10'd479) max_y <= 10'd479;
                
                // Start at top-left of bounding box
                curr_x <= min3(v0_x, v1_x, v2_x);
                curr_y <= min3(v0_y, v1_y, v2_y);
                
                state <= RASTER;
            end
            
            RASTER: begin
                // Check if current pixel is inside triangle
                if (inside) begin
                    // Prepare to write pixel
                    fb_addr <= curr_y * 10'd640 + curr_x;
                    fb_data <= color;
                    state <= WRITE_PIX;
                end else begin
                    // Move to next pixel without writing
                    if (curr_x >= max_x) begin
                        curr_x <= min_x;
                        if (curr_y >= max_y) begin
                            // Done rasterizing
                            state <= DONE_STATE;
                        end else begin
                            curr_y <= curr_y + 10'd1;
                        end
                    end else begin
                        curr_x <= curr_x + 10'd1;
                    end
                end
            end
            
            WRITE_PIX: begin
                // Write pixel to framebuffer
                fb_write <= 1'b1;
                
                // Move to next pixel
                if (curr_x >= max_x) begin
                    curr_x <= min_x;
                    if (curr_y >= max_y) begin
                        state <= DONE_STATE;
                    end else begin
                        curr_y <= curr_y + 10'd1;
                        state <= RASTER;
                    end
                end else begin
                    curr_x <= curr_x + 10'd1;
                    state <= RASTER;
                end
            end
            
            DONE_STATE: begin
                fb_write <= 1'b0;
                busy <= 1'b0;
                done <= 1'b1;
                state <= IDLE;
            end
            
            default: state <= IDLE;
        endcase
    end
end

endmodule
