from utils.canonical_item import Item
from utils.production import Production
from utils.state import State
from utils.symbol_grammar import Symbol
#from grammar_SLR import GrammarSLR

class AutomatonLR0():
    def __init__(self, grammar):
        self.grammar = grammar

        # Construimos los estados con la gramática
        self.states = self.construct_states()
        # Identificamos su estado final
        self.find_terminal()
    
    def construct_states(self):
        # Obtenemos el primer símbolo y producción de la gramática
        grammar_first_symbol = self.grammar.start_symbol
        grammar_first_production = (self.grammar.get_productions_by_symbol_lhs(grammar_first_symbol))[0]

        # Cremamos una nueva producción para no modificar la original
        first_production = Production(
            Symbol(grammar_first_symbol.name, False),
            [Symbol(symbol.name, symbol.is_terminal) for symbol in grammar_first_production.rhs]
        )
        
        # Construimos I_0
        i_0 = Item(first_production)

        # Construimos S_0
        # Aplicando cerradura al primer item
        current_id = 0
        s_0 = State(self.grammar.closure([i_0]), current_id)

        # Lista de estados
        states = [s_0] 

        # Lista de id para evitar incluir estados duplicados
        unique_states = {s_0.get_items(): current_id}
        current_id += 1

        # Creamos los estados recursivamente
        added = True

        # Obtenemos los simbolos de la gramática
        terminals = self.grammar.terminal_symbols
        non_terminals = self.grammar.non_terminal_symbols
        epsilon_symbol = self.grammar.find_in_simbols("epsilon")
        non_terminals.remove(epsilon_symbol)

        while added:
            added = False
            # Verificamos cada estado en la lista 
            for state in states:
                # Iteramos sobre cada simbolo
                for symbol in terminals + non_terminals:
                    # Obtenemos los items canónicos al hacer GOTO con el símbolo
                    new_items = self.grammar.goto_operation(state, Symbol(symbol.name, symbol in terminals))

                    # Si obtenemos items con el símbolo
                    if new_items:
                        # Creamos un nuevo estado
                        new_state = State(new_items, current_id)
                        
                        # Verificamos si el estado ya ha sido creado
                        items = new_state.get_items()

                        if items not in unique_states:
                            # Si no ha sido agregado lo agremamos xd
                            unique_states[items] = current_id
                            states.append(new_state)
                            current_id += 1
                            added = True
                        
                        # Agregamos sus transiciones 
                        state.transitions[symbol] = unique_states[items]

        return states

    # Buscamos el estado final 
    # S' := S$.
    def find_terminal(self):
        for state in self.states:
            for item in state.items:
                rhs = item.production.rhs
                if rhs[item.dot_position-1].name == "$":
                    state.is_final = True

    # Obtiene todos los estados que tienen una 
    # producción del estilo
    # E := EBcD.
    # con el punto al final
    def find_dot_end_states(self):
        states = {}
        for state in self.states:
            items = state.get_dot_end_items()
            if items:
                if state.id not in states:
                    states[state.id] = []

                for item in items:
                    states[state.id].append(item)
        return states

"""Prueba

grammar = GrammarSLR(['+','*','-','/','n', '(', ')'], ['E','T','F'], 'E', ['E := E + T | E - T | T', 'T := T * F | T / F | F', 'F := ( E ) | n'])

grammar.augment_grammar()
#print()
#print(grammar)

automaton_lr0 = AutomatonLR0(grammar)

for state in automaton_lr0.states:
    print(state)

print()
print()
dot_end = automaton_lr0.find_dot_end_states()

for state in dot_end:
    print(state)
"""