# Description: Generate blif file for ISCAS89 benchmarks with coloring constraints
#
# Modified from sudoku/blif_gen_auto.py
# This script generates a blif file for ISCAS89 benchmarks with coloring constraints.
# 
# Author: Arhtur Nieh
# Date: 2025-03-25
# Reference: https://www.notion.so/DQBF-on-Graphs-1ac570d5afa980eca2deef656ebd8b68?pvs=4

import sys
import math

iscas_case = sys.argv[1]
input_file = f"./benchmarks/{iscas_case}.blif"
output_file = f"./sample/{iscas_case}_color.blif"
abc_file = f"./abc_output.txt"

blif_lines = []
N = 0
colorability = 4
c_digits = math.ceil(math.log2(colorability))

u_num = v_num = 0
c_num = d_num = c_digits

FF_DQ_map = dict()
FF_ind_map = dict()

PI_num = 0
PI_dict = dict()

def parse_bench():
    global N, u_num, v_num, c_num, d_num
    print(f"Reading file: {abc_file}")
    with open(abc_file, "r") as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.split(' ')
        if len(line) < 2:
            continue
        
        elif line[1] == "inputs":
            PI_num = int(line[2].strip("():"))
            for i in range(PI_num):
                pi = line[4+i].strip('\n').split('=')[1]
                PI_dict.update({i: pi})
                print(f"PI_dict: {i} -> {pi}")
            print(f"Number of inputs: {PI_num}")

        elif line[0] == "Latches":

            N = int(line[1].strip("():"))
            u_num = v_num = N
            print(f"Number of nodes: {N}")
            
            for i in range(N):
                ff = line[4+i].replace('(','=').replace(')','=').split('=')
                print(f"FF_DQ_map: {ff[1]} -> {ff[2]}")
                FF_DQ_map.update({ff[1]: ff[2]})
                print(f"FF_ind_map: {ff[1]} -> {i}")
                print(f"FF_ind_map: {ff[2]} -> {i}")
                FF_ind_map.update({ff[1]: i})
                FF_ind_map.update({ff[2]: i})
            break

    return

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
    blif_lines.append("\n")
    blif_lines.append(".outputs f\n")

### Graph subcircuit
    blif_lines.append(".subckt graph ")
    for i in range(u_num):
        blif_lines.append("U" + str(i) + "=u" + str(i) + " ")
    for i in range(v_num):
        blif_lines.append("V" + str(i) + "=v" + str(i) + " ")
    blif_lines.append("E=e1\n")

    blif_lines.append(".subckt graph ")
    for i in range(u_num):
        blif_lines.append("U" + str(i) + "=v" + str(i) + " ")
    for i in range(v_num):
        blif_lines.append("V" + str(i) + "=u" + str(i) + " ")
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
    blif_lines.append(".subckt onehot" + str(c_num) + " ")
    for i in range(c_num):
        blif_lines.append("I" + str(i) + "=c" + str(i) + " ")
    blif_lines.append("O=conehot\n")

    blif_lines.append(".subckt onehot" + str(d_num) + " ")
    for i in range(d_num):
        blif_lines.append("I" + str(i) + "=d" + str(i) + " ")
    blif_lines.append("O=donehot\n")

### Main circuit
    blif_lines.append(".subckt imply I0=e I1=ncolor O=diffcolor\n")

    blif_lines.append(".subckt and2 I0=conehot I1=donehot O=conehotdonehot\n")

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

    blif_lines.append(".subckt and2 I0=diffcolor I1=conehotdonehot O=temp1\n")
    blif_lines.append(".subckt and2 I0=notsamecolornode I1=temp1 O=f\n")

    blif_lines.append(".end\n\n")

def add_implicit_graph():
    blif_lines.append(".model graph\n")
    blif_lines.append(".inputs ")
    for i in range(u_num):
        blif_lines.append("U" + str(i) + " ")
    for i in range(v_num):
        blif_lines.append("V" + str(i) + " ")
    blif_lines.append("\n")
    blif_lines.append(".outputs E\n")
    
    for i in range(u_num-1):
        blif_lines.append(".subckt equiv I0=U" + str(i) + " I1=V" + str(i+1) + " O=equal" + str(i) + "\n")
    blif_lines.append(f".subckt xor{len(xor_gates)} ")
    for i in range(len(xor_gates)):
        blif_lines.append(f"I{i}=U{xor_gates[i]-1} ")
    blif_lines.append("O=e\n")
    blif_lines.append(f".subckt equiv I0=V0 I1=e O=equal{u_num-1}\n")
    blif_lines.append(f".subckt and{u_num} ")
    for i in range(u_num):
        blif_lines.append(f"I{i}=equal{i} ")
    blif_lines.append("O=E\n")
    blif_lines.append(".end\n\n")
    return

def add_color_not_equal():
    blif_lines.append(".model color_not_equal\n")
    blif_lines.append(".inputs ")
    for i in range(c_num):
        blif_lines.append("C" + str(i) + " ")
    for i in range(d_num):
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

def add_1_comparator():
    blif_lines.append(".model comparator\n")
    blif_lines.append(".inputs A B E\n")
    blif_lines.append(".outputs G C\n")
    blif_lines.append(".names A B E G\n")
    blif_lines.append("101 1\n")
    blif_lines.append(".names A B E C\n")
    blif_lines.append("111 1\n")
    blif_lines.append("001 1\n")
    blif_lines.append(".end\n\n")

def add_fit_color_limit(c_limit):
    if c_limit <= 0 or c_limit >= math.pow(2, c_num):
        print("Error: c_limit should be greater than 0 and less than c_num")
        sys.exit(1)
    b_c_limit = bin(c_limit)[2:]
    b_c_limit = b_c_limit.zfill(c_digits)
    print(f"c_limit: {b_c_limit}")

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
    
    # compare, if C > I, G = 1
    blif_lines.append(f".subckt comparator{c_num} ")
    for i in range(c_num):
        blif_lines.append(f"A{i}=C{i} ")
    for i in range(c_num):
        blif_lines.append(f"B{i}=I{i} ")
    blif_lines.append("G=G\n")

    blif_lines.append(".end\n\n")

def add_n_comparator(num):
    add_1_comparator()
    
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

### All fundamental gates
def add_not_gate():
    blif_lines.append(".model not\n")
    blif_lines.append(".inputs I\n")
    blif_lines.append(".outputs O\n")
    blif_lines.append(".names I O\n")
    blif_lines.append("0 1\n")
    blif_lines.append(".end\n\n")
    return

def add_imply_gate():
    blif_lines.append(".model imply\n")
    blif_lines.append(".inputs I0 I1\n")
    blif_lines.append(".outputs O\n")
    blif_lines.append(".names I0 I1 O\n")
    blif_lines.append("0- 1\n")
    blif_lines.append("-1 1\n")
    blif_lines.append(".end\n\n")
    return

def add_equiv_gate():
    blif_lines.append(".model equiv\n")
    blif_lines.append(".inputs I0 I1\n")
    blif_lines.append(".outputs O\n")
    blif_lines.append(".names I0 I1 O\n")
    blif_lines.append("11 1\n")
    blif_lines.append("00 1\n")
    blif_lines.append(".end\n\n")
    return

def add_nequiv_gate(): # xor gate
    blif_lines.append(".model xor2\n")
    blif_lines.append(".inputs I0 I1\n")
    blif_lines.append(".outputs O\n")
    blif_lines.append(".names I0 I1 O\n")
    blif_lines.append("01 1\n")
    blif_lines.append("10 1\n")
    blif_lines.append(".end\n\n")
    return

def add_or_num(num):
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

def add_and_num(num):
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

def add_xor_num(num):
    if num <= 2:
        print("Error: num should be greater than 2 for xor_num")
        return
    blif_lines.append(".model xor" + str(num) + "\n")
    blif_lines.append(".inputs ")
    for i in range(num):
        blif_lines.append("I" + str(i) + " ")
    blif_lines.append("\n.outputs O\n")
    blif_lines.append(".subckt xor2 I0=I0 I1=I1 O=t1\n")
    for i in range(2, num-1):
        blif_lines.append(f".subckt xor2 I0=I{i} I1=t{i-1} O=t{i}\n")
    blif_lines.append(f".subckt xor2 I0=I{num-1} I1=t{num-2} O=O\n")
    blif_lines.append(".end\n\n")
    return

def add_UnequivV(num):
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

def add_UxequivVx():
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

def add_onehot(num):
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

def add_subcircuit_model():
    # add_not_gate()
    add_or_num(2)
    add_and_num(2)
    # add_xor_2()         #
    if len(xor_gates) > 2:
        add_xor_num(len(xor_gates))#
    add_imply_gate()    #
    add_equiv_gate()    #
    add_nequiv_gate()   # xor2
    add_or_num(u_num)   #
    add_and_num(u_num)  #
    add_UnequivV(u_num) #
    if u_num != c_num: 
        if c_num != 2:
            add_or_num(c_num)
        add_UnequivV(c_num)
    # add_and_num(int(u_num/2))
    
    # add_UxequivVx()
    add_onehot(c_num)   #
    return

if __name__ == "__main__":
    # parse blif file generated by abc
    parse_bench()



    # add_main_model()
    # add_implicit_graph()
    # add_color_not_equal()
    add_n_comparator(c_num)
    add_or_num(2)
    # add_or_num(3)
    add_fit_color_limit(colorability)
    # add_subcircuit_model()
    with open(output_file, "w") as f:
        f.writelines(blif_lines)
    print("\nGenerate blif file successfully!\n")