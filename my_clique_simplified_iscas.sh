#!/bin/bash
# Auto Generate iscas.blif and run the DQBF solver
# Author: Arthur Nieh
# Date: 2025/9/19
# Usage: ./iscas.sh

instance=$1
clique_size=$2
FF_tokeep=$3
if [ -z "$instance" ]; then
    echo "Usage: $0 <iscas89_instance> <clique_size> <FF_tokeep>"
    exit 1
fi
if [ -z "$clique_size" ]; then
    echo "Usage: $0 <iscas89_instance> <clique_size> <FF_tokeep>"
    exit 1
fi
if [ -z "$FF_tokeep" ]; then
    echo "Usage: $0 <iscas89_instance> <clique_size> <FF_tokeep>"
    exit 1
fi

echo "######################################################"
echo "Solving $instance for $clique_size size clique\n"

# Generate the blif file
cd ./iscas89
python3 simplify_bench.py "$instance" "$FF_tokeep"
python3 bench_to_blif.py "${instance}_simplified"

start2=`date +%s.%N`
python3 blif_gen_iscas_clique.py "${instance}_simplified" "$clique_size"
# this will generate lsfr.blif

# Generate DQDIMACS for the DQBF solver
# echo "######################################################"
echo "Generate DQDIMACS file"
    ## this part is written at /home/arthur/program/abc/dqbf
    ## the abc have been modified to support DQBF
cd ../abc/dqbf
python3 convert_to_cnf_clique.py "../../iscas89/sample/${instance}_simplified_clique.blif"

start3=`date +%s.%N`
# Run the DQBF solver
cd ../../pedant-solver/build/src
timeout 1h ./pedant ../../../abc/dqbf/dqdimacs.txt --cnf model

end2=`date +%s.%N`

runtime2=$( echo "$end2 - $start2" | bc -l )
echo -e "\nRuntime for DQBF was $runtime2 seconds.\n"
runtime3=$( echo "$end2 - $start3" | bc -l )
echo -e "\nRuntime for pedant was $runtime3 seconds.\n"
