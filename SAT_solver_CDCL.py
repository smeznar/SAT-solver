import sys
import numpy as np

class Formula:
    def __init__(self, src_path: str):
        self.sat_clauses = []
        self.unsat_clauses = []
        with open(src_path, "r") as file:
            line = file.readline()
            while line[0] == "c":
                line = file.readline()
            self.num_of_vars = int(line.split()[2])
            self.negated = [0]*(self.num_of_vars+1)
            self.non_negated = [0]*(self.num_of_vars+1)
            for l in file:
                if not l == "":
                    self.add_clause(l.strip())

    def __str__(self):
        return " ∧ ".join([str(c) for c in self.unsat_clauses])

    def add_clause(self, clause_str: str):
        self.unsat_clauses.append(Clause(self, clause_str))

    def simplify(self, number: int, value: bool):
        # returns the list of newly satisfied clauses
        sat_clauses = []
        unsat_clauses = []
        for c in self.unsat_clauses:
            c.apply(number, value)
            if c.is_solved:
                sat_clauses.append(c)
            else:
                unsat_clauses.append(c)
        self.sat_clauses.extend(sat_clauses)
        self.unsat_clauses = unsat_clauses
        return sat_clauses

    def undo(self, number: int, modified: list = None):
        for c in self.unsat_clauses:
            c.undo(number)
        if modified == None:
            for c in self.sat_clauses:
                c.undo(number)
                if not c.is_solved:
                    self.sat_clauses.remove(c)
                    self.unsat_clauses.append(c)
        else:
            for c in modified:
                c.undo(number)
                self.sat_clauses.remove(c)
                self.unsat_clauses.append(c)

    def find_unit_clause(self):
        for c in self.unsat_clauses:
            if len(c) == 1:
                unused = c.unused_literals[0]
                return (unused.number, not unused.is_negated), [i.number for i in c.used_literals]
        return None, None

    def contains_empty(self):
        for c in self.unsat_clauses:
            if len(c) == 0:
                return True
        return False

    def find_empty_clause(self):
        for c in self.unsat_clauses:
            if len(c) == 0:
                return [i.number for i in c.used_literals]
        return None

    def find_pure(self):
        for i,(n1,n2) in enumerate(zip(self.negated,self.non_negated)):
            if n1 == 0 and n2 > 0:
                return i, True
            elif n2 == 0 and n1 > 0:
                return i, False
        return None, None

    def add_induced_clause(self, causes):
        new_clause = Clause(self, None)
        for c in causes: # c = (int, bool)
            new_literal = Literal(new_clause, None)
            new_literal.number = c[0]
            new_literal.is_negated = c[1] # value of literal must be false with current assignment
            new_clause.used_literals.append(new_literal)
        self.unsat_clauses.append(new_clause)

    def get_literal(self):
        # TODO: smarter literal extraction
        return self.unsat_clauses[0].unused_literals[0].number, not self.unsat_clauses[0].unused_literals[0].is_negated


class Clause:
    def __init__(self, f: Formula, clause_str: str):
        self.super = f
        self.unused_literals = []
        self.used_literals = []
        self.is_solved = False
        self.solving_var = None
        if clause_str is not None:
            literals = clause_str.split()
            for l in literals[:-1]:
                self.unused_literals.append(Literal(self, l))

    def __str__(self):
        return f"({' ∨ '.join([str(l) for l in self.unused_literals])}"

    def __len__(self):
        return len(self.unused_literals)

    def apply(self, number: int, value: bool):
        literals = list(filter(lambda l: l.number == number, self.unused_literals))
        if len(literals) > 0:
            for l in literals:
                if l.eval(value):
                    self.is_solved = True
                    self.solving_var = number
            if self.is_solved:
                for l in self.unused_literals:
                    if l.is_negated:
                        self.super.negated[l.number] -= 1
                    else:
                        self.super.non_negated[l.number] -= 1
            else:
                for l in literals:
                    self.unused_literals.remove(l)
                    self.used_literals.append(l)
                    if l.is_negated:
                        self.super.negated[l.number] -= 1
                    else:
                        self.super.non_negated[l.number] -= 1

    def undo(self, number: int):
        # literals = filter(lambda l: l.number == number, self.used_literals)
        if self.is_solved:
            if self.solving_var == number:
                self.is_solved = False
                self.solving_var = None
                for l in self.unused_literals:
                    if l.is_negated:
                        self.super.negated[l.number]+=1
                    else:
                        self.super.non_negated[l.number]+=1
        else:
            for l in self.used_literals:
                if l.number == number:
                    self.unused_literals.append(l)
                    self.used_literals.remove(l)
                    if l.is_negated:
                        self.super.negated[number] += 1
                    else:
                        self.super.non_negated[number] += 1


