from pyscipopt import Model

def read_graph(filename):
    """
    Reads a graph file in this format:
      p edge <num_nodes> <num_edges>
      e u v
    Returns:
      n: number of nodes (assumes nodes are 1..n)
      edges: list of (u, v) tuples, 1-based
    """
    edges = []
    n = None
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if parts[0] == 'p':
                # “p edge 8 7”
                if len(parts) >= 4 and parts[1] == 'edge':
                    n = int(parts[2])
                    m = int(parts[3])  # edges count, we may ignore
            elif parts[0] == 'e':
                # “e 1 2”
                if len(parts) >= 3:
                    u = int(parts[1])
                    v = int(parts[2])
                    edges.append((u, v))
            else:
                # unknown / ignore
                pass
    if n is None:
        raise ValueError("File did not contain a \"p edge\" line")
    if len(edges) != m:
        print(f"Warning: expected {m} edges but found {len(edges)}")
    
    # This is undirected graph, remove all duplicates
    edges = list(set(tuple(sorted(edge)) for edge in edges))

    return n, edges

def build_max_k_cut_model(n, edges, K):
    """
    Build a SCIP model for the max-K-cut ILP (placeholder).
    n: number of nodes (1..n)
    edges: list of (u, v)
    K: desired number of partitions / cuts
    Returns: SCIP model, and any variable containers you’d like to track
    """
    model = Model("MaxKCut")

    # Example: you might introduce x[i, p] = 1 if node i is assigned to partition p
    x = {}  # dictionary (i, p) -> SCIP variable
    for i in range(1, n+1):
        for p in range(K):
            x[(i, p)] = model.addVar(f"x_{i}_{p}", vtype="BINARY")

    # Each node i must pick exactly one partition:
    for i in range(1, n+1):
        model.addCons(sum(x[(i, p)] for p in range(K)) == 1)

    # For each edge (i, j), if they are in different partitions, contribute +1 (or edge weight)
    # You may need extra variables or linearization depending on your formulation.
    # Placeholder: let d_{ij} be binary if edge is cut (i, j) across partitions
    d = {}
    for (i, j) in edges:
        d[(i, j)] = model.addVar(f"d_{i}_{j}", vtype="BINARY")
        # x_ip + x_jp + d_ij <= 2 for all p
        for p in range(K):
            model.addCons(x[(i, p)] + x[(j, p)] + d[(i, j)] <= 2)

    # Objective: maximize sum_{(i,j)} d_{(i,j)}
    model.setObjective(sum(d[(i, j)] for (i, j) in edges), "maximize")

    return model, x, d

def solve_max_k_cut(graph_filename, K):
    n, edges = read_graph(graph_filename)
    model, x, d = build_max_k_cut_model(n, edges, K)
    model.optimize()
    status = model.getStatus()
    print("Status:", status)
    if status == "optimal":
        obj = model.getObjVal()
        print("Objective value:", obj)
        # Retrieve the assignment
        assignment = {u: None for u in range(1, n+1)}
        for i in range(1, n+1):
            for p in range(K):
                if model.getVal(x[(i, p)]) > 0.5:
                    assignment[i] = p
                    break
        print("Assignment:", assignment)
    else:
        print("No optimal solution found.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python max_k_cut_scip.py <graphfile> <K>")
        sys.exit(1)
    graph_file = sys.argv[1]
    K = int(sys.argv[2])
    solve_max_k_cut(graph_file, K)
