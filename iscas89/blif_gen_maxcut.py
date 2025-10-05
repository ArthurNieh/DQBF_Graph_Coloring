# blif_gen_maxcut.py
#
# This script generates a blif form Max-Cut problem.
# import functions from blif_gen_iscas_coloring.py
#
# Author: Arthur Nieh
# Date: 2025-08-11

import sys
from blif_gen_iscas_coloring import *
import argparse

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

def maxcut_add_main_model_2(blif_lines, iscas_case, u_num, PI_num, k_bits):
    # 子傑's formula
    print(f"u_num: {u_num}")
    print(f"iscas_case: {iscas_case}")
    print(f"PI_num: {PI_num}")
    print(f"k_bits: {k_bits}")

### I/O parameters
    blif_lines.append(f".model {iscas_case}\n")
    blif_lines.append(".inputs ")
    blif_lines.extend(f"u{i} " for i in range(u_num))
    blif_lines.extend(f"v{i} " for i in range(u_num))
    blif_lines.append("w ")

    blif_lines.extend(f"x{i} " for i in range(PI_num))
    blif_lines.extend(f"c{i} " for i in range(k_bits))
    blif_lines.extend(f"d{i} " for i in range(k_bits))
    blif_lines.append("\n.outputs f\n")

### Graph subcircuit
    # graph(u,v,x)
    # blif_lines.append(".subckt graph ")
    # blif_lines.extend(f"U{i}=u{i} " for i in range(u_num))
    # blif_lines.extend(f"V{i}=v{i} " for i in range(u_num))
    # blif_lines.extend(f"I{i}=x{i} " for i in range(PI_num))
    # blif_lines.append("E=e1\n")

    # blif_lines.append(".subckt graph ")
    # blif_lines.extend(f"U{i}=v{i} " for i in range(u_num))
    # blif_lines.extend(f"V{i}=u{i} " for i in range(u_num))
    # blif_lines.extend(f"I{i}=x{i} " for i in range(PI_num))
    # blif_lines.append("E=e2\n")
    # blif_lines.append(".subckt or2 I0=e1 I1=e2 O=euvx\n")
    blif_lines.append(".names euvx\n1\n")

### u, v the same
    blif_lines.append(f".subckt UequV{u_num} ")
    blif_lines.extend(f"U{i}=u{i} " for i in range(u_num))
    blif_lines.extend(f"V{i}=v{i} " for i in range(u_num))
    blif_lines.append("O_equal=uvsame\n")

### c, d (y1, y2) the same
    if k_bits > 1:
        blif_lines.append(f".subckt UequV{k_bits} ")
        blif_lines.extend(f"U{i}=c{i} " for i in range(k_bits))
        blif_lines.extend(f"V{i}=d{i} " for i in range(k_bits))
        blif_lines.append("O_equal=cdsame\n")
        ### c, d < k
        blif_lines.append(f".subckt fit_color_limit ")
        blif_lines.extend(f"I{i}=c{i} " for i in range(k_bits))
        blif_lines.append(f"G=cfitlimit\n")

        blif_lines.append(f".subckt fit_color_limit ")
        blif_lines.extend(f"I{i}=d{i} " for i in range(k_bits))
        blif_lines.append(f"G=dfitlimit\n")

        blif_lines.append(f".subckt and2 I0=cfitlimit I1=dfitlimit O=cutfit\n")

    elif k_bits == 1:
        blif_lines.append(f".subckt equiv ")
        blif_lines.append(f"I0=c0 I1=d0 ")
        blif_lines.append("O=cdsame\n")
    else:
        print("k_bits should be at least 1")
        sys.exit(1)

### c, d (y1, y2) not same
    blif_lines.append(f".subckt not I=cdsame O=cdnotsame\n")

### main circuit
    blif_lines.append(".subckt and2 I0=uvsame I1=cdsame O=phi1\n")

    blif_lines.append(f".subckt and2 I0=euvx I1=cdnotsame O=fi\n")
    blif_lines.append(f".subckt and2 I0=fi I1=w O=phi2\n")  

    if k_bits > 1:
        blif_lines.append(".subckt or2 I0=phi1 I1=phi2 O=phi12\n")
        blif_lines.append(".subckt and2 I0=phi12 I1=cutfit O=f\n")
    else:
        blif_lines.append(".subckt or2 I0=phi1 I1=phi2 O=f\n")
    # blif_lines.append(".subckt and2 I0=euvx I1=w O=f\n")
    
    blif_lines.append(".end\n\n")

def maxcut_add_subcircuit_2(blif_lines, u_num, k_bits, k_cut):
    add_not_gate(blif_lines)
    add_or_num(blif_lines, 2)
    add_and_num(blif_lines, 2)
    add_and_num(blif_lines, u_num)
    add_equiv_gate(blif_lines)
    add_UequivV(blif_lines, u_num)
    
    if u_num != k_bits and k_bits > 1:
        add_and_num(blif_lines, k_bits)
        add_UequivV(blif_lines, k_bits)

    if k_bits > 1:
        add_fit_color_limit(blif_lines, k_cut, k_bits)
        add_or_num(blif_lines, k_bits)
    

if __name__ == "__main__":
    # Check if the script is being run directly
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Generate BLIF for Max-Cut problem.")
    parser.add_argument("--case", type=str, help="Name of the ISCAS case", required=True)
    parser.add_argument("-k", type=int, default=2, help="Value of k for the Max-Cut problem")
    parser.add_argument("--version", type=int, default=2, help="Version of the Max-Cut encoding (1 or 2)\n1: original version\n2: version by 子傑", choices=[1, 2])
    args = parser.parse_args()

    iscas_case = args.case
    k_cut = args.k
    version = args.version

    input_file = f"./benchmarks/{iscas_case}.blif"
    output_file = f"./sample/{iscas_case}_maxcut.blif"

    blif_lines = []

    u_num, PI_num = parse_bench()
    k_bits = (k_cut - 1).bit_length()
    print(f"u_num: {u_num}, PI_num: {PI_num}, k_bits: {k_bits}")

    if version == 2:
        maxcut_add_main_model_2(blif_lines, iscas_case, u_num, PI_num, k_bits)
        maxcut_add_subcircuit_2(blif_lines, u_num, k_bits, k_cut)
        # add_and_num(blif_lines, 2)
    else:
        maxcut_add_main_model(blif_lines, iscas_case, u_num, PI_num)
        maxcut_add_subcircuit(blif_lines, u_num)
    
    add_implicit_graph(blif_lines, input_file)
    print("\nAdding graph subcircuit...")

    print("\nWriting blif file...")
    with open(output_file, "w") as f:
        f.writelines(blif_lines)
    print("\nGenerate blif file successfully!\n")