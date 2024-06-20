class Production:
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def is_equal(self, production):

        if self.lhs.name != production.lhs.name:
            return False

        if len(self.rhs) != len(production.rhs):
            return False

        rhs_1 = self.rhs
        rhs_2 = production.rhs

        for symbol1, symbol2 in zip(rhs_1, rhs_2):
            if symbol1.name != symbol2.name:
                return False
        
        return True

    def __repr__(self):
        return f"{self.lhs} := {self.rhs}"