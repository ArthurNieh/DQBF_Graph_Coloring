# blif_gen_iscas_edge.py
#
# This script generates a blif form edge coloring problem for the ISCAS89 benchmark circuits.
# import functions from blif_gen_iscas_coloring.py
#
# Author: Arthur Nieh
# Date: 2025-05-05

from blif_gen_iscas_coloring import *
import sys


def edge_add_main_model(blif_lines, iscas_case, u_num, PI_num):
    print(f"u_num: {u_num}")
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
    
    blif_lines.extend(f"c{i} " for i in range(c_num))
    blif_lines.extend(f"d{i} " for i in range(c_num))
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
    blif_lines.extend(f"U{i}=u{i} " for i in range(u_num))
    blif_lines.extend(f"V{i}=w{i} " for i in range(u_num))
    blif_lines.extend(f"I{i}=y{i} " for i in range(PI_num))
    blif_lines.append("E=e3\n")

    blif_lines.append(".subckt graph ")
    blif_lines.extend(f"U{i}=w{i} " for i in range(u_num))
    blif_lines.extend(f"V{i}=u{i} " for i in range(u_num))
    blif_lines.extend(f"I{i}=y{i} " for i in range(PI_num))
    blif_lines.append("E=e4\n")
    blif_lines.append(".subckt or2 I0=e3 I1=e4 O=euwy\n")

    blif_lines.append(".subckt and2 I0=euvx I1=euwy O=eu\n")

### u, v, w not the same
    blif_lines.append(f".subckt UneqV{u_num} ")
    blif_lines.extend(f"U{i}=u{i} " for i in range(u_num))
    blif_lines.extend(f"V{i}=v{i} " for i in range(u_num))
    blif_lines.append("O_equal=uvnotsame\n")

    blif_lines.append(f".subckt UneqV{u_num} ")
    blif_lines.extend(f"U{i}=u{i} " for i in range(u_num))
    blif_lines.extend(f"V{i}=w{i} " for i in range(u_num))
    blif_lines.append("O_equal=uwnotsame\n")
    
    blif_lines.append(f".subckt UneqV{u_num} ")
    blif_lines.extend(f"U{i}=v{i} " for i in range(u_num))
    blif_lines.extend(f"V{i}=w{i} " for i in range(u_num))
    blif_lines.append("O_equal=vwnotsame\n")
    blif_lines.append(".subckt not I=vwnotsame O=vwsame\n")
    
    blif_lines.append(".subckt and2 I0=uvnotsame I1=uwnotsame O=unotsame\n")

### color subcircuit
    blif_lines.append(".subckt color_not_equal ")
    blif_lines.extend(f"C{i}=c{i} " for i in range(c_num))
    blif_lines.extend(f"D{i}=d{i} " for i in range(c_num))
    blif_lines.append("O_nequal=ncolor\n")
    blif_lines.append(".subckt not I=ncolor O=color\n")

### color limit
    blif_lines.append(".subckt fit_color_limit ")
    blif_lines.extend(f"I{i}=c{i} " for i in range(c_num))
    blif_lines.append("G=clessthan\n")

    blif_lines.append(".subckt fit_color_limit ")
    blif_lines.extend(f"I{i}=d{i} " for i in range(c_num))
    blif_lines.append("G=dlessthan\n")
    blif_lines.append(".subckt and2 I0=clessthan I1=dlessthan O=colorencode\n")
    
### main circuit

    blif_lines.append(".subckt and2 I0=eu I1=vwnotsame O=evwnot\n")
    blif_lines.append(".subckt imply I0=evwnot I1=ncolor O=evwnotcolor\n")

    blif_lines.append(".subckt and2 I0=eu I1=vwsame O=evwsame\n")
    blif_lines.append(".subckt imply I0=evwsame I1=color O=evwsamecolor\n")

    blif_lines.append(".subckt and2 I0=evwnotcolor I1=evwsamecolor O=ecolor\n")
    blif_lines.append(".subckt imply I0=unotsame I1=ecolor O=unotsameecolor\n")

    blif_lines.append(".subckt and2 I0=unotsameecolor I1=colorencode O=f\n")
    
    blif_lines.append(".end\n\n")

def edge_add_subcircuit(blif_lines, u_num, c_num, colorability):
    add_not_gate(blif_lines)
    add_or_num(blif_lines, 2)
    add_and_num(blif_lines, 2)
    add_imply_gate(blif_lines)    #
    add_equiv_gate(blif_lines)    #
    add_nequiv_gate(blif_lines)   # xor2
    add_or_num(blif_lines, u_num)   #
    add_and_num(blif_lines, u_num)  #
    add_UnequivV(blif_lines, u_num) #
    if u_num != c_num: 
        if c_num != 2:
            add_or_num(blif_lines, c_num)
        # add_UnequivV(blif_lines, c_num)
    add_fit_color_limit(blif_lines, colorability, c_num)

if __name__ == "__main__":
    # Check if the script is being run directly
    # Parse command line arguments
    if len(sys.argv) > 3:
        print("Usage: python blif_gen_iscas_triangular.py <iscas_case> <colorability>")
        sys.exit(1)

    iscas_case = sys.argv[1]
    colorability = int(sys.argv[2])

    c_num = d_num = c_digits = math.ceil(math.log2(colorability))

    input_file = f"./benchmarks/{iscas_case}.blif"
    output_file = f"./sample/{iscas_case}_edge.blif"

    blif_lines = []

    u_num, PI_num = parse_bench()
    edge_add_main_model(blif_lines, iscas_case, u_num, PI_num)
    add_implicit_graph(blif_lines, input_file)
    print("\nAdding graph subcircuit...")
    add_color_not_equal(blif_lines, c_num)
    edge_add_subcircuit(blif_lines, u_num, c_num, colorability)
    print("\nWriting blif file...")
    with open(output_file, "w") as f:
        f.writelines(blif_lines)
    print("\nGenerate blif file successfully!\n")