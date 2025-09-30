#!/bin/bash

# Lookup table: circuit -> FF number
declare -A ff_table=(
    [s27]=3
    [s208]=8
    [s208a]=8
    [s298]=14
    [s344]=15
    [s349]=15
    [s382]=21
    [s386]=6
    [s400]=21
    [s420]=16
    [s420a]=16
    [s444]=21
    [s510]=6
    [s526]=21
	[s526a]=21
    [s641]=19
    [s713]=19
    [s820]=5
    [s832]=5
    [s838]=32
	[s838a]=32
    [s953]=29
    [s1196]=18
    [s1238]=18
    [s1423]=74
    [s1488]=6
    [s1494]=6
    [s5378]=179
    [s9234]=211
    [s13207]=638
    [s15850]=534
    [s35932]=1728
    [s38417]=1636
    [s38584]=1426
)

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