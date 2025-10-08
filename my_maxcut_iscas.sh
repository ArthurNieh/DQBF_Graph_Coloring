#!/bin/bash
# Auto Generate iscas.blif and run the DSSAT solver
# Author: Arthur Nieh
# Date: 2025/9/14
# Usage: ./my_maxcut_iscas.sh

instance=$1
FF_to_keep=$2
k_cut=$3
if [ -z "$instance" ]; then
    echo "Usage: $0 <iscas89_instance> <FF_to_keep> <k_cut>"
    exit 1
fi
if [ -z "$FF_to_keep" ]; then
    echo "Usage: $0 <iscas89_instance> <FF_to_keep> <k_cut>"
    exit 1
fi
if [ -z "$k_cut" ]; then
    echo "Usage: $0 <iscas89_instance> <FF_to_keep> <k_cut>"
    exit 1
fi

echo "######################################################"
echo "Solving $instance for max-cut\n"


start2=`date +%s.%N`
# Generate the blif file
cd ./iscas89
# python3 bench_to_blif.py "$instance"
python3 reduce_bench2blif.py "$instance" "$FF_to_keep" "0"
python3 blif_gen_maxcut.py --case "${instance}_simplified" -k "$k_cut" --version 2
# this will generate maxcut.blif
# exit 1
# Generate SDIMACS for the DSSAT solver
echo "Generate SDIMACS file"
    ## this part is written at /home/arthur/program/abc/dqbf
    ## the abc have been modified to support DQBF
cd ../abc/dqbf
python3 convert_to_cnf_maxcut.py \
    --input "../../iscas89/sample/${instance}_simplified_maxcut.blif" \
    --version 2

echo "######################################################"
# Run the DSSAT solver
cd ../../DSSATpre/build/src
./DSSATpre --to_qbf dep ../../../abc/dqbf/dqdimacs.txt -o dssat_input.sdimacs

echo "######################################################"

cd ../../../SharpSSAT
./SharpSSAT -s -p ../DSSATpre/build/src/dssat_input.sdimacs
# cd ../../../../solvers/elimssat/
# ./abc -q "ssat" ~/DQBF_Graph_Coloring/DSSATpre/build/src/dssat_input.sdimacs
# cd ../../../../solvers/ClauSSat
# ./claussat -sguwc ../../DQBF_Graph_Coloring/DSSATpre/build/src/dssat_input.sdimacs

end2=`date +%s.%N`

echo "######################################################"

runtime2=$( echo "$end2 - $start2" | bc -l )
echo -e "\nRuntime for DSSAT was $runtime2 seconds.\n"
