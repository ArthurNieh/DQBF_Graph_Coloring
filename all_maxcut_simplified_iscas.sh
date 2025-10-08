#!/bin/bash

# Load FF table
source ./ff_table.sh

mkdir -p iscas89/result/simplified_maxcut/
rm iscas89/benchmarks/*simplified.*

for (( FF_num=3; FF_num<=3; FF_num=FF_num+1 )); do
	for (( i=2; i<=2; i=i+1 )); do
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

			output="iscas89/result/simplified_maxcut/${ins}_FF${FF_num}_Cut${i}"

			echo "${ins}"
			echo "FF_tokeep=${FF_num}"
			echo "cut=${i}"

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
			echo "FF_tokeep=${FF_num}" &>> "$output"
			echo "cut=${i}" &>> "$output"

			./my_maxcut_iscas.sh "$ins" "$FF_num" "$i" &>> "$output"

			rm iscas89/benchmarks/*simplified.*
		done
	done
done