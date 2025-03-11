# Description: Generate blif file for LSFR
#
# Modified from sudoku/blif_gen_auto.py
# This script generates a blif file for a Fibonacci LSFR circuit. The generated blif file can be used to simulate the LSFR circuit.
# 
# Author: Arhtur Nieh
# Date: 2025-03-10
# Reference: https://www.notion.so/DQBF-on-Graphs-1ac570d5afa980eca2deef656ebd8b68?pvs=4


import math

output_file = "./sample/lsfr.blif"

blif_lines = []
N = 4
colorability = 3    # 2-colorable for even cycle, 3-colorable for odd cycle
u_num = v_num = N
c_num = d_num = colorability

# xor_gates = [11, 13, 14, 16]
xor_gates = [2, 4]

def add_main_model():

### I/O parameters
    blif_lines.append(".model lsfr\n")
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

# def add_xor_2():
#     blif_lines.append(".model xor2\n")
#     blif_lines.append(".inputs I0 I1\n")
#     blif_lines.append(".outputs O\n")
#     blif_lines.append(".names I0 I1 O\n")
#     blif_lines.append("01 1\n")
#     blif_lines.append("10 1\n")
#     blif_lines.append(".end\n\n")
#     return

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
    add_not_gate()
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
    add_main_model()
    add_implicit_graph()
    add_color_not_equal()
    add_subcircuit_model()
    with open(output_file, "w") as f:
        f.writelines(blif_lines)