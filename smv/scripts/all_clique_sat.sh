#!/bin/bash

RESULT_DIR="../result/clique/sat/"
mkdir -p "$RESULT_DIR"
MAX_JOBS=8  # Max parallel jobs

function run_task {
    FF_num=$1
    clique_size=$2
    bench=$3

    ins=$(basename "$bench" .blif)
    output="${RESULT_DIR}/${ins}_FF${FF_num}_clique${clique_size}.log"

    echo "[Color][Sat] ${ins} with FF_tokeep=${FF_num} and clique_size=${clique_size}"

    echo "$bench" &> "$output"
    echo "Instance=${ins}" &>> "$output"
    echo "FF_tokeep=${FF_num}" &>> "$output"
    echo "Clique_size=${clique_size}" &>> "$output"

    ./sat_color_smv.sh "$ins.blif" "$clique_size" "$FF_num" &>> "$output"
}

function count_latches {
    local blif_file=$1
    grep -c '^\.latch' "$blif_file"
}

# Loop and launch tasks
for (( FF_num=3; FF_num<=39; FF_num++ )); do
    for (( clique_size=3; clique_size<=8; clique_size++ )); do
        for bench in ../benchmarks/blif/*.blif; do

            latch_num=$(count_latches "$bench")

            if (( FF_num > latch_num )); then
                echo "[SKIP] $(basename "$bench") : FF_num=${FF_num} > latches=${latch_num}"
                continue
            fi

            run_task "$FF_num" "$clique_size" "$bench" &

            # Wait if we reach max parallel jobs
            while (( $(jobs -r | wc -l) >= MAX_JOBS )); do
                sleep 1
            done

        done
    done
done


wait  # Wait for remaining jobs
