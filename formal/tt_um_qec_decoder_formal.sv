module tt_um_qec_decoder_formal (
    input  wire [7:0] ui_in,
    output wire [7:0] uo_out,
    input  wire [7:0] uio_in,
    output wire [7:0] uio_out,
    output wire [7:0] uio_oe,
    input  wire       ena,
    input  wire       clk,
    input  wire       rst_n
);

    tt_um_qec_decoder dut (
        .ui_in(ui_in),
        .uo_out(uo_out),
        .uio_in(uio_in),
        .uio_out(uio_out),
        .uio_oe(uio_oe),
        .ena(ena),
        .clk(clk),
        .rst_n(rst_n)
    );

    wire [2:0] syndrome       = ui_in[2:0];
    wire       test_mode      = ui_in[4];
    wire [1:0] correction     = uo_out[1:0];
    wire       error_detected = uo_out[2];
    wire       uncorrectable  = uo_out[3];

    // ========================================================================
    // ASSERTIONS: Syndrome Decoding Correctness (Core QEC Functionality)
    // ========================================================================
    
    always @(posedge clk) begin
        if (rst_n && !test_mode) begin
            case(syndrome)
                // No error: 000 -> no correction, no flags
                3'b000: assert(correction == 2'b00 && !error_detected && !uncorrectable);
                
                // Correctable single-bit errors
                3'b001: assert(correction == 2'b11 && error_detected && !uncorrectable);
                3'b010: assert(correction == 2'b10 && error_detected && !uncorrectable);
                3'b011: assert(correction == 2'b01 && error_detected && !uncorrectable);
                3'b100: assert(correction == 2'b01 && error_detected && !uncorrectable);
                3'b101: assert(correction == 2'b10 && error_detected && !uncorrectable);
                3'b110: assert(correction == 2'b11 && error_detected && !uncorrectable);
                
                // Uncorrectable error: 111 -> no correction, both flags set
                3'b111: assert(correction == 2'b00 && error_detected && uncorrectable);
            endcase
        end
    end

    // ========================================================================
    // ASSERTIONS: Error Flag Logic
    // ========================================================================
    
    always @(posedge clk) begin
        if (rst_n && !test_mode) begin
            // Uncorrectable flag only set for syndrome 111
            if (syndrome == 3'b111)
                assert(uncorrectable);
            else
                assert(!uncorrectable);
            
            // Error detected flag set for all non-zero syndromes
            if (syndrome == 3'b000)
                assert(!error_detected);
            else
                assert(error_detected);
        end
    end

    // ========================================================================
    // ASSERTIONS: Interface Constraints
    // ========================================================================
    
    // Bidirectional pins unused (as per design spec)
    always @(posedge clk) begin
        assert(uio_out == 8'b0 && uio_oe == 8'b0);
    end

    // ========================================================================
    // COVER PROPERTIES: Reachability Checks
    // ========================================================================
    
    always @(posedge clk) begin
        if (rst_n && !test_mode) begin
            // Verify all syndrome cases are reachable
            cover(syndrome == 3'b000);
            cover(syndrome == 3'b001);
            cover(syndrome == 3'b010);
            cover(syndrome == 3'b011);
            cover(syndrome == 3'b100);
            cover(syndrome == 3'b101);
            cover(syndrome == 3'b110);
            cover(syndrome == 3'b111);
            
            // Verify flag states are reachable
            cover(error_detected);
            cover(!error_detected);
            cover(uncorrectable);
            cover(error_detected && !uncorrectable);
        end
    end

endmodule
