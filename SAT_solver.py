import sys
import copy


class Formula:
    def __init__(self, variables: int, clauses: int):
        self.num_of_vars = variables
        self.num_of_clauses = clauses
        self.clauses = []

    def __str__(self):
        ret = ""
        for c in self.clauses:
            ret += str(c)
            ret += " | "
        return ret

    def __copy__(self):
        f = Formula(self.num_of_vars, self.num_of_clauses)
        f.clauses = [copy.copy(c) for c in self.clauses]
        return f

    def add_clause(self, clause_str: str):
        self.clauses.append(Clause(clause_str))

    def simplify(self, number: int, value: bool):
        # returns simplified formula and list of clauses that are removed/satisfied
        sat_clauses = []
        unsat_clauses = []
        for c in self.clauses:
            if c.does_it_solve(number, value):
                sat_clauses.append(c)
            else:
                unsat_clauses.append(c)
        self.clauses = unsat_clauses
        return self, sat_clauses

    def undo(self, number):
        for c in self.clauses:
            c.undo_clause(number)

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
        # TODO !!!!
        pass

    def get_literal(self):
        return self.clauses[0].unused_literals[0].number

class Clause:
    def __init__(self, clause_str):
        self.unused_literals = []
        self.used_literals = []
        self.is_solved = False
        if clause_str is not None:
            literals = clause_str.split(" ")
            for l in literals[:-1]:
                self.unused_literals.append(Literal(l))

    def __str__(self):
        return " ".join([str(l) for l in self.unused_literals])

    def __copy__(self):
        c = Clause(None)
        c.unused_literals = [copy.copy(l) for l in self.unused_literals]
        c.used_literals = [copy.copy(l) for l in self.used_literals]
        return c

    def __len__(self):
        return len(self.unused_literals)

    # TODO: preden das da je kul poglej da ni recimo (p, r, !p)
    def does_it_solve(self, number: int, value: bool):
        literals = list(filter(lambda l: l.number == number, self.unused_literals))
        if len(literals) > 0:
            for l in literals:
                if l.eval(value):
                    self.is_solved = True
                    return True
                else:
                    self.unused_literals.remove(l)
                    self.used_literals.append(l)
        return False

    def undo_clause(self, number: int):
        literals = filter(lambda l: l.number == number, self.used_literals)
        for l in literals:
            self.is_solved = False
            self.unused_literals.append(l)
            self.used_literals.remove(l)


class Literal:
    def __init__(self, literal_str):
        self.is_negated = False
        self.number = 0
        if literal_str is not None:
            if literal_str[0] == '-':
                self.is_negated = True
                literal_str = literal_str[1:]
            self.number = int(literal_str)

    def __str__(self):
        if self.is_negated:
            return "-" + str(self.number)
        return str(self.number)

    def __copy__(self):
        l = Literal(None)
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
        problem = line.split(" ")
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
            f.undo(var)
            f.clauses+=clauses
            # print(f, 'undo')
            return None
    else:
        n = formula.get_literal()
        #print(formula, 'pred simplify 1')
        f, clauses = formula.simplify(n, True)
        if dpll(f) is not None:
            solution.append((n,True))
            return solution
        f.undo(n)
        f.clauses += clauses
        #print(f,'pred simplify 2')
        f2, clauses = f.simplify(n, False)
        if dpll(f2) is not None:
            solution.append((n, False))
            return solution
        else:
            return None



if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Not enough arguments")
        sys.exit(1)
    formula = read_file(sys.argv[1])
    print(dpll(formula))
    s = dpll(formula)
    write_output(sys.argv[2], s)
