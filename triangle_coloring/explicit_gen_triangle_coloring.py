## generate by chatGPT
## 2025/5/26

import networkx as nx
import itertools
import sys

def generate_triangle_adjacency_graph(n):
    # Step 1: Create the complete graph K_n
    G = nx.complete_graph(n)

    # Step 2: Find all triangles (3-cliques)
    triangles = [tuple(sorted(tri)) for tri in itertools.combinations(G.nodes, 3)
                 if G.has_edge(tri[0], tri[1]) and G.has_edge(tri[1], tri[2]) and G.has_edge(tri[0], tri[2])]

    # Step 3: Create the triangle graph
    triangle_graph = nx.Graph()

    # Add each triangle as a node (we label by the original nodes in the triangle)
    for i, tri in enumerate(triangles):
        triangle_graph.add_node(i, triangle=tri)

    # Step 4: Add edges between triangle nodes if they share an edge
    for i, tri1 in enumerate(triangles):
        for j in range(i + 1, len(triangles)):
            tri2 = triangles[j]
            shared_edges = set(itertools.combinations(tri1, 2)) & set(itertools.combinations(tri2, 2))
            if shared_edges:
                triangle_graph.add_edge(i, j)

    return triangle_graph, triangles

def dump_triangle_graph(graph, filename):
    with open(filename, 'w') as f:
        f.write(f"p edge {graph.number_of_nodes()} {graph.number_of_edges()}\n")
        for u, v in graph.edges:
            f.write(f"e {u+1} {v+1}\n")

if __name__ == "__main__":
    
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    
    # Example usage
    triangle_graph, triangles = generate_triangle_adjacency_graph(n)

    # print("Triangles (nodes in triangle graph):")
    # for i, tri in enumerate(triangles):
    #     print(f"Node {i}: Triangle {tri}")

    # print("\nEdges in triangle adjacency graph:")
    # for u, v in triangle_graph.edges:
    #     print(f"({u}, {v})")
    
    output_file = "triangle_adjacency_graph.txt"
    dump_triangle_graph(triangle_graph, output_file)
    print(f"\nTriangle adjacency graph dumped to {output_file}")
