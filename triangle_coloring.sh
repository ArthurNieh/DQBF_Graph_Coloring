#!/bin/bash
# Auto Generate triangle_color.blif and run the DQBF solver
# Author: Arthur Nieh
# Date: 2025/5/26
# Usage: ./triangle_coloring.sh <node Number> <colorability>

nodeNum=$1
colorability=$2
timelimit=$((3 * 60 * 60))
if [ -z "$nodeNum" ]; then
    echo "Usage: $0 <node Number> <colorability>"
    exit 1
fi
if [ -z "$colorability" ]; then
    echo "Usage: $0 <node Number> <colorability>"
    exit 1
fi

# Generate the blif file
cd ./triangle_coloring/

start1=`date +%s.%N`
python3 explicit_gen_triangle_coloring.py "$nodeNum"
# this will generate iscas_graph.txt
end_p=`date +%s.%N`
# Run the POPSAT solver
# echo "######################################################"
echo -e "\nRun the POPSAT solver"
cd ../popsatgcpbcp/source
python3 main.py "--instance=../../triangle_coloring/triangle_adjacency_graph.txt" "--model=POP-S" "--timelimit=$timelimit"

end1=`date +%s.%N`

echo "######################################################"
cd ../../triangle_coloring/
start2=`date +%s.%N`
# Generate the blif file
python3 blif_gen_triangle_coloring.py "$nodeNum" "$colorability"
# this will generate triangle_color.blif

# Generate DQDIMACS for the DQBF solver
# echo "######################################################"
echo "Generate DQDIMACS file"
    ## this part is written at /home/arthur/program/abc/dqbf
    ## the abc have been modified to support DQBF
cd ../abc/dqbf
python3 convert_to_cnf_triangle.py "../../triangle_coloring/triangle_color.blif"

# Run the DQBF solver
cd ../../pedant-solver/build/src
./pedant ../../../abc/dqbf/dqdimacs.txt --cnf model

end2=`date +%s.%N`

runtime1=$( echo "$end1 - $start1" | bc -l )
echo -e "\nRuntime for SAT was $runtime1 seconds.\n"
runtime_p=$( echo "$end_p - $start1" | bc -l )
echo -e "\nRuntime for explicit_gen_triangle_coloring.py was $runtime_p seconds.\n"
runtime2=$( echo "$end2 - $start2" | bc -l )
echo -e "\nRuntime for DQBF was $runtime2 seconds.\n"