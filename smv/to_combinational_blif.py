## Call abc -f to_cnf.sh to convert the input file to CNF format

import os
# import subprocess
from subprocess import check_output
import sys
import argparse

# working directory Dqbf_Graph_Coloring/iscas89
abc_dir = '../abc/'
abc_output = 'abc_output.txt'
iscas_bench_dir = './benchmarks/'

def gen_parse_bench_script(input_file, blif_output):
    print('[log] Generating parse_bench.sh...')
    print(f'read input {input_file}')
    print(f'write output {blif_output}\n')

    with open(f'{iscas_bench_dir}parse_bench.sh', 'w') as f:
        f.write('read ' + input_file + '\n')
        f.write('print_io\n')
        f.write('comb\n')
        f.write('fraig\n')
        f.write('strash\n')
        f.write('write_blif ' + blif_output + '\n')
        f.write('quit\n')

def convert_to_blif(input_file, blif_output):
    gen_parse_bench_script(input_file, blif_output)

    # os.system('cd ' + abc_dir)
    # os.system('../abc -f to_cnf.sh')
    out = check_output([f'{abc_dir}abc', '-f', f'{iscas_bench_dir}parse_bench.sh'])
    # print(out.decode('utf-8'))
    with open(abc_output, 'w') as f:
        f.write(out.decode('utf-8'))
    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Convert blif file to combinational format"
    )
    parser.add_argument("-i", "--input_file", type=str, required=True)
    parser.add_argument("-o", "--output_file", type=str, required=True)

    args = parser.parse_args()
    
    convert_to_blif(args.input_file, args.output_file)