#!/bin/bash
# Auto Generate iscas.blif and run the DQBF solver
# Author: Arthur Nieh
# Date: 2025/4/7
# Usage: ./iscas.sh

instance=$1
colorability=$2
if [ -z "$instance" ]; then
    echo "Usage: $0 <iscas89_instance> <colorability>"
    exit 1
fi
if [ -z "$colorability" ]; then
    echo "Usage: $0 <iscas89_instance> <colorability>"
    exit 1
fi

echo "######################################################"
echo "Solving $instance for $colorability color\n"


start2=`date +%s.%N`
# Generate the blif file
cd ./iscas89
python3 bench_to_blif.py "$instance"
python3 blif_gen_iscas_coloring.py "$instance" "$colorability" "1"
# this will generate lsfr.blif

# Generate DQDIMACS for the DQBF solver
# echo "######################################################"
echo "Generate DQDIMACS file"
    ## this part is written at /home/arthur/program/abc/dqbf
    ## the abc have been modified to support DQBF
cd ../abc/dqbf
python3 convert_to_cnf.py "../../iscas89/sample/${instance}_color.blif"

# Run the DQBF solver
cd ../../pedant-solver/build/src
./pedant ../../../abc/dqbf/dqdimacs.txt --cnf model

end2=`date +%s.%N`

runtime2=$( echo "$end2 - $start2" | bc -l )
echo -e "\nRuntime for DQBF was $runtime2 seconds.\n"
