#!/bin/bash
# Auto Generate iscas.blif and run the DQBF solver
# Author: Arthur Nieh
# Date: 2025/10/11
# Usage: ./iscas.sh

instance=$1
FF_tokeep=$2
cut=$3
timelimit=$((60 * 60))

if [ -z "$instance" ]; then
    echo "Usage: $0 <iscas89_instance> <FF_tokeep> <cut>"
    exit 1
fi

if [ -z "$cut" ]; then
    echo "Usage: $0 <iscas89_instance> <FF_tokeep> <cut>"
    exit 1
fi

if [ -z "$FF_tokeep" ]; then
    echo "Usage: $0 <iscas89_instance> <FF_tokeep> <cut>"
    exit 1
fi

# Generate the blif file of the iscas89 benchmark
cd ./iscas89/
g++ -o gen_testcase gen_testcase.cpp
for i in {3..30}; do
    if [ ! -f ./sample/test_cases_$i.txt ]; then
        ./gen_testcase $i
    fi
done

# python3 simplify_bench.py "$instance" "$FF_tokeep"

# python3 bench_to_blif.py "${instance}_simplified"
python3 reduce_bench2blif.py "$instance" "$FF_tokeep" 0

start1=`date +%s.%N`
timeout 1h python3 explicit_gen_iscas.py "${instance}_simplified"
# this will generate iscas_graph.txt
end_p=`date +%s.%N`
# Run the SCIP ILP solver
echo -e "\nRun the SCIP ILP solver"
timeout 1h python3 maxcut_solver_scip.py ./sample/iscas_graph.txt "$cut"

end1=`date +%s.%N`

runtime1=$( echo "$end1 - $start1" | bc -l )
echo -e "\nRuntime for SAT was $runtime1 seconds.\n"
runtime_p=$( echo "$end_p - $start1" | bc -l )
echo -e "\nRuntime for explicit_gen_iscas.py was $runtime_p seconds.\n"
runtime_solver=$( echo "$end1 - $end_p" | bc -l )
echo -e "\nRuntime for SCIP solver was $runtime_solver seconds.\n"
