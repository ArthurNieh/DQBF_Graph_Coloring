# Description: Generate blif file for random graph with coloring constraints
#
# Modified from sudoku/blif_gen_auto.py
# This script generates a blif file for ISCAS89 benchmarks with coloring constraints.
# 
# Author: Arhtur Nieh
# Date: 2025-09-24
# Reference: https://www.notion.so/DQBF-on-Graphs-1ac570d5afa980eca2deef656ebd8b68?pvs=4

import sys
import math
import argparse

def add_main_model():

### I/O parameters
    blif_lines.append(f".model {iscas_case}\n")
    blif_lines.append(".inputs ")
    for i in range(u_num):
        blif_lines.append("u" + str(i) + " ")
    for i in range(v_num):
        blif_lines.append("v" + str(i) + " ")
    for i in range(c_num):
        blif_lines.append("c" + str(i) + " ")
    for i in range(d_num):
        blif_lines.append("d" + str(i) + " ")
    for i in range(PI_num):
        blif_lines.append("pi" + str(i) + " ")
    blif_lines.append("\n")
    blif_lines.append(".outputs f\n")

### Graph subcircuit
    blif_lines.append(".subckt graph ")
    for i in range(u_num):
        blif_lines.append("U" + str(i) + "=u" + str(i) + " ")
    for i in range(v_num):
        blif_lines.append("V" + str(i) + "=v" + str(i) + " ")
    for i in range(PI_num):
        blif_lines.append("I" + str(i) + "=pi" + str(i) + " ")
    blif_lines.append("E=e1\n")

    blif_lines.append(".subckt graph ")
    for i in range(u_num):
        blif_lines.append("U" + str(i) + "=v" + str(i) + " ")
    for i in range(v_num):
        blif_lines.append("V" + str(i) + "=u" + str(i) + " ")
    for i in range(PI_num):
        blif_lines.append("I" + str(i) + "=pi" + str(i) + " ")
    blif_lines.append("E=e2\n")

    # graph = 0, if u = 0000...0, v = 0000...0
    # blif_lines.append(f".subckt or{u_num} ")
    # for i in range(u_num):
    #     blif_lines.append(f"I{i}=u{i} ")
    # blif_lines.append("O=e0\n")

    blif_lines.append(".subckt or2 I0=e1 I1=e2 O=e0\n")

    blif_lines.append(f".subckt UneqV{u_num} ")
    for i in range(u_num):
        blif_lines.append(f"U{i}=u{i} ")
    for i in range(v_num):
        blif_lines.append(f"V{i}=v{i} ")
    blif_lines.append("O_equal=notsame\n")
    blif_lines.append(".subckt and2 I0=e0 I1=notsame O=e\n")

### Color subcircuit
    blif_lines.append(".subckt color_not_equal ")
    for i in range(c_num):
        blif_lines.append("C" + str(i) + "=c" + str(i) + " ")
    for i in range(d_num):
        blif_lines.append("D" + str(i) + "=d" + str(i) + " ")
    blif_lines.append("O_nequal=ncolor\n")

### Onehot subcircuit
    if binary_color == '0':
        blif_lines.append(".subckt onehot" + str(c_num) + " ")
        for i in range(c_num):
            blif_lines.append("I" + str(i) + "=c" + str(i) + " ")
        blif_lines.append("O=conehot\n")

        blif_lines.append(".subckt onehot" + str(d_num) + " ")
        for i in range(d_num):
            blif_lines.append("I" + str(i) + "=d" + str(i) + " ")
        blif_lines.append("O=donehot\n")
        blif_lines.append(".subckt and2 I0=conehot I1=donehot O=colorencode\n")
### Binary color subcircuit
    elif binary_color == '1':
        blif_lines.append(".subckt fit_color_limit ")
        for i in range(c_num):
            blif_lines.append(f"I{i}=c{i} ")
        blif_lines.append("G=clessthan\n")
        blif_lines.append(".subckt fit_color_limit ")
        for i in range(d_num):
            blif_lines.append(f"I{i}=d{i} ")
        blif_lines.append("G=dlessthan\n")
        blif_lines.append(".subckt and2 I0=clessthan I1=dlessthan O=colorencode\n")
        
    else:
        print("Error: binary_color should be 0 or 1")
        sys.exit(1)

