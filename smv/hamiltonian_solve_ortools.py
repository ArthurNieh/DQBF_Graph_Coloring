"""Simple Travelling Salesperson Problem (TSP) between cities."""

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import argparse

def read_graph_file(filename):
    """Reads the graph from a file."""
    """Adjacency matrix of unweighted undirected graph (0: no edge, 1: edge)"""
    """Written in graph format"""
    """Example format:
        p edge 64 125
        e 1 2
        ...
        assume from 1 to 64
    """
    with open(filename, "r") as file:
        lines = file.readlines()
        adjacency_matrix = []
        for line in lines:
            if line.startswith("p edge"):
                parts = line.strip().split()
                size = int(parts[2])
                adjacency_matrix = [[0] * size for _ in range(size)]
            elif line.startswith("e"):
                parts = line.strip().split()
                u, v = int(parts[1]) - 1, int(parts[2]) - 1
                adjacency_matrix[u][v] = 1
                adjacency_matrix[v][u] = 1
    return adjacency_matrix, size

def read_data_file(filename):
    """Reads the data from a file."""
    """Adjacency matrix of unweighted undirected graph (0: no edge, 1: edge)"""
    """Written in .csv file"""
    with open(filename, "r") as file:
        lines = file.readlines()
        adjacency_matrix = []
        for line in lines:
            row = list(map(int, line.strip().split(",")))
            adjacency_matrix.append(row)
    return adjacency_matrix

def generate_adjacency_matrix(size):
    """Generates a random adjacency matrix of given size."""
    import random
    adjacency_matrix = [[0] * size for _ in range(size)]
    for i in range(size):
        for j in range(i + 1, size):
            if random.random() < 0.01:  # Randomly decide if there is an edge
                adjacency_matrix[i][j] = 1
                adjacency_matrix[j][i] = 1
    return adjacency_matrix

def create_data_model(filename="graph.txt"):
    data = {}
    # Adjacency matrix of unweighted undirected graph (0: no edge, 1: edge)
    # adjacency_matrix = read_data_file("adjacency_matrix_512.csv")
    # adjacency_matrix = generate_adjacency_matrix(2048)  # Generate a random matrix of size 512
    adjacency_matrix, var_num = read_graph_file(filename)  # Read from a file
    if not adjacency_matrix:
        raise ValueError("Adjacency matrix is empty. Please check the input file.")
    print("Adjacency matrix generated with size:", len(adjacency_matrix))
    # Convert adjacency matrix to distance matrix
    INF = var_num  # Large number to prevent routing through non-edges
    size = len(adjacency_matrix)
    # Use list comprehensions for efficiency
    distance_matrix = [
        [
            0 if i == j else (1 if adjacency_matrix[i][j] == 1 else INF)
            for j in range(size)
        ]
        for i in range(size)
    ]
    print("distance_matrix: ", distance_matrix)
    print("Distance matrix generated with size:", len(distance_matrix))

    data["distance_matrix"] = distance_matrix
    data["num_vehicles"] = 1
    data["depot"] = 0
    return data


def print_solution(manager, routing, solution):
    """Prints solution on console."""
    print(f"Objective: {solution.ObjectiveValue()} miles")
    index = routing.Start(0)
    plan_output = "Route for vehicle 0:\n"
    route_distance = 0
    while not routing.IsEnd(index):
        plan_output += f" {manager.IndexToNode(index)} ->"
        previous_index = index
        index = solution.Value(routing.NextVar(index))
        route_distance += routing.GetArcCostForVehicle(previous_index, index, 0)
    plan_output += f" {manager.IndexToNode(index)}\n"
    plan_output += f"Route distance: {route_distance}miles\n"
    print(plan_output)

    return route_distance


def main(input_file):
    """Entry point of the program."""
    # Instantiate the data problem.
    instance = input_file  # Change this to your graph file
    data = create_data_model(instance)

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(
        len(data["distance_matrix"]), data["num_vehicles"], data["depot"]
    )

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)


    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data["distance_matrix"][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if solution:
        route_distance = print_solution(manager, routing, solution)
        if route_distance == len(data["distance_matrix"]):
            print("The graph is Hamiltonian.")
        else:
            print("The graph is NOT Hamiltonian.")
    else:
        print("No solution found !")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Solve Hamiltonian Path Problem using OR-Tools.")
    parser.add_argument("-i", "--input_file", type=str, required=True, help="Path to the input graph file.")
    args = parser.parse_args()
    input_file = args.input_file
    
    main(input_file)