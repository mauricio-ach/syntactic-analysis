from symbol_grammar import Symbol
from production import Production

    
class Grammar:
    def __init__(self, terminal_symbols, non_terminal_symbols, start_symbol, productions):
        self.terminal_symbols = [Symbol(t, True) for t in terminal_symbols]
        self.non_terminal_symbols = [Symbol(t, False) for t in non_terminal_symbols]
        self.start_symbol = self.find_in_simbols(start_symbol)
        # Creamos el símbolo epsilon para utilizarlo después
        self.non_terminal_symbols.append(Symbol('epsilon', False))
        self.productions = self.get_production_from_string(productions)
        self.first_sets = {}
        self.follow_sets = {}
    
    # Busca un símbolo de la gramática por su nombre
    # Si existe regresa tal símbolo, sino regresa None
    def find_in_simbols(self, name):
        for symbol in self.terminal_symbols + self.non_terminal_symbols:
            if symbol.name == name:
                return symbol
        return None        
    
    # Aumenta la gramatica añadiendo S'
    # como símbolo inicial
    # y la producción S' -> S
    def augment_grammar(self):
        initial_symbol = self.start_symbol
        new_symbol_name = initial_symbol.name + "'"

        # Verificamos si el símbolo ya existe,
        # pues eliminar recursión izquierda suele 
        # añadir este tipo de nombres
        symbol_exists = self.find_in_simbols(new_symbol_name)

        # Añadimos ' hasta que el símbolo se pueda agregar xd
        while symbol_exists:
            new_symbol_name = new_symbol_name + "'"

            if self.find_in_simbols(new_symbol_name) is None:
                symbol_exists = False

        # Creamos el símbolo 
        new_symbol = Symbol(new_symbol_name, False)
        self.non_terminal_symbols.insert(0, new_symbol)

        # Añadimos $
        eof_symbol = self.add_eof_symbol()

        # Creamos el lado derecho de la producción
        rhs = [self.start_symbol, eof_symbol]
        
        # Añadimos la producción S' := S
        self.productions.insert(0, Production(new_symbol, rhs))

        # Actualizamos el símbolo inicial
        self.start_symbol = new_symbol

    # Añade el símbolo $ a la gramática
    # Útil para los parsers
    def add_eof_symbol(self):
        new_symbol = Symbol('$', is_terminal=True)
        self.terminal_symbols.append(new_symbol)
        return new_symbol
    
    # Dado un conjunto de cadenas del estilo "E := F t"
    # crea un objeto de Production para cada cadena
    def get_production_from_string(self, productions):
        productions_list = []

        # Separamos el lado derecho e izquierdo de la producción
        # haciendo split en ":="
        for str in productions:
            lhs, rhs = str.split(' := ')
            l_symbol = self.find_in_simbols(lhs)

            # Si la producción tiene varias opciones separamos por "|"
            # Ejemplo "E := F t | F | t"
            derivations = rhs.split(' | ')

            # Creamos las produccciones
            for derivation in derivations:
                r_symbols = [self.find_in_simbols(symbol) for symbol in derivation.split()]
                productions_list.append(Production(l_symbol, r_symbols))

        return productions_list

    # Aplica el algoritmo para eliminar recursión izquierda de una gramática
    # en producciones del estilo "E := E t | F"
    def remove_left_recursion(self):
        new_productions = []
        
        
        for symbol in self.non_terminal_symbols:
            recursive_productions = []
            non_recursive_productions = []
            
            
            for production in self.productions:
                if production.lhs == symbol:
                    # ¿ E: = E alpha?
                    if production.rhs[0] == symbol:
                        recursive_productions.append(production.rhs[1:])
                    else:
                        non_recursive_productions.append(production.rhs)
            
            if recursive_productions:
                # Crea E'
                new_symbol_name = f"{symbol.name}'"
                new_symbol = Symbol(new_symbol_name, False)
                self.non_terminal_symbols.append(new_symbol)                
                
                # Crear producciones E := beta E'
                for non_rec_prod in non_recursive_productions:
                    new_productions.append(Production(symbol, non_rec_prod + [new_symbol]))

                # Crear nuevas producciones E' := alpha E'
                for rec_prod in recursive_productions:
                    new_productions.append(Production(new_symbol, rec_prod + [new_symbol]))        

                # Agregamos la producción vacía E' := epsilon
                new_productions.append(Production(new_symbol, [self.find_in_simbols('epsilon')]))
            
            else:
                # Si no hay recursión izquierda mantenemos las mismas producciones
                for prod in non_recursive_productions:
                    new_productions.append(Production(symbol, prod))
        
        # Actualizamos la gramatica
        self.productions = new_productions

    # Obtiene todas las producciones que tienen un símbolo E
    # en su lado izquierdo "E := ft"
    def get_productions_by_symbol_lhs(self, symbol):
        
        productions = []

        for production in self.productions:
            if symbol == production.lhs:
                productions.append(production)

        return productions
    
    # Obtiene todas las producciones que tienen un símbolo E
    # en su lado izquierdo "R := fE"
    def get_productions_by_symbol_rhs(self, symbol):
        
        productions = []

        for production in self.productions:
            rhs = production.rhs

            for curr_symbol in rhs:
                if symbol == curr_symbol:
                    productions.append(production)

        return productions

    # Aplica el algoritmo para encontrar el conjunto FIRST de
    # un símbolo no terminal
    def get_first_set_symbol(self, symbol, visited=None):

        # Creamos la lista visitados si no se ha visitado
        # a nadie
        if visited is None:
            visited = set()        
        
        # Si el símbolo está en visitados terminamos recursión
        if symbol in visited:
            return set()

        # Si no ha sido visitado lo agregamos a visitados
        visited.add(symbol)        

        # Si ya hemos calculado el conjunto FIRST del símbolo
        # regresamos el conjunto y quitamos el símbolo de
        # visitados
        if self.first_sets[symbol]:
            visited.remove(symbol)
            return self.first_sets[symbol]
        
        # Creamos el conjunto FIRST
        first_set = set()

        # Obtenemos todos las producciones que contienen el
        # símbolo en su lado izquierdo
        productions_with_symbol = self.get_productions_by_symbol_lhs(symbol)

        # Procesamos cada producción
        for production in productions_with_symbol:
                # Obtenemos su lado derecho
                rhs = production.rhs
                # Si es un símbolo terminal o epsilon 
                # lo añadimos al conjunto FIRST
                if rhs[0].is_terminal or rhs[0].name == 'epsilon':
                    first_set.add(production.rhs[0])
                else:
                    # Si no hacemos recursión con el FIRST
                    # del símbolo no terminal
                    first_set.update(self.get_first_set_symbol(rhs[0], visited))
        
        # Eliminamos el simbolo
        # de visitados
        visited.remove(symbol)

        # Actualizamos el conjunto correspondiente de la gramática
        self.first_sets[symbol] = first_set

        # Devolvemos el conjunto para la
        # ejecución correcta de la recursión
        return first_set

    # Obtiene el conjunto FIRST de todos los símbolos no terminales
    # de la gramática
    def get_first_set(self):        
        # Creamos los conjuntos FIRST vacíos
        for symbol in self.non_terminal_symbols:
            if symbol != self.find_in_simbols('epsilon'):
                self.first_sets[symbol] = []
                
        # Calculamos los conjuntos FIRST
        for symbol in self.non_terminal_symbols:
            if symbol.name != 'epsilon':
                self.get_first_set_symbol(symbol)
    
    # Aplica el algoritmo para encontrar el conjunto FOLLOW de
    # un símbolo no terminal
    def get_follow_set_symbol(self, symbol, visited=None):
        
        # Creamos la lista visitados si no se ha visitado
        # a nadie
        if visited is None:
            visited = set()
        
        # Si el símbolo está en visitados terminamos recursión
        if symbol in visited:
            return set()
        
        # Si no ha sido visitado lo agregamos a visitados
        visited.add(symbol)

        # Si ya hemos calculado el conjunto FOLLOW del símbolo
        # regresamos el conjunto y quitamos el símbolo de
        # visitados
        if self.follow_sets[symbol]:
            visited.remove(symbol)
            return self.follow_sets[symbol]
        
        # Creamos el conjunto FIRST
        follow_set = set()

        # Verificamos el símbolo inicial
        if symbol == self.start_symbol:            
            # Verificamos si ya existe el FOLLOW del símbolo inicial
            start_follow = self.follow_sets[symbol]
            
            if not start_follow:
                # Si no existe agregamos el símbolo $
                # y lo agregamos a FOLLOW(S)
                eof_symbol = self.add_eof_symbol()
                follow_set.add(eof_symbol)

        # Obtenemos todos las producciones que contienen el
        # símbolo en su lado derecho
        productions_with_symbol = self.get_productions_by_symbol_rhs(symbol)

        # Procesamos cada producción
        for production in productions_with_symbol:
            # obtenemos su lado derecho
            rhs = production.rhs

            # Iteramos sobre los símbolos del lado derecho
            for i in range(len(rhs)):
                # Simbolo a calcular FOLLOW E'
                if rhs[i] == symbol:
                    # ¿E := TSE'?
                    if i == len(rhs) - 1:
                        # Si está al final de la producción agregamos
                        # FOLLOW de E
                        lhs_follow_set = self.get_follow_set_symbol(production.lhs, visited)
                        follow_set.update(lhs_follow_set)
                    else:
                        # Verificamos el símbolo que sigue de E'
                        next_symbol = rhs[i + 1]
                        # ¿E := TSE'a?
                        if next_symbol.is_terminal:
                            # Si es un terminal lo añadimos a su FOLLOW
                            follow_set.add(next_symbol)
                        # ¿E := TSE'R?
                        else:
                            # Si sigue un símbolo no terminal obtenemos el
                            # FIRST del siguiente simbolo
                            next_symbol = rhs[i + 1]
                            next_symbol_first_set = self.first_sets[next_symbol]
                            epsilon_symbol = self.find_in_simbols('epsilon')

                            # Agregamos todos los símbolos de FIRST al FOLLOW
                            for curr_symbol in next_symbol_first_set:
                                if curr_symbol != epsilon_symbol:
                                    follow_set.add(curr_symbol)
                            
                            # Si el símbolo es anulable hacemos recursión
                            # sobre el símbolo siguiente y lo añadimos a FOLLOW
                            if epsilon_symbol in next_symbol_first_set:
                                follow_set.update(self.get_follow_set_symbol(next_symbol, visited))
        # Eliminamos el simbolo
        # de visitados
        visited.remove(symbol)
        
        # Actualizamos el conjunto correspondiente de la gramática
        self.follow_sets[symbol] = follow_set

        # Devolvemos el conjunto para la
        # ejecución correcta de la recursión
        return follow_set

    # Obtiene el conjunto FOLLOW de todos los símbolos no terminales
    # de la gramática
    def get_follow_set(self):
        # Creamos los conjuntos FOLLOW vacíos
        for symbol in self.non_terminal_symbols: 
            if symbol != self.find_in_simbols('epsilon'):
                self.follow_sets[symbol] = set()
        
        # Obtenemos el conjunto FOLLOW de cada símbolo
        # excepto epsilon
        for symbol in self.non_terminal_symbols:
            if symbol.name != 'epsilon':
                self.get_follow_set_symbol(symbol)
    
    # Imprime el objeto de una forma presentable
    def __repr__(self) -> str:
        output = (
            f"Gramatica con simbolo inicial {self.start_symbol}\n"
            f"Simbolos terminales {self.terminal_symbols}\n"
            f"Simbolos no terminales {self.non_terminal_symbols}\n"
            f"Producciones {self.productions}"
        )
        return output
    
    def __str__(self) -> str:
        output = (
            f"Gramatica con simbolo inicial {self.start_symbol}\n"
            f"Simbolos terminales {self.terminal_symbols}\n"
            f"Simbolos no terminales {self.non_terminal_symbols}\n"
            f"Producciones {self.productions}"
        )
        return output

# Si se descomenta este fragmento aparecerá en 
# instancias de LL1 y SLR
"""grammar = Grammar(['+','*','-','/','n', '(', ')'], ['E','T','F'], 'E', ['E := E + T | E - T | T', 'T := T * F | T / F | F', 'F := ( E ) | n'])

grammar1 = Grammar(['0','1','2'], ['S','X'], 'S', ['S := X S 0 | epsilon', 'X := 1 X 2 | S S'])

print(grammar)
print()
print(grammar1)

grammar.remove_left_recursion()

grammar.augment_grammar()

print(grammar)"""