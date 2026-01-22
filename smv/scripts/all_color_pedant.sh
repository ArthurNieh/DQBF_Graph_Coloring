#!/bin/bash

# Load FF table
# source ./ff_table.sh

# Create result folder
RESULT_DIR="../result/color/pedant/"
mkdir -p "$RESULT_DIR"

# Loop over FF numbers and colors
for (( FF_num=3; FF_num<=3; FF_num++ )); do
    for (( i=2; i<=2; i++ )); do

        # Loop over all .smv files in benchmarks/blif
        for bench in ../benchmarks/blif/*.blif; do
            echo "##############################"
            echo "Processing: $bench"
            echo "Current time: $(date)"

            # Extract the base name without extension
            ins=$(basename "$bench" .smv)

            # Prepare output file
            output="${RESULT_DIR}/${ins}_C${i}_FF${FF_num}.log"

            echo "$bench" &> "$output"
            echo "Instance=${ins}" &>> "$output"
            echo "color=${i}" &>> "$output"
            echo "FF_tokeep=${FF_num}" &>> "$output"

            # Print to console
            echo "Instance=${ins}"
            echo "color=${i}"
            echo "FF_tokeep=${FF_num}"

            # Check FF threshold
            # ff_threshold=${ff_table[$ins]}
            # if [ -z "$ff_threshold" ]; then
            #     echo "No FF number found for $ins, skipping..." &>> "$output"
            #     continue
            # fi
            # if (( ff_threshold < FF_num )); then
            #     echo "$ins skip (threshold=$ff_threshold, FF_num=$FF_num)" &>> "$output"
            #     continue
            # fi

            # Call the new script
            ./pedant_color_smv.sh "$ins" "$i" "$FF_num" &>> "$output"

        done
    done
done
