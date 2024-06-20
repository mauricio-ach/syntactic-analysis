# Implementación de los parsers LL1 y SLR para análisis sintáctico en Python

## Objetivo
En este repositorio se encuentra la implementación de diversos algoritmos que se aplican en el análisis sintáctico de compiladores. Se deja la implementación como pública para ser reutilizada o mejorada, cualquier comentario es bienvenido.

## Funcionamiento

### LL1
1. Se construye una gramática a partir de la entrada del usuario
2. Se obtienen las cadenas que se quieren parsear
3. Se construye la tabla LL1
    - Elimina recursión izquierda
    - Calcula los conjuntos FIRST y FOLLOW
    - Usando los conjuntos y la gramática construye la tabla LL1
    - Arroja los resultados en un archivo .txt para una mejor lectura
4. Se parsean las cadenas 
    - Emite un mensaje si la cadena puede ser parseada o no
    - Si es parseada arroja los pasos del parsing en un archivo .csv

### SLR
1. Se construye una gramática a partir de la entrada del usuario
2. Se obtienen las cadenas que se quieren parsear
3. Se construye el automáta LR(0)
    - Se utiliza la construcción de ítems canónicos usando la gramática
4. Se construye la tabla SLR
    - Calcula los conjuntos FIRST y FOLLOW
    - Se define la función GOTO y la cerradura de un ítem
    - Usando los elementos anteriores se construye la tabla SLR
    - Arroja los resultados en un archivo .txt para una mejor lectura
5. Se parsean las cadenas 
    - Emite un mensaje si la cadena puede ser parseada o no
    - Si es parseada arroja los pasos del parsing en un archivo .csv