import copy, re, csv
from grammar import Grammar

class GrammarLL1(Grammar):

    # Construye la tabla de parsing LL(1)
    def construct_ll_1_table(self):
        # Guardamos la gramática original para utilizarla
        # en el archivo de la salida
        original_grammar = copy.deepcopy(self)

        # Eliminamos recursion izquierda
        self.remove_left_recursion()

        # Calculamos conjuntos FIRST y FOLLOW de cada
        # símbolo no terminal
        self.get_first_set()
        self.get_follow_set()

        # Creamos la tabla como un diccionario
        table = {}

        # Construimos la tabla LL(1) vacía
        for symbol_nt in self.non_terminal_symbols:
            if symbol_nt.name != 'epsilon':
                table[symbol_nt] = {}

                for symbol_ts in self.terminal_symbols:
                    table[symbol_nt][symbol_ts] = {}

        # Llenamos la tabla iterando en cada símbolo
        # no terminal
        for symbol in self.non_terminal_symbols:
            # Ignoramos epsilon
            if symbol.name != 'epsilon':
                
                # Obtenemos las producciones que contienen al símbolo
                # en su lado izquierdo
                productions_with_symbol = self.get_productions_by_symbol_lhs(symbol)

                # Procesamos cada producción
                for production in productions_with_symbol:
                    # Obtenemos su lado derecho
                    rhs = production.rhs
                    # Obtenemos el primer símbolo
                    # del lado derecho
                    first_symbol = rhs[0]
                    
                    if first_symbol.is_terminal:
                        # Si es terminal llenamos [E,t] con la
                        # producción correspondiente
                        table[symbol][first_symbol] = production
                    elif first_symbol.name == 'epsilon':
                        # Si es una producción E := epsilon
                        # obtenemos FOLLOW del símbolo
                        follow_symbol = self.follow_sets[symbol]
                        
                        # Y llenamos [E,t_i] con la producción correspondiente
                        # donde t_i pertenece a FOLLOW(E)
                        for curr_symbol in follow_symbol:
                            table[symbol][curr_symbol] = production
                    else:
                        # Si es una producción E := R alpha
                        # Obtenemos FIRST(R)
                        first_next = self.first_sets[first_symbol]

                        # Llenamos en [E,t_i] con la producción correspondiente
                        # donde t_i pertenece a FOLLOW(e) excepto epsilon
                        for curr_symbol in first_next:
                            if curr_symbol.name != 'epsilon':
                                table[symbol][curr_symbol] = production
        
        # Guardamos los resultados en un
        # archivo para poder leer mejor
        file_name = 'll1_results.txt'

        with open(file_name, 'w', encoding='utf-8') as file:
            file.write('Gramatica original')
            file.write("\n" + "\n")
            file.write(str(original_grammar))
            file.write("\n" + "\n")
            file.write('Gramatica sin recursion izquierda')
            file.write("\n" + "\n")
            file.write(str(self))
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

    def parse_ll_1_string(self, input, table):

        # Agregamos $ al final del input
        input.append(self.find_in_simbols('$'))

        # Stack
        # Simulamos producción S' -> S$
        stack = [self.find_in_simbols('$'),self.start_symbol]

        # Guardamos cada paso
        # del parsing
        parsing_steps = []

        # Consumimos un símbolo
        for curr_symbol in input:
            
            # Operamos hasta que podamos pasar
            # al siguiente símbolo
            while True:
                # Para guardar en archivo
                stack_representation = ' '.join([sym.name for sym in stack])
                parsing_steps.append([curr_symbol.name, stack_representation])
                
                # Sacamos el tope de la pila
                top = stack.pop()
                
                # Si vemos epsilon continuamos
                if top.name == 'epsilon':
                    continue
                
                # Si es terminal veríficamos que suceda n = n
                # sino lanzamos un error pues no se pudo parsear
                # el input
                if top.is_terminal:
                    if top.name == curr_symbol.name:
                        # Avanzamos al siguiente símbolo
                        break
                    else:
                        raise SyntaxError(f"Error: {top.name} != {curr_symbol.name}")

                # Obtenemos la producción correspondiente en la tabla
                production = table[top][curr_symbol]

                # Si la producción no existe lanzamos un error pues no 
                # se pudo parsear el input
                if not production:
                    raise SyntaxError(f"Error: no existe la producción para {curr_symbol.name} con {top.name} en la tabla LL(1)")

                # Invertimos el orden de la producción
                rhs = production.rhs[::-1]

                # Agregamos al stack 
                stack.extend(rhs)

        # Si el stack no está vacío al final no se pudo parsear el input
        if stack != []:
            raise SyntaxError(f"Parsing incorrecto: Input = {input}, Stack no vacía {stack}")
        
        # Para guardar en documento
        stack_representation = ' '.join([sym.name for sym in stack])
        parsing_steps.append([curr_symbol.name, stack_representation])
        
        # Guardamos los resultados en un archivo
        csv_filename = 'parsing_ll1_results.csv'
        
        with open(csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(['Current Symbol', 'Stack'])
        
            # Agregar cada paso del proceso de parsing
            for step in parsing_steps:
                csv_writer.writerow(step)
        
        print(f"Parsing correcto: Input = {input}, Stack vacío {stack}")

grammar = GrammarLL1(['+','*','-','/','n', '(', ')'], ['E','T','F'], 'E', ['E := E + T | E - T | T', 'T := T * F | T / F | F', 'F := ( E ) | n'])

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

# Parsing con LL(1)
# Guardara los datos de la gramatica en un archivo ll1_results.txt
# y los parsing correctos en un archivo parsing_results.csv
table = grammar.construct_ll_1_table()
for string_tokens in tokens_to_parse:
    try:
        grammar.parse_ll_1_string(string_tokens, table)
    except Exception as e:
        print(f"{e}")