#!/bin/bash

# FF_num=$1
# if [ -z "$FF_num" ]; then
# 	echo "Usage: $0 <FF_tokeep>"
# 	exit 1
# fi

mkdir -p iscas89/result/clique_simplified/
rm iscas89/benchmarks/*simplified.*

for (( FF_num=17; FF_num<=18; FF_num=FF_num+1 )); do
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

			output="iscas89/result/clique_simplified/${ins}_Clique${i}_FF${FF_num}"

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

			if [[ "$ins" == "s298" || \
				"$ins" == "s344" || \
				"$ins" == "s349" || \
				"$ins" == "s420" ]]; then
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

			./my_clique_simplified_iscas.sh "$ins" "$i" "$FF_num" &>> "$output"

			rm iscas89/benchmarks/*simplified.*
		done
	done
done