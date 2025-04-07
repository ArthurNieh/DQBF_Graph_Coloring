### This file is used to generate explicit graph of iscas benchmark circuits
## need file ./benchmarks/s{case}.bench
## need file ./benchmarks/s{case}.blif

from subprocess import check_output
import sys
import os
from itertools import product

sample_dir = '/home/arthur/course/sat/DQBF_Graph_Coloring/iscas89/sample/'
bench_dir = '/home/arthur/course/sat/DQBF_Graph_Coloring/iscas89/benchmarks/'
output_file = "iscas_graph.txt"
test_case_file = "test_cases.txt"
abc_script = "abc_script.sh"
abc_output = "abc_output.txt"

E = [] # List of edges

input_num = 0
FF_num = 0
total_states = 0

def parse_iscas_file(ins):
    global input_num, FF_num, total_states
    global bench_dir
    global sample_dir

    file_path = bench_dir + f"{ins}.bench"
    print(f"Parsing {file_path}...")

    with open(file_path, "r") as f:
        lines = f.readlines()
        for line in lines:
            spl = line.split()
            if len(spl) == 3:
                if spl[2] == "inputs":
                    input_num = int(spl[1])
                    continue
            elif len(spl) == 4:
                if spl[3] == "flipflops":
                    FF_num = int(spl[1])
                    total_states = 2 ** FF_num
                    break
    if FF_num == 0:
        print("Error: No flipflops found in the file.")
        exit(1)
    print(f"Input num: {input_num}")
    print(f"FF num: {FF_num}")
    return

def generate_test_cases():
    global input_num, FF_num

    with open(sample_dir + test_case_file, "w") as f:
        for state in product([0, 1], repeat=FF_num):
            st = "".join(str(x) for x in state)
            for input in product([0, 1], repeat=input_num):
                x = "".join(str(y) for y in input)
                f.write(f"{x}{st}\n")
    return

def gen_abc_script(ins):

    with open(sample_dir + abc_script, "w") as f:
        f.write(f"read {bench_dir}{ins}.blif\n")
        f.write("strash\n")
        f.write("sim -A " + sample_dir + test_case_file + " -v \n")
        f.write("quit\n")
    return

def exec_abc():
    os.system('cd /home/arthur/course/sat/DQBF_Graph_Coloring/')

    # out = check_output(['/home/arthur/program/abc/abc', '-f', f'{sample_dir}{abc_script}'])
    out = check_output(['/home/arthur/program/abc/abc', '-f', '/home/arthur/course/sat/DQBF_Graph_Coloring/iscas89/sample/abc_script.sh'])
    # print(out.decode('utf-8'))
    decoded = out.decode('utf-8')
    with open(sample_dir + abc_output, 'w') as f:
        f.write(decoded)
    
    return decoded

def gen_expicit(out):
    global E, FF_num

    for line in out.splitlines():
        if line.startswith('0') or line.startswith('1'):
            spl = line.split()
            if len(spl) == 2:
                a = int(spl[0][-FF_num:], base=2) + 1
                b = int(spl[1][-FF_num:], base=2) + 1
                if a == b:
                    continue
                if a > b:
                    E.append((b, a))
                else:
                    E.append((a, b))
                # duplicate edges will be removed later
        else:
            continue
    return

def print_stats():
    global E
    print("========Stats========")
    print(f"total edge num = {len(E)}")

def print_graph():
    global E
    print("========Graph========")
    for e in E:
        print(e[0], e[1])

def dump_graph():
    global E, total_states, output_file, sample_dir
    with open(sample_dir + output_file, "w") as f:
        f.write(f"p edge {total_states} {len(E)}\n")
        for e in E:
            f.write(f"e {e[0]} {e[1]}\n")

def remove_dup(x):
    # Remove duplicates from list while preserving order
    # This is a common Python idiom to remove duplicates
    # while maintaining the order of elements
  return list(dict.fromkeys(x))

if __name__ == "__main__":

    instance = sys.argv[1]
    parse_iscas_file(instance)
    generate_test_cases()
    gen_abc_script(instance)
    abc_output = exec_abc()
    gen_expicit(abc_output)
    
    E = remove_dup(E)
    E.sort(key = lambda x: (x[0], x[1])) # Sort the edges
    print_graph()
    dump_graph()
    print("\nExplicit Graph is generated successfully\n")
    print_stats()
