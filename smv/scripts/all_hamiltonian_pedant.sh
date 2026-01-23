#!/bin/bash

RESULT_DIR="../result/hamiltonian/pedant/"
mkdir -p "$RESULT_DIR"
MAX_JOBS=8  # Max parallel jobs

function run_task {
    FF_num=$1
    bench=$2

    ins=$(basename "$bench" .blif)
    output="${RESULT_DIR}/${ins}_FF${FF_num}.log"

    echo "[Hamiltonian][Pedant] ${ins} with FF_tokeep=${FF_num}"

    echo "$bench" &> "$output"
    echo "Instance=${ins}" &>> "$output"
    echo "FF_tokeep=${FF_num}" &>> "$output"

    ./pedant_hamiltonian_smv.sh "$ins.blif" "$FF_num" &>> "$output"
}

# Loop and launch tasks
for (( FF_num=3; FF_num<=16; FF_num++ )); do
    for bench in ../benchmarks/blif/*.blif; do
        run_task "$FF_num" "$bench" &
        
        # Wait if we reach max parallel jobs
        while (( $(jobs -r | wc -l) >= MAX_JOBS )); do
            sleep 1
        done
    done
done

wait  # Wait for remaining jobs
