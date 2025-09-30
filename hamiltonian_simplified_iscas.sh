#!/bin/bash
# Auto Generate iscas.blif and run the DQBF solver
# Author: Arthur Nieh
# Date: 2025/8/11
# Usage: ./hamiltonian_iscas.sh

instance=$1
FF_tokeep=$2

if [ -z "$instance" ]; then
    echo "Usage: $0 <iscas89_instance> <FF_tokeep>"
    exit 1
fi
if [ -z "$FF_tokeep" ]; then
    echo "Usage: $0 <iscas89_instance> <FF_tokeep>"
    exit 1
fi

# Generate the blif file of the iscas89 benchmark
cd ./iscas89/
g++ -o gen_testcase gen_testcase.cpp
for i in {3..50}; do
    if [ ! -f ./sample/test_cases_$i.txt ]; then
        ./gen_testcase $i
    fi
done

python3 simplify_bench.py "$instance" "$FF_tokeep"

python3 bench_to_blif.py "${instance}_simplified"

start1=`date +%s.%N`
python3 explicit_gen_iscas.py "${instance}_simplified"
# this will generate iscas_graph.txt
end_p=`date +%s.%N`
# Run the google ortool solver
echo -e "\nRun the google ortool solver"
python3 hamiltonian_solve_ortools.py

end1=`date +%s.%N`

echo "######################################################"
start2=`date +%s.%N`
# Generate the blif file
python3 blif_gen_iscas_hamiltonian.py "${instance}_simplified"
# this will generate {instance}_hamiltonian.blif

# Generate DQDIMACS for the DQBF solver
# echo "######################################################"
echo "Generate DQDIMACS file"
    ## this part is written at /home/arthur/program/abc/dqbf
    ## the abc have been modified to support DQBF
cd ../abc/dqbf
python3 convert_to_cnf_hamiltonian.py "../../iscas89/sample/${instance}_simplified_hamiltonian.blif"

# Run the DQBF solver
cd ../../pedant-solver/build/src
timeout 1h ./pedant ../../../abc/dqbf/dqdimacs.txt --cnf model

end2=`date +%s.%N`

echo "######################################################"
runtime1=$( echo "$end1 - $start1" | bc -l )
echo -e "\nRuntime for ortool was $runtime1 seconds.\n"
runtime_p=$( echo "$end_p - $start1" | bc -l )
echo -e "\nRuntime for explicit_gen_iscas.py was $runtime_p seconds.\n"
runtime2=$( echo "$end2 - $start2" | bc -l )
echo -e "\nRuntime for DQBF was $runtime2 seconds.\n"