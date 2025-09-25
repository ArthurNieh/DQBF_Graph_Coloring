#!/bin/bash

# FF_num=$1
# if [ -z "$FF_num" ]; then
# 	echo "Usage: $0 <FF_tokeep>"
# 	exit 1
# fi

dir_path="iscas89/result/simplified_sat/"

mkdir -p "$dir_path"
rm iscas89/benchmarks/*simplified.*

for (( FF_num=11; FF_num<=14; FF_num=FF_num+1 )); do
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

		if [[ "$ins" == "s27" || \
			"$ins" == "s208" || \
			"$ins" == "s208a" || \
			"$ins" == "s386" || \
			"$ins" == "s510" || \
			"$ins" == "s820" || \
			"$ins" == "s832" || \
			"$ins" == "s1488" || \
			"$ins" == "s1494" ]]; then
			echo "$ins skip"
			continue
		fi

		./sat_simplified_iscas.sh "$ins" "$FF_num" &>> "$file_name"

		rm iscas89/benchmarks/*simplified.*
	done
done