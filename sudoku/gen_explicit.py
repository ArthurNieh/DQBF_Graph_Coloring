### This file is used to generate explicit graph of sudoku

from math import sqrt
import random
from sudoku_gen import Sudoku


output_file = "./explicit/sudoku_graph.txt"
sample_file = "./sample/sudoku.txt"

n = 3 # Size of subgrid: n x n
N = n*n # Size of Sudoku: N x N
remove_ratio = 0.7 # Ratio of digits to be removed
wrong_digit_num = 3 # Number of wrong digits to be added
K = int(N*N * remove_ratio) # Number of digits to be removed
E = [] # List of edges
Sudoku_game = [] # List of sudoku game
count_nonzero = 0

### Board to graph
# [ 9 10 11 12 13 14 15 16 17]
# [18 19 20 21 22 23 24 25 26]
# ...
# [72 73 74 75 76 77 78 79 80]

### Colors for inititializing the sudoku
# [ 0  1  2  3  4  5  6  7  8]

def generate_sudoku():
    # Create a Sudoku object
    # Functions import from sudoku_gen.py
    global N, K, sample_file
    sudoku = Sudoku(N, K)
    sudoku.fillValues()
    sudoku.printSudoku()
    sudoku.dumpSudoku(sample_file)

def initialize_sudoku_board():
    for i in range(1, N+1): # For each row
        for j in range(N): # For each column
            for k in range(i+1, N+1):
                E.append((i*N+j, k*N+j)) # Add edges in the same column
            for k in range(j+1, N):
                E.append((i*N+j, i*N+k)) # Add edges in the same row
    # For each subgrid
    for i in range(n):
        for j in range(n): 
            # For each cell in the subgrid
            for k in range(n):
                for l in range(n):
                    for m in range(k+1, n):
                        for o in range(n):
                            if o == l:
                                continue
                            E.append(((i*n+k+1)*N+j*n+l, (i*n+m+1)*N+j*n+o))
    for i in range(N):
        for j in range(i+1, N):
            E.append((i, j))

# Add edges for the initial sudoku game
def add_edge(color:int, node:int):
    for i in range(N):
        if i != color:
            E.append((i, node))
            # print("e " + str(i) + " " + str(node))
    return

def read_sudoku_game():
    global count_nonzero
    with open(sample_file, "r") as f:
        count_row = 1
        for line in f:
            # print(line)
            row = line.split()
            Sudoku_game.append(row)
            for i in range(N):
                # print(row[i])
                if row[i] == "0":
                    continue
                elif row[i] != "0" and row[i] <= "9" and row[i] >= "1":
                    add_edge(int(row[i])-1, count_row*N+i)
                    count_nonzero += 1
                else:
                    print("Invalid input")
                    exit(1)
            count_row += 1

def add_wrong_edge(num):
    while(num > 0):
        color = random.randint(0, N-1)
        i, j = 0, 0
        while(Sudoku_game[i][j] != "0"):
            i = random.randint(0, N-1)
            j = random.randint(0, N-1)
        node = (i+1)*N+j
        # if (color, node) not in E:
        print(str(node) + " in color " + str(color))
        for k in range(N):
            if k != color:
                E.append((k, node))
        num -= 1

def print_stats():
    global count_nonzero
    print("N = " + str(N))
    print("n = " + str(n))
    print("total edge num = " + str(len(E)))
    theoretical_edge_num = N*N*(3*N-2*n-1)/2
    print("theoretical edge num = " + str(int(theoretical_edge_num + count_nonzero*(N-1) + N*(N-1)/2)))

def print_graph():
    # print("total edge num = " + str(len(E)))
    for e in E:
        print(e[0], e[1])

def dump_graph():
    with open(output_file, "w") as f:
        f.write("p edge " + str(N*N) + " " + str(len(E)) + "\n")
        for e in E:
            f.write("e " + str(e[0]) + " " + str(e[1]) + "\n")

if __name__ == "__main__":
    if N != n*n:
        print("N is not a perfect square")
        exit(1)

    initialize_sudoku_board()
    generate_sudoku()
    read_sudoku_game()
    add_wrong_edge(wrong_digit_num)
    E.sort(key = lambda x: (x[0], x[1])) # Sort the edges
    # print_graph()
    print_stats()
    dump_graph()
