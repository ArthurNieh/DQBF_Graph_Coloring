## Call abc -f to_cnf.sh to convert the input file to CNF format

import os
from pathlib import Path
# from subprocess import check_output
import sys
import argparse
from subprocess import Popen, PIPE

# Directory of *this* Python file
SCRIPT_DIR = Path(__file__).resolve().parent

# abc is in ../abc/ relative to this script
ABC_DIR = SCRIPT_DIR / ".." / "abc"
ABC_BIN = ABC_DIR / "abc"

def gen_parse_bench_script(input_file, blif_output):
    print('[log] Generating parse_bench.sh...')
    print(f'read input {input_file}')
    print(f'write output {blif_output}\n')

    script = (
        f"read {input_file}\n"
        "print_io\n"
        "comb\n"
        "fraig\n"
        "strash\n"
        f"write_blif {blif_output}\n"
        "quit\n"
    )
    return script

def convert_to_blif(input_file, blif_output, abc_output_file, abc_bin, abc_dir):
    script = gen_parse_bench_script(input_file, blif_output)

    p = Popen(
        [str(abc_bin)],
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        cwd=str(abc_dir),
        text=True
    )

    out, err = p.communicate(script)

    with open(abc_output_file, "w") as f:
        f.write(out)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Convert blif file to combinational format"
    )
    parser.add_argument("-i", "--input_file", type=str, required=True)
    parser.add_argument("-o", "--output_file", type=str, required=True)
    parser.add_argument("--abc", type=str, required=True)

    args = parser.parse_args()
    
    convert_to_blif(args.input_file, args.output_file, args.abc, ABC_BIN, ABC_DIR)