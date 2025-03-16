#!/bin/bash
# Auto Generate lsfr.blif and run the DQBF solver
# Author: Arthur Nieh
# Date: 2025/3/11
# Usage: ./lsfr.sh

# lsfr configuration can be found at /home/arthur/course/sat/DQBF_Graph_Coloring/lsfr/config.py

start1=`date +%s.%N`

# Generate the lsfr
cd /home/arthur/course/sat/DQBF_Graph_Coloring/lsfr
python3 explicit_gen_lsfr.py
# this will generate lsfr.txt

# Run the POPSAT solver
# echo "######################################################"
echo -e "\nRun the POPSAT solver"
cd /home/arthur/course/sat/DQBF_Graph_Coloring/popsatgcpbcp/source
python3 main.py --instance=../../lsfr/sample/lsfr_graph.txt --model=POP-S

end1=`date +%s.%N`

echo "######################################################"
start2=`date +%s.%N`
# Generate the blif file
cd /home/arthur/course/sat/DQBF_Graph_Coloring/lsfr
python3 blif_gen_lsfr_coloring.py 
# this will generate lsfr.blif

# Generate DQDIMACS for the DQBF solver
# echo "######################################################"
echo "Generate DQDIMACS file"
    ## this part is written at /home/arthur/program/abc/dqbf
    ## the abc have been modified to support DQBF
cd /home/arthur/program/abc/dqbf
python3 convert_to_cnf.py /home/arthur/course/sat/DQBF_Graph_Coloring/lsfr/sample/lsfr.blif

# Run the DQBF solver
cd /home/arthur/course/sat/DQBF_Graph_Coloring/pedant-solver/build/src
./pedant /home/arthur/program/abc/dqbf/dqdimacs.txt --cnf model

end2=`date +%s.%N`

runtime1=$( echo "$end1 - $start1" | bc -l )
echo -e "\nRuntime for SAT was $runtime1 seconds.\n"
runtime2=$( echo "$end2 - $start2" | bc -l )
echo -e "\nRuntime for DQBF was $runtime2 seconds.\n"