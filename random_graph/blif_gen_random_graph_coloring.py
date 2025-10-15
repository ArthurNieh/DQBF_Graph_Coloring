# Description: Generate blif file for random graph with coloring constraints
#
# Modified from sudoku/blif_gen_auto.py
# This script generates a blif file for ISCAS89 benchmarks with coloring constraints.
# 
# Author: Arthur Nieh
# Date: 2025-10-15
# Reference: https://www.notion.so/DQBF-on-Graphs-1ac570d5afa980eca2deef656ebd8b68?pvs=4

import sys
import math
import argparse
import random

def add_main_model(u_num, c_num):

### I/O parameters
    blif_lines.append(f".model random{u_num}\n")
    blif_lines.append(".inputs ")
    blif_lines.extend([f"u{i} " for i in range(u_num)])
    blif_lines.extend([f"v{i} " for i in range(u_num)])
    blif_lines.extend([f"c{i} " for i in range(c_num)])
    blif_lines.extend([f"d{i} " for i in range(c_num)])
    blif_lines.append("\n")
    blif_lines.append(".outputs f\n")

### Graph subcircuit
    blif_lines.append(".subckt graph ")
    blif_lines.extend([f"U{i}=u{i} " for i in range(u_num)])
    blif_lines.extend([f"V{i}=v{i} " for i in range(u_num)])
    blif_lines.append("E=e0\n")

    # blif_lines.append(".subckt graph ")
    # blif_lines.extend([f"U{i}=v{i} " for i in range(u_num)])
    # blif_lines.extend([f"V{i}=u{i} " for i in range(u_num)])
    # blif_lines.append("E=e2\n")

    # blif_lines.append(".subckt or2 I0=e1 I1=e2 O=e0\n")

### U, V not equal subcircuit
    blif_lines.append(f".subckt UneqV{u_num} ")
    blif_lines.extend([f"U{i}=u{i} " for i in range(u_num)])
    blif_lines.extend([f"V{i}=v{i} " for i in range(u_num)])
    blif_lines.append("O_equal=uvnotsame\n")

    blif_lines.append(".subckt and2 I0=e0 I1=uvnotsame O=e\n")

    blif_lines.append(".subckt not I=uvnotsame O=uvsame\n")

### Color not equal subcircuit
    blif_lines.extend([f".subckt UneqV{c_num} "])
    blif_lines.extend([f"U{i}=c{i} " for i in range(c_num)])
    blif_lines.extend([f"V{i}=d{i} " for i in range(c_num)])
    blif_lines.extend(["O_equal=colornotsame\n"])

    blif_lines.append(".subckt not I=colornotsame O=colorsame\n")

### Binary color subcircuit
    if c_num > 1:
        blif_lines.extend([".subckt fit_color_limit "] + [f"I{i}=c{i} " for i in range(c_num)] + ["G=clessthan\n"])
        blif_lines.extend([".subckt fit_color_limit "] + [f"I{i}=d{i} " for i in range(c_num)] + ["G=dlessthan\n"])
        blif_lines.extend([".subckt and2 I0=clessthan I1=dlessthan O=colorencode\n"])
    elif c_num == 1:
        blif_lines.append(".names colorencode\n1\n")
    else:
        print("Error: c_num should be at least 1")
        sys.exit(1)

### Main circuit
    blif_lines.append(".subckt imply I0=e I1=colornotsame O=phi1\n")

    blif_lines.append(".subckt imply I0=uvsame I1=colorsame O=phi2\n")

    blif_lines.append(".subckt and2 I0=phi1 I1=phi2 O=phi12\n")
    blif_lines.append(".subckt and2 I0=colorencode I1=phi12 O=f\n")

    blif_lines.append(".end\n\n")

