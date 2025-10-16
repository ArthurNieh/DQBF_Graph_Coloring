#!/bin/bash
# Auto Generate iscas.blif and run the DQBF solver
# Author: Arthur Nieh
# Date: 2025/10/16
# Usage: ./my_random.sh
# working directory: /DQBF_Graph_Coloring/random_graph/scripts

instance=$1
trial=$2
solver=$3
if [ -z "$instance" ]; then
    echo "Usage: $0 <instance> [trial] [solver]"
    exit 1
fi
if [ -z "$trial" ]; then
    echo "No trial specified, defaulting to 0"
    trial=0
fi
if [ -z "$solver" ]; then
    echo "No solver specified, defaulting to pedant"
    solver="pedant"
fi

echo "######################################################"
echo "Solving $instance for $k_num color\n"


start2=`date +%s.%N`
# Generate the blif file
cd ../
python3 blif_gen_random_graph_ham.py -n "$instance" -t "$trial"
# this will generate sample.blif

# Generate DQDIMACS for the DQBF solver
# echo "######################################################"
echo "Generate DQDIMACS file"
    ## this part is written at /home/arthur/program/abc/dqbf
    ## the abc have been modified to support DQBF
cd ../abc/dqbf
python3 convert_to_cnf_hamiltonian.py \
    "../../random_graph/sample/random_graph_hamiltonian_n${instance}_trial${trial}.blif"

# Run the DQBF solver
if [ "$solver" == "pedant" ]; then
    echo "Run pedant solver"
    cd ../../pedant-solver/build/src
    timeout 1h ./pedant ../../../abc/dqbf/dqdimacs.txt --cnf model
else
    echo "Run DQBDD solver"
    cd ../../bin/
    timeout 1h ./dqbdd ../abc/dqbf/dqdimacs.txt
fi

end2=`date +%s.%N`

runtime2=$( echo "$end2 - $start2" | bc -l )
echo -e "\nRuntime for DQBF was $runtime2 seconds.\n"
