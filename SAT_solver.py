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
        self.literals = []
        if clause_str is not None:
            literals = clause_str.split(" ")
            for l in literals[:-1]:
                self.literals.append(Literal(l))

    def __str__(self):
        return " ".join([str(l) for l in self.literals])

    def __copy__(self):
        c = Clause(None)
        c.literals = [copy.copy(l) for l in self.literals]
        return c


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
    # print(formula)
