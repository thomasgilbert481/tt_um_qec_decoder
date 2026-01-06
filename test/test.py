import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

@cocotb.test()
async def test_qec_basic(dut):
    """Test basic syndrome decoding"""
    dut._log.info("Starting QEC decoder test")
    
    # Start clock
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())
    
    # Reset
    dut.rst_n.value = 0
    dut.ena.value = 1
    dut.ui_in.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)
    
    # Test Case 1: No error (syndrome = 000)
    dut._log.info("Test 1: No error syndrome")
    dut.ui_in.value = 0b000000
    await ClockCycles(dut.clk, 1)
    
    assert int(dut.uo_out.value) & 0b11 == 0b00, "Expected no correction"
    assert (dut.uo_out.value >> 2) & 1 == 0, "Expected no error flag"
    dut._log.info("✓ No error case passed")
    
    # Test Case 2: Error on qubit 0 (syndrome = 011)
    dut._log.info("Test 2: Error on qubit 0")
    dut.ui_in.value = 0b000011
    await ClockCycles(dut.clk, 1)
    
    correction = int(dut.uo_out.value) & 0b11
    error_flag = (dut.uo_out.value >> 2) & 1
    
    assert correction == 0b01, f"Expected correction=01, got {correction:02b}"
    assert error_flag == 1, "Expected error flag set"
    dut._log.info("✓ Qubit 0 error case passed")
    
    # Test Case 3: Error on qubit 1 (syndrome = 010)
    dut._log.info("Test 3: Error on qubit 1")
    dut.ui_in.value = 0b000010
    await ClockCycles(dut.clk, 1)
    
    correction = int(dut.uo_out.value) & 0b11
    assert correction == 0b10, f"Expected correction=10, got {correction:02b}"
    dut._log.info("✓ Qubit 1 error case passed")
    
    # Test Case 4: Error on qubit 2 (syndrome = 001)
    dut._log.info("Test 4: Error on qubit 2")
    dut.ui_in.value = 0b000001
    await ClockCycles(dut.clk, 1)
    
    correction = int(dut.uo_out.value) & 0b11
    assert correction == 0b11, f"Expected correction=11, got {correction:02b}"
    dut._log.info("✓ Qubit 2 error case passed")
    
    # Test Case 5: Uncorrectable error (syndrome = 111)
    dut._log.info("Test 5: Uncorrectable error")
    dut.ui_in.value = 0b000111
    await ClockCycles(dut.clk, 1)
    
    uncorrectable = (dut.uo_out.value >> 3) & 1
    assert uncorrectable == 1, "Expected uncorrectable flag"
    dut._log.info("✓ Uncorrectable error case passed")
    
    # Test Case 6: Error counter
    dut._log.info("Test 6: Error counter")
    
    # Clear stats
    dut.ui_in.value = 0b100000
    await ClockCycles(dut.clk, 2)
    dut.ui_in.value = 0b000000
    await ClockCycles(dut.clk, 1)
    
    # Generate 5 errors
    for i in range(5):
        dut.ui_in.value = 0b000001  # syndrome = 001 (error on q2)
        await ClockCycles(dut.clk, 1)
    
    # Wait one more cycle for the last counter update to propagate
    await ClockCycles(dut.clk, 1)
    
    error_count = (dut.uo_out.value >> 4) & 0xF
    assert error_count == 5, f"Expected error_count=5, got {error_count}"
    dut._log.info("✓ Error counter test passed")
    
    dut._log.info("🎉 All tests passed!")


@cocotb.test()
async def test_qec_test_mode(dut):
    """Test the built-in test pattern generator"""
    dut._log.info("Starting test mode verification")
    
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())
    
    # Reset
    dut.rst_n.value = 0
    dut.ena.value = 1
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    
    # Enable test mode
    dut.ui_in.value = 0b010000
    await ClockCycles(dut.clk, 1)
    
    # Watch the LFSR cycle through patterns
    dut._log.info("Test mode patterns:")
    for i in range(10):
        await ClockCycles(dut.clk, 1)
        correction = int(dut.uo_out.value) & 0b11
        error_flag = (dut.uo_out.value >> 2) & 1
        dut._log.info(f"  Cycle {i}: correction={correction:02b}, error={error_flag}")
    
    dut._log.info("✓ Test mode working")
