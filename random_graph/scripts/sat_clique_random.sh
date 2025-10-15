#!/bin/bash
# Auto Generate iscas.blif and run the DQBF solver
# Author: Arthur Nieh
# Date: 2025/10/16
# Usage: ./iscas.sh

instance=$1
trial=$2
Clique_size=$3
timelimit=$((60 * 60))

if [ -z "$instance" ]; then
    echo "Usage: $0 <iscas89_instance> <trial> <Clique_size>"
    exit 1
fi
if [ -z "$trial" ]; then
    echo "No trial specified, defaulting to 0"
    trial=0
fi
if [ -z "$Clique_size" ]; then
    echo "Usage: $0 <iscas89_instance> <trial> <Clique_size>"
    exit 1
fi

# Generate the blif file of the iscas89 benchmark
# cd ./iscas89/
# g++ -o gen_testcase gen_testcase.cpp
# for i in {3..30}; do
#     if [ ! -f ./sample/test_cases_$i.txt ]; then
#         ./gen_testcase $i
#     fi
# done

cd ../
echo "$instance, trial $trial"
python3 blif_gen_random_graph_coloring.py -n "$instance" -t "$trial" --gen_graph

start1=`date +%s.%N`
timeout 1h python3 explicit_gen_random_graph.py -n "$instance" -t "$trial"
# this will generate iscas_graph.txt
end_p=`date +%s.%N`
# Run the k-clique solver
# echo "######################################################"
cd ../iscas89/
# Run the PYSAT solver
echo -e "\nRun the PYSAT solver"
python3 clique_sat_solver.py -k $Clique_size --graph_file ../random_graph/sample/iscas_graph.txt

end1=`date +%s.%N`

runtime1=$( echo "$end1 - $start1" | bc -l )
echo -e "\nRuntime for SAT was $runtime1 seconds.\n"
runtime_p=$( echo "$end_p - $start1" | bc -l )
echo -e "\nRuntime for explicit_gen_random_graph.py was $runtime_p seconds.\n"
runtime_solver=$( echo "$end1 - $end_p" | bc -l )
echo -e "\nRuntime for POPSAT solver was $runtime_solver seconds.\n"