def add_simple_implicit_graph(blif_lines, graph_file, u_num, output_graph_file):
    if "\n.model graph\n" in blif_lines:
        print("[Warning] model graph already exists.")
        return
    
    A_b = []
    with open(graph_file, 'r') as f:
        for line in f:
            A_b.extend([int(x) for x in line.strip().split(',')])

    assert (len(A_b) == 2*u_num + 1), f"Error: Graph file should contain {2*u_num + 1} elements, but got {len(A_b)}"

    blif_graph = []

    blif_graph.append("\n.model graph\n")
    blif_graph.append(".inputs ")
    blif_graph.extend([f"U{i} " for i in range(u_num)])
    blif_graph.extend([f"V{i} " for i in range(u_num)])
    blif_graph.append("\n")
    blif_graph.append(".outputs E\n")

    # Create a constant-1 signal
    blif_graph.append(f".names CONST1\n1\n")

    queue = []
    queue2 = [] # queue2 for symmetric edges

    for j in range(2 * u_num):
        if A_b[j] == 1:
            if j < u_num:
                inp = f"U{j}"
                inp2 = f"V{j}"
            else:
                inp = f"V{j - u_num}"
                inp2 = f"U{j - u_num}"
            queue.append(inp)
            queue2.append(inp2)
    if A_b[-1] == 1:
        queue.append("CONST1")
        queue2.append("CONST1")
    
    while(len(queue) > 1):
        a = queue.pop(0)
        b = queue.pop(0)
        new_signal = f"G{len(queue)}"
        blif_graph.append(f".subckt xor2 I0={a} I1={b} O={new_signal}\n")
        queue.append(new_signal)
    final_output = queue[0]

    while(len(queue2) > 1):
        a = queue2.pop(0)
        b = queue2.pop(0)
        new_signal = f"Gs{len(queue2)}"
        blif_graph.append(f".subckt xor2 I0={a} I1={b} O={new_signal}\n")
        queue2.append(new_signal)
    final_output2 = queue2[0]

    blif_graph.append(f".subckt or2 I0={final_output} I1={final_output2} O=E\n")
    blif_graph.append(".end\n\n")

    blif_lines.extend(blif_graph)

    add_nequiv_gate(blif_graph)
    # add_and_num(blif_graph, 2)
    add_or_num(blif_graph, 2)

    with open(output_graph_file, "w") as f:
        f.writelines(blif_graph)

    return

