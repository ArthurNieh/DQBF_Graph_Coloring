### This file is used to generate explicit graph of iscas benchmark circuits
## need file ./benchmarks/s{case}.bench
## need file ./benchmarks/s{case}.blif

from subprocess import Popen, PIPE
import sys
import os
from itertools import product
import time
import argparse
from pathlib import Path

# Directory of *this* Python file
SCRIPT_DIR = Path(__file__).resolve().parent

# abc is in ../abc/ relative to this script
ABC_DIR = SCRIPT_DIR / ".." / "abc"
ABC_BIN = ABC_DIR / "abc"

SAMPLE_DIR = SCRIPT_DIR / ".." / "iscas89" / "sample"

# sample_dir = './sample/'

E = [] # List of edges

input_num = 0
FF_num = 0
total_states = 0

def parse_benchmark_file(file_path):
    print(f"Parsing {file_path}...")

    input_num = 0
    FF_num = 0
    in_inputs_block = False

    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Start of .inputs
            if line.startswith(".inputs"):
                in_inputs_block = True
                has_continuation = line.endswith("\\")

                # remove ".inputs" and trailing "\"
                content = line[len(".inputs"):].rstrip("\\").strip()
                if content:
                    input_num += len(content.split())

                if not has_continuation:
                    in_inputs_block = False
                continue

            # Continuation of .inputs
            if in_inputs_block:
                has_continuation = line.endswith("\\")
                content = line.rstrip("\\").strip()
                if content:
                    input_num += len(content.split())

                if not has_continuation:
                    in_inputs_block = False
                continue

            # Count latches
            # if line.startswith(".latch"):
            #     FF_num += 1

    # if FF_num == 0:
    #     print("Error: No flipflops found in the file.")
    #     exit(1)

    # total_states = 2 ** FF_num

    print(f"Input num: {input_num}")
    # print(f"FF num: {FF_num}")
    # print(f"Total states: {total_states}")

    return input_num

# def generate_test_cases():
#     global input_num, FF_num

#     if not os.path.exists(sample_dir):
#         os.makedirs(sample_dir)
#     if not os.path.exists(sample_dir + f"test_cases_{input_num+FF_num}.txt"):
#         os.system(f"./gen_testcase {input_num+FF_num}") 
#     return

def gen_abc_comb_script(readin_file, writeout_file):

    script = (
        f"read {readin_file}\n"
        "comb\n"
        "fraig\n"
        # "cleanup\n"
        f"write_blif {writeout_file}\n"
        "quit\n"
    )
    return script

def gen_abc_sim_script(input_file, test_case_file):

    script = (
        f"read {input_file}\n"
        "fraig\n"
        "strash\n"
        "time\n"
        f"sim -A {test_case_file} -v\n"
        "time\n"
        "quit\n"
    )
    return script

def exec_abc(script, abc_bin, abc_dir):
    p = Popen(
        [str(abc_bin)],
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        cwd=str(abc_dir),
        text=True
    )

    out, err = p.communicate(script)

    return out, err


def gen_expicit(out, FF_num, directed_flag):
    
    E = []

    for line in out.splitlines():
        if line.startswith('0') or line.startswith('1'):
            spl = line.split()
            if len(spl) == 2:
                a = int(spl[0][-FF_num:], base=2) + 1
                b = int(spl[1][-FF_num:], base=2) + 1
                if directed_flag:
                    E.append((a, b))
                else:
                    if a == b:
                        continue
                    elif a > b:
                        E.append((b, a))
                    else:
                        E.append((a, b))
                # duplicate edges will be removed later
        elif line.startswith('elapse'):
            print(line)
            continue
        else:
            continue
    return E

def print_stats(E):
    print("========Stats========")
    print(f"total edge num = {len(E)}")

def print_graph(E):
    print("========Graph========")
    for e in E:
        print(e[0], e[1])

def dump_graph(E, output_file, FF_num):
    total_states = 2 ** FF_num

    with open(output_file, "w") as f:
        f.write(f"p edge {total_states} {len(E)}\n")
        for e in E:
            f.write(f"e {e[0]} {e[1]}\n")

# def dump_graph_maxcut():
#     global E, total_states, output_file, sample_dir
#     with open(sample_dir + output_file, "w") as f:
#         f.write(f"{total_states} {len(E)}\n")
#         for e in E:
#             f.write(f"{e[0]} {e[1]} 1\n")

def remove_dup(x):
    # Remove duplicates from list while preserving order
    # This is a common Python idiom to remove duplicates
    # while maintaining the order of elements
  return list(dict.fromkeys(x))

# def gen_graph_visual():
#     from graphviz import Graph
#     from graphviz import Digraph
#     global E, instance, vflag
    
