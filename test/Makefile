SIM ?= icarus
TOPLEVEL_LANG ?= verilog

# RTL simulation (default)
VERILOG_SOURCES = $(PWD)/../src/tt_um_qec_decoder.v
TOPLEVEL = tt_um_qec_decoder
MODULE = test

# Gate-level simulation
ifeq ($(GATES),yes)
    VERILOG_SOURCES = $(PWD)/gate_level_netlist.v
    COMPILE_ARGS += -DUSE_POWER_PINS
    COMPILE_ARGS += -DFUNCTIONAL
    COMPILE_ARGS += -DUNIT_DELAY=#1
    
    # Include SKY130 standard cell libraries
    VERILOG_SOURCES += $(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/verilog/primitives.v
    VERILOG_SOURCES += $(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/verilog/sky130_fd_sc_hd.v
    
    # For gate-level we need to use the GL testbench
    MODULE = test_gl
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
