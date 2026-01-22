# Simplify smv benchmark circuits
# This script is used to replace some latch in the smv circuits with constants
# to create a simplified version of the circuit with less latch.

# Find latch:
    # .latch c1 l2 0
    # .latch i86 l154 0
    # .latch i84 l158 0
    # .latch i80 l162 0
    # .latch i76 l168 0
    # .latch i72 l172 0
    # Delete some of the lines directly, keep n of the latches
import argparse

def read_file(file_path):
    with open(file_path, 'r') as f:
        return f.readlines()

def write_file(file_path, lines):
    with open(file_path, 'w') as f:
        f.writelines(lines)

def simplify_blif(lines, num_latches_to_keep=3):
    latch_lines = []
    header_lines = []
    other_lines = []

    seen_latches = False

    # First pass: collect latch lines
    for line in lines:
        if line.strip().startswith(".latch"):
            latch_lines.append(line)
            seen_latches = True
        elif not seen_latches:
            header_lines.append(line)
        else:
            other_lines.append(line)

    # Decide which latches to keep
    if len(latch_lines) < num_latches_to_keep:
        # Keep all latches
        print(f"Warning: Number of latches in the circuit ({len(latch_lines)}) is less than the number to keep ({num_latches_to_keep}). Keeping all latches.", file=sys.stderr)
        num_latches_to_keep = len(latch_lines)
        
    kept_latches = latch_lines[-num_latches_to_keep:] if num_latches_to_keep > 0 else []
    removed_latches = latch_lines[:-num_latches_to_keep] if num_latches_to_keep > 0 else latch_lines

    new_lines = []
    new_lines.extend(header_lines)

    # Add kept latches
    new_lines.extend(kept_latches)

    # Replace removed latches with constants
    for line in removed_latches:
        tokens = line.strip().split()
        # .latch <in> <out> [init]
        out_signal = tokens[2]
        init_val = tokens[3] if len(tokens) > 3 else "0"

        # BLIF constant definition
        new_lines.append(f".names {out_signal}\n")
        if init_val == "1":
            new_lines.append("1\n")
        else:
            new_lines.append("0\n")

    # Add the rest of the lines
    new_lines.extend(other_lines)

    return new_lines

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Simplify BLIF circuits by replacing latches with constants"
    )
    parser.add_argument("-i", "--input_file", type=str, required=True)
    parser.add_argument("-o", "--output_file", type=str)
    parser.add_argument(
        "-n", "--num_latches_to_keep",
        type=int,
        default=3,
        help="Number of latches to keep (keep last N)"
    )

    args = parser.parse_args()

    if not args.output_file:
        args.output_file = args.input_file.replace('.blif', '_simplified.blif').replace('blif/', 'simplified_blif/')

    if args.num_latches_to_keep < 0:
        raise ValueError("Number of latches to keep must be non-negative")

    lines = read_file(args.input_file)
    simplified = simplify_blif(lines, args.num_latches_to_keep)
    write_file(args.output_file, simplified)
