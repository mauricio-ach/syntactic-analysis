class Symbol:
    def __init__(self, name, is_terminal):
        self.name = name
        self.is_terminal = is_terminal

    def __repr__(self):
        return self.name