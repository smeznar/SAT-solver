import sys
import copy
import numpy as np

class Formula:
    def __init__(self, variables: int, clauses: int):
        self.num_of_vars = variables
        self.num_of_clauses = clauses
        self.clauses = []
        self.negated = [0]*(variables+1)
        self.non_negated = [0]*(clauses+1)

    def __str__(self):
        ret = ""
        for c in self.clauses:
            ret += str(c)
            ret += " | "
        return ret[:-3]

    def __copy__(self):
        f = Formula(self.num_of_vars, self.num_of_clauses)
        f.clauses = [copy.copy(c) for c in self.clauses]
        f.negated = self.negated[:]
        f.non_negated = self.non_negated[:]
        return f

    def add_clause(self, clause_str: str):
        self.clauses.append(Clause(self, clause_str))

    def simplify(self, number: int, value: bool):
        # returns simplified formula and list of clauses that are removed/satisfied
        sat_clauses = []
        unsat_clauses = []
        for c in self.clauses:
            if c.does_it_solve(self, number, value):
                sat_clauses.append(c)
            else:
                unsat_clauses.append(c)
        self.clauses = unsat_clauses
        return self, sat_clauses

    def undo(self, number):
        for c in self.clauses:
            c.undo_clause(self, number)

    def find_unit_clause(self):
        for c in self.clauses:
            if len(c) == 1:
                return c.unused_literals[0].number, not c.unused_literals[0].is_negated
        return None, None

    def contains_empty(self):
        for c in self.clauses:
            if len(c) == 0:
                return True
        return False

    def find_pure(self):
        for i,(n1,n2) in enumerate(zip(self.negated,self.non_negated)):
            if n1 == 0 and n2 > 0:
                return i, True
            elif n2 == 0 and n1 > 0:
                return i, False
        return None, None

    def get_literal(self):
        return self.clauses[0].unused_literals[0].number, not self.clauses[0].unused_literals[0].is_negated


class Clause:
    def __init__(self, f: Formula, clause_str):
        self.unused_literals = []
        self.used_literals = []
        self.is_solved = False
        if clause_str is not None:
            literals = clause_str.split()
            for l in literals[:-1]:
                self.unused_literals.append(Literal(f, l))

    def __str__(self):
        return " ".join([str(l) for l in self.unused_literals])

    def __copy__(self):
        c = Clause(None, None) #! Should not be called! Clause constructor needs the parent formula!
        c.unused_literals = [copy.copy(l) for l in self.unused_literals]
        c.used_literals = [copy.copy(l) for l in self.used_literals]
        return c

    def __len__(self):
        return len(self.unused_literals)

    def does_it_solve(self, f: Formula, number: int, value: bool):
        literals = list(filter(lambda l: l.number == number, self.unused_literals))
        if len(literals) > 0:
            for l in literals:
                if l.eval(value):
                    self.is_solved = True
            if self.is_solved:
                for l in self.unused_literals:
                    if l.is_negated:
                        f.negated[l.number] -= 1
                    else:
                        f.non_negated[l.number] -= 1
            else:
                for l in literals:
                    self.unused_literals.remove(l)
                    self.used_literals.append(l)
                    if l.is_negated:
                        f.negated[l.number] -= 1
                    else:
                        f.non_negated[l.number] -= 1
        return self.is_solved

    def undo_clause(self, f: Formula, number: int):
        # literals = filter(lambda l: l.number == number, self.used_literals)
        if self.is_solved:
            self.is_solved = False
            for l in self.unused_literals:
                if l.is_negated:
                    f.negated[l.number]+=1
                else:
                    f.non_negated[l.number]+=1
        else:
            for l in self.used_literals:
                if l.number == number:
                    self.unused_literals.append(l)
                    self.used_literals.remove(l)
                    if l.is_negated:
                        f.negated[number] += 1
                    else:
                        f.non_negated[number] += 1


class Literal:
    def __init__(self, f: Formula, literal_str):
        self.is_negated = False
        self.number = 0
        if literal_str is not None:
            if literal_str[0] == '-':
                self.is_negated = True
                literal_str = literal_str[1:]
                f.negated[int(literal_str)] += 1
            else:
                f.non_negated[int(literal_str)] += 1
            self.number = int(literal_str)

    def __str__(self):
        if self.is_negated:
            return "-" + str(self.number)
        return str(self.number)

    def __copy__(self):
        l = Literal(None, None) #! Should not be called! Literal constructor needs the parent formula!
        l.is_negated = self.is_negated
        l.number = self.number
        return l

    def eval(self, value):
        return value != self.is_negated


def read_file(filename: str):
    with open(filename, "r") as file:
        line = file.readline()
        while line[0] == "c":
            line = file.readline()
        problem = line.split()
        num_of_vars = int(problem[2])
        num_of_clauses = int(problem[3])
        formula = Formula(num_of_vars, num_of_clauses)
        for l in file:
            if not l == "":
                formula.add_clause(l.strip())
        return formula


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


solution = []
def dpll(formula):
    #print(formula)
    if len(formula.clauses) == 0:
        return solution
    if formula.contains_empty():
        return None
    var, val = formula.find_unit_clause()
    if var is not None:
        f, clauses = formula.simplify(var,val)
        if dpll(f) is not None:
            solution.append((var,val))
            return solution
        else:
            f.clauses += clauses
            f.undo(var)
            #print(f, 'undo', var)
            return None

    var, val = formula.find_pure()
    if var is not None:
        f, clauses = formula.simplify(var,val)
        if dpll(f) is not None:
            solution.append((var,val))
            return solution
        else:
            f.clauses += clauses
            f.undo(var)
            #print(f, 'undo pure', var)
            return None
    else:
        n, b = formula.get_literal()
        f, clauses = formula.simplify(n, b)
        #print('poenostavi', n, 'true')
        if dpll(f) is not None:
            solution.append((n, b))
            return solution
        f.clauses += clauses
        f.undo(n)
        #print('undo',n)
        #print(f,'pred simplify 2')
        #print('poenostavi', n, 'false')
        f, clauses = f.simplify(n, not b)
        if dpll(f) is not None:
            solution.append((n, not b))
            return solution
        else:
            f.clauses += clauses
            f.undo(n)
            #print('undo', n)
            return None


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Not enough arguments")
        sys.exit(1)
    verbose = False
    if verbose:
        print("Reading...")
    formula = read_file(sys.argv[1])
    if verbose:
        print("Solving...")
    s = dpll(formula)
    prettyPrintResult(s)
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