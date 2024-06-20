import re, copy, csv
from collections import deque
from utils.grammar import Grammar
from utils.canonical_item import Item
from utils.symbol_grammar import Symbol
from utils.state import State
from automaton_lr0 import AutomatonLR0

class GrammarSLR(Grammar):

    def __init__(self, terminal_symbols, non_terminal_symbols, start_symbol, productions):
        super().__init__(terminal_symbols, non_terminal_symbols, start_symbol, productions)
        self.enum_productions = {}

    # Obtenemos la cerradura de un item
    # E := a.R
    def closure(self, items: list[Item]):
        closure = set(items)
        added = True
        while added:
            added = False
            new_items = set()

            closure_list = list(closure)

            # Iteramos sobre todos los items del estado
            for item in closure_list:
                # Si podemos mover el punto operamos
                # E := a.R | E := a.a continuamos
                # E := aR. omitimos
                if item.dot_position < len(item.production.rhs):
                    rhs = item.production.rhs
                    dot_position = item.dot_position
                    next_symbol = rhs[dot_position]
                    # Si es un no terminal continuamos
                    # E := a.R
                    if not next_symbol.is_terminal:
                        for production in self.productions:
                            lhs = production.lhs
                            # Si el lado izquierdo coincide con el símbolo agregamos
                            # las producciones a la cerradura
                            if lhs.name == next_symbol.name:
                                # Creamos un nuevo item canónico
                                new_item = Item(production, 0)
                                # Verificamos si el item ya ha sido creado
                                if not any(curr_item.is_equal(new_item) for curr_item in closure):
                                    new_items.add(new_item)
                                    added = True
                closure.update(new_items)
        return closure
    
    # Operacion GOTO
    # Dado un estado y un símbolo obtiene los items resultantes
    # de la operación moviendo el punto un símbolo a la derecha
    # obteniendo la cerradura si es necesario
    def goto_operation(self, state: State, symbol: Symbol):
        next_items = set()

        # Iteramos en cada item del estado
        for item in state.items:
            # Si podemos mover el punto operamos
            # E := a.R | E := a.a continuamos
            # E := aR. omitimos
            if item.dot_position < len(item.production.rhs):
                # Si el símbolo siguiente al punto coincide con el símbolo
                # que se está procesando continuamos
                # Símbolo E, E := aRs.Ra -> continua
                # Símbolo E, E := aR.sRa -> ignora
                if item.production.rhs[item.dot_position].name == symbol.name:
                    # Construimos y agregamos el siguiente item con la misma producción
                    # pero moviendo el punto en una posición
                    next_items.add(Item(item.production, item.dot_position+1))
        
        return self.closure(next_items)
    
    def construct_slr_table(self, lr0_automaton: AutomatonLR0):
        # Guardamos la gramática original para utilizarla
        # en el archivo de la salida
        grammar = copy.deepcopy(self)

        # Calculamos FOLLOW y FIRST de cada símbolo
        self.get_first_set()
        self.get_follow_set()

        # Creamos la tabla como un diccionario
        table = {}

        symbols = self.terminal_symbols + self.non_terminal_symbols

        # Construimos la tabla SLR vacía
        for state in lr0_automaton.states:
            table[state.id] = {}

            for symbol in symbols:
                # Ignoramos S' pues siempre
                # comenzamos en el estado 0
                if symbol.name != self.start_symbol.name:
                    table[state.id][symbol.name] = {}

        # Llenamos la tabla

        # Obtenemos los estados que tienen producciones
        # con el punto al final, E := EdR.
        dot_end_states = lr0_automaton.find_dot_end_states()

        # Enumeramos las producciones 
        productions_num = {}
        p_num = 0
        for production in self.productions:
            productions_num["r" + str(p_num)] = production
            p_num += 1
        self.enum_productions = productions_num
        
        # Iteramos sobre todos los estados
        for state in lr0_automaton.states:
            # Iteramos sobre las transiciones del estado
            # GOTO(S_i,symbol) -> S_j 
            for symbol,to_state in state.transitions.items():
                symbol_grammar = self.find_in_simbols(symbol.name)
                if symbol_grammar.is_terminal:
                    table[state.id][symbol.name] = "s" + str(to_state)
                    continue
                table[state.id][symbol.name] = "g" + str(to_state)
            
            # Verificamos si el estado contiene producciones
            # E -> EdR.
            # Y guardamos la reducción correspondiente
            if state.id in dot_end_states:
                # Iteramos sobre los items del estado que
                # cumplen la condición
                items = dot_end_states[state.id]
                for item in items:
                    # Buscamos la producción dentro de la 
                    # gramática original enumerada
                    for num,production in productions_num.items():
                        if production.is_equal(item.production):
                            # Obtenemos el follow del símbolo
                            # izquierdo de la producción
                            follow = self.follow_sets[production.lhs]

                            # Rellenamos en la tabla con el follow y
                            # la reducción
                            for symbol in follow:
                                
                                # Ubicamos la casilla de aceptación
                                if state.is_final and symbol.name == "$":
                                    table[state.id][symbol.name] = "a"
                                    continue
                                
                                # Rellenamos con la fila con la reducción
                                table[state.id][symbol.name] = num
        # Guardamos los resultados en un
        # archivo para poder leer mejor
        file_name = 'slr_results.txt'

        with open(file_name, 'w', encoding='utf-8') as file:
            file.write('Gramatica')
            file.write("\n" + "\n")
            file.write(str(grammar))
            file.write("\n" + "\n")
            file.write('Conjuntos FIRST')
            file.write("\n")
            file.write(str(self.first_sets))
            file.write("\n" + "\n")
            file.write('Conjuntos FOLLOW')
            file.write("\n")
            file.write(str(self.follow_sets))
            file.write("\n" + "\n")
            file.write('Tabla LL(1)')
            file.write("\n")    
            for symbol, sub_table in table.items():
                file.write(f"{symbol}: {sub_table}")
                file.write("\n")

        return table

    def parse_slr_string(self, input, table):
        # Agregamos $ al final del input
        input.append(self.find_in_simbols('$'))

        # Stack para estados
        # Comenzamos en el estado inicial
        states = deque()
        states.append(0)
        # Stack de símbolos
        stack = deque()
        # Stack de acciones
        parsing_steps = []

        # Consumimos un símbolo
        for curr_symbol in input:

            # Operamos hasta que podamos pasar
            # al siguiente punto
            while True:
                last_state = states[-1]
                action = table.get(last_state, {}).get(curr_symbol.name)

                # Para guardar en archivo
                stack_representation = ' '.join([sym.name for sym in stack])
                states_representation = ' '.join([str(state) for state in states])
                parsing_steps.append([states_representation, stack_representation, curr_symbol.name, action])

                # Si no encontramos una acción el parsing falló
                if action == {}:                    
                    raise SyntaxError(f"Parsing incorrrecto: Input = {input} no existe la producción para {curr_symbol.name} con el estado {last_state}")

                # a -> accepts
                if action[0] == "a":
                    break
                
                # g -> goto
                elif action[0] == "g":
                    # Agregamos el estado al stack de estados
                    state_id = int(action[1:])
                    states.append(state_id)
                    continue

                # s -> shift
                elif action[0] == "s":

                    # Verificamos si vemos el símbolo de $ antes de un shift
                    # y lo dejamos en el input para poder seguir transitando
                    if curr_symbol.name == "$":
                        state_id = int(action[1:])
                        states.append(state_id)
                        continue

                    # Agregamos el estado al stack de estados
                    state_id = int(action[1:])
                    states.append(state_id)
                    # Agregamos el símbolo al stack de símbolos
                    stack.append(curr_symbol)
                    # Continuamos al siguiente símbolo
                    break

                # r -> reduce
                elif action[0] == "r":
                    # Calculamos los elementos a sacar del stack
                    production = self.enum_productions[action]
                    r_num = len(production.rhs)

                    # Eliminamos los elementos necesarios del stack
                    for _ in range(r_num):
                        stack.pop()
                        states.pop()
                    
                    # Agregamos el símbolo al stack de símbolos
                    stack.append(production.lhs)

                    # Verificamos el estado a donde transitar
                    go_to = table[states[-1]][stack[-1].name]
                    go_to = int(go_to[1:])
                    
                    # Agregamos el estado al stack de estado
                    states.append(go_to)
                    continue
                
                else:
                    raise SyntaxError(f"Parsing incorrecto: Input = {input} Acción inválida {action}")
        
        # Para guardar en documento
        stack_representation = ' '.join([sym.name for sym in stack])
        states_representation = ' '.join([str(state) for state in states])
        parsing_steps.append([states_representation, stack_representation, curr_symbol.name, action])

        # Guardamos los resultados en un archivo
        csv_filename = 'parsing_slr_results.csv'
        
        with open(csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(['Estados', 'Stack', 'Current Symbol', 'Action'])
        
            # Agregar cada paso del proceso de parsing
            for step in parsing_steps:
                csv_writer.writerow(step)

        print(f"Parsing correcto: Input = {input} se llegó al estado de aceptación")

grammar = GrammarSLR(['+','*','-','/','n', '(', ')'], ['E','T','F'], 'E', ['E := E + T | E - T | T', 'T := T * F | T / F | F', 'F := ( E ) | n'])
# Aumentamos la gramática
grammar.augment_grammar()

# Procesamos las cadenas a parsear
strings_to_parse = [
    "10+12/3",
    "10+",
    "3*(2+4)/5",
    "3*4+"
]

tokens_to_parse = []

for string in strings_to_parse:
    # Usamos una regex para parsear enteros y flotantes 
    # dentro de una cadena de texto
    pattern = re.compile(r'(\d+(\.\d+)?)|([+\-*/()])')
    tokens = [match.group() for match in pattern.finditer(string)]

    string_tokens = []

    # Procesamos los tokens y buscamos su símbolo
    # dentro de la gramática
    for token in tokens:
        if token.isdigit():
            # 10 -> n
            string_tokens.append(grammar.find_in_simbols('n'))
        else:
            string_tokens.append(grammar.find_in_simbols(token))
    
    tokens_to_parse.append(string_tokens)

# Creamos el automata LR(0)
lr0_automaton = AutomatonLR0(grammar)

# Construimos la tabla SLR
slr_table = grammar.construct_slr_table(lr0_automaton)

"""for row,column in slr_table.items():
    print(row, column)"""

# Procesamos las tokens
for string_tokens in tokens_to_parse:
    try:
        grammar.parse_slr_string(string_tokens, slr_table)
    except Exception as e:
        print(f"{e}")