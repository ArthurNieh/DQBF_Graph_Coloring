### This file is used to generate explicit graph of iscas benchmark circuits
## need file ./benchmarks/s{case}.bench
## need file ./benchmarks/s{case}.blif

from subprocess import check_output
import sys
import os
from itertools import product
import time
import argparse

def generate_test_cases(num):
    if not os.path.exists(sample_dir):
        os.makedirs(sample_dir)
    if not os.path.exists(sample_dir + f"test_cases_{num}.txt"):
        os.system(f"./gen_testcase {num}") 
    return

def gen_abc_script(num, script_file="abc_script.sh", graph_file=None):
    test_case_file = f"test_cases_{2*num}.txt"

    with open(script_file, "w") as f:
        f.write(f"read {graph_file}\n")
        f.write("strash\n")
        f.write("time\n")
        f.write("sim -A ../iscas89/sample/" + test_case_file + " -v \n")
        f.write("time\n")
        f.write("quit\n")
    return

def exec_abc(script_file="abc_script.sh"):
    # os.system('cd /home/arthur/course/sat/DQBF_Graph_Coloring/')

    out = check_output(['../abc/abc', '-f', f'{script_file}'])
    # out = check_output(['/home/arthur/program/abc/abc', '-f', '/home/arthur/course/sat/DQBF_Graph_Coloring/iscas89/sample/abc_script.sh'])
    # print(out.decode('utf-8'))
    decoded = out.decode('utf-8')
    # with open(sample_dir + abc_output, 'w') as f:
    #     f.write(decoded)

    return decoded

def gen_explicit(out, E, n, directed=False):

    for line in out.splitlines():
        # print(line)
        if line.startswith('0') or line.startswith('1'):
            spl = line.split()
            if len(spl) == 2:
                if int(spl[1], base=2) == 0:
                    continue
                a = int(spl[0][:n], base=2) + 1
                b = int(spl[0][-n:], base=2) + 1
                # print(f"Edge: {a} {b}")
                if directed:
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

def print_stats(E):
    print("========Stats========")
    print(f"total edge num = {len(E)}")

def print_graph(E):
    print("========Graph========")
    for e in E:
        print(e[0], e[1])

def dump_graph(E, n, file_name="iscas_graph.txt"):
    with open(file_name, "w") as f:
        f.write(f"p edge {2**n} {len(E)}\n")
        for e in E:
            f.write(f"e {e[0]} {e[1]}\n")

def remove_dup(x):
    # Remove duplicates from list while preserving order
    # This is a common Python idiom to remove duplicates
    # while maintaining the order of elements
  return list(dict.fromkeys(x))

def gen_graph_visual(E, directed=False):
    from graphviz import Graph
    from graphviz import Digraph
        
    if directed:
        g = Digraph('G', filename='graph.gv')
    else:
        g = Graph('G', filename='graph.gv')
    
    g.attr(rankdir='LR')
    # g.attr(size='8,5')
    g.attr('node', shape='circle')
    g.attr('graph', ranksep='0.1')
    g.attr('node', style='filled', fillcolor='lightgrey')
    g.attr('edge', color='black')
    g.attr('node', fillcolor='lightblue')

    for e in E:
        g.edge(str(e[0]), str(e[1]), color='black')
    
    if not directed:
        g.render(filename=f"random_n{n}_u", format='png', cleanup=True)
    else:
        g.render(filename=f"random_n{n}_d", format='png', cleanup=True)
    # g.view()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate explicit graph from random graph instance.')
    parser.add_argument('-n', type=int, help='Size of the hash function (number of bits).', required=True)
    parser.add_argument('-d', action='store_true', help='Generate directed graph (default is undirected).')
    parser.add_argument('--trial', '-t', type=int, default=0, help='Trial number (default is 0).')
    parser.add_argument('--png', action='store_true', help='Generate graph visualization in PNG format.')
    args = parser.parse_args()

    n = args.n

    directed = args.d

    png = args.png

    trial = args.trial

    iscas_dir = './'
    sample_dir = './sample/'
    bench_dir = './benchmarks/'
    output_file = "iscas_graph.txt"
    abc_script = "abc_script.sh"

    random_graph_file = f"./graphs/random_graph_n{n}_trial{trial}_graph.blif"
    output_graph_file = f"./sample/random_graph_n{n}_trial{trial}_explicit.txt"
    E = [] # List of edges

    start_time = time.time()
    gen_abc_script(n, abc_script, graph_file=random_graph_file)
    gen_script_time = time.time()
    print(f"Generate abc script time: {gen_script_time - start_time:.2f} seconds")

    abc_output = exec_abc(abc_script)
    exec_abc_time = time.time()
    print(f"Exec abc time: {exec_abc_time - gen_script_time:.2f} seconds")
    
    gen_explicit(abc_output, E, n, directed)
    gen_explicit_time = time.time()
    print(f"Generate explicit graph time: {gen_explicit_time - exec_abc_time:.2f} seconds")
    
    E = remove_dup(E)
    remove_dup_time = time.time()
    print(f"Remove duplicate time: {remove_dup_time - gen_explicit_time:.2f} seconds")
    # E.sort(key = lambda x: (x[0], x[1])) # Sort the edges
    # print_graph(E)

    dump_graph(E, n, sample_dir + output_file)
    dump_time = time.time()
    print(f"Dump graph time: {dump_time - remove_dup_time:.2f} seconds")
    print(f"Total time: {dump_time - start_time:.2f} seconds")
    print("\nExplicit Graph is generated successfully\n")
    print_stats(E)

    if png:
        gen_graph_visual(E, directed)
