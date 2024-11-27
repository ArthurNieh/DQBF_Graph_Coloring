## Call abc -f to_cnf.sh to convert the input file to CNF format

import os
# import subprocess
from subprocess import check_output
import sys
import re

dir = '/home/arthur/program/abc/dqbf/'
abc_output = 'abc_output.txt'

def gen_to_cnf_script(input_file, output_file):
    formula = ''
    with open(input_file, 'r') as f:
        formula = f.read()
    with open('to_cnf.sh', 'w') as f:
        f.write('read_formula ' + formula + '\n')
        f.write('strash\n')
        f.write('&get\n')
        f.write('&write_cnf ' + dir + output_file + '\n')
        # f.write('write_cnf ' + dir + output_file + '\n')
        f.write('quit\n')

def convert_to_cnf(input_file, output_file):
    gen_to_cnf_script(input_file, output_file)

    os.system('cd ' + dir)
    # os.system('../abc -f to_cnf.sh')
    # subprocess.run(['../abc', '-f', 'to_cnf.sh'])
    out = check_output(['../abc', '-f', 'to_cnf.sh'])
    # print(out.decode('utf-8'))
    with open(abc_output, 'w') as f:
        f.write(out.decode('utf-8'))
    
    os.system('rm to_cnf.sh')
    return

def parse_abc_output():
    print('[log] Parsing abc output...')
    ids, vars = [], []
    nCis = -1
    with open(abc_output, 'r') as f:
        lines = f.readlines()
    for line in lines:
        if 'id' in line:
            data = re.split('\<|\>', line)
            if 'id' in data[0]:
                ids.append(int(data[1]))
            else:
                print('[Error][parse abc]: id not found')
            if 'name' in data[2]:
                vars.append(str(data[3]))
            else:
                print('[Error][parse abc]: var name not found')
            # print(data)
        if 'stats' in line:
            data = re.sub(' ', '', line)
            data = re.split('=|\.', data)
            if 'Vars' in data[0]:
                nCis = int(data[1])
            else:
                print('[Error][parse abc]: Vars num not found')
            # print(data)
    return ids, vars, nCis
    

if __name__ == '__main__':
    convert_to_cnf(sys.argv[1], sys.argv[2])
    ids, vars, nCis= parse_abc_output()
    print(ids)
    print(vars)
    print(nCis)

