#!/bin/bash

# Load FF table
source ./ff_table.sh
source ./pi_table.sh

dir_path="iscas89/result/simplified_sat/"

mkdir -p "$dir_path"
rm iscas89/benchmarks/*simplified.*

for (( FF_num=28; FF_num<=28; FF_num=FF_num+1 )); do
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

		file_name="${dir_path}/${ins}_FF${FF_num}"

		echo $bench &> "$file_name"
		echo "${ins}" &>> "$file_name"
		echo "FF_tokeep=${FF_num}" &>> "$file_name"

		echo "${ins}"
		echo "FF_tokeep=${FF_num}"

		ff_threshold=${ff_table[$ins]}
		if [ -z "$ff_threshold" ]; then
			echo "No FF number found for $ins, skipping..."
			continue
		fi
		if (( ff_threshold < FF_num )); then
			echo "$ins skip"
			continue
		fi
		pi_threshold=${pi_table[$ins]}
		if [ -z "$pi_threshold" ]; then
			echo "No PI number found for $ins, skipping..."
			continue
		fi
		if (( pi_threshold+FF_num > 30 )); then
			echo "$ins skip"
			continue
		fi

		./sat_simplified_iscas.sh "$ins" "$FF_num" &>> "$file_name"

		rm iscas89/benchmarks/*simplified.*
	done
done