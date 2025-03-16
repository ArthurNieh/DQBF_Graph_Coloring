### This file is used to generate explicit graph of lsfr

from math import sqrt
import random
from config import *
# In config.py, we have:
# N  # digit number
# colorability = 2 or 3
# xor_gates = [2, 4, 10] # digit of xor gates

output_file = "./sample/lsfr_graph.txt"
E = [] # List of edges
total_states = 2**N

def generate_mask():
    global N, xor_gates
    mask1 = 0
    for i in xor_gates:
        mask1 |= 1 << (N-i)
    mask2 = 0
    for i in range(N):
        mask2 |= 1 << i
    return mask1, mask2

def next_state(state, mask1):
    next_state = state >> 1
    next_state |= (bin(state & mask1).count('1') % 2) << (N-1)
    return next_state

def generate_lsfr():
    global N, xor_gates, E, total_states

    mask1, mask2 = generate_mask()
    # For each state
    for i in range(total_states):
        E.append((i, next_state(i, mask1)))

def check_xor_gates():
    global N, xor_gates
    for i in xor_gates:
        if i > N:
            print("Invalid xor gate")
            return False
    return True

def print_stats():
    global N, E
    print("========Stats========")
    print(f"N = {N}")
    print(f"total edge num = {len(E)}")

def print_graph():
    global E
    print("========Graph========")
    for e in E:
        print(e[0], e[1])

def dump_graph():
    global E, total_states, output_file
    with open(output_file, "w") as f:
        f.write(f"p edge {total_states} {len(E)}\n")
        for e in E:
            f.write(f"e {e[0]} {e[1]}\n")

if __name__ == "__main__":

    if not check_xor_gates():
        exit(1)

    generate_lsfr()
    # E.sort(key = lambda x: (x[0], x[1])) # Sort the edges
    # print_graph()
    dump_graph()
    print("\nExplicit Graph is generated successfully\n")
    print_stats()
