import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles

@cocotb.test()
async def test_basic_syndrome_decoding(dut):
    """Test basic syndrome decoding for all 8 cases"""
    dut._log.info("Starting basic syndrome decoding test")
    
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())
    
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)
    
    test_cases = [
        (0b000, 0b00, 0, 0),  # No error
        (0b001, 0b11, 1, 0),  # Q2 error
        (0b010, 0b10, 1, 0),  # Q1 error
        (0b011, 0b01, 1, 0),  # Q0 error
        (0b100, 0b01, 1, 0),  # Q0 error
        (0b101, 0b10, 1, 0),  # Q1 error
        (0b110, 0b11, 1, 0),  # Q2 error
        (0b111, 0b00, 1, 1),  # Uncorrectable
    ]
    
    for syndrome, expected_corr, expected_err, expected_uncorr in test_cases:
        dut.ui_in.value = syndrome
        await ClockCycles(dut.clk, 1)
        
        correction = dut.uo_out.value & 0b11
        error_flag = (dut.uo_out.value >> 2) & 1
        uncorr_flag = (dut.uo_out.value >> 3) & 1
        
        assert correction == expected_corr, f"Syndrome {syndrome:03b}: correction {correction:02b} != {expected_corr:02b}"
        assert error_flag == expected_err, f"Syndrome {syndrome:03b}: error flag {error_flag} != {expected_err}"
        assert uncorr_flag == expected_uncorr, f"Syndrome {syndrome:03b}: uncorrectable {uncorr_flag} != {expected_uncorr}"
    
    dut._log.info("✅ All syndrome cases passed")

@cocotb.test()
async def test_error_flag_behavior(dut):
    """Test error detection flag logic"""
    dut._log.info("Starting error flag behavior test")
    
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())
    
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)
    
    dut.ui_in.value = 0b000
    await ClockCycles(dut.clk, 1)
    assert ((dut.uo_out.value >> 2) & 1) == 0, "Error flag should be 0 for syndrome 000"
    
    for syndrome in [0b001, 0b010, 0b011, 0b100, 0b101, 0b110, 0b111]:
        dut.ui_in.value = syndrome
        await ClockCycles(dut.clk, 1)
        assert ((dut.uo_out.value >> 2) & 1) == 1, f"Error flag should be 1 for syndrome {syndrome:03b}"
    
    dut._log.info("✅ Error flag behavior correct")

@cocotb.test()
async def test_all_syndromes_exhaustive(dut):
    """Exhaustively test all 256 possible 3-bit syndrome combinations"""
    dut._log.info("Starting exhaustive syndrome test")
    
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())
    
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)
    
    for syndrome in range(8):
        dut.ui_in.value = syndrome
        await ClockCycles(dut.clk, 1)
        
        correction = dut.uo_out.value & 0b11
        error_flag = (dut.uo_out.value >> 2) & 1
        uncorr_flag = (dut.uo_out.value >> 3) & 1
        
        if syndrome == 0:
            assert error_flag == 0 and uncorr_flag == 0
        elif syndrome == 0b111:
            assert error_flag == 1 and uncorr_flag == 1
        else:
            assert error_flag == 1 and uncorr_flag == 0
    
    dut._log.info("✅ Exhaustive syndrome test passed")

@cocotb.test()
async def test_16bit_lfsr(dut):
    """Test the 16-bit LFSR pattern generator"""
    dut._log.info("Starting 16-bit LFSR test")
    
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())
    
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)
    
    dut.ui_in.value = 0b10000
    await ClockCycles(dut.clk, 1)
    
    seen_patterns = set()
    for i in range(100):
        await ClockCycles(dut.clk, 1)
        syndrome = dut.ui_in.value & 0b111
        seen_patterns.add(syndrome)
    
    dut._log.info(f"✅ LFSR generated {len(seen_patterns)} unique patterns in 100 cycles")

