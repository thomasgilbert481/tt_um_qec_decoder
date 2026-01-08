import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

@cocotb.test()
async def test_gl_basic(dut):
    """Basic gate-level test - syndrome decoding"""
    dut._log.info("Starting gate-level basic test")
    
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())
    
    # Reset
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)
    
    # Test a few key syndromes
    test_cases = [
        (0b000, 0b00),  # No error
        (0b001, 0b11),  # Error on Q2
        (0b010, 0b10),  # Error on Q1
        (0b011, 0b01),  # Error on Q0
    ]
    
    for syndrome, expected_corr in test_cases:
        dut.ui_in.value = syndrome
        await ClockCycles(dut.clk, 2)  # Extra cycle for gate delays
        correction = int(dut.uo_out.value) & 0b11
        dut._log.info(f"Syndrome {syndrome:03b} -> Correction {correction:02b} (expected {expected_corr:02b})")
        assert correction == expected_corr, f"GL test failed: syndrome {syndrome:03b}"
    
    dut._log.info("? Gate-level basic test passed")

@cocotb.test()
async def test_gl_reset(dut):
    """Gate-level reset test"""
    dut._log.info("Starting gate-level reset test")
    
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())
    
    # Reset
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)
    
    # Inject some errors
    for _ in range(5):
        dut.ui_in.value = 0b001
        await ClockCycles(dut.clk, 2)
    
    # Reset again
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)
    
    # Check outputs are cleared
    dut.ui_in.value = 0b000
    await ClockCycles(dut.clk, 2)
    error_count = (int(dut.uo_out.value) >> 4) & 0xF
    assert error_count == 0, "Counter should be zero after reset"
    
    dut._log.info("? Gate-level reset test passed")

@cocotb.test()
async def test_gl_error_flags(dut):
    """Gate-level error flag test"""
    dut._log.info("Starting gate-level error flag test")
    
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())
    
    # Reset
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)
    
    # No error case
    dut.ui_in.value = 0b000
    await ClockCycles(dut.clk, 2)
    error_flag = (int(dut.uo_out.value) >> 2) & 1
    assert error_flag == 0, "Error flag should be 0 for no error"
    
    # Error cases
    dut.ui_in.value = 0b001
    await ClockCycles(dut.clk, 2)
    error_flag = (int(dut.uo_out.value) >> 2) & 1
    assert error_flag == 1, "Error flag should be 1 for error"
    
    dut._log.info("? Gate-level error flag test passed")
