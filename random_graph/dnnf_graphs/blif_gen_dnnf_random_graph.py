import random
import itertools
import hashlib

class DNNFNode:
    _id_iter = itertools.count()

    def __init__(self, kind, children=None, var=None, neg=False):
        self.id = next(DNNFNode._id_iter)
        self.kind = kind        # 'AND', 'OR', 'LIT', 'TOP', 'BOT'
        self.children = children or []
        self.var = var
        self.neg = neg
        self.name = f"N{self.id}"

def random_partition(vars, k):
    random.shuffle(vars)
    return [vars[i::k] for i in range(k)]

def generate_dnnf(vars, depth, p_and=0.5):
    if not vars:
        return DNNFNode('TOP')

    if depth == 0 or len(vars) == 1:
        v = random.choice(vars)
        return DNNFNode('LIT', var=v, neg=random.choice([True, False]))

    r = random.random()

    # AND node (decomposable)
    if r < p_and:
        k = random.randint(2, min(3, len(vars)))
        blocks = random_partition(vars[:], k)
        children = [generate_dnnf(b, depth - 1, p_and) for b in blocks]
        return DNNFNode('AND', children)

    # OR node
    else:
        k = random.randint(2, 3)
        children = [generate_dnnf(vars, depth - 1, p_and) for _ in range(k)]
        return DNNFNode('OR', children)

def emit_blif(node, lines):
    for c in node.children:
        emit_blif(c, lines)

    if node.kind == 'LIT':
        lines.append(f".names {node.var} {node.name}")
        if node.neg:
            lines.append("0 1\n")
        else:
            lines.append("1 1\n")

    elif node.kind == 'TOP':
        lines.append(f".names {node.name}")
        lines.append("1\n")

    elif node.kind == 'BOT':
        lines.append(f".names {node.name}\n")

    elif node.kind == 'AND':
        ins = " ".join(c.name for c in node.children)
        lines.append(f".names {ins} {node.name}")
        lines.append("".join("1" for _ in node.children) + " 1\n")

    elif node.kind == 'OR':
        ins = " ".join(c.name for c in node.children)
        lines.append(f".names {ins} {node.name}")
        for i in range(len(node.children)):
            pat = ["-"] * len(node.children)
            pat[i] = "1"
            lines.append("".join(pat) + " 1")
        lines.append("")

def generate_random_hierarchical_dnnf_blif(n, filename, depth=4, seed=None):
    if seed is not None:
        random.seed(seed)

    vars = [f"U{i}" for i in range(n)] + [f"V{i}" for i in range(n)]
    root = generate_dnnf(vars, depth)

    lines = []
    lines.append(f"# Random hierarchical DNNF with {n} variables, depth {depth} and seed {seed}")
    lines.append(".model graph")
    lines.append(".inputs " + " ".join(vars))
    lines.append(".outputs E\n")

    emit_blif(root, lines)

    lines.append(f".names {root.name} E")
    lines.append("1 1\n")
    lines.append(".end")

    with open(filename, "w") as f:
        f.write("\n".join(lines))

    print(f"Hierarchical random DNNF written to {filename}")

def make_seed(i, j, salt="arthur_dnnf"):
    h = hashlib.sha256(f"{salt}_{i}_{j}".encode()).digest()
    return int.from_bytes(h[:4], "little")

# Example usage:
if __name__ == "__main__":

    for i in range(3, 20):
        for j in range(5):

            # generate random seed for each file
            seed = make_seed(i, j)

            generate_random_hierarchical_dnnf_blif(
                n=i,
                filename=f"dnnf_graph_n{i}_{j}.blif",
                depth=i,
                seed=seed
            )
