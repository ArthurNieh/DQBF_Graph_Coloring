#!/bin/bash

mkdir -p ../result/coloring_random_pedant/
mkdir -p ../sample/

for (( inst_n=3; inst_n<=3; inst_n=inst_n+1 )); do
	for (( i=2; i<=2; i=i+1 )); do

		for (( t=0; t<5; t=t+1 )); do	
			echo "##############################"
			echo "Current instance: $inst_n, coloring: $i, trial: $t"
			echo "Current time: $(date)"

			output="../result/coloring_random_pedant/${inst_n}_color${i}_t${t}"

			echo "N${inst_n}_C${i}_T${t}" &> "$output"
			echo "N=${inst_n}" &>> "$output"
			echo "color=${i}" &>> "$output"
			echo "trial=${t}" &>> "$output"

			echo "N=${inst_n}"
			echo "color=${i}" 
			echo "trial=${t}" 

			./my_coloring_random.sh "$inst_n" "$i" "$t" &>> "$output"
		done
	done
done