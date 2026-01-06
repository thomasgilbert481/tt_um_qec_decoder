module tt_um_qec_decoder (
    input  wire [7:0] ui_in,
    output wire [7:0] uo_out,
    input  wire [7:0] uio_in,
    output wire [7:0] uio_out,
    output wire [7:0] uio_oe,
    input  wire       ena,
    input  wire       clk,
    input  wire       rst_n
);

    wire [2:0] syndrome       = ui_in[2:0];
    wire       mode_select    = ui_in[3];
    wire       test_mode      = ui_in[4];
    wire       clear_stats    = ui_in[5];
    
    reg [1:0]  correction;
    reg        error_detected;
    reg        uncorrectable;
    reg [3:0]  error_count;
    reg [2:0]  test_syndrome;
    
    wire lfsr_feedback = test_syndrome[2] ^ test_syndrome[1];
    
    always @(posedge clk) begin
        if (!rst_n)
            test_syndrome <= 3'b001;
        else if (test_mode)
            test_syndrome <= {test_syndrome[1:0], lfsr_feedback};
    end
    
    wire [2:0] active_syndrome = test_mode ? test_syndrome : syndrome;
    
    always @(*) begin
        correction = 2'b00;
        error_detected = 1'b0;
        uncorrectable = 1'b0;
        
        case(active_syndrome)
            3'b000: begin
                correction = 2'b00;
                error_detected = 1'b0;
            end
            
            3'b001: begin
                correction = 2'b11;
                error_detected = 1'b1;
            end
            
            3'b010: begin
                correction = 2'b10;
                error_detected = 1'b1;
            end
            
            3'b011: begin
                correction = 2'b01;
                error_detected = 1'b1;
            end
            
            3'b100: begin
                correction = 2'b01;
                error_detected = 1'b1;
            end
            
            3'b101: begin
                correction = 2'b10;
                error_detected = 1'b1;
            end
            
            3'b110: begin
                correction = 2'b11;
                error_detected = 1'b1;
            end
            
            3'b111: begin
                correction = 2'b00;
                error_detected = 1'b1;
                uncorrectable = 1'b1;
            end
        endcase
    end
    
    always @(posedge clk) begin
        if (!rst_n || clear_stats)
            error_count <= 4'b0000;
        else if (error_detected && !uncorrectable)
            error_count <= error_count + 1'b1;
    end
    
    assign uo_out[1:0] = correction;
    assign uo_out[2]   = error_detected;
    assign uo_out[3]   = uncorrectable;
    assign uo_out[7:4] = error_count;
    
    assign uio_out = 8'b0;
    assign uio_oe  = 8'b0;
    
    wire _unused = &{ena, uio_in, mode_select, 1'b0};

endmodule
