#!/bin/bash

problem="clique"
solver="dqbdd"

mkdir -p "../result/${problem}_random_${solver}/"
mkdir -p ../sample/

for (( inst_n=3; inst_n<=3; inst_n=inst_n+1 )); do
	for (( i=3; i<=3; i=i+1 )); do

		for (( t=0; t<5; t=t+1 )); do	
			echo "##############################"
			echo "Current instance: $inst_n, k: $i, trial: $t"
			echo "Current time: $(date)"

			output="../result/${problem}_random_${solver}/${inst_n}_k${i}_t${t}"

			echo "N${inst_n}_K${i}_T${t}" &> "$output"
			echo "N=${inst_n}" &>> "$output"
			echo "k=${i}" &>> "$output"
			echo "trial=${t}" &>> "$output"

			echo "N=${inst_n}"
			echo "k=${i}" 
			echo "trial=${t}" 

			./my_clique_random.sh "$inst_n" "$i" "$t" "$solver" &>> "$output"
		done
	done
done