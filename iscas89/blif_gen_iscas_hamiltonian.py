# blif_gen_iscas_hamiltonian.py
#
# This script generates a blif form Hamiltonian cycle problem for the ISCAS89 benchmark circuits.
# import functions from blif_gen_iscas_coloring.py
#
# Author: Arthur Nieh
# Date: 2025-08-11

from blif_gen_iscas_coloring import *
import sys


def hamiltonian_add_main_model(blif_lines, iscas_case, u_num, PI_num):
    print(f"u_num: {u_num}")
    print(f"iscas_case: {iscas_case}")
    print(f"PI_num: {PI_num}")

### I/O parameters
    blif_lines.append(f".model {iscas_case}\n")
    blif_lines.append(".inputs ")
    blif_lines.extend(f"u{i} " for i in range(u_num))
    blif_lines.extend(f"v{i} " for i in range(u_num))
    
    blif_lines.extend(f"x{i} " for i in range(PI_num))
    
    blif_lines.extend(f"c{i} " for i in range(u_num))
    blif_lines.extend(f"d{i} " for i in range(u_num))
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

### c+1 = d
    ## const 1
    for i in range(u_num):
        blif_lines.append(f".names const{i}\n")
        if i == 0:
            blif_lines.append("1\n")
        else:
            blif_lines.append("0\n")

    blif_lines.append(f".subckt adder{u_num} ")
    blif_lines.extend(f"A{i}=c{i} " for i in range(u_num))
    blif_lines.extend(f"B{i}=const{i} " for i in range(u_num))
    blif_lines.extend(f"S{i}=cplus1{i} " for i in range(u_num))
    blif_lines.append("\n")

    blif_lines.append(f".subckt UequV{u_num} ")
    blif_lines.extend(f"U{i}=cplus1{i} " for i in range(u_num))
    blif_lines.extend(f"V{i}=d{i} " for i in range(u_num))
    blif_lines.append("O_equal=cplus1equald\n")

### u, v the same
    blif_lines.append(f".subckt UequV{u_num} ")
    blif_lines.extend(f"U{i}=u{i} " for i in range(u_num))
    blif_lines.extend(f"V{i}=v{i} " for i in range(u_num))
    blif_lines.append("O_equal=uvsame\n")

### c, d (s1, s2) the same
    blif_lines.append(f".subckt UequV{u_num} ")
    blif_lines.extend(f"U{i}=c{i} " for i in range(u_num))
    blif_lines.extend(f"V{i}=d{i} " for i in range(u_num))
    blif_lines.append("O_equal=cdsame\n")

### Initial condition
    ## Break Symmetry, u = 0 -> c = 0
    blif_lines.append(".subckt is_zero ")
    blif_lines.extend(f"I{i}=u{i} " for i in range(u_num))
    blif_lines.append("O=uis0\n")

    blif_lines.append(".subckt is_zero ")
    blif_lines.extend(f"I{i}=c{i} " for i in range(u_num))
    blif_lines.append("O=cis0\n")

    blif_lines.append(".subckt imply I0=uis0 I1=cis0 O=uc0\n")

### main circuit

    blif_lines.append(".subckt imply I0=cplus1equald I1=euvx O=sequence\n")

    blif_lines.append(".subckt equiv I0=uvsame I1=cdsame O=uvcdsame\n")

    blif_lines.append(".subckt and2 I0=sequence I1=uvcdsame O=fi\n")

    blif_lines.append(".subckt and2 I0=fi I1=uc0 O=f\n")
    
    blif_lines.append(".end\n\n")

def hamiltonian_add_subcircuit(blif_lines, u_num):
    add_or_num(blif_lines, 2)
    add_and_num(blif_lines, 2)
    add_imply_gate(blif_lines)
    add_equiv_gate(blif_lines)
    add_and_num(blif_lines, u_num)

    add_UequivV(blif_lines, u_num)
    add_n_adder(blif_lines, u_num)
    add_is_0(blif_lines, u_num)

if __name__ == "__main__":
    # Check if the script is being run directly
    # Parse command line arguments
    if len(sys.argv) > 2:
        print("Usage: python blif_gen_iscas_hamiltonian.py <iscas_case>")
        sys.exit(1)

    iscas_case = sys.argv[1]

    input_file = f"./benchmarks/{iscas_case}.blif"
    output_file = f"./sample/{iscas_case}_hamiltonian.blif"

    blif_lines = []

    u_num, PI_num = parse_bench()
    hamiltonian_add_main_model(blif_lines, iscas_case, u_num, PI_num)
    add_implicit_graph(blif_lines, input_file)
    print("\nAdding graph subcircuit...")
    
    hamiltonian_add_subcircuit(blif_lines, u_num)
    print("\nWriting blif file...")
    with open(output_file, "w") as f:
        f.writelines(blif_lines)
    print("\nGenerate blif file successfully!\n")