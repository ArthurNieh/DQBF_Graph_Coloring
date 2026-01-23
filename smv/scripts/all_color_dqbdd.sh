#!/bin/bash

RESULT_DIR="../result/color/dqbdd/"
mkdir -p "$RESULT_DIR"
MAX_JOBS=8  # Max parallel jobs

function run_task {
    FF_num=$1
    color=$2
    bench=$3

    ins=$(basename "$bench" .blif)
    output="${RESULT_DIR}/${ins}_C${color}_FF${FF_num}.log"

    echo "$bench" &> "$output"
    echo "Instance=${ins}" &>> "$output"
    echo "color=${color}" &>> "$output"
    echo "FF_tokeep=${FF_num}" &>> "$output"

    ./dqbdd_color_smv.sh "$ins.blif" "$color" "$FF_num" &>> "$output"
}

# Loop and launch tasks
for (( FF_num=3; FF_num<=16; FF_num++ )); do
    for (( color=2; color<=5; color++ )); do
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
