#!/bin/bash

RESULT_DIR="../result/clique/dqbdd/"
mkdir -p "$RESULT_DIR"
MAX_JOBS=8  # Max parallel jobs

function run_task {
    FF_num=$1
    color=$2
    bench=$3

    ins=$(basename "$bench" .blif)
    output="${RESULT_DIR}/${ins}_C${color}_FF${FF_num}.log"

    echo "[Clique][DQBDD] ${ins} with color=${color} and FF_tokeep=${FF_num}"

    echo "$bench" &> "$output"
    echo "Instance=${ins}" &>> "$output"
    echo "color=${color}" &>> "$output"
    echo "FF_tokeep=${FF_num}" &>> "$output"

    ./dqbdd_clique_smv.sh "$ins.blif" "$color" "$FF_num" &>> "$output"
}

# Loop and launch tasks
for (( FF_num=3; FF_num<=16; FF_num++ )); do
    for (( color=3; color<=8; color++ )); do
        for bench in ../benchmarks/blif/*.blif; do
            run_task "$FF_num" "$color" "$bench" &
            
            # Wait if we reach max parallel jobs
            while (( $(jobs -r | wc -l) >= MAX_JOBS )); do
                sleep 1
            done
        done
    done
done

wait  # Wait for remaining jobs
