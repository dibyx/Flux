`default_nettype none

module gpu_top (
    input  wire        clk,
    input  wire        rst_n,

    // Host Interface (AXI-Lite Slave Stub)
    input  wire [31:0] host_awaddr,
    input  wire        host_awvalid,
    output wire        host_awready,
    input  wire [31:0] host_wdata,
    input  wire        host_wvalid,
    output wire        host_wready,
    output wire [1:0]  host_bresp,
    output wire        host_bvalid,
    input  wire        host_bready,

    // Video Output (VGA/HDMI Stub)
    output wire [7:0]  video_r,
    output wire [7:0]  video_g,
    output wire [7:0]  video_b,
    output wire        video_hsync,
    output wire        video_vsync,
    output wire        video_de
);

    // -------------------------------------------------------------------------
    // Registers & Control
    // -------------------------------------------------------------------------
    logic [31:0] scratchpad_reg;

    // Simple Host Write Handling (Stub)
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            scratchpad_reg <= 32'h0;
        end else begin
            if (host_awvalid && host_wvalid) begin
                scratchpad_reg <= host_wdata;
            end
        end
    end

    assign host_awready = 1'b1;
    assign host_wready  = 1'b1;
    assign host_bresp   = 2'b00; // OKAY
    assign host_bvalid  = 1'b1; // Always valid for stub

    // -------------------------------------------------------------------------
    // Video Pattern Generator (Stub)
    // -------------------------------------------------------------------------
    logic [10:0] h_count;
    logic [10:0] v_count;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            h_count <= 0;
            v_count <= 0;
        end else begin
            // Trivial counter logic
            if (h_count == 1023) begin
                h_count <= 0;
                if (v_count == 767) v_count <= 0;
                else v_count <= v_count + 1;
            end else begin
                h_count <= h_count + 1;
            end
        end
    end

    assign video_r = h_count[7:0];
    assign video_g = v_count[7:0];
    assign video_b = scratchpad_reg[7:0]; // Controlled by host
    assign video_hsync = (h_count < 96) ? 1'b0 : 1'b1;
    assign video_vsync = (v_count < 2)  ? 1'b0 : 1'b1;
    assign video_de    = 1'b1;

endmodule
