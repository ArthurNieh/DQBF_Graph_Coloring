#!/bin/bash
# Auto Generate iscas.blif and run the DQBF solver
# Author: Arthur Nieh
# Date: 2025/3/31
# Usage: ./iscas.sh

instance=$1

# Generate the lsfr
cd /home/arthur/course/sat/DQBF_Graph_Coloring/iscas89/
python3 bench_to_blif.py "$instance"

start1=`date +%s.%N`
python3 explicit_gen_iscas.py "$instance"
# this will generate iscas_graph.txt

# Run the POPSAT solver
# echo "######################################################"
echo -e "\nRun the POPSAT solver"
cd /home/arthur/course/sat/DQBF_Graph_Coloring/popsatgcpbcp/source
python3 main.py --instance=../../iscas89/sample/iscas_graph.txt --model=POP-S

end1=`date +%s.%N`

echo "######################################################"
start2=`date +%s.%N`
# Generate the blif file
cd /home/arthur/course/sat/DQBF_Graph_Coloring/iscas89
python3 blif_gen_iscas_coloring.py "$instance"
# this will generate lsfr.blif

# Generate DQDIMACS for the DQBF solver
# echo "######################################################"
echo "Generate DQDIMACS file"
    ## this part is written at /home/arthur/program/abc/dqbf
    ## the abc have been modified to support DQBF
cd /home/arthur/program/abc/dqbf
python3 convert_to_cnf.py "/home/arthur/course/sat/DQBF_Graph_Coloring/iscas89/sample/${instance}_color.blif"

# Run the DQBF solver
cd /home/arthur/course/sat/DQBF_Graph_Coloring/pedant-solver/build/src
./pedant /home/arthur/program/abc/dqbf/dqdimacs.txt --cnf model

end2=`date +%s.%N`

runtime1=$( echo "$end1 - $start1" | bc -l )
echo -e "\nRuntime for SAT was $runtime1 seconds.\n"
runtime2=$( echo "$end2 - $start2" | bc -l )
echo -e "\nRuntime for DQBF was $runtime2 seconds.\n"