### Main circuit
    blif_lines.append(".subckt imply I0=e I1=ncolor O=diffcolor\n")

    # not same node
    blif_lines.append(".subckt UneqV" + str(u_num) + " ")
    for i in range(u_num):
        blif_lines.append("U" + str(i) + "=u" + str(i) + " ")
    for i in range(v_num):
        blif_lines.append("V" + str(i) + "=v" + str(i) + " ")
    blif_lines.append("O_equal=notsamenode\n")

    # not same color
    blif_lines.append(".subckt UneqV" + str(c_num) + " ")
    for i in range(c_num):
        blif_lines.append("U" + str(i) + "=c" + str(i) + " ")
    for i in range(d_num):
        blif_lines.append("V" + str(i) + "=d" + str(i) + " ")
    blif_lines.append("O_equal=notsamecolor\n")

    blif_lines.append(".subckt imply I0=notsamecolor I1=notsamenode O=notsamecolornode\n")

    blif_lines.append(".subckt and2 I0=diffcolor I1=colorencode O=temp1\n")
    blif_lines.append(".subckt and2 I0=notsamecolornode I1=temp1 O=f\n")

    blif_lines.append(".end\n\n")

def add_implicit_graph(blif_lines, matrix_A_file, vector_b_file, u_num):

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

    blif_lines.append("\n.model graph\n")
    blif_lines.append(".inputs ")
    blif_lines.extend([f"U{i} " for i in range(u_num)])
    blif_lines.extend([f"V{i} " for i in range(u_num)])
    blif_lines.append("\n")
    blif_lines.append(".outputs E\n")

    # create a constant-1 signal
    blif_lines.append(f".names CONST1\n1\n")

    for i, row in enumerate(A):
        count = 0

        # Initialize accumulator A{i}0 = constant 0
        blif_lines.append(f".names A{i}{count}\n")
        blif_lines.append("0\n")

        # XOR all selected inputs in this row
        for j in range(2 * u_num):
            if row[j] == 1:
                if j < u_num:
                    inp = f"U{j}"
                else:
                    inp = f"V{j - u_num}"

                blif_lines.append(
                    f".subckt xor2 I0={inp} I1=A{i}{count} O=A{i}{count+1}\n"
                )
                count += 1

        # Add bias term b[i] if needed
        if b[i] == 1:
            blif_lines.append(
                f".subckt xor2 I0=CONST1 I1=A{i}{count} O=A{i}{count+1}\n"
            )
            count += 1

        # Define the final output bit h_i(x)
        blif_lines.append(f".names A{i}{count} H{i}\n1 1\n")
    
    # Final output E = XOR of all H{i}
    # XOR all Hi together into one final output H_final
    hi_count = 0

    # Start accumulator = 0
    blif_lines.append(f".names XOR_ACC{hi_count}\n")
    blif_lines.append("0\n")

    for i in range(len(A)):  # A has n rows → n Hi signals
        blif_lines.append(
            f".subckt xor2 I0=H{i} I1=XOR_ACC{hi_count} O=XOR_ACC{hi_count+1}\n"
        )
        hi_count += 1

    # Final output
    blif_lines.append(f".names XOR_ACC{hi_count} E\n1 1\n")

    blif_lines.append(".end\n\n")
    return

def add_color_not_equal(blif_lines, c_num):
    blif_lines.append(".model color_not_equal\n")
    blif_lines.append(".inputs ")
    for i in range(c_num):
        blif_lines.append("C" + str(i) + " ")
    for i in range(c_num):
        blif_lines.append("D" + str(i) + " ")
    blif_lines.append("\n.outputs O_nequal\n")

    for i in range(c_num):
        blif_lines.append(".subckt xor2 I0=C" + str(i) + " I1=D" + str(i) + " O=unequal" + str(i) + "\n")
    blif_lines.append(".subckt or" + str(c_num))
    for i in range(c_num):
        blif_lines.append(" I" + str(i) + "=unequal" + str(i))
    blif_lines.append(" O=O_nequal\n")
    blif_lines.append(".end\n\n")
    return