def add_implicit_graph(blif_lines, matrix_A_file, vector_b_file, u_num, output_graph_file):

    if "\n.model graph\n" in blif_lines:
        print("[Warning] model graph already exists.")
        return
    
    # Read in matrix A and vector b
    A = []
    with open(matrix_A_file, 'r') as f:
        for line in f:
            row = [int(x) for x in line.strip().split(',')]
            A.append(row)

    b = []
    with open(vector_b_file, 'r') as f:
        for line in f:
            b.extend([int(x) for x in line.strip().split(',')])

    # check whether A is of size (2*u_num) x (2*u_num)
    if len(A) != 2*u_num or any(len(row) != 2*u_num for row in A):
        print(f"Error: Matrix A should be of size {(2*u_num)} x {(2*u_num)}")
        print(f"Actual size: {len(A)} x {len(A[0]) if A else 0}")
        sys.exit(1)
    if len(b) != 2*u_num:
        print(f"Error: Vector b should be of length {2*u_num}")
        print(f"Actual length: {len(b)}")
        sys.exit(1)

    blif_graph = []

    blif_graph.append("\n.model graph\n")
    blif_graph.append(".inputs ")
    blif_graph.extend([f"U{i} " for i in range(u_num)])
    blif_graph.extend([f"V{i} " for i in range(u_num)])
    blif_graph.append("\n")
    blif_graph.append(".outputs E\n")

    # create a constant-1 signal
    blif_graph.append(f".names CONST1\n1\n")

    for i, row in enumerate(A):
        count = 0

        # Initialize accumulator A{i}0 = constant 0
        blif_graph.append(f".names A{i}{count}\n")
        blif_graph.append("0\n")

        # XOR all selected inputs in this row
        for j in range(2 * u_num):
            if row[j] == 1:
                if j < u_num:
                    inp = f"U{j}"
                else:
                    inp = f"V{j - u_num}"

                blif_graph.append(
                    f".subckt xor2 I0={inp} I1=A{i}{count} O=A{i}{count+1}\n"
                )
                count += 1

        # Add bias term b[i] if needed
        if b[i] == 1:
            blif_graph.append(
                f".subckt xor2 I0=CONST1 I1=A{i}{count} O=A{i}{count+1}\n"
            )
            count += 1

        # Define the final output bit h_i(x)
        blif_graph.append(f".names A{i}{count} H{i}\n1 1\n")
    
    # ============================
    # Combine all H_i into final E
    # ============================

    queue = [f"H{i}" for i in range(len(A))]
    prob = {f"H{i}": 0.5 for i in range(len(A))}  # assume each H_i has prob 1/2

    gate_count = 0
    while len(queue) > 1:
        a = queue.pop(0)
        b = queue.pop(0)
        pa, pb = prob[a], prob[b]

        por = pa + pb - pa * pb
        pand = pa * pb

        central_prob = 0.1

        # Randomly choose AND or OR, but try to keep probability towards central_prob
        if abs(por - central_prob) <= abs(pand - central_prob):
            gate_type = "or2"
        elif abs(por - central_prob) > abs(pand - central_prob):
            gate_type = "and2"
        else:
            print("[RANDOM] Equal distance to central_prob, randomly choose AND/OR")
            gate_type = random.choice(["and2", "or2"])
        new_signal = f"G{gate_count}"
        gate_count += 1

        blif_graph.append(f".subckt {gate_type} I0={a} I1={b} O={new_signal}\n")

        # Compute probability of output = 1
        if gate_type == "and2":
            p_out = pand
        else:  # or2
            p_out = por
        # print(f"[Info] Combining {a} (p={pa:.4f}) and {b} (p={pb:.4f}) with {gate_type}, new signal {new_signal} has prob={p_out:.4f}")
        prob[new_signal] = p_out
        queue.append(new_signal)

    # The remaining element in queue is the final output
    final_output = queue[0]
    blif_graph.append(f".names {final_output} E\n1 1\n")

    print(f"[Info] Final output E has estimated prob={prob[final_output]:.4f}")
    blif_graph.append(".end\n\n")
    
    blif_lines.extend(blif_graph)

    add_nequiv_gate(blif_graph)
    add_and_num(blif_graph, 2)
    add_or_num(blif_graph, 2)

    with open(output_graph_file, "w") as f:
        f.writelines(blif_graph)
    return

def add_1_comparator(blif_lines):
    # G = 1 if A > B
    # C = 1 if A = B
    # E = 1 if A = B in the significant bit
    if ".model comparator\n" in blif_lines:
        return
    blif_lines.append(".model comparator\n")
    blif_lines.append(".inputs A B E\n")
    blif_lines.append(".outputs G C\n")
    blif_lines.append(".names A B E G\n")
    blif_lines.append("101 1\n")
    blif_lines.append(".names A B E C\n")
    blif_lines.append("111 1\n")
    blif_lines.append("001 1\n")
    blif_lines.append(".end\n\n")

def add_fit_color_limit(blif_lines, c_limit, c_num):
    if c_limit <= 0 or c_limit > math.pow(2, c_num):
        print("Error: c_limit should be greater than 0 and less than c_num")
        print(f"c_limit: {c_limit}, c_num: {c_num}")
        sys.exit(1)
    b_c_limit = bin(c_limit-1)[2:]
    b_c_limit = b_c_limit.zfill(c_num)
    print(f"c_limit: {b_c_limit}")

    add_n_comparator(blif_lines, c_num)

    blif_lines.append(".model fit_color_limit\n")
    blif_lines.append(".inputs ")
    for i in range(c_num):
        blif_lines.append(f"I{i} ")
    blif_lines.append("\n")
    blif_lines.append(".outputs G\n")

    # set C[i] = b_c_limit[-i-1]
    for i in range(c_num):
        blif_lines.append(f".names C{i}\n")
        blif_lines.append(f"{b_c_limit[-i-1]}\n")
        print(f"C{i}={b_c_limit[-i-1]}")
    
    # compare, if C >= I, G = 1
    blif_lines.append(f".subckt comparator{c_num} ")
    for i in range(c_num):
        blif_lines.append(f"A{i}=C{i} ")
    for i in range(c_num):
        blif_lines.append(f"B{i}=I{i} ")
    blif_lines.append("G=G\n")

    blif_lines.append(".end\n\n")

def add_n_comparator(blif_lines, num):
    
    if f".model comparator{num}\n" in blif_lines:
        return
    
    add_1_comparator(blif_lines)
    add_or_num(blif_lines, num)
    
    # G = 1 if A >= B
    blif_lines.append(f".model comparator{num}\n")
    blif_lines.append(".inputs ")
    for i in range(num):
        blif_lines.append(f"A{i} ")
    for i in range(num):
        blif_lines.append(f"B{i} ")
    blif_lines.append("\n")
    blif_lines.append(".outputs G\n")
    
    # set C_num = 1
    blif_lines.append(f".names C{num}\n")
    blif_lines.append("1\n")

    for i in range(num-1, -1, -1):
        blif_lines.append(f".subckt comparator A=A{i} B=B{i} E=C{i+1} G=G{i} C=C{i}\n")
    blif_lines.append(f".subckt or{num}")
    for i in range(num):
        blif_lines.append(f" I{i}=G{i}")
    blif_lines.append(" O=o1\n")
    blif_lines.append(".subckt or2 I0=o1 I1=C0 O=G\n")

    blif_lines.append(".end\n\n")

def add_1_adder(blif_lines):
    # A + B = S, C_out
    if ".model adder\n" in blif_lines:
        return
    
    blif_lines.append(".model adder\n")
    blif_lines.append(".inputs A B C_in\n")
    blif_lines.append(".outputs S C_out\n")
    blif_lines.append(".names A B C_in S\n")
    # blif_lines.append("000 0\n")
    blif_lines.append("001 1\n")
    blif_lines.append("010 1\n")
    # blif_lines.append("011 0\n")
    blif_lines.append("100 1\n")
    # blif_lines.append("101 0\n")
    # blif_lines.append("110 0\n")
    blif_lines.append("111 1\n")
    
    blif_lines.append(".names A B C_in C_out\n")
    # blif_lines.append("000 0\n")
    # blif_lines.append("001 0\n")
    # blif_lines.append("010 0\n")
    blif_lines.append("011 1\n")
    # blif_lines.append("100 0\n")
    blif_lines.append("101 1\n")
    blif_lines.append("110 1\n")
    blif_lines.append("111 1\n")

    blif_lines.append(".end\n\n")

def add_n_adder(blif_lines, num):
    # A + B = S, do a mod sum, no addition bit
    add_1_adder(blif_lines)

    if f".model adder{num}\n" in blif_lines:
        return
    
    blif_lines.append(f".model adder{num}\n")
    blif_lines.append(".inputs ")
    for i in range(num):
        blif_lines.append(f"A{i} ")
    for i in range(num):
        blif_lines.append(f"B{i} ")
    blif_lines.append("\n.outputs ")
    for i in range(num):
        blif_lines.append(f"S{i} ")
    blif_lines.append("\n")

    # set C_num = 0
    blif_lines.append(f".names C0\n")
    blif_lines.append("0\n")

    for i in range(0, num):
        blif_lines.append(f".subckt adder A=A{i} B=B{i} C_in=C{i} S=S{i} C_out=C{i+1}\n")

    blif_lines.append(".end\n\n")

def add_is_0(blif_lines, num):
    if f".model is_zero\n" in blif_lines:
        return

    blif_lines.append(".model is_zero\n")
    blif_lines.append(".inputs ")
    for i in range(num):
        blif_lines.append(f"I{i} ")
    blif_lines.append("\n.outputs O\n")
    blif_lines.append(".names ")
    for i in range(num):
        blif_lines.append(f"I{i} ")
    blif_lines.append("O\n")
    blif_lines.append("0" * num + " 1\n")
    blif_lines.append(".end\n\n")

### All fundamental gates
def add_not_gate(blif_lines):
    if ".model not\n" in blif_lines:
        return
    blif_lines.append(".model not\n")
    blif_lines.append(".inputs I\n")
    blif_lines.append(".outputs O\n")
    blif_lines.append(".names I O\n")
    blif_lines.append("0 1\n")
    blif_lines.append(".end\n\n")
    return

def add_imply_gate(blif_lines):
    if ".model imply\n" in blif_lines:
        return
    blif_lines.append(".model imply\n")
    blif_lines.append(".inputs I0 I1\n")
    blif_lines.append(".outputs O\n")
    blif_lines.append(".names I0 I1 O\n")
    blif_lines.append("0- 1\n")
    blif_lines.append("-1 1\n")
    blif_lines.append(".end\n\n")
    return

def add_equiv_gate(blif_lines):
    if ".model equiv\n" in blif_lines:
        return
    blif_lines.append(".model equiv\n")
    blif_lines.append(".inputs I0 I1\n")
    blif_lines.append(".outputs O\n")
    blif_lines.append(".names I0 I1 O\n")
    blif_lines.append("11 1\n")
    blif_lines.append("00 1\n")
    blif_lines.append(".end\n\n")
    return

def add_nequiv_gate(blif_lines): # xor gate
    if ".model xor2\n" in blif_lines:
        return
    blif_lines.append(".model xor2\n")
    blif_lines.append(".inputs I0 I1\n")
    blif_lines.append(".outputs O\n")
    blif_lines.append(".names I0 I1 O\n")
    blif_lines.append("01 1\n")
    blif_lines.append("10 1\n")
    blif_lines.append(".end\n\n")
    return

def add_or_num(blif_lines, num):
    if f".model or{num}\n" in blif_lines:
        return
    blif_lines.append(".model or" + str(num) + "\n")
    blif_lines.append(".inputs ")
    for i in range(num):
        blif_lines.append("I" + str(i) + " ")
    blif_lines.append("\n.outputs O\n")
    blif_lines.append(".names ")
    for i in range(num):
        blif_lines.append("I" + str(i) + " ")
    blif_lines.append("O\n")
    for i in range(num):
        line = "-" * num + " 1\n"
        line = line[:i] + '1' + line[i+1:]
        blif_lines.append(line)

    blif_lines.append(".end\n\n")
    return

def add_and_num(blif_lines, num):
    if f".model and{num}\n" in blif_lines:
        return
    blif_lines.append(".model and" + str(num) + "\n")
    blif_lines.append(".inputs ")
    for i in range(num):
        blif_lines.append("I" + str(i) + " ")
    blif_lines.append("\n.outputs O\n")
    blif_lines.append(".names ")
    for i in range(num):
        blif_lines.append("I" + str(i) + " ")
    blif_lines.append("O\n")
    blif_lines.append("1" * num + " 1\n")

    blif_lines.append(".end\n\n")
    return

def add_UnequivV(blif_lines, num):
    # vector U and V are not equivalent
    if f".model UneqV{num}\n" in blif_lines:
        return
    
    add_nequiv_gate(blif_lines) # xor2
    add_or_num(blif_lines, num)

    blif_lines.append(".model UneqV" + str(num) + "\n")
    blif_lines.append(".inputs ")
    for i in range(num):
        blif_lines.append("U" + str(i) + " ")
    for i in range(num):
        blif_lines.append("V" + str(i) + " ")
    blif_lines.append("\n")
    blif_lines.append(".outputs O_equal\n")
    
    for i in range(num):
        blif_lines.append(".subckt xor2 I0=U" + str(i) + " I1=V" + str(i) + " O=unequal" + str(i) + "\n")
    blif_lines.append(".subckt or" + str(num))
    for i in range(num):
        blif_lines.append(" I" + str(i) + "=unequal" + str(i))
    blif_lines.append(" O=O_equal\n")
    blif_lines.append(".end\n\n")
    return

