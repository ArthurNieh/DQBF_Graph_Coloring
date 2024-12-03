### This file is used to generate explicit graph of sudoku

from math import sqrt


N = 16 # Size of Sudoku: N x N
n = int(sqrt(N)) # Size of subgrid: n x n
E = [] # List of edges

### Board to graph
#[ 0  1  2  3  4  5  6  7  8]
#[ 9 10 11 12 13 14 15 16 17]
# ...
#[72 73 74 75 76 77 78 79 80]

def add_edges():
    for i in range(N): # For each row
        for j in range(N): # For each column
            for k in range(i+1, N):
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
                            E.append(((i*n+k)*N+j*n+l, (i*n+m)*N+j*n+o))

def print_stats():
    print("N = " + str(N))
    print("n = " + str(n))
    print("total edge num = " + str(len(E)))

def print_graph():
    # print("total edge num = " + str(len(E)))
    for e in E:
        print(e[0], e[1])

def dump_graph():
    with open("./explicit/sudoku_graph.txt", "w") as f:
        f.write("p edge " + str(N*N) + " " + str(len(E)) + "\n")
        for e in E:
            f.write("e " + str(e[0]) + " " + str(e[1]) + "\n")

if __name__ == "__main__":
    if N != n*n:
        print("N is not a perfect square")
        exit(1)

    add_edges()
    E.sort(key = lambda x: (x[0], x[1])) # Sort the edges
    # print_graph()
    print_stats()
    dump_graph()
    
