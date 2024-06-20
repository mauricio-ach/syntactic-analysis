from utils.production import Production

class Item:
    def __init__(self, production: Production, dot_position=0):
        self.production = production
        self.dot_position = dot_position

    def __repr__(self):
        first_part = self.production.rhs[:self.dot_position]
        second_part = self.production.rhs[self.dot_position:]
        return f"{self.production.lhs.name} := {first_part if first_part != [] else ''} . {second_part if second_part != [] else ''}"

    def is_equal(self, item):
        if self.production.lhs.name == item.production.lhs.name:
            if [symbol.name for symbol in self.production.rhs] == [symbol.name for symbol in item.production.rhs]:
                if self.dot_position == item.dot_position:
                    return True
        return False
        