def add_UequivV(blif_lines, num):
    # vector U and V are equivalent
    if f".model UequV{num}\n" in blif_lines:
        return
    blif_lines.append(".model UequV" + str(num) + "\n")
    blif_lines.append(".inputs ")
    for i in range(num):
        blif_lines.append("U" + str(i) + " ")
    for i in range(num):
        blif_lines.append("V" + str(i) + " ")
    blif_lines.append("\n")
    blif_lines.append(".outputs O_equal\n")

    for i in range(num):
        blif_lines.append(".subckt equiv I0=U" + str(i) + " I1=V" + str(i) + " O=equal" + str(i) + "\n")
    blif_lines.append(".subckt and" + str(num))
    for i in range(num):
        blif_lines.append(" I" + str(i) + "=equal" + str(i))
    blif_lines.append(" O=O_equal\n")
    blif_lines.append(".end\n\n")
    return

def add_onehot(blif_lines, num):
    if f".model onehot{num}\n" in blif_lines:
        return
    blif_lines.append(".model onehot" + str(num) + "\n")
    blif_lines.append(".inputs ")
    for i in range(num):
        blif_lines.append("I" + str(i) + " ")
    blif_lines.append("\n.outputs O\n")
    blif_lines.append(".names ")
    for i in range(num):
        blif_lines.append("I" + str(i) + " ")
    blif_lines.append("O\n")
    for i in range(num):
        line = "0" * num + " 1\n"
        line = line[:i] + '1' + line[i+1:]
        blif_lines.append(line)

    blif_lines.append(".end\n\n")
    return

def add_subcircuit_model(blif_lines, u_num, c_num):

    add_not_gate(blif_lines)
    add_or_num(blif_lines, 2)
    add_and_num(blif_lines, 2)
    add_imply_gate(blif_lines)
    # add_equiv_gate(blif_lines)
    add_nequiv_gate(blif_lines)# xor2
    add_UnequivV(blif_lines, u_num)
    add_UnequivV(blif_lines, c_num)

    return

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Generate blif file for random graph with coloring constraints.")
    parser.add_argument('-n', type=int, help='Number of nodes = 2^n (required)', required=True)
    parser.add_argument('-c', type=int, help='Colorability (required)', default=2)
    parser.add_argument('-t', type=int, help='Trial number (for random graph generation)', default=0)
    parser.add_argument('--gen_graph', action='store_true', help='Generate implicit graph blif file')
    args = parser.parse_args()

    u_num = args.n
    colorability = args.c
    c_num = math.ceil(math.log2(colorability))
    trial = args.t

    # matrix_A_file = f"./graphs/hash_matrix_A_size_{2*u_num}.csv"
    # vector_b_file = f"./graphs/hash_vector_b_size_{2*u_num}.csv"
    graph_file = f"./graphs/random_graph_n{u_num}_trial{trial}.csv"

    output_blif_file = f"./sample/random_graph_coloring_n{u_num}_c{colorability}_trial{trial}.blif"
    output_graph_file = f"./graphs/random_graph_n{u_num}_trial{trial}_graph.blif"

    blif_lines = []

    # parse blif file generated by abc
    add_main_model(u_num, c_num)
    # add_implicit_graph(blif_lines, matrix_A_file, vector_b_file, u_num, output_graph_file)
    add_simple_implicit_graph(blif_lines, graph_file, u_num, output_graph_file)
    if args.gen_graph:
        exit(0)
    
    if c_num > 1:
        add_fit_color_limit(blif_lines, colorability, c_num)
    add_subcircuit_model(blif_lines, u_num, c_num)
    
    print("\nWriting blif file...")
    with open(output_blif_file, "w") as f:
        f.writelines(blif_lines)
    print(f"Colorability: {colorability}")
    print("\nGenerate blif file successfully!\n")