#!/bin/bash
# Auto Generate Sudoku blif/explicit file
# Author: Arthur Nieh
# Date: 2025/1/12
# Usage: ./sudoku.sh

# Generate the sudoku and explicit file
cd /home/arthur/course/sat/DQBF_Graph_Coloring/sudoku
python3 gen_explicit.py
# Generate the blif file
python3 blif_gen_auto.py

# Run the POPSAT solver
echo "##################"
echo "Run the POPSAT solver"
cd /home/arthur/course/sat/DQBF_Graph_Coloring/popsatgcpbcp/source
python3 main.py --instance=../../sudoku/explicit/sudoku_graph.txt --model=POP-S

# Generate DQDIMACS for the DQBF solver
# echo "##################"
# echo "Generate DQDIMACS file"
#     ## this part is written at /home/arthur/program/abc/dqbf
#     ## the abc have been modified to support DQBF
# cd /home/arthur/program/abc/dqbf
# python3 convert_to_cnf.py /home/arthur/course/sat/DQBF_Graph_Coloring/sudoku/sudoku.blif

# Run the DQBF solver
# cd /home/arthur/course/sat/DQBF_Graph_Coloring/pedant-solver/build/src
# ./pedant /home/arthur/program/abc/dqbf/dqdimacs.txt --cnf model