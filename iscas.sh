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

# Generate the blif file of the iscas89 benchmark
cd ./iscas89/
g++ -o gen_testcase gen_testcase.cpp
python3 bench_to_blif.py "$instance"

start1=`date +%s.%N`
python3 explicit_gen_iscas.py "$instance"
# this will generate iscas_graph.txt
end_p=`date +%s.%N`
# Run the POPSAT solver
# echo "######################################################"
echo -e "\nRun the POPSAT solver"
cd ../popsatgcpbcp/source
python3 main.py --instance=../../iscas89/sample/iscas_graph.txt --model=POP-S

end1=`date +%s.%N`

echo "######################################################"
start2=`date +%s.%N`
# Generate the blif file
cd ../../iscas89
python3 blif_gen_iscas_coloring.py "$instance" "$colorability"
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

runtime1=$( echo "$end1 - $start1" | bc -l )
echo -e "\nRuntime for SAT was $runtime1 seconds.\n"
runtime_p=$( echo "$end_p - $start1" | bc -l )
echo -e "\nRuntime for explicit_gen_iscas.py was $runtime_p seconds.\n"
runtime2=$( echo "$end2 - $start2" | bc -l )
echo -e "\nRuntime for DQBF was $runtime2 seconds.\n"