
import random
import csv
import argparse

def generate_random_graph(num_nodes):
    """Generate a random row for hash random graph."""

    length = 2*num_nodes + 1

    num_rows = 1
    
    prob = 1/2

    row = [[1 if random.random() < prob else 0 for _ in range(length)] for _ in range(num_rows)]

    return row

def dump_row_csv(row, filename):
    """Dump a row to a CSV file."""
    with open(filename, 'w') as f:
        for r in row:
            f.write(','.join(map(str, r)))
            f.write('\n')

def main():
    parser = argparse.ArgumentParser(description="Generate a random graph.")
    # parser.add_argument('-n', type=int, default=10, help="Number of nodes in the graph")
    # args = parser.parse_args()

    for i in range(3, 20):
        for j in range(5):
            num_nodes = i
            row = generate_random_graph(num_nodes)
            print("Generated row:", row)
            filename = f'random_graph_n{num_nodes}_trial{j}.csv'
            dump_row_csv(row, filename)
            print(f"Row dumped to {filename}")

if __name__ == "__main__":
    main()