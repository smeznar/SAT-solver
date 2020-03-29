import sys, os, random

if __name__ == '__main__':
    if len(sys.argv) < 5:
        print("Usage: " + sys.argv[0] + " <output file> <variables> <clauses> <clause size>")
        sys.exit(1)

    num_vars = int(sys.argv[2])
    num_clauses = int(sys.argv[3])
    clause_size = int(sys.argv[4])

    path = os.path.dirname(sys.argv[0])
    if path != "":
        os.chdir(path)

    suff = None
    if os.path.exists("append_suffix"):
        with open("append_suffix", "r") as suff_f:
            suff = int(suff_f.readline())
        with open("append_suffix", "w") as suff_f:
            suff_f.write(str(suff + 1))

    out_path, out_ext = os.path.splitext(sys.argv[1])
    if suff != None:
        out_path += f"_{suff}"
    if out_ext == "":
        out_ext = ".txt"
    out_path += out_ext

    with open(out_path, "w") as f_out:
        f_out.write("c randomly generated formula in CNF\n")
        f_out.write(f"c clause size: {clause_size}\n")
        f_out.write("c\n")
        f_out.write(f"p cnf {num_vars} {num_clauses}\n")
        indices = list(range(1, num_vars + 1))
        for i in range(num_clauses):
            clause = random.sample(indices, clause_size)
            clause = " ".join([str(-i if random.choice([True, False]) else i) for i in clause])
            clause += " 0\n"
            f_out.write(clause)
