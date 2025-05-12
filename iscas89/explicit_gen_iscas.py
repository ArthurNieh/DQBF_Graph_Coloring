### This file is used to generate explicit graph of iscas benchmark circuits
## need file ./benchmarks/s{case}.bench
## need file ./benchmarks/s{case}.blif

from subprocess import check_output
import sys
import os
from itertools import product
import time

iscas_dir = './'
sample_dir = './sample/'
bench_dir = './benchmarks/'
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

    # with open(sample_dir + test_case_file, "w") as f:
        # for state in product([0, 1], repeat=FF_num):
        #     st = "".join(str(x) for x in state)
        #     for input in product([0, 1], repeat=input_num):
        #         x = "".join(str(y) for y in input)
        #         f.write(f"{x}{st}\n")
        # for test_case in product([0, 1], repeat=input_num + FF_num):
        #     x = "".join(str(y) for y in test_case)
        #     f.write(f"{x}\n")
        # f.writelines(
        #     "".join(map(str, test_case)) + "\n"
        #     for test_case in product([0, 1], repeat=input_num + FF_num)
        # )
    os.system(f"./gen_testcase {input_num+FF_num}") 
    return

def gen_abc_script(ins):

    with open(sample_dir + abc_script, "w") as f:
        f.write(f"read ../iscas89/benchmarks/{ins}.blif\n")
        f.write("strash\n")
        f.write("time\n")
        f.write("sim -A ../iscas89/sample/" + test_case_file + " -v \n")
        f.write("time\n")
        f.write("quit\n")
    return

def exec_abc():
    # os.system('cd /home/arthur/course/sat/DQBF_Graph_Coloring/')

    out = check_output(['../abc/abc', '-f', f'{sample_dir}{abc_script}'])
    # out = check_output(['/home/arthur/program/abc/abc', '-f', '/home/arthur/course/sat/DQBF_Graph_Coloring/iscas89/sample/abc_script.sh'])
    # print(out.decode('utf-8'))
    decoded = out.decode('utf-8')
    # with open(sample_dir + abc_output, 'w') as f:
    #     f.write(decoded)
    
    return decoded

def gen_expicit(out):
    global E, FF_num, vflag

    for line in out.splitlines():
        if line.startswith('0') or line.startswith('1'):
            spl = line.split()
            if len(spl) == 2:
                a = int(spl[0][-FF_num:], base=2) + 1
                b = int(spl[1][-FF_num:], base=2) + 1
                if vflag == "d":
                    E.append((a, b))
                else:
                    if a == b:
                        continue
                    if a > b:
                        E.append((b, a))
                    else:
                        E.append((a, b))
                # duplicate edges will be removed later
        elif line.startswith('elapse'):
            print(line)
            continue
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

def gen_graph_visual():
    from graphviz import Graph
    from graphviz import Digraph
    global E, instance, vflag
    
    if vflag == "v":
        g = Graph('G', filename='graph.gv')
    elif vflag == "d":
        g = Digraph('G', filename='graph.gv')
    g.attr(rankdir='LR')
    # g.attr(size='8,5')
    g.attr('node', shape='circle')
    g.attr('graph', ranksep='0.1')
    g.attr('node', style='filled', fillcolor='lightgrey')
    g.attr('edge', color='black')
    g.attr('node', fillcolor='lightblue')

    for e in E:
        g.edge(str(e[0]), str(e[1]), color='black')
    
    if vflag == "v":
        g.render(filename=f"{instance}_u", format='png', cleanup=True)
    elif vflag == "d":
        g.render(filename=f"{instance}_d", format='png', cleanup=True)
    # g.view()

if __name__ == "__main__":

# print execution time of each function
    instance = sys.argv[1]
    vflag = ''
    if len(sys.argv) == 3:
        vflag = sys.argv[2].strip('-')
    if vflag == "v" or vflag == "d":
        print("Verbose mode enabled")
    else:
        print("Verbose mode disabled")
    start_time = time.time()
    parse_iscas_file(instance)
    parse_file_time = time.time()
    print(f"Parse time: {parse_file_time - start_time:.2f} seconds")
    
    generate_test_cases()
    gen_test_time = time.time()
    print(f"Generate test case time: {gen_test_time - parse_file_time:.2f} seconds")
    
    gen_abc_script(instance)
    gen_script_time = time.time()
    print(f"Generate abc script time: {gen_script_time - gen_test_time:.2f} seconds")
    
    abc_output = exec_abc()
    exec_abc_time = time.time()
    print(f"Exec abc time: {exec_abc_time - gen_script_time:.2f} seconds")

    gen_expicit(abc_output)
    gen_explicit_time = time.time()
    print(f"Generate explicit graph time: {gen_explicit_time - exec_abc_time:.2f} seconds")
    
    E = remove_dup(E)
    remove_dup_time = time.time()
    print(f"Remove duplicate time: {remove_dup_time - gen_explicit_time:.2f} seconds")
    # E.sort(key = lambda x: (x[0], x[1])) # Sort the edges
    # print_graph()
    dump_graph()
    dump_time = time.time()
    print(f"Dump graph time: {dump_time - remove_dup_time:.2f} seconds")
    print(f"Total time: {dump_time - start_time:.2f} seconds")
    print("\nExplicit Graph is generated successfully\n")
    print_stats()

    if vflag == "v" or vflag == "d":
        gen_graph_visual()
