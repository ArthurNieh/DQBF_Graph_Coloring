#!/bin/bash

problem="hamiltonian"
solver="pedant"

mkdir -p "../result/${problem}_random_${solver}/"
mkdir -p ../sample/

for (( inst_n=3; inst_n<=3; inst_n=inst_n+1 )); do
	for (( t=0; t<5; t=t+1 )); do	
		echo "##############################"
		echo "Current instance: $inst_n, trial: $t"
		echo "Current time: $(date)"

		output="../result/${problem}_random_${solver}/${inst_n}_t${t}"

		echo "N${inst_n}_T${t}" &> "$output"
		echo "N=${inst_n}" &>> "$output"
		echo "trial=${t}" &>> "$output"

		echo "N=${inst_n}"
		echo "trial=${t}"

		./my_ham_random.sh "$inst_n" "$t" "$solver" &>> "$output"
	done
done