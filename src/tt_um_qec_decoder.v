// Enhanced 3-Qubit QEC Syndrome Decoder with Advanced Statistics
// Author: Thomas Gilbert
// Enhanced Version: January 2026
// 
// NEW FEATURES:
// - 16-bit total error counter (was 4-bit)
// - 16-bit maximal-length LFSR (was 3-bit)
// - Per-qubit error classification counters
// - 8-entry syndrome history buffer
// - Dual-mode parallel decoding capability
// - Extended statistics via bidirectional pins

module tt_um_qec_decoder (
    input  wire [7:0] ui_in,      // Dedicated inputs
    output wire [7:0] uo_out,     // Dedicated outputs
    input  wire [7:0] uio_in,     // Bidirectional inputs
    output wire [7:0] uio_out,    // Bidirectional outputs
    output wire [7:0] uio_oe,     // Bidirectional enable (1=output)
    input  wire       ena,        // Enable
    input  wire       clk,        // Clock
    input  wire       rst_n       // Active-low reset
);

    // =========================================================================
    // INPUT DECODING
    // =========================================================================
    wire [2:0] syndrome       = ui_in[2:0];  // 3-bit syndrome input
    wire       mode_select    = ui_in[3];    // 0=bit-flip, 1=phase-flip
    wire       test_mode      = ui_in[4];    // Enable LFSR test generation
    wire       clear_stats    = ui_in[5];    // Clear all statistics counters
    wire [1:0] stats_select   = uio_in[1:0]; // Select which stats to display
    
    // =========================================================================
    // OUTPUT SIGNALS (Main)
    // =========================================================================
    reg [1:0]  correction;           // Correction decision
    reg        error_detected;       // Error flag
    reg        uncorrectable;        // Uncorrectable error flag
    reg [15:0] error_count;          // 16-bit total error counter
    
    // =========================================================================
    // ENHANCED STATISTICS
    // =========================================================================
    reg [7:0]  q0_error_count;       // Qubit 0 error counter
    reg [7:0]  q1_error_count;       // Qubit 1 error counter
    reg [7:0]  q2_error_count;       // Qubit 2 error counter
    reg [7:0]  uncorrectable_count;  // Uncorrectable error counter
    
    // =========================================================================
    // SYNDROME HISTORY BUFFER (8 entries)
    // =========================================================================
    reg [2:0]  syndrome_history [0:7];
    reg [2:0]  history_ptr;
    
    // =========================================================================
    // 16-BIT LFSR TEST GENERATOR (Maximal-length: period = 65535)
    // =========================================================================
    reg [15:0] test_lfsr;
    wire       lfsr_feedback = test_lfsr[15] ^ test_lfsr[14] ^ 
                                test_lfsr[12] ^ test_lfsr[3];
    
    always @(posedge clk) begin
        if (!rst_n) begin
            test_lfsr <= 16'h0001;  // Non-zero seed
        end else if (test_mode) begin
            test_lfsr <= {test_lfsr[14:0], lfsr_feedback};
        end
    end
    
    wire [2:0] test_syndrome = test_lfsr[2:0];
    
    // =========================================================================
    // ACTIVE SYNDROME SELECTION
    // =========================================================================
    wire [2:0] active_syndrome = test_mode ? test_syndrome : syndrome;
    
    // =========================================================================
    // DUAL-MODE PARALLEL SYNDROME DECODER
    // =========================================================================
    // Decode for bit-flip mode
    reg [1:0] bitflip_correction;
    reg       bitflip_error;
    reg       bitflip_uncorrectable;
    
    always @(*) begin
        bitflip_correction = 2'b00;
        bitflip_error = 1'b0;
        bitflip_uncorrectable = 1'b0;
        
        case(active_syndrome)
            3'b000: begin
                bitflip_correction = 2'b00;
                bitflip_error = 1'b0;
            end
            
            3'b001: begin  // Qubit 2 error
                bitflip_correction = 2'b11;
                bitflip_error = 1'b1;
            end
            
            3'b010: begin  // Qubit 1 error
                bitflip_correction = 2'b10;
                bitflip_error = 1'b1;
            end
            
            3'b011: begin  // Qubit 0 error
                bitflip_correction = 2'b01;
                bitflip_error = 1'b1;
            end
            
            3'b100: begin  // Qubit 0 error (alternate)
                bitflip_correction = 2'b01;
                bitflip_error = 1'b1;
            end
            
            3'b101: begin  // Qubit 1 error (alternate)
                bitflip_correction = 2'b10;
                bitflip_error = 1'b1;
            end
            
            3'b110: begin  // Qubit 2 error (alternate)
                bitflip_correction = 2'b11;
                bitflip_error = 1'b1;
            end
            
            3'b111: begin  // Uncorrectable (multiple errors)
                bitflip_correction = 2'b00;
                bitflip_error = 1'b1;
                bitflip_uncorrectable = 1'b1;
            end
        endcase
    end
    
    // Decode for phase-flip mode (same logic, different interpretation)
    reg [1:0] phaseflip_correction;
    reg       phaseflip_error;
    reg       phaseflip_uncorrectable;
    
    always @(*) begin
        phaseflip_correction = bitflip_correction;    // Same mapping
        phaseflip_error = bitflip_error;
        phaseflip_uncorrectable = bitflip_uncorrectable;
    end
    
    // Mode multiplexer
    always @(*) begin
        if (mode_select) begin
            correction = phaseflip_correction;
            error_detected = phaseflip_error;
            uncorrectable = phaseflip_uncorrectable;
        end else begin
            correction = bitflip_correction;
            error_detected = bitflip_error;
            uncorrectable = bitflip_uncorrectable;
        end
    end
    
    // =========================================================================
    // STATISTICS COUNTERS (Sequential Logic)
    // =========================================================================
    always @(posedge clk) begin
        if (!rst_n || clear_stats) begin
            // Reset all counters
            error_count <= 16'h0000;
            q0_error_count <= 8'h00;
            q1_error_count <= 8'h00;
            q2_error_count <= 8'h00;
            uncorrectable_count <= 8'h00;
        end else if (error_detected) begin
            // Increment total error count (with saturation)
            if (error_count != 16'hFFFF) begin
                error_count <= error_count + 1'b1;
            end
            
            // Increment per-qubit counters (with saturation)
            if (uncorrectable) begin
                if (uncorrectable_count != 8'hFF) begin
                    uncorrectable_count <= uncorrectable_count + 1'b1;
                end
            end else begin
                // Classify by which qubit had the error
                case(correction)
                    2'b01: begin  // Qubit 0 error
                        if (q0_error_count != 8'hFF) begin
                            q0_error_count <= q0_error_count + 1'b1;
                        end
                    end
                    
                    2'b10: begin  // Qubit 1 error
                        if (q1_error_count != 8'hFF) begin
                            q1_error_count <= q1_error_count + 1'b1;
                        end
                    end
                    
                    2'b11: begin  // Qubit 2 error
                        if (q2_error_count != 8'hFF) begin
                            q2_error_count <= q2_error_count + 1'b1;
                        end
                    end
                endcase
            end
        end
    end
    
    // =========================================================================
    // SYNDROME HISTORY BUFFER
    // =========================================================================
    always @(posedge clk) begin
        if (!rst_n) begin
            history_ptr <= 3'h0;
            syndrome_history[0] <= 3'h0;
            syndrome_history[1] <= 3'h0;
            syndrome_history[2] <= 3'h0;
            syndrome_history[3] <= 3'h0;
            syndrome_history[4] <= 3'h0;
            syndrome_history[5] <= 3'h0;
            syndrome_history[6] <= 3'h0;
            syndrome_history[7] <= 3'h0;
        end else begin
            // Store current syndrome in circular buffer
            syndrome_history[history_ptr] <= active_syndrome;
            history_ptr <= history_ptr + 1'b1;  // Auto-wraps at 8
        end
    end
    
    // =========================================================================
    // OUTPUT ASSIGNMENTS
    // =========================================================================
    
    // Main outputs (uo_out)
    assign uo_out[1:0] = correction;
    assign uo_out[2]   = error_detected;
    assign uo_out[3]   = uncorrectable;
    assign uo_out[7:4] = error_count[3:0];  // Low nibble of 16-bit counter
    
    // Extended statistics output (uio_out) - selected by stats_select
    reg [7:0] extended_stats;
    
    always @(*) begin
        case(stats_select)
            2'b00: extended_stats = error_count[15:8];      // High byte of total count
            2'b01: extended_stats = q0_error_count;         // Qubit 0 errors
            2'b10: extended_stats = q1_error_count;         // Qubit 1 errors
            2'b11: extended_stats = {q2_error_count[7:5],   // Qubit 2 errors (upper 3 bits)
                                     syndrome_history[history_ptr], // Current history entry
                                     uncorrectable_count[1:0]};     // Uncorrectable count (lower 2 bits)
        endcase
    end
    
    assign uio_out = extended_stats;
    assign uio_oe  = 8'hFF;  // All bidirectional pins configured as outputs
    
    // Suppress unused signal warnings
    wire _unused = &{ena, uio_in[7:2], 1'b0};

endmodule
