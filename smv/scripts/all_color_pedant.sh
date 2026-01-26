#!/bin/bash

RESULT_DIR="../result/color/pedant/"
mkdir -p "$RESULT_DIR"
MAX_JOBS=8  # Max parallel jobs

function run_task {
    FF_num=$1
    color=$2
    bench=$3

    ins=$(basename "$bench" .blif)
    output="${RESULT_DIR}/${ins}_C${color}_FF${FF_num}.log"

    echo "[Color][Pedant] ${ins} with color=${color} and FF_tokeep=${FF_num}"

    echo "$bench" &> "$output"
    echo "Instance=${ins}" &>> "$output"
    echo "color=${color}" &>> "$output"
    echo "FF_tokeep=${FF_num}" &>> "$output"

    ./pedant_color_smv.sh "$ins.blif" "$color" "$FF_num" &>> "$output"
}

function count_latches {
    local blif_file=$1
    grep -c '^\.latch' "$blif_file"
}

# Loop and launch tasks
for (( FF_num=3; FF_num<=16; FF_num++ )); do
    for (( color=2; color<=5; color++ )); do
        for bench in ../benchmarks/blif/*.blif; do

            latch_num=$(count_latches "$bench")

            if (( FF_num > latch_num )); then
                echo "[SKIP] $(basename "$bench") : FF_num=${FF_num} > latches=${latch_num}"
                continue
            fi

            run_task "$FF_num" "$color" "$bench" &

            # Wait if we reach max parallel jobs
            while (( $(jobs -r | wc -l) >= MAX_JOBS )); do
                sleep 1
            done

        done
    done
done


wait  # Wait for remaining jobs
