# from graphviz import Graph
from collections import defaultdict
import itertools

def gen_line_graph(edges):
    # Original graph: edges defined by pairs of nodes
    # original_edges = [('A', 'B'), ('A', 'C'), ('B', 'C'), ('C', 'D')]

    original_edges = [(str(u), str(v)) for u, v in edges]

    # Step 1: Create original graph for visualization (optional)
    # original_graph = Graph('Original')
    # nodes = set(itertools.chain.from_iterable(original_edges))
    # for node in nodes:
    #     original_graph.node(node)
    # for u, v in original_edges:
    #     original_graph.edge(u, v)

    # original_graph.render('original_graph', view=True)
    # original_graph.render(filename="original_graph", format='png', cleanup=True)

    # Step 2: Build line graph structure
    # Map edge to a node name in the line graph
    # edge_to_node = {edge: f'e{i}' for i, edge in enumerate(original_edges)}
    edge_to_node = {edge: (i+1) for i, edge in enumerate(original_edges)}
    line_graph_edges = []

    # Compare all pairs of edges
    for (e1, e2) in itertools.combinations(original_edges, 2):
        # If the two edges share a vertex, connect their corresponding nodes
        if set(e1) & set(e2):
            n1 = edge_to_node[e1]
            n2 = edge_to_node[e2]
            line_graph_edges.append((n1, n2))

    # Step 3: Create line graph in Graphviz
    # line_graph = Graph('LineGraph')
    # for node in edge_to_node.values():
    #     line_graph.node(node)
    # for u, v in line_graph_edges:
    #     line_graph.edge(u, v)

    # line_graph.render('line_graph', view=True)
    # line_graph.render(filename="line_graph", format='png', cleanup=True)

    # Optional: print edge-to-node mapping
    print("Edge to Line Graph Node Mapping:")
    for edge, node in edge_to_node.items():
        print(f"{edge} -> {node}")
    
    return line_graph_edges
