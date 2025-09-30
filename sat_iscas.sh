#!/bin/bash
# Auto Generate iscas.blif and run the DQBF solver
# Author: Arthur Nieh
# Date: 2025/4/7
# Usage: ./iscas.sh

instance=$1
timelimit=$((5 * 24 * 60 * 60))
if [ -z "$instance" ]; then
    echo "Usage: $0 <iscas89_instance>"
    exit 1
fi

# Generate the blif file of the iscas89 benchmark
cd ./iscas89/
g++ -o gen_testcase gen_testcase.cpp
for i in {3..50}; do
    if [ ! -f ./sample/test_cases_$i.txt ]; then
        ./gen_testcase $i
    fi
done
python3 bench_to_blif.py "$instance"

start1=`date +%s.%N`
python3 explicit_gen_iscas.py "$instance"
# this will generate iscas_graph.txt
end_p=`date +%s.%N`
# Run the POPSAT solver
# echo "######################################################"
echo -e "\nRun the POPSAT solver"
cd ../popsatgcpbcp/source
python3 main.py "--instance=../../iscas89/sample/iscas_graph.txt" "--model=POP-S" "--timelimit=$timelimit"

end1=`date +%s.%N`

echo "######################################################"

runtime1=$( echo "$end1 - $start1" | bc -l )
echo -e "\nRuntime for SAT was $runtime1 seconds.\n"
runtime_p=$( echo "$end_p - $start1" | bc -l )
echo -e "\nRuntime for explicit_gen_iscas.py was $runtime_p seconds.\n"