def add_1_comparator(blif_lines):
    # G = 1 if A > B
    # C = 1 if A = B
    # E = 1 if A = B in the significant bit
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
    b_c_limit = b_c_limit.zfill(c_digits)
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
    if ".model comparator\n" not in blif_lines:
        add_1_comparator(blif_lines)
    if f".model comparator{num}\n" in blif_lines:
        return
    
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
    if ".model adder\n" not in blif_lines:
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
    blif_lines.append(".model not\n")
    blif_lines.append(".inputs I\n")
    blif_lines.append(".outputs O\n")
    blif_lines.append(".names I O\n")
    blif_lines.append("0 1\n")
    blif_lines.append(".end\n\n")
    return

def add_imply_gate(blif_lines):
    blif_lines.append(".model imply\n")
    blif_lines.append(".inputs I0 I1\n")
    blif_lines.append(".outputs O\n")
    blif_lines.append(".names I0 I1 O\n")
    blif_lines.append("0- 1\n")
    blif_lines.append("-1 1\n")
    blif_lines.append(".end\n\n")
    return

def add_equiv_gate(blif_lines):
    blif_lines.append(".model equiv\n")
    blif_lines.append(".inputs I0 I1\n")
    blif_lines.append(".outputs O\n")
    blif_lines.append(".names I0 I1 O\n")
    blif_lines.append("11 1\n")
    blif_lines.append("00 1\n")
    blif_lines.append(".end\n\n")
    return

def add_nequiv_gate(blif_lines): # xor gate
    blif_lines.append(".model xor2\n")
    blif_lines.append(".inputs I0 I1\n")
    blif_lines.append(".outputs O\n")
    blif_lines.append(".names I0 I1 O\n")
    blif_lines.append("01 1\n")
    blif_lines.append("10 1\n")
    blif_lines.append(".end\n\n")
    return

def add_or_num(blif_lines, num):
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
    # num = int(u_num/2)
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

def add_UxequivVx(blif_lines):
    # vector Ux and Vx are equivalent
    num = int(u_num/2)
    blif_lines.append(".model UxequVx\n")
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

    # add_not_gate()
    # add_or_num(blif_lines, 2)
    # add_and_num(blif_lines, 2)
    # add_imply_gate(blif_lines)    #
    # add_equiv_gate(blif_lines)    #
    add_nequiv_gate(blif_lines)   # xor2
    # add_or_num(blif_lines, u_num)   #
    # add_and_num(blif_lines, u_num)  #
    # add_UnequivV(blif_lines, u_num) #
    # if u_num != c_num: 
    #     if c_num != 2:
    #         add_or_num(blif_lines, c_num)
    #     add_UnequivV(blif_lines, c_num)

    # add_fit_color_limit(blif_lines, colorability, c_num)

    return

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Generate blif file for random graph with coloring constraints.")
    parser.add_argument('-n', type=int, help='Number of nodes = 2^n (required)', required=True)
    parser.add_argument('-c', type=int, help='Colorability (required)', required=True)
    args = parser.parse_args()

    u_num = args.n
    colorability = args.c
    c_num = math.ceil(math.log2(colorability))

    matrix_A_file = f"./graphs/hash_matrix_A_size_{2*u_num}.csv"
    vector_b_file = f"./graphs/hash_vector_b_size_{2*u_num}.csv"

    output_blif_file = f"./sample/random_graph_coloring_n{u_num}_c{colorability}.blif"

    blif_lines = []

    # parse blif file generated by abc
    # add_main_model()
    add_implicit_graph(blif_lines, matrix_A_file, vector_b_file, u_num)
    # add_color_not_equal(blif_lines, c_num)
    add_subcircuit_model(blif_lines, u_num, c_num)
    # print("\nWriting blif file...")
    with open(output_blif_file, "w") as f:
        f.writelines(blif_lines)
    print(f"Colorability: {colorability}")
    print("\nGenerate blif file successfully!\n")