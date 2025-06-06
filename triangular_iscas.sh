#!/bin/bash
# Auto Generate iscas.blif and run the DQBF solver
# Author: Arthur Nieh
# Date: 2025/5/5
# Usage: ./triangular_iscas.sh

instance=$1
if [ -z "$instance" ]; then
    echo "Usage: $0 <iscas89_instance>"
    exit 1
fi

# Generate the blif file of the iscas89 benchmark
cd ./iscas89/
g++ -o gen_testcase gen_testcase.cpp
python3 bench_to_blif.py "$instance"

echo "######################################################"
start2=`date +%s.%N`
# Generate the blif file
python3 blif_gen_iscas_triangular.py "$instance" "-f"
# this will generate {instance}_triangular.blif

# Generate DQDIMACS for the DQBF solver
# echo "######################################################"
echo "Generate DQDIMACS file"
    ## this part is written at /home/arthur/program/abc/dqbf
    ## the abc have been modified to support DQBF
cd ../abc/dqbf
python3 convert_to_cnf.py "../../iscas89/sample/${instance}_triangular.blif"

# Run the DQBF solver
cd ../../pedant-solver/build/src
./pedant ../../../abc/dqbf/dqdimacs.txt --cnf model

end2=`date +%s.%N`

runtime2=$( echo "$end2 - $start2" | bc -l )
echo -e "\nRuntime for DQBF was $runtime2 seconds.\n"