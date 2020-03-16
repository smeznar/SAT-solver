import sys


class Formula:
    def __init__(self, variables: int, clauses: int):
        self.num_of_vars = variables
        self.num_of_clauses = clauses
        self.clauses = []

    def add_clause(self, clause_str: str):
        self.clauses.append(Clause(clause_str))

    def __str__(self):
        ret = ""
        for c in self.clauses:
            ret += str(c)
            ret += "\n"
        return ret


class Clause:
    def __init__(self, clause_str: str):
        self.literals = []
        literals = clause_str.split(" ")
        for l in literals[:-2]:
            self.literals.append(Literal(l))

    def __str__(self):
        return " ".join([str(l) for l in self.literals])


class Literal:
    def __init__(self, literal_str: str):
        self.is_negated = False
        if literal_str[0] == '-':
            self.is_negated = True
            literal_str = literal_str[1:]
        self.number = int(literal_str)

    def __str__(self):
        if self.is_negated:
            return "-" + str(self.number)
        return str(self.number)


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
            formula.add_clause(l)
        return formula


if __name__ == '__main__':
    if len(sys.argv)<3:
        print("Not enough arguments")
        sys.exit(1)
    formula = read_file(sys.argv[1])
    print(formula)
