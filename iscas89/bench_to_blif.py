## Call abc -f to_cnf.sh to convert the input file to CNF format

import os
# import subprocess
from subprocess import check_output
import sys

# working directory Dqbf_Graph_Coloring/iscas89
abc_dir = '../abc/'
abc_output = 'abc_output.txt'
iscas_bench_dir = './benchmarks/'

def gen_parse_bench_script(input_file):
    print('[log] Generating parse_bench.sh...')
    print(f'read input {iscas_bench_dir}{input_file}')
    print(f'write output {iscas_bench_dir}{blif_output}\n')

    with open(f'{iscas_bench_dir}parse_bench.sh', 'w') as f:
        f.write('read ' + iscas_bench_dir + input_file + '\n')
        f.write('fraig\n')
        f.write('strash\n')
        f.write('print_io\n')
        f.write('comb\n')
        f.write('write_blif ' + iscas_bench_dir + blif_output + '\n')
        f.write('quit\n')

def convert_to_blif(input_file):
    gen_parse_bench_script(input_file)

    # os.system('cd ' + abc_dir)
    # os.system('../abc -f to_cnf.sh')
    out = check_output([f'{abc_dir}abc', '-f', f'{iscas_bench_dir}parse_bench.sh'])
    # print(out.decode('utf-8'))
    with open(abc_output, 'w') as f:
        f.write(out.decode('utf-8'))
    
    # os.system(f'rm {iscas_bench_dir}parse_bench.sh')
    return

if __name__ == '__main__':
    bench_flie = sys.argv[1] + '.bench'
    blif_output = sys.argv[1] + '.blif'
    
    convert_to_blif(bench_flie)
