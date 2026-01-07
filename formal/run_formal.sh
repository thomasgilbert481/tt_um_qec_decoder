#!/bin/bash
set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔬 QEC Decoder Formal Verification"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "📋 Checking dependencies..."

if ! command -v sby &> /dev/null; then
    echo "  ❌ SymbiYosys (sby) not found"
    exit 1
else
    echo "  ✅ SymbiYosys (sby) found"
fi

if ! command -v yosys &> /dev/null; then
    echo "  ❌ Yosys not found"
    exit 1
else
    echo "  ✅ Yosys found"
fi

if ! command -v boolector &> /dev/null; then
    echo "  ❌ Boolector (SMT solver) not found"
    exit 1
else
    echo "  ✅ Boolector (SMT solver) found"
fi

echo ""
echo "✅ All dependencies satisfied!"
echo ""

echo "What would you like to run?"
echo "  1) Quick check (10 cycles, ~10 seconds)"
echo "  2) Medium check (30 cycles, ~30 seconds)"
echo "  3) Full verification (all tasks, ~4 minutes)"
echo ""
read -p "Enter choice [1-3]: " choice

echo ""

case $choice in
    1)
        echo "🔍 Running quick BMC (10 cycles)..."
        make bmc_quick
        ;;
    2)
        echo "🔍 Running medium BMC (30 cycles)..."
        make bmc_medium
        ;;
    3)
        echo "🔍 Running full verification suite..."
        make all
        ;;
    *)
        echo "Invalid choice. Running quick check by default..."
        make bmc_quick
        ;;
esac

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Verification Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

make report

echo ""
echo "📁 Results saved in qec_decoder_*/ directories"
echo ""
