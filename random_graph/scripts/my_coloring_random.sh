#!/bin/bash
# Auto Generate iscas.blif and run the DQBF solver
# Author: Arthur Nieh
# Date: 2025/10/5
# Usage: ./my_random.sh
# working directory: /DQBF_Graph_Coloring/random_graph/scripts

instance=$1
colorability=$2
# solver=$3
if [ -z "$instance" ]; then
    echo "Usage: $0 <instance> <colorability>"
    exit 1
fi
if [ -z "$colorability" ]; then
    echo "Usage: $0 <instance> <colorability>"
    exit 1
fi
# if [ -z "$solver" ]; then
#     echo "No solver specified, defaulting to pedant"
#     solver="pedant"
# fi

echo "######################################################"
echo "Solving $instance for $colorability color\n"


start2=`date +%s.%N`
# Generate the blif file
cd ../
python3 blif_gen_random_graph_coloring.py -n "$instance" -c "$colorability"
# this will generate sample.blif

# Generate DQDIMACS for the DQBF solver
# echo "######################################################"
echo "Generate DQDIMACS file"
    ## this part is written at /home/arthur/program/abc/dqbf
    ## the abc have been modified to support DQBF
cd ../abc/dqbf
python3 convert_to_cnf.py \
    "../../random_graph/sample/random_graph_coloring_n${instance}_c${colorability}.blif"

# Run the DQBF solver
cd ../../pedant-solver/build/src
./pedant ../../../abc/dqbf/dqdimacs.txt --cnf model

end2=`date +%s.%N`

runtime2=$( echo "$end2 - $start2" | bc -l )
echo -e "\nRuntime for DQBF was $runtime2 seconds.\n"