#     if vflag == "v":
#         g = Graph('G', filename='graph.gv')
#     elif vflag == "d":
#         g = Digraph('G', filename='graph.gv')
#     g.attr(rankdir='LR')
#     # g.attr(size='8,5')
#     g.attr('node', shape='circle')
#     g.attr('graph', ranksep='0.1')
#     g.attr('node', style='filled', fillcolor='lightgrey')
#     g.attr('edge', color='black')
#     g.attr('node', fillcolor='lightblue')

#     for e in E:
#         g.edge(str(e[0]), str(e[1]), color='black')
    
#     if vflag == "v":
#         g.render(filename=f"{instance}_u", format='png', cleanup=True)
#     elif vflag == "d":
#         g.render(filename=f"{instance}_d", format='png', cleanup=True)
#     # g.view()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Generate explicit graph from SMV benchmark.')
    parser.add_argument('-b', '--benchmark', type=str, required=True, help='Path to the benchmark file (e.g., ./benchmarks/s{case}.bench)')
    parser.add_argument('--ff', type=int, required=True, help='Number of flip-flops in the benchmark')
    parser.add_argument('--explicit_blif', type=str, default='iscas_graph.txt', help='Output file for the explicit blif graph')
    parser.add_argument('--explicit_graph_output', type=str, default='iscas_explicit_graph.txt', help='Output file for the explicit graph edges')
    parser.add_argument('-d', '--directed', action='store_true', help='Generate directed graph')
    
    args = parser.parse_args()

    benchmark_file = args.benchmark
    FF_num = args.ff
    explicit_blif = args.explicit_blif
    explicit_graph_output = args.explicit_graph_output
    directed_flag = args.directed

    start_time = time.time()
    # Step 1: Transform to combinational BLIF
    script = gen_abc_comb_script(benchmark_file, explicit_blif)
    abc_output, abc_error = exec_abc(script, ABC_BIN, ABC_DIR)
    
    # print(abc_output)
    
    # Step 2: Parse benchmark to get input_num
    input_num = parse_benchmark_file(explicit_blif)

    if input_num > 29:
        print("Error: The total number of inputs exceeds 29. Exiting.")
        sys.exit(1)

    test_case_file = f"{SAMPLE_DIR}/test_cases_{input_num}.txt"
    
    # Step 3: Run ABC simulation
    script = gen_abc_sim_script(explicit_blif, test_case_file)
    gen_script_time = time.time()
    abc_output, abc_error = exec_abc(script, ABC_BIN, ABC_DIR)

    # if abc_error:
    #     print("ABC Error:", abc_error)
    # print(abc_output)
# print execution time of each function
    # instance = sys.argv[1]
    # vflag = ''
    # if len(sys.argv) == 3:
    #     vflag = sys.argv[2].strip('-')
    # if vflag == "v" or vflag == "d":
    #     print("Verbose mode enabled")
    # elif vflag == "e":
    #     print("Edge mode enabled")
    # elif vflag == "m":
    #     print("Maxcut mode enabled")
    # else:
    #     print("Verbose mode disabled")

    # start_time = time.time()
    # parse_benchmark_file(instance)
    # parse_file_time = time.time()
    # print(f"Parse time: {parse_file_time - start_time:.2f} seconds")
    
    # generate_test_cases()
    # gen_test_time = time.time()
    # print(f"Generate test case time: {gen_test_time - parse_file_time:.2f} seconds")

    # gen_abc_script(instance)
    # gen_script_time = time.time()
    # print(f"Generate abc script time: {gen_script_time - gen_test_time:.2f} seconds")
    
    # abc_output = exec_abc()
    exec_abc_time = time.time()
    print(f"Exec abc time: {exec_abc_time - gen_script_time:.2f} seconds")

    E = gen_expicit(abc_output, FF_num, directed_flag)
    gen_explicit_time = time.time()
    print(f"Generate explicit graph time: {gen_explicit_time - exec_abc_time:.2f} seconds")
    
    E = remove_dup(E)
    remove_dup_time = time.time()
    print(f"Remove duplicate time: {remove_dup_time - gen_explicit_time:.2f} seconds")
    # E.sort(key = lambda x: (x[0], x[1])) # Sort the edges
    # print_graph()

    # if vflag == "e":
    #     E = gen_line_graph(E)
    
    # if vflag == "m":
    #     dump_graph_maxcut()
    # else:
    dump_graph(E, explicit_graph_output, FF_num)
    
    dump_time = time.time()
    print(f"Dump graph time: {dump_time - remove_dup_time:.2f} seconds")
    print(f"Total time: {dump_time - start_time:.2f} seconds")
    print("\nExplicit Graph is generated successfully\n")
    print_stats(E)

    # if vflag == "v" or vflag == "d":
    #     gen_graph_visual()
