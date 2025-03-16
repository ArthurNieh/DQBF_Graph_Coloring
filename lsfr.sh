#!/bin/bash
# Auto Generate lsfr.blif
# Author: Arthur Nieh
# Date: 2025/3/11
# Usage: ./lsfr.sh

# Generate the lsfr
cd /home/arthur/course/sat/DQBF_Graph_Coloring/lsfr
# python3 gen_explicit.py

# Generate the blif file
python3 blif_gen_lsfr_coloring.py 
# this will generate lsfr.blif

# Run the POPSAT solver
# echo "##################"
# echo "Run the POPSAT solver"
# cd /home/arthur/course/sat/DQBF_Graph_Coloring/popsatgcpbcp/source
# python3 main.py --instance=../../sudoku/explicit/sudoku_graph.txt --model=POP-S

# Generate DQDIMACS for the DQBF solver
echo "##################"
echo "Generate DQDIMACS file"
    ## this part is written at /home/arthur/program/abc/dqbf
    ## the abc have been modified to support DQBF
cd /home/arthur/program/abc/dqbf
python3 convert_to_cnf.py /home/arthur/course/sat/DQBF_Graph_Coloring/lsfr/sample/lsfr.blif

# Run the DQBF solver
cd /home/arthur/course/sat/DQBF_Graph_Coloring/pedant-solver/build/src
./pedant /home/arthur/program/abc/dqbf/dqdimacs.txt --cnf model