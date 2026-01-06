import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles

@cocotb.test()
async def test_qec_basic(dut):
    """Test basic syndrome decoding"""
    dut._log.info("Starting QEC decoder test")
    
    # Create clock
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())
    
    # Reset
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)
    
    # Test 1: No error syndrome (000)
    dut._log.info("Test 1: No error syndrome")
    dut.ui_in.value = 0b000
    await ClockCycles(dut.clk, 1)
    output = int(dut.uo_out.value)
    assert output & 0b11 == 0b00, "Expected no correction"
    assert (output >> 2) & 1 == 0, "Expected no error flag"
    
    # Test 2: Error on qubit 0 (syndrome 011)
    dut._log.info("Test 2: Error on qubit 0")
    dut.ui_in.value = 0b011
    await ClockCycles(dut.clk, 1)
    output = int(dut.uo_out.value)
    assert output & 0b11 == 0b01, "Expected correction 01"
    assert (output >> 2) & 1 == 1, "Expected error flag"
    
    # Test 3: Error on qubit 1 (syndrome 010)
    dut._log.info("Test 3: Error on qubit 1")
    dut.ui_in.value = 0b010
    await ClockCycles(dut.clk, 1)
    output = int(dut.uo_out.value)
    assert output & 0b11 == 0b10, "Expected correction 10"
    
    # Test 4: Error on qubit 2 (syndrome 001)
    dut._log.info("Test 4: Error on qubit 2")
    dut.ui_in.value = 0b001
    await ClockCycles(dut.clk, 1)
    output = int(dut.uo_out.value)
    assert output & 0b11 == 0b11, "Expected correction 11"
    
    # Test 5: Uncorrectable error (syndrome 111)
    dut._log.info("Test 5: Uncorrectable error")
    dut.ui_in.value = 0b111
    await ClockCycles(dut.clk, 1)
    output = int(dut.uo_out.value)
    assert (output >> 3) & 1 == 1, "Expected uncorrectable flag"

@cocotb.test()
async def test_qec_test_mode(dut):
    """Test the built-in test pattern generator"""
    dut._log.info("Starting test mode verification")
    
    # Create clock
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())
    
    # Reset
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    
    # Enable test mode
    dut.ui_in.value = 0b10000  # Bit 4 = test_mode
    
    # Run and observe patterns
    dut._log.info("Test mode patterns:")
    for i in range(10):
        await ClockCycles(dut.clk, 1)
        output = int(dut.uo_out.value)
        correction = output & 0b11
        error_flag = (output >> 2) & 1
        dut._log.info(f"  Cycle {i}: correction={correction:02b}, error={error_flag}")