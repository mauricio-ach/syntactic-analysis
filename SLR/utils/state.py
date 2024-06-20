from utils.canonical_item import Item

class State:
    def __init__(self, items: set[Item], id: int, is_final=False):
        self.items = set(items)
        self.transitions = {}
        self.id = id
        self.is_final = is_final

    def __repr__(self):
        return f"Estado {self.id}\nEs terminal {self.is_final}\nItems canónicos:\n{self.items}\n Transiciones:\n{self.transitions}\n"
    
    def get_items(self):
        item_strings = sorted([str(item) for item in self.items])
        return " | ".join(item_strings)
    
    # Devuelve los items con producción
    # E -> EdR.
    def get_dot_end_items(self):
        items = []

        for item in self.items:
            rhs = item.production.rhs
            if len(rhs) == item.dot_position:
                items.append(item)
                
        return items


    def contains(self, item):
        return any(curr_item.is_equal(item) for curr_item in self.items)