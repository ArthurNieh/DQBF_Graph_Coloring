# Reduce benchmark for ISCAS89 circuits
# This script is used to replace some DFF and Primary Inputs in the ISCAS89 circuits with constants
# to create a simplified version of the circuit with less DFF and PIs.

# Modify:
    # "# 8 D-type flipflops"
    # the number of DFFs to keep
# Find DFF:
    # G5 = DFF(G10)
    # G6 = DFF(G11)
    # G7 = DFF(G13)
    # Delete some of the lines directly, keep n of the DFFs
import sys
from subprocess import check_output

abc_dir = '../abc/'
abc_output = 'abc_output.txt'
iscas_bench_dir = './benchmarks/'


def read_bench_file(file_path):
    with open(file_path, 'r') as file:
        return file.readlines()
    
def write_bench_file(file_path, lines):
    with open(file_path, 'w') as file:
        file.writelines(lines)

def gen_reduce_bench2blif_script(input_bench, output_blif, script_file, num_dffs_to_keep, num_pis_to_keep):
    print(f'[log] Generating: {script_file}')
    print(f'[log] Keeping {num_dffs_to_keep} DFFs and {num_pis_to_keep} PIs in the benchmark.')

    with open(script_file, 'w') as f:
        f.write('read ' + input_bench + '\n')
        f.write('fraig\n')
        f.write('strash\n')
        f.write('print_io\n')
        f.write('comb\n')
        f.write('write_blif ' + output_blif + '\n')
        f.write('quit\n')

def reduce_bench(lines, num_dffs_to_keep=3, num_pis_to_keep=3):
    new_lines = []
    dff_count = 0
    pi_count = 0

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
                if int(parts[1]) >= num_dffs_to_keep:
                    print(f"Reducing flipflops from {parts[1]} to {num_dffs_to_keep}")
                    parts[1] = str(num_dffs_to_keep)
                else:
                    print(f"[Warning] Keeping flipflops at {parts[1]}")
                new_lines.append(' '.join(parts) + '\n')
        elif 'INPUT' in line:
            if pi_count < num_pis_to_keep:
                new_lines.append(line)
                pi_count += 1
            else:
                continue  # Skip this PI
        elif 'inputs' in line:
            # Modify the line to reflect the number of PIs kept
            parts = line.split()
            if len(parts) > 1:
                if int(parts[1]) >= num_pis_to_keep:
                    print(f"Reducing inputs from {parts[1]} to {num_pis_to_keep}")
                    parts[1] = str(num_pis_to_keep)
                else:
                    print(f"[Warning] Keeping inputs at {parts[1]}")
                new_lines.append(' '.join(parts) + '\n')
        elif 'OUTPUT' in line:
            continue  # Skip all OUTPUT lines
        else:
            new_lines.append(line)
    
    return new_lines

def gen_parse_reduce_bench_script(input_file, blif_output):
    print('[log] Generating parse_bench.sh...')
    print(f'read input {input_file}')
    print(f'write output {blif_output}\n')

    with open(f'{dir_path}parse_bench.sh', 'w') as f:
        f.write('read ' + input_file + '\n')
        f.write('print_io\n')
        f.write('comb\n')
        f.write('fraig\n')
        f.write('strash\n')
        f.write('write_blif ' + blif_output + '\n')
        f.write('quit\n')

def convert_to_blif(input_file, blif_output):
    gen_parse_reduce_bench_script(input_file, blif_output)

    # os.system('cd ' + abc_dir)
    # os.system('../abc -f to_cnf.sh')
    out = check_output([f'{abc_dir}abc', '-f', f'{dir_path}parse_bench.sh'])
    # print(out.decode('utf-8'))
    with open(abc_output, 'w') as f:
        f.write(out.decode('utf-8'))
    
    # os.system(f'rm {iscas_bench_dir}parse_bench.sh')
    return

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python simplify_bench.py <instance> <num_dffs_to_keep> <number of PIs to keep>")
        exit(1)
    
    dir_path = './benchmarks/'
    input_file = dir_path + sys.argv[1] + '.bench'
    output_file = dir_path + sys.argv[1] + '_simplified.bench'
    num_dffs_to_keep = int(sys.argv[2])
    num_pis_to_keep = int(sys.argv[3])
    
    if num_dffs_to_keep < 0:
        print("Number of DFFs to keep must be non-negative.")
        exit(1)

    if num_pis_to_keep < 0:
        print("Number of PIs to keep must be non-negative.")
        exit(1)

    lines = read_bench_file(input_file)
    simplified_lines = reduce_bench(lines, num_dffs_to_keep=num_dffs_to_keep, num_pis_to_keep=num_pis_to_keep)
    write_bench_file(output_file, simplified_lines)

    blif_output = dir_path + sys.argv[1] + '_simplified.blif'
    convert_to_blif(output_file, blif_output)
