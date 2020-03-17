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
            ret += "\n"
        return ret

    def __copy__(self):
        f = Formula(self.num_of_vars, self.num_of_clauses)
        f.clauses = [copy.copy(c) for c in self.clauses]
        return f

    def add_clause(self, clause_str: str):
        self.clauses.append(Clause(clause_str))


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

    def does_it_solve(self, number: int, value: bool):
        literals = list(filter(lambda l: l.number == number, self.unused_literals))
        if len(literals) > 0:
            for l in literals:
                if l.solve(value):
                    self.is_solved = True
                    return True
                else:
                    self.unused_literals.remove(l)
                    self.used_literals.append(l)
        return False

    def unsolve(self, number: int):
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

    def solve(self, value):
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


if __name__ == '__main__':
    if len(sys.argv)<3:
        print("Not enough arguments")
        sys.exit(1)
    formula = read_file(sys.argv[1])
    c = formula.clauses[88]
    pass
    # print(formula)
