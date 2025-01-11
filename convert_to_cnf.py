## Call abc -f to_cnf.sh to convert the input file to CNF format

import os
# import subprocess
from subprocess import check_output
import sys
import re

dir = '/home/arthur/program/abc/dqbf/'
abc_output = 'abc_output.txt'

def gen_to_cnf_script(input_file, output_file):
    # formula = ''
    # with open(input_file, 'r') as f:
    #     formula = f.read()
    with open('to_cnf.sh', 'w') as f:
        f.write('read_blif ' + input_file + '\n')
        f.write('fraig\n')
        f.write('rf\n')
        f.write('rw\n')
        f.write('rs\n')
        f.write('dch\n')
        f.write('dc2\n')
        f.write('compress\n')
        f.write('compress2\n')
        f.write('b\n')
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
    nVar = -1
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
                nVar = int(data[1])
            else:
                print('[Error][parse abc]: Vars num not found')
            # print(data)
    nCis = len(ids)
    for i in range(nCis):
        ids[i] = nVar - (nCis - ids[i])
    return ids, vars, nCis, nVar

def determine_quantifier(ids, vars, nCis, nVar):
    vec_u, vec_v = [], []
    vec_c, vec_d = [], []
    vec_others = []

    for i in range(1, nVar - nCis +1):
        vec_others.append(i)

    for i in range(nCis):
        if 'u' in vars[i]:
            vec_u.append(ids[i])
        elif 'v' in vars[i]:
            vec_v.append(ids[i])
        elif 'c' in vars[i]:
            vec_c.append(ids[i])
        elif 'd' in vars[i]:
            vec_d.append(ids[i])
        else:
            vec_others.append(ids[i])
    return vec_u, vec_v, vec_c, vec_d, vec_others

def gen_DQDIMACS(cnf_file, v_u, v_v, v_c, v_d, v_others):
    with open(cnf_file, 'r') as f:
        lines = f.readlines()
    with open('dqdimacs.txt', 'w') as f:
        ignore = True
        for line in lines:
            if 'cnf' in line:
                f.write(line)
                ignore = False
                
                if len(v_u) > 0 or len(v_v) > 0:
                    f.write('a ')
                    if len(v_u) > 0:
                        f.write(''.join(str(u) + ' ' for u in v_u))
                    if len(v_v) > 0:
                        f.write(''.join(str(v) + ' ' for v in v_v))
                    f.write('0\n')

                if len(v_others) > 0:
                    f.write('e ')
                    f.write(''.join(str(o) + ' ' for o in v_others))
                    f.write('0\n')

                for c in v_c:
                    f.write('d ' + str(c) + ' ')
                    f.write(''.join(str(u) + ' ' for u in v_u))
                    f.write('0\n')

                for d in v_d:
                    f.write('d ' + str(d) + ' ')
                    f.write(''.join(str(v) + ' ' for v in v_v))
                    f.write('0\n')

            elif not ignore:
                f.write(line)
            else:
                continue
    return

    

if __name__ == '__main__':
    convert_to_cnf(sys.argv[1], sys.argv[2])
    ids, vars, nCis, nVar= parse_abc_output()
    print(ids)
    print(vars)
    print("Number of Cis = " + str(nCis))
    print("Number of Vars = " + str(nVar))

    vec_u, vec_v, vec_c, vec_d, vec_others = determine_quantifier(ids, vars, nCis, nVar)
    
    gen_DQDIMACS(sys.argv[2], vec_u, vec_v, vec_c, vec_d, vec_others)


