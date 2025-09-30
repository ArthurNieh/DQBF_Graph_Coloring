#!/bin/bash

# Load FF table
source ./ff_table.sh

mkdir -p iscas89/result/clique_simplified_sat/
rm iscas89/benchmarks/*simplified.*

for (( FF_num=3; FF_num<=16; FF_num=FF_num+1 )); do
	for (( i=3; i<=8; i=i+1 )); do
	# Create an array of sorted benchmarks by numeric instance number
		mapfile -t sorted_benches < <(
			for f in iscas89/benchmarks/s*.bench; do
				num=$(basename "$f" .bench | sed 's/^s//')
				echo "$num $f"
			done | sort -n | awk '{print $2}'
		)

		for bench in "${sorted_benches[@]}"; do	
			echo "##############################"
			# echo "##############################"
			echo $bench;
			echo "Current time: $(date)"

			prefix="iscas89/benchmarks/"
			suffix=".bench"
			ins=${bench#"$prefix"}
			ins=${ins%"$suffix"}

			output="iscas89/result/clique_simplified_sat/${ins}_Clique${i}_FF${FF_num}"

			ff_threshold=${ff_table[$ins]}
			if [ -z "$ff_threshold" ]; then
				echo "No FF number found for $ins, skipping..."
				continue
			fi
			if (( ff_threshold < FF_num )); then
				echo "$ins skip"
				continue
			fi
			
			echo $bench &> "$output"
			echo "${ins}" &>> "$output"
			echo "clique_size=${i}" &>> "$output"
			echo "FF_tokeep=${FF_num}" &>> "$output"

			echo "${ins}"
			echo "clique_size=${i}"
			echo "FF_tokeep=${FF_num}"

			./sat_clique_simplified_iscas.sh "$ins" "$i" "$FF_num" &>> "$output"

			rm iscas89/benchmarks/*simplified.*
		done
	done
done