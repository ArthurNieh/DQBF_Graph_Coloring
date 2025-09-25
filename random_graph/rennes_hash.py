import math
import random
import csv
import argparse

def inverse_binary_entropy(p):
    """Inverse of the binary entropy function H(x)."""
    if not (0 <= p <= 1):
        raise ValueError("p must be in [0,1]")

    if p == 0:
        return 0.0
    if p == 1:
        return 0.5

    low, high = 0.0, 0.5
    while high - low > 1e-12:
        mid = (low + high) / 2.0
        h = -mid * math.log2(mid) - (1 - mid) * math.log2(1 - mid)
        if h < p:
            low = mid
        else:
            high = mid
    return (low + high) / 2.0


def rennes_hash(x, k=10):
    """Rennes hash function h(x) = A x + b (mod 2).

    Parameters
    ----------
    x : list[int]
        Boolean vector (list of 0/1).
    k : int
        Parameter controlling sparsity.

    Returns
    -------
    list[int]
        Hashed boolean vector (same length as x).
    """
    n = len(x)
    hashed_x = []

    A = []
    b = []

    for i in range(1, n + 1):  # rows indexed from 1..n
        # Step 1: compute delta
        delta = i / (i + math.log2(k))

        # Step 2: compute inverse entropy
        h_inverse = inverse_binary_entropy(delta)

        # Step 3: row density p_i
        if h_inverse > 0:
            pi = 16.0 / h_inverse * math.log2(i) / float(i) if i > 1 else 0.5
        else:
            pi = 0.5

        print(f"Row {i}: delta={delta:.4f}, h_inverse={h_inverse:.4f}, p_i={pi:.4f}")

        pi = min(0.5, pi)  # clamp to [0, 0.5]


        # Step 4: sample row A[i,*]
        row = [1 if random.random() < pi else 0 for _ in range(n)]
        A.append(row)

        # Step 5: compute dot product mod 2
        dot = sum(row[j] * x[j] for j in range(n)) % 2

        # Step 6: add random b[i]
        b_i = 1 if random.random() < 0.5 else 0
        b.append(b_i)
        hashed_x.append((dot + b_i) % 2)

    print("Matrix A:")
    for row in A:
        print(row)

    print("Vector b:")
    print(b)

    return hashed_x

def gen_hash_matrix(n, k=10):
    """Generate the hash matrix A and vector b for the Rennes hash function.

    Parameters
    ----------
    n : int
        Length of the boolean vector (list of 0/1).
    k : int
        Parameter controlling sparsity.

    Returns
    -------
    A : list[list[int]]
        Hash matrix (n x n) with entries in {0, 1}.
    b : list[int]
        Random vector (length n) with entries in {0, 1}.
    """
    A = []
    b = []

    for i in range(1, n + 1):  # rows indexed from 1..n
        # Step 1: compute delta
        delta = i / (i + math.log2(k))

        # Step 2: compute inverse entropy
        h_inverse = inverse_binary_entropy(delta)

        # Step 3: row density p_i
        if h_inverse > 0:
            pi = 16.0 / h_inverse * math.log2(i) / float(i) if i > 1 else 0.5
        else:
            pi = 0.5

        print(f"Row {i}: delta={delta:.4f}, h_inverse={h_inverse:.4f}, p_i={pi:.4f}")

        pi = min(0.5, pi)  # clamp to [0, 0.5]


        # Step 4: sample row A[i,*]
        row = [1 if random.random() < pi else 0 for _ in range(n)]
        A.append(row)

        # Step 6: add random b[i]
        b_i = 1 if random.random() < 0.5 else 0
        b.append(b_i)

    print("Matrix A:")
    for row in A:
        print(row)

    print("Vector b:")
    print(b)

    return A, b

def dump_matrix(matrix, filename):
    """Dump a matrix to a CSV file."""
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(matrix)

if __name__ == "__main__":
    # Example usage
    # x is a boolean vector with length 32
    # x = [1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 1, 0,
    #      1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1]
    # k = 512
    # hashed = rennes_hash(x, k)
    # print("Original:", x)
    # print("Hashed:", hashed)

    # input parameters specify n, use flag -n <value>
    parser = argparse.ArgumentParser(description="Generate Rennes hash matrix and vector.")
    parser.add_argument('-n', type=int, help='Length of the boolean vector (required)', required=True)
    parser.add_argument('-k', type=int, default=512, help='Parameter controlling sparsity (default: 512)')
    parser.add_argument('--output_dir', type=str, default='./graphs', help='Directory to save output files (default: current directory)')
    args = parser.parse_args()

    n = args.n
    k = args.k
    dir_path = args.output_dir
    A, b = gen_hash_matrix(n, k)
    # A is the hash matrix, b is the random vector

    # dump A and b to file
    dump_matrix(A, f"{dir_path}/hash_matrix_A_size_{n}.csv")
    dump_matrix([b], f"{dir_path}/hash_vector_b_size_{n}.csv")