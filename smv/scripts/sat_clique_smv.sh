#!/bin/bash

######################################################
# Arguments
######################################################

blif_file=$1
clique_size=$2
FF_tokeep=$3
timelimit=$((60 * 60))

if [ -z "$blif_file" ] || [ -z "$clique_size" ] || [ -z "$FF_tokeep" ]; then
    echo "Usage: $0 <blif_file> <clique_size> <FF_tokeep>"
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
COMB_DIR="$SMV_DIR/benchmarks/explicit_graph_blif"
SAMPLE_DIR="$SMV_DIR/sample/explicit"

######################################################
# Files
######################################################

BLIF_IN="$BLIF_DIR/$blif_file"
SIMPLIFIED_BLIF="$SIMPLIFIED_DIR/${blif_file}_simplified${FF_tokeep}.blif"
COMB_BLIF="$COMB_DIR/${blif_file}_combinational${FF_tokeep}.blif"
SAMPLE_BLIF="$SAMPLE_DIR/${blif_file}_FF${FF_tokeep}_sample.blif"

######################################################
# Sanity checks
######################################################

for f in "$BLIF_IN" ; do
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
# Step 2: Convert to explicit graph
######################################################

echo "######################################################"
echo "Convert to explicit graph"

start2=$(date +%s.%N)

timeout 1h python3 "$SMV_DIR/explicit_gen_smv.py" \
    -b "$SIMPLIFIED_BLIF" \
    --ff "$FF_tokeep" \
    --explicit_blif "$COMB_BLIF" \
    --explicit_graph_output "$SAMPLE_BLIF" \

######################################################
# Step 3: Run the PYSAT solver
######################################################

echo "######################################################"
echo "Run the PYSAT solver"
if [ ! -f "$SAMPLE_BLIF" ]; then
    echo "ERROR: Colored BLIF not found: $SAMPLE_BLIF"
    exit 1
fi

start3=$(date +%s.%N)

timeout 1h python3 "$SMV_DIR/clique_sat_solver.py" \
    -k $clique_size \
    --graph_file "$SAMPLE_BLIF"

end=$(date +%s.%N)

######################################################
# Runtime summary
######################################################

runtime_gen_explicit=$(echo "$start3 - $start2" | bc -l)
runtime_sat=$(echo "$end - $start3" | bc -l)

echo
echo "================ Runtime Summary ================"
echo "Explicit graph gen : $runtime_gen_explicit s"
echo "PYSAT solver      : $runtime_sat s"
echo "================================================="

# Cleanup