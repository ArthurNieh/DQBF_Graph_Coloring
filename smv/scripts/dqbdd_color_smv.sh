#!/bin/bash

######################################################
# Arguments
######################################################

blif_file=$1
colorability=$2
FF_tokeep=$3

if [ -z "$blif_file" ] || [ -z "$colorability" ] || [ -z "$FF_tokeep" ]; then
    echo "Usage: $0 <blif_file> <colorability> <FF_tokeep>"
    exit 1
fi

######################################################
# Directory resolution
######################################################

# smv/scripts
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)

# smv
SMV_DIR=$(cd "$SCRIPT_DIR/.." && pwd)

# root
ROOT_DIR=$(cd "$SMV_DIR/.." && pwd)

# SMV subdirs
BLIF_DIR="$SMV_DIR/benchmarks/blif"
SIMPLIFIED_DIR="$SMV_DIR/benchmarks/simplified_blif"
COMB_DIR="$SMV_DIR/benchmarks/combinational_blif"
SAMPLE_DIR="$SMV_DIR/sample/color/dqbdd"

# External tools
ABC_DQBF_DIR="$ROOT_DIR/abc/dqbf"
SOLVER_BIN="$ROOT_DIR/../bin/dqbdd"

######################################################
# Files
######################################################

BLIF_IN="$BLIF_DIR/$blif_file"
SIMPLIFIED_BLIF="$SIMPLIFIED_DIR/${blif_file}_simplified${FF_tokeep}.blif"
COMB_BLIF="$COMB_DIR/${blif_file}_combinational${FF_tokeep}.blif"
SAMPLE_BLIF="$SAMPLE_DIR/${blif_file}_FF${FF_tokeep}_color${colorability}_sample.blif"

ABC_OUTPUT_FILE=$(mktemp)
CNF_OUTPUT_FILE=$(mktemp)
DQDIMACS_OUTPUT_FILE=$(mktemp)

######################################################
# Sanity checks
######################################################

for f in "$BLIF_IN" "$SOLVER_BIN"; do
    if [ ! -e "$f" ]; then
        echo "ERROR: Missing file $f"
        exit 1
    fi
done

mkdir -p "$SIMPLIFIED_DIR" "$COMB_DIR" "$SAMPLE_DIR"

######################################################
# Step 1: Simplify BLIF
######################################################

echo "######################################################"
echo "Simplify BLIF"

python3 "$SMV_DIR/simplify_blif_benchmark.py" \
    -i "$BLIF_IN" \
    -o "$SIMPLIFIED_BLIF" \
    -n "$FF_tokeep"

######################################################
# Step 2: Convert to combinational BLIF
######################################################

echo "######################################################"
echo "Convert to combinational BLIF"

python3 "$SMV_DIR/to_combinational_blif.py" \
    -i "$SIMPLIFIED_BLIF" \
    -o "$COMB_BLIF" \
    --abc "$ABC_OUTPUT_FILE"

######################################################
# Step 3: Generate colored SMV/BLIF
######################################################

echo "######################################################"
echo "Generate colored BLIF"

start2=$(date +%s.%N)

python3 "$SMV_DIR/blif_gen_smv_coloring.py" \
    -i "$COMB_BLIF" \
    -o "$SAMPLE_BLIF" \
    -c "$colorability" \
    --abc "$ABC_OUTPUT_FILE"

######################################################
# Step 4: BLIF → DQDIMACS
######################################################

echo "######################################################"
echo "Generate DQDIMACS file"

if [ ! -f "$SAMPLE_BLIF" ]; then
    echo "ERROR: Colored BLIF not found: $SAMPLE_BLIF"
    exit 1
fi

start3=$(date +%s.%N)

python3 "$ABC_DQBF_DIR/smv_convert_to_cnf.py" \
    -i "$SAMPLE_BLIF" \
    -c "$CNF_OUTPUT_FILE" \
    -d "$DQDIMACS_OUTPUT_FILE"

######################################################
# Step 5: Run DQBDD solver
######################################################

echo "######################################################"
echo "Run DQBDD solver"

start4=$(date +%s.%N)

timeout 1h "$SOLVER_BIN" "$DQDIMACS_OUTPUT_FILE"

end=$(date +%s.%N)

######################################################
# Runtime summary
######################################################

runtime_coloring=$(echo "$start3 - $start2" | bc -l)
runtime_cnf=$(echo "$start4 - $start3" | bc -l)
runtime_pedant=$(echo "$end - $start4" | bc -l)

echo
echo "================ Runtime Summary ================"
echo "Coloring generation : $runtime_coloring s"
echo "DQDIMACS generation : $runtime_cnf s"
echo "DQBDD solver       : $runtime_pedant s"
echo "================================================="

# Cleanup
# cat "$CNF_OUTPUT_FILE" > debug_cnf.txt
# cat "$DQDIMACS_OUTPUT_FILE" > debug.txt
rm -f "$ABC_OUTPUT_FILE" "$CNF_OUTPUT_FILE" "$DQDIMACS_OUTPUT_FILE"