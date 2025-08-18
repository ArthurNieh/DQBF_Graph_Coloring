# Simplify benchmark for ISCAS89 circuits
# This script is used to replace some DFF in the ISCAS89 circuits with constants
# to create a simplified version of the circuit with less DFF.

# Modify:
    # "# 8 D-type flipflops"
    # the number of DFFs to keep
# Find DFF:
    # G5 = DFF(G10)
    # G6 = DFF(G11)
    # G7 = DFF(G13)
    # Delete some of the lines directly, keep n of the DFFs
import sys

def read_bench_file(file_path):
    with open(file_path, 'r') as file:
        return file.readlines()
    
def write_bench_file(file_path, lines):
    with open(file_path, 'w') as file:
        file.writelines(lines)

def simplify_bench(lines, num_dffs_to_keep=3):
    new_lines = []
    dff_count = 0
    
    for line in lines:
        if 'DFF' in line:
            if dff_count < num_dffs_to_keep:
                new_lines.append(line)
                dff_count += 1
            else:
                continue  # Skip this DFF
        elif 'flipflops' in line:
            # Modify the line to reflect the number of DFFs kept
            parts = line.split()
            if len(parts) > 1:
                parts[1] = str(num_dffs_to_keep)
                new_lines.append(' '.join(parts) + '\n')
        else:
            new_lines.append(line)
    
    return new_lines
    
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python simplify_bench.py <instance> <num_dffs_to_keep>")
        exit(1)
    
    dir_path = './benchmarks/'
    input_file = dir_path + sys.argv[1] + '.bench'
    output_file = dir_path + sys.argv[1] + '_simplified.bench'
    num_dffs_to_keep = int(sys.argv[2])
    
    if num_dffs_to_keep < 0:
        print("Number of DFFs to keep must be non-negative.")
        exit(1)
    
    lines = read_bench_file(input_file)
    simplified_lines = simplify_bench(lines, num_dffs_to_keep=num_dffs_to_keep)
    write_bench_file(output_file, simplified_lines)