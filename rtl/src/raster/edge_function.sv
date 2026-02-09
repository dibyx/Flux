// Edge Function Module
// Computes the edge function for triangle rasterization
// Edge function: f(x,y) = (y0 - y1)*x + (x1 - x0)*y + x0*y1 - x1*y0
// Used for inside-triangle testing

module edge_function (
    input  wire signed [10:0] v0_x,  // Vertex 0 X (signed for calculation)
    input  wire signed [10:0] v0_y,  // Vertex 0 Y
    input  wire signed [10:0] v1_x,  // Vertex 1 X
    input  wire signed [10:0] v1_y,  // Vertex 1 Y
    input  wire signed [10:0] px,    // Point X to test
    input  wire signed [10:0] py,    // Point Y to test
    output reg signed [21:0]  result // Edge function result
);

// Intermediate calculations
wire signed [10:0] dy = v0_y - v1_y;  // y0 - y1
wire signed [10:0] dx = v1_x - v0_x;  // x1 - x0

// Products (need wider bits)
wire signed [21:0] term1 = dy * px;           // (y0-y1) * x
wire signed [21:0] term2 = dx * py;           // (x1-x0) * y
wire signed [21:0] term3 = v0_x * v1_y;       // x0 * y1
wire signed [21:0] term4 = v1_x * v0_y;       // x1 * y0

// Compute edge function
always @(*) begin
    result = term1 + term2 + term3 - term4;
end

endmodule
