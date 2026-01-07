.PHONY: all bmc_quick bmc_medium bmc_deep cover clean report help

all: bmc_quick bmc_medium cover
	@echo ""
	@echo "=================================================="
	@echo "✅ ALL FORMAL VERIFICATION TESTS PASSED!"
	@echo "=================================================="
	@echo ""

bmc_quick:
	@echo "🔍 Running quick BMC (10 cycles)..."
	sby -f qec_decoder.sby bmc_quick

bmc_medium:
	@echo "🔍 Running medium BMC (30 cycles)..."
	sby -f qec_decoder.sby bmc_medium

bmc_deep:
	@echo "🔍 Running deep BMC (100 cycles)..."
	sby -f qec_decoder.sby bmc_deep

prove:
	@echo "🔬 Running induction proof (advanced)..."
	@echo "⚠️  Note: Induction may fail for combinational logic (this is OK)"
	sby -f qec_decoder.sby prove

cover:
	@echo "📊 Running coverage analysis..."
	sby -f qec_decoder.sby cover

report:
	@echo ""
	@echo "=================================================="
	@echo "📊 FORMAL VERIFICATION SUMMARY"
	@echo "=================================================="
	@for task in bmc_quick bmc_medium bmc_deep prove cover; do \
		if [ -d qec_decoder_$$task ]; then \
			status=$$(grep "^SBY.*DONE" qec_decoder_$$task/logfile.txt | tail -1); \
			echo "$$task: $$status"; \
		fi \
	done
	@echo "=================================================="

clean:
	rm -rf qec_decoder_*

help:
	@echo "Formal Verification Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  make all        - Run standard verification (BMC + coverage)"
	@echo "  make bmc_quick  - Quick BMC check (10 cycles, ~1s)"
	@echo "  make bmc_medium - Medium BMC (30 cycles, ~5s)"
	@echo "  make bmc_deep   - Deep BMC (100 cycles, ~30s)"
	@echo "  make prove      - K-induction proof (may fail for combinational logic)"
	@echo "  make cover      - Coverage analysis"
	@echo "  make report     - Show verification summary"
	@echo "  make clean      - Remove generated files"
