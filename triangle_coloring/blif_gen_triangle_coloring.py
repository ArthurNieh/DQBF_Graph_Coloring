import sys
import math

sys.path.insert(1, '../iscas89')

from blif_gen_iscas_coloring import *

def add_triangle_main_model(blif_lines):
    blif_lines.append(f".model triangle_coloring\n")
    blif_lines.append(".inputs ")
    blif_lines.extend(f"u{i} " for i in range(u_num))
    blif_lines.extend(f"v{i} " for i in range(u_num))
    blif_lines.extend(f"w{i} " for i in range(u_num))
    blif_lines.extend(f"t{i} " for i in range(u_num))

    blif_lines.extend(f"c{i} " for i in range(c_num))
    blif_lines.extend(f"d{i} " for i in range(c_num))
    blif_lines.append("\n")
    blif_lines.append(".outputs f\n")

    blif_lines.append(f".subckt UneqV{u_num} ")
    blif_lines.extend(f"U{i}=w{i} " for i in range(u_num))
    blif_lines.extend(f"V{i}=t{i} " for i in range(u_num))
    blif_lines.append("O_equal=wtnotsame\n")
    blif_lines.append(".subckt not I=wtnotsame O=wtsame\n")

    blif_lines.append(f".subckt UneqV{c_num} ")
    blif_lines.extend(f"U{i}=c{i} " for i in range(c_num))
    blif_lines.extend(f"V{i}=d{i} " for i in range(c_num))
    blif_lines.append("O_equal=cdnotsame\n")
    blif_lines.append(".subckt not I=cdnotsame O=cdsame\n")

    blif_lines.append(".subckt and2 I0=wtsame I1=cdsame O=wtcdsame\n")
    blif_lines.append(".subckt and2 I0=wtnotsame I1=cdnotsame O=wtcdnotsame\n")
    blif_lines.append(".subckt or2 I0=wtcdsame I1=wtcdnotsame O=wtcd\n")

# color limit
    blif_lines.append(".subckt fit_color_limit ")
    blif_lines.extend(f"I{i}=c{i} " for i in range(c_num))
    blif_lines.append("G=clessthan\n")

    blif_lines.append(".subckt fit_color_limit ")
    blif_lines.extend(f"I{i}=d{i} " for i in range(c_num))
    blif_lines.append("G=dlessthan\n")
    blif_lines.append(".subckt and2 I0=clessthan I1=dlessthan O=colorencode\n")
# node limit
    blif_lines.append(".subckt fit_node_limit ")
    blif_lines.extend(f"I{i}=u{i} " for i in range(u_num))
    blif_lines.append("G=ulessthan\n")

    blif_lines.append(".subckt fit_node_limit ")
    blif_lines.extend(f"I{i}=v{i} " for i in range(u_num))
    blif_lines.append("G=vlessthan\n")

    blif_lines.append(".subckt fit_node_limit ")
    blif_lines.extend(f"I{i}=w{i} " for i in range(u_num))
    blif_lines.append("G=wlessthan\n")

    blif_lines.append(".subckt fit_node_limit ")
    blif_lines.extend(f"I{i}=t{i} " for i in range(u_num))
    blif_lines.append("G=tlessthan\n")

    blif_lines.append(".subckt and2 I0=ulessthan I1=vlessthan O=uvlessthan\n")
    blif_lines.append(".subckt and2 I0=wlessthan I1=tlessthan O=wtlessthan\n")
    blif_lines.append(".subckt and2 I0=uvlessthan I1=wtlessthan O=uvwtlessthan\n")
# main output
    blif_lines.append(".subckt and2 I0=wtcd I1=colorencode O=wtcdcolorencode\n")
    blif_lines.append(".subckt imply I0=uvwtlessthan I1=wtcdcolorencode O=f\n")

    blif_lines.append(".end\n")
    # return blif_lines

def add_fit_node_limit(blif_lines, N, u_num):
    if N <= 0 or N > math.pow(2, u_num):
        print("Error: n should be greater than 0 and less than u_num")
        print(f"node number: {N}, u_num: {u_num}")
        sys.exit(1)
    b_N = bin(N-1)[2:]
    b_N = b_N.zfill(u_num)
    print(f"N: {b_N}")

    add_n_comparator(blif_lines, u_num)

    blif_lines.append(".model fit_node_limit\n")
    blif_lines.append(".inputs ")
    for i in range(u_num):
        blif_lines.append(f"I{i} ")
    blif_lines.append("\n")
    blif_lines.append(".outputs G\n")

    # set C[i] = b_N[-i-1]
    for i in range(u_num):
        blif_lines.append(f".names C{i}\n")
        blif_lines.append(f"{b_N[-i-1]}\n")
        print(f"C{i}={b_N[-i-1]}")
    
    # compare, if C >= I, G = 1
    blif_lines.append(f".subckt comparator{u_num} ")
    for i in range(u_num):
        blif_lines.append(f"A{i}=C{i} ")
    for i in range(u_num):
        blif_lines.append(f"B{i}=I{i} ")
    blif_lines.append("G=G\n")

    blif_lines.append(".end\n\n")

def add_triangle_subcircuit_model(blif_lines, u_num, c_num, colorability, N):
    add_not_gate(blif_lines)
    add_or_num(blif_lines, 2)
    add_and_num(blif_lines, 2)
    add_imply_gate(blif_lines)
    # add_equiv_gate(blif_lines)
    add_nequiv_gate(blif_lines)   # xor2
    if u_num != 2:
        add_or_num(blif_lines, u_num)   #
    # add_and_num(blif_lines, u_num)
    add_UnequivV(blif_lines, u_num) #
    if u_num != c_num: 
        if c_num != 2:
            add_or_num(blif_lines, c_num)
        add_UnequivV(blif_lines, c_num)
    # add_and_num(int(u_num/2))
    
    add_fit_color_limit(blif_lines, colorability, c_num)
    add_fit_node_limit(blif_lines, N, u_num)


if __name__ == "__main__":

    if len(sys.argv) != 3:
        print("Usage: python3 blif_gen_triangle_coloring.py <node number> <colorability>")
        print("Example: python3 blif_gen_triangle_coloring.py 5 7")
        sys.exit(1)
    N = int(sys.argv[1]) # Nuber of nodes
    colorability = int(sys.argv[2])

    output_file = "./triangle_color.blif"

    u_num = math.ceil(math.log2(N))
    c_num = math.ceil(math.log2(colorability))

    blif_lines = []

    add_triangle_main_model(blif_lines)
    add_triangle_subcircuit_model(blif_lines, u_num, c_num, colorability, N)
    print("\nWriting blif file...")
    with open(output_file, "w") as f:
        f.writelines(blif_lines)
    print(f"Colorability: {colorability}")
    print("\nGenerate blif file successfully!\n")