class Literal:
    def __init__(self, c: Clause, literal_str):
        self.super = c
        self.is_negated = False
        self.number = 0
        if literal_str is not None:
            if literal_str[0] == '-':
                self.is_negated = True
                literal_str = literal_str[1:]
                c.super.negated[int(literal_str)] += 1
            else:
                c.super.non_negated[int(literal_str)] += 1
            self.number = int(literal_str)

    def __str__(self):
        return f"{'-' if self.is_negated else ''}{self.number}"

    def eval(self, value):
        return value != self.is_negated


class Graph: # class that represents a directed graph
    class Node:
        def __init__(self, label):
            self.label = label
            self.prev = [] # list of nodes
            self.next = []

    def __init__(self):
        self.V = dict() # {name: Node}

    def __contains__(self, label):
        return label in self.V

    def add_node(self, label):
        if label in self.V:
            raise NameError(f"Node {label} already exists!")
        newNode = self.Node(label)
        self.V[label] = newNode

    def delete_node(self, label):
        if label in self.V:
            node = self.V[label]
            for e in node.prev:
                e.next.remove(node)
            for e in node.next:
                e.prev.remove(node)
            del node
            del self.V[label]
        else:
            NameError(f"Node {label} does not exist!")

    def connect(self, start, end):
        if start in self.V:
            if end in self.V:
                start_node = self.V[start]
                end_node = self.V[end]
                start_node.next.append(end_node)
                end_node.prev.append(start_node)
            else:
                NameError(f"Node {end} does not exist!")
        else:
            NameError(f"Node {start} does not exist!")

    def prev(self, label):
        if label in self.V:
            return [i.label for i in self.V[label].prev]
        else:
            NameError(f"Node {label} does not exist!")

    def next(self, label):
        if label in self.V:
            return [i.label for i in self.V[label].next]
        else:
            NameError(f"Node {label} does not exist!")


class CDCL:
    def __init__(self, f: Formula):
        self.formula = f
        self.solution = [] # (int, bool) list
        self.impl_graph = Graph()
        self.graph_assigns = dict() # {int: (int, bool, int)}
        self.conflict = None

    def solve(self):
        if self.search(0):
            return [(i[0], i[1]) for i in self.solution]
        return None

    # search for a solution, return whether a solution was found
    # and the backtracking decision level beta
    def search(self, d: int):
        if self.decide(d):
            return True, None
        while True:
            if not self.deduce(d):
                success, beta = self.search(d + 1)
                if success:
                    return True, None
                elif beta != d:
                    self.erase(d)
                    return False, beta
            success, beta = self.diagnose(d)
            if not success:
                self.erase(d)
                return False, beta
            self.erase(d)

    # choose a variable assignment, return whether the assignment solves the formula
    def decide(self, d: int):
        if len(self.formula.unsat_clauses) > 0:
            var, val = self.formula.get_literal()
            self.formula.simplify(var, val)
            self.solution.append((var, val, d))
            self.impl_graph.add_node((var, val, d))
            self.graph_assigns[var] = (var, val, d)
        if len(self.formula.unsat_clauses) == 0:
            return True
        return False

    # find a conflict or resolve all implications, return whether a conflict occured
    def deduce(self, d: int):
        loop = True
        while loop:
            loop = False
            unsat = self.formula.find_empty_clause() # None or int list
            if unsat != None:
                # arrived at a conflict => create conflict node
                self.conflict = [self.graph_assigns[i] for i in unsat]
                return True
            unused, used = self.formula.find_unit_clause()
            if unused != None:
                # found a unit clause => simplify formula
                self.formula.simplify(*unused)
                self.solution.append((*unused, d))
                try:
                    causes = [self.graph_assigns[i] for i in used]
                except:
                    pass
                node = (unused[0], unused[1], d)
                self.graph_assigns[unused[0]] = node
                self.impl_graph.add_node(node)
                for i in causes:
                    self.impl_graph.connect(i, node)
                loop = True
        return False
        # TODO: add pure variable processing here?

    # computes a list of causes and maximum of their depths
    def causes_of(self, node):
        prevs = self.impl_graph.prev(node)
        if len(prevs) == 0:
            # the value was decided
            return [(node[0], node[1], node[2])], node[2]
        ret = []
        max_depth = -1
        for i in prevs:
            if i[2] < node[2]:
                # cause from lower depth
                ret.append(i)
                max_depth = max(max_depth, i[2])
            else:
                # cause from same depth => recurse
                causes, rec_depth = self.causes_of(i)
                ret.extend(causes)
                max_depth = max(max_depth, rec_depth)
        return ret, max_depth

    def causes_of_conflict(self, d):
        ret = []
        max_depth = -1
        for i in self.conflict:
            if i[2] < d:
                # cause from lower depth
                ret.append(i)
                max_depth = max(max_depth, i[2])
            else:
                # cause from same depth => recurse
                causes, rec_depth = self.causes_of(i)
                ret.extend(causes)
                max_depth = max(max_depth, rec_depth)
        # make the causes unique
        return list(set(ret)), max_depth

    # tries to resolve the problem on the current level,
    # otherwise returns the level beta to backtrack
    def diagnose(self, d):
        induced, beta = self.causes_of_conflict(d)
        if beta < d:
            self.conflict = induced
            return False, beta
        self.formula.add_induced_clause(induced)
        return True, None

    def erase(self, d: int):
        for i in reversed(self.solution):
            if i[2] < d:
                return
            self.solution.pop()
            del self.graph_assigns[i[0]]
            self.impl_graph.delete_node(i)
            self.formula.undo(i[0])



def write_output(file, solution):
    f = open(file, 'w')
    if solution is None:
        f.write('0')
    else:
        for (var, val) in solution:
            if val:
                f.write(str(var) + ' ')
            else:
                f.write('-' + str(var) + ' ')
    f.close()


def prettyPrintResult(result, division = 6):
    if result == None:
        print("No solution!")
    else:
        temp = sorted(result, key = lambda x: x[0])
        chunks = len(temp) // division
        for i in range(chunks):
            prt = str(temp[i * division][0]) + ": " + str(temp[i * division][1])
            for j in range(1, division):
                prt += ",\t" + str(temp[i * division + j][0]) + ": " + str(temp[i * division + j][1])
            print(prt)
        if len(temp) > division * chunks:
            prt = str(temp[chunks * division][0]) + ": " + str(temp[chunks * division][1])
            for j in range(1, len(temp) - division * chunks):
                prt += ",\t" + str(temp[chunks*division+j][0]) + ": " + str(temp[chunks*division+j][1])
            print(prt)


def readSolution(file):
    with open(file, "r") as f_in:
        values = f_in.readline().split()
    ret = map(lambda x: int(x), values)
    ret = map(lambda y: (y, True) if y > 0 else (-y, False), ret)
    return list(ret)


def hexRepresentation(solution):
    ret = 0
    for i in range(len(solution)):
        if solution[i][1]:
            ret += pow(2, solution[i][0]-1)
    return hex(ret)


def check(formula, solution):
    for idx, val in solution:
        formula.simplify(idx, val)
    if len(formula.unsat_clauses) == 0:
        return True
    return False


if __name__ == '__main__':
    #if len(sys.argv) < 3:
    #    print("Usage: " + sys.argv[0] + " <input file> <output file>")
    #    sys.exit(1)
    verbose = True
    if verbose:
        print("Reading...")
    #formula = Formula(sys.argv[1])
    formula = Formula("tests/izraz.txt")
    if verbose:
        print("Solving...")
    solver = CDCL(formula)
    s = solver.solve()
    if verbose:
        print("Printing...")
    prettyPrintResult(s)
    #print(hexRepresentation(s))
    #print(hexRepresentation(readSolution(sys.argv[2])))
    print(check(Formula(sys.argv[1]), s))
    #write_output(sys.argv[2], s)

    '''
    # izpis za sudoku
    trues = list(map(lambda x: x[0] - 1, filter(lambda r: r[1], s)))
    nums = [(a % 9) for a in trues]
    x = [((a - b) // 9) % 9 for a, b in zip(trues, nums)]
    y = [(a - 9 * b - c) // 81 for a, b, c in zip(trues, x, nums)]
    sol = [(a + 1, b + 1, c + 1) for a, b, c in zip(y, x, nums)]
    sud = np.zeros((9, 9)).astype(int)
    for x, y, z in sol:
        sud[x - 1, y - 1] = z
    print(sud)
    '''