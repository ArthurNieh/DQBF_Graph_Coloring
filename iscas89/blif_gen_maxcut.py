# blif_gen_maxcut.py
#
# This script generates a blif form Max-Cut problem.
# import functions from blif_gen_iscas_coloring.py
#
# Author: Arthur Nieh
# Date: 2025-08-11

import sys
from blif_gen_iscas_coloring import *


def maxcut_add_main_model(blif_lines, iscas_case, u_num, PI_num):
    print(f"u_num: {u_num}")
    print(f"iscas_case: {iscas_case}")
    print(f"PI_num: {PI_num}")

### I/O parameters
    blif_lines.append(f".model {iscas_case}\n")
    blif_lines.append(".inputs ")
    blif_lines.extend(f"u{i} " for i in range(u_num))
    blif_lines.extend(f"v{i} " for i in range(u_num))
    blif_lines.extend(f"w{i} " for i in range(u_num * 2))
    
    blif_lines.extend(f"x{i} " for i in range(PI_num))

    blif_lines.append("c d\n")
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

### u, v the same
    blif_lines.append(f".subckt UequV{u_num} ")
    blif_lines.extend(f"U{i}=u{i} " for i in range(u_num))
    blif_lines.extend(f"V{i}=v{i} " for i in range(u_num))
    blif_lines.append("O_equal=uvsame\n")

### c, d (y1, y2) the same
    blif_lines.append(f".subckt equiv ")
    blif_lines.append(f"I0=c I1=d ")
    blif_lines.append("O=cdsame\n")

### c, d (y1, y2) xor
    blif_lines.append(f".subckt xor2 I0=c I1=d O=cdxor\n")

### Or all Wi
    blif_lines.append(f".subckt or{u_num * 2} ")
    blif_lines.extend(f"I{i}=w{i} " for i in range(u_num * 2))
    blif_lines.append("O=orwis\n")

### main circuit

    blif_lines.append(".subckt imply I0=uvsame I1=cdsame O=phi1\n")

    blif_lines.append(f".subckt or2 I0=cdxor I1=orwis O=fi\n")
    blif_lines.append(f".subckt imply I0=euvx I1=fi O=phi2\n")

    blif_lines.append(".subckt and2 I0=phi1 I1=phi2 O=f\n")
    
    blif_lines.append(".end\n\n")

def maxcut_add_subcircuit(blif_lines, u_num):
    add_or_num(blif_lines, 2)
    add_and_num(blif_lines, 2)
    add_imply_gate(blif_lines)
    add_equiv_gate(blif_lines)
    add_nequiv_gate(blif_lines)
    add_and_num(blif_lines, u_num)

    add_UequivV(blif_lines, u_num)
    add_or_num(blif_lines, 2 * u_num)

if __name__ == "__main__":
    # Check if the script is being run directly
    # Parse command line arguments
    if len(sys.argv) > 2:
        print("Usage: python blif_gen_iscas_hamiltonian.py <iscas_case>")
        sys.exit(1)

    iscas_case = sys.argv[1]

    input_file = f"./benchmarks/{iscas_case}.blif"
    output_file = f"./sample/{iscas_case}_maxcut.blif"

    blif_lines = []

    u_num, PI_num = parse_bench()
    maxcut_add_main_model(blif_lines, iscas_case, u_num, PI_num)
    add_implicit_graph(blif_lines, input_file)
    print("\nAdding graph subcircuit...")

    maxcut_add_subcircuit(blif_lines, u_num)
    print("\nWriting blif file...")
    with open(output_file, "w") as f:
        f.writelines(blif_lines)
    print("\nGenerate blif file successfully!\n")