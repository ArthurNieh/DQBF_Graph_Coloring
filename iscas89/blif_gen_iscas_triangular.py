# blif_gen_iscas_triangular.py
#
# This script generates a blif form triangular free problem for the ISCAS89 benchmark circuits.
# import functions from blif_gen_iscas_coloring.py
#
# Author: Arthur Nieh
# Date: 2025-05-05

from blif_gen_iscas_coloring import *
import sys


def tri_add_main_model(iscas_case, tri_f, u_num, PI_num):
    global blif_lines
    print(f"u_num: {u_num}")
    print(f"tri_f: {tri_f}")
    print(f"iscas_case: {iscas_case}")
    print(f"PI_num: {PI_num}")

### I/O parameters
    blif_lines.append(f".model {iscas_case}\n")
    blif_lines.append(".inputs ")
    blif_lines.extend(f"u{i} " for i in range(u_num))
    blif_lines.extend(f"v{i} " for i in range(u_num))
    blif_lines.extend(f"w{i} " for i in range(u_num))
    
    blif_lines.extend(f"x{i} " for i in range(PI_num))
    blif_lines.extend(f"y{i} " for i in range(PI_num))
    blif_lines.extend(f"z{i} " for i in range(PI_num))
    blif_lines.append("\n")
    blif_lines.append(".outputs f\n")

### Graph subcircuit
    # graph(u,v,x)
    blif_lines.append(".subckt graph ")
    blif_lines.extend(f"U{i}=u{i} " for i in range(u_num))
    blif_lines.extend(f"V{i}=v{i} " for i in range(u_num))
    blif_lines.extend(f"I{i}=x{i} " for i in range(PI_num))
    blif_lines.append("E=e1\n")

    blif_lines.append(".subckt graph ")
    blif_lines.extend(f"U{i}=v{i} " for i in range(u_num))
    blif_lines.extend(f"V{i}=u{i} " for i in range(u_num))
    blif_lines.extend(f"I{i}=x{i} " for i in range(PI_num))
    blif_lines.append("E=e2\n")
    blif_lines.append(".subckt or2 I0=e1 I1=e2 O=euvx\n")
    # graph(v,w,y)
    blif_lines.append(".subckt graph ")
    blif_lines.extend(f"U{i}=v{i} " for i in range(u_num))
    blif_lines.extend(f"V{i}=w{i} " for i in range(u_num))
    blif_lines.extend(f"I{i}=y{i} " for i in range(PI_num))
    blif_lines.append("E=e3\n")

    blif_lines.append(".subckt graph ")
    blif_lines.extend(f"U{i}=w{i} " for i in range(u_num))
    blif_lines.extend(f"V{i}=v{i} " for i in range(u_num))
    blif_lines.extend(f"I{i}=y{i} " for i in range(PI_num))
    blif_lines.append("E=e4\n")
    blif_lines.append(".subckt or2 I0=e3 I1=e4 O=evwy\n")
    # graph(u,w,z)
    blif_lines.append(".subckt graph ")
    blif_lines.extend(f"U{i}=u{i} " for i in range(u_num))
    blif_lines.extend(f"V{i}=w{i} " for i in range(u_num))
    blif_lines.extend(f"I{i}=z{i} " for i in range(PI_num))
    blif_lines.append("E=e5\n")

    blif_lines.append(".subckt graph ")
    blif_lines.extend(f"U{i}=w{i} " for i in range(u_num))
    blif_lines.extend(f"V{i}=u{i} " for i in range(u_num))
    blif_lines.extend(f"I{i}=z{i} " for i in range(PI_num))
    blif_lines.append("E=e6\n")
    blif_lines.append(".subckt or2 I0=e5 I1=e6 O=euwz\n")

    blif_lines.append(".subckt and2 I0=euvx I1=evwy O=eu\n")
    blif_lines.append(".subckt and2 I0=eu I1=euwz O=e_tri\n")

### u, v, w not the same
    blif_lines.append(f".subckt UneqV{u_num} ")
    blif_lines.extend(f"U{i}=u{i} " for i in range(u_num))
    blif_lines.extend(f"V{i}=v{i} " for i in range(u_num))
    blif_lines.append("O_equal=uvnotsame\n")

    blif_lines.append(f".subckt UneqV{u_num} ")
    blif_lines.extend(f"U{i}=v{i} " for i in range(u_num))
    blif_lines.extend(f"V{i}=w{i} " for i in range(u_num))
    blif_lines.append("O_equal=vwnotsame\n")

    blif_lines.append(f".subckt UneqV{u_num} ")
    blif_lines.extend(f"U{i}=u{i} " for i in range(u_num))
    blif_lines.extend(f"V{i}=w{i} " for i in range(u_num))
    blif_lines.append("O_equal=uwnotsame\n")

    blif_lines.append(".subckt and2 I0=uvnotsame I1=vwnotsame O=uvwnotsame\n")
    blif_lines.append(".subckt and2 I0=uvwnotsame I1=uwnotsame O=notsame\n")

### main circuit
    if tri_f == 1:
        blif_lines.append(".subckt not I=e_tri O=netri\n")
        blif_lines.append(".subckt imply I0=notsame I1=e_tri O=f\n")
        # blif_lines.append(".subckt not I=notsame O=f\n")
        
    else:
        print("detect triangular is not supported yet!")
        sys.exit(1)

    blif_lines.append(".end\n\n")

def tri_add_subcircuit():
    global u_num
    add_not_gate()
    add_or_num(2)
    add_and_num(2)
    add_imply_gate()    #
    add_equiv_gate()    #
    add_nequiv_gate()   # xor2
    add_or_num(u_num)   #
    add_and_num(u_num)  #
    add_UnequivV(u_num) #
    

if __name__ == "__main__":
    # Check if the script is being run directly
    # Parse command line arguments
    if len(sys.argv) != 3:
        print("Usage: python blif_gen_iscas_triangular.py <iscas_case>")
        sys.exit(1)

    iscas_case = sys.argv[1]
    if len(sys.argv) == 3:
        if sys.argv[2] == "-f":
            tri_f = 1
        else:
            tri_f = 0
    else:
        tri_f = 0
    # tri_f = 1 for triangular free
    # tri_f = 0 for with-triangular

    input_file = f"./benchmarks/{iscas_case}.blif"
    output_file = f"./sample/{iscas_case}_triangular.blif"

    u_num, PI_num = parse_bench()
    tri_add_main_model(iscas_case, tri_f, u_num, PI_num)
    add_implicit_graph(input_file)
    tri_add_subcircuit()
    print("\nWriting blif file...")
    with open(output_file, "w") as f:
        f.writelines(blif_lines)
    print("\nGenerate blif file successfully!\n")