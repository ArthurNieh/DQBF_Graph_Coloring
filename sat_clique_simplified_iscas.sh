#!/bin/bash
# Auto Generate iscas.blif and run the DQBF solver
# Author: Arthur Nieh
# Date: 2025/4/7
# Usage: ./iscas.sh

instance=$1
Clique_size=$2
FF_tokeep=$3
timelimit=$((60 * 60))

if [ -z "$instance" ]; then
    echo "Usage: $0 <iscas89_instance> <Clique_size> <FF_tokeep>"
    exit 1
fi

if [ -z "$Clique_size" ]; then
    echo "Usage: $0 <iscas89_instance> <Clique_size> <FF_tokeep>"
    exit 1
fi

if [ -z "$FF_tokeep" ]; then
    echo "Usage: $0 <iscas89_instance> <Clique_size> <FF_tokeep>"
    exit 1
fi

# Generate the blif file of the iscas89 benchmark
cd ./iscas89/
g++ -o gen_testcase gen_testcase.cpp

# python3 simplify_bench.py "$instance" "$FF_tokeep"

# python3 bench_to_blif.py "${instance}_simplified"
python3 reduce_bench2blif.py "$instance" "$FF_tokeep" 100

start1=`date +%s.%N`
timeout 1h python3 explicit_gen_iscas.py "${instance}_simplified"
# this will generate iscas_graph.txt
end_p=`date +%s.%N`
# Run the PYSAT solver
echo -e "\nRun the PYSAT solver"
python3 clique_sat_solver.py -k $Clique_size --graph_file ./sample/iscas_graph.txt

end1=`date +%s.%N`

runtime1=$( echo "$end1 - $start1" | bc -l )
echo -e "\nRuntime for SAT was $runtime1 seconds.\n"
runtime_p=$( echo "$end_p - $start1" | bc -l )
echo -e "\nRuntime for explicit_gen_iscas.py was $runtime_p seconds.\n"
runtime_solver=$( echo "$end1 - $end_p" | bc -l )
echo -e "\nRuntime for PYSAT solver was $runtime_solver seconds.\n"
