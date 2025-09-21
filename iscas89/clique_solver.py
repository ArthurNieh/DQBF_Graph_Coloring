import networkx as nx

def read_graph_file(filename):
    """Reads the graph from a file."""
    """Make it nx.Graph()"""
    """Written in graph format"""
    """Example format:
        p edge 64 125
        e 1 2
        ...
"""
    G = nx.Graph()
    with open(filename, "r") as file:
        lines = file.readlines()
        for line in lines:
            if line.startswith("p edge"):
                parts = line.strip().split()
                size = int(parts[2])
                G.add_nodes_from(range(1, size + 1))
            elif line.startswith("e"):
                parts = line.strip().split()
                u, v = int(parts[1]), int(parts[2])
                G.add_edge(u, v)
    return G

def main():
    graph = read_graph_file("./sample/iscas_graph.txt")
    
    # solve max clique
    # max_clique = nx.max_weight_clique(graph, weight=None)
    max_clique = max(nx.find_cliques(graph), key=len)
    print("Max clique:", max_clique)
    print("Max clique size:", len(max_clique))

if __name__ == "__main__":
    main()