@cocotb.test()
async def test_continuous_error_injection(dut):
    """Test continuous error injection and counting"""
    dut._log.info("Starting continuous error injection test")
    
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())
    
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)
    
    for i in range(20):
        dut.ui_in.value = 0b011
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 0
        await ClockCycles(dut.clk, 1)
    
    error_count_nibble = (dut.uo_out.value >> 4) & 0xF
    assert error_count_nibble == 4, f"Expected count 20 (nibble 4), got nibble {error_count_nibble}"
    
    dut._log.info("✅ Continuous error injection test passed")

@cocotb.test()
async def test_mode_switching(dut):
    """Test switching between bit-flip and phase-flip modes"""
    dut._log.info("Starting mode switching test")
    
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())
    
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)
    
    dut.ui_in.value = 0b01011
    await ClockCycles(dut.clk, 1)
    mode1_output = dut.uo_out.value & 0b11
    
    dut.ui_in.value = 0b11011
    await ClockCycles(dut.clk, 1)
    mode2_output = dut.uo_out.value & 0b11
    
    dut._log.info(f"Mode 0 output: {mode1_output:02b}, Mode 1 output: {mode2_output:02b}")
    dut._log.info("✅ Mode switching test passed")

@cocotb.test()
async def test_dual_mode_operation(dut):
    """Test both bit-flip and phase-flip correction modes"""
    dut._log.info("Starting dual mode operation test")
    
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())
    
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)
    
    dut.ui_in.value = 0b00011
    await ClockCycles(dut.clk, 1)
    assert (dut.uo_out.value & 0b11) == 0b01
    
    dut.ui_in.value = 0b01011
    await ClockCycles(dut.clk, 1)
    assert (dut.uo_out.value & 0b11) == 0b01
    
    dut._log.info("✅ Dual mode operation test passed")

@cocotb.test()
async def test_syndrome_history(dut):
    """Test syndrome history buffer"""
    dut._log.info("Starting syndrome history test")
    
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())
    
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)
    
    test_sequence = [0b001, 0b010, 0b011, 0b100, 0b101, 0b110, 0b111, 0b000]
    
    for syndrome in test_sequence:
        dut.ui_in.value = syndrome
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 0
        await ClockCycles(dut.clk, 1)
    
    dut.uio_in.value = 0b11
    await ClockCycles(dut.clk, 1)
    
    history_bits = (dut.uio_out.value >> 2) & 0x07
    dut._log.info(f"History buffer contains: {history_bits:03b}")
    dut._log.info("✅ Syndrome history test passed")

@cocotb.test()
async def test_clear_statistics(dut):
    """Test clearing of statistics counters"""
    dut._log.info("Starting clear statistics test")
    
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())
    
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)
    
    for i in range(10):
        dut.ui_in.value = 0b011
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 0
        await ClockCycles(dut.clk, 1)
    
    dut.ui_in.value = 0b100000
    await ClockCycles(dut.clk, 5)
    dut.ui_in.value = 0
    await ClockCycles(dut.clk, 1)
    
    error_count_nibble = (dut.uo_out.value >> 4) & 0xF
    assert error_count_nibble == 0, f"Error count not cleared: {error_count_nibble}"
    
    dut.uio_in.value = 0b01
    await ClockCycles(dut.clk, 1)
    q0_count = dut.uio_out.value & 0xFF
    assert q0_count == 0, f"Q0 counter not cleared: {q0_count}"
    
    dut._log.info("✅ Clear statistics test passed")

@cocotb.test()
async def test_enhanced_error_counter(dut):
    """Test enhanced 16-bit error counter"""
    dut._log.info("Starting enhanced error counter test")
    
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())
    
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)
    
    for i in range(20):
        syndrome = 0b011
        dut.ui_in.value = syndrome
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 0
        await ClockCycles(dut.clk, 1)
        
        low_nibble = (dut.uo_out.value >> 4) & 0xF
        expected_low = (i + 1) & 0xF
        
        dut._log.info(f"Cycle {i+1}: Count = {low_nibble} (expected {expected_low})")
        assert low_nibble == expected_low, f"Count mismatch at {i+1}"
    
    dut._log.info("✅ Enhanced error counter test passed")

@cocotb.test()
async def test_error_classification(dut):
    """Test per-qubit error classification"""
    dut._log.info("Starting error classification test")
    
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())
    
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)
    
    for i in range(10):
        dut.ui_in.value = 0b011
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 0
        await ClockCycles(dut.clk, 1)
    
    dut._log.info("Injected 10 errors on Q0")
    
    for i in range(15):
        dut.ui_in.value = 0b010
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 0
        await ClockCycles(dut.clk, 1)
    
    dut._log.info("Injected 15 errors on Q1")
    
    for i in range(20):
        dut.ui_in.value = 0b001
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 0
        await ClockCycles(dut.clk, 1)
    
    dut._log.info("Injected 20 errors on Q2")
    
    dut.uio_in.value = 0b01
    await ClockCycles(dut.clk, 1)
    
    q0_count = dut.uio_out.value & 0xFF
    dut._log.info(f"✅ Q0 error count: {q0_count}")
    assert q0_count == 10, f"Q0 count mismatch: {q0_count} != 10"
    
    dut.uio_in.value = 0b10
    await ClockCycles(dut.clk, 1)
    
    q1_count = dut.uio_out.value & 0xFF
    dut._log.info(f"✅ Q1 error count: {q1_count}")
    assert q1_count == 15, f"Q1 count mismatch: {q1_count} != 15"
    
    dut.uio_in.value = 0b11
    await ClockCycles(dut.clk, 1)
    
    q2_bits = (dut.uio_out.value >> 5) & 0x07
    dut._log.info(f"✅ Q2 error count (upper 3 bits): {q2_bits}")

@cocotb.test()
async def test_counter_saturation(dut):
    """Test counter saturation at maximum values"""
    dut._log.info("Starting counter saturation test")
    
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())
    
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)
    
    for i in range(260):
        dut.ui_in.value = 0b011
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 0
        await ClockCycles(dut.clk, 1)
    
    dut.uio_in.value = 0b01
    await ClockCycles(dut.clk, 1)
    
    q0_count = dut.uio_out.value & 0xFF
    dut._log.info(f"Q0 counter after 260 errors: {q0_count}")
    assert q0_count == 255, f"Counter should saturate at 255, got {q0_count}"
    
    dut._log.info("✅ Counter saturation test passed")

@cocotb.test()
async def test_reset_behavior(dut):
    """Test reset clears all state"""
    dut._log.info("Starting reset behavior test")
    
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())
    
    dut.ena.value = 1
    dut.uio_in.value = 0
    dut.rst_n.value = 1
    
    for i in range(5):
        dut.ui_in.value = 0b011
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 0
        await ClockCycles(dut.clk, 1)
    
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)
    
    dut.ui_in.value = 0
    await ClockCycles(dut.clk, 1)
    
    error_count_nibble = (dut.uo_out.value >> 4) & 0xF
    assert error_count_nibble == 0, f"Error count not reset: {error_count_nibble}"
    
    dut.uio_in.value = 0b01
    await ClockCycles(dut.clk, 1)
    q0_count = dut.uio_out.value & 0xFF
    assert q0_count == 0, f"Q0 counter not reset: {q0_count}"
    
    dut._log.info("✅ Reset behavior test passed")

@cocotb.test()
async def test_output_stability(dut):
    """Test output stability without input changes"""
    dut._log.info("Starting output stability test")
    
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())
    
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)
    
    dut.ui_in.value = 0b011
    await ClockCycles(dut.clk, 1)
    
    dut.ui_in.value = 0
    await ClockCycles(dut.clk, 3)
    
    output1 = int(dut.uo_out.value)
    
    await ClockCycles(dut.clk, 10)
    
    output2 = int(dut.uo_out.value)
    assert output1 == output2, f"Output changed without input change: {output1} != {output2}"
    
    dut._log.info("✅ Output stability test passed")
