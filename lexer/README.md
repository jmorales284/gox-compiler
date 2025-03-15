# Analizador Léxico para el Lenguaje GOX

## Descripción del Código

El analizador léxico está implementado en la clase `Lexer`, la cual se encarga de recorrer el texto de entrada y generar tokens de acuerdo con la gramática del lenguaje.

### Token

La clase `Token` representa una unidad léxica con tres atributos:
- `type`: Tipo del token (ej. `ID`, `INTEGER`, `PLUS`).
- `value`: Valor asociado al token.
- `lineno`: Número de línea en la que se encuentra el token.

### Tokens Soportados

El lexer reconoce diferentes tipos de tokens:
- **Palabras clave**: `const`, `var`, `print`, `return`, `break`, `continue`, `if`, `else`, `while`, `func`, `import`, `true`, `false`, `int`, `float`, `char`, `bool`.
- **Operadores de dos caracteres**: `<=`, `>=`, `==`, `!=`, `&&`, `||`.
- **Operadores y símbolos de un solo carácter**: `+`, `-`, `*`, `/`, `<`, `>`, `=`, `;`, `(`, `)`, `{`, `}`, `,`, `` ` ``.
- **Identificadores**: Variables y nombres de funciones.
- **Números enteros y flotantes**.
- **Caracteres**.
- **Booleanos**: `true`, `false`.
- **Comentarios**: De una línea (`// comentario`) y de bloque (`/* comentario */`).

### Proceso de Tokenización

1. **Ignorar espacios en blanco y tabulaciones.**
2. **Contar las líneas para reportar errores precisos.**
3. **Detectar comentarios de una línea y de bloque.**
4. **Identificar operadores de dos caracteres.**
5. **Identificar operadores y símbolos de un solo carácter.**
6. **Detectar palabras clave e identificadores.**
7. **Detectar booleanos, números, y caracteres.**
8. **Lanzar un error si se encuentra un caracter ilegal.**



### Manejo de Errores

Si el lexer encuentra un caracter ilegal, lanza una excepción `ValueError` con el número de línea y el caracter problemático.

```python
ValueError: 3: Caracter ilegal '%'
```

### Problemas al momento de hacer las pruebas unitarias y de probar con codigo gox real

El principal problema al momento de hacer el codigo fue que se estructuró mal la parte de el metodo tokenize haciendo que genere errores, el error era que se puso primero el condicional de los enteros antes que el de los float haciendo que no detecte bien estos numeros float haciendo que por ejemplo los separe 3.14 agarre 3 como entero y .14 como flotante cuando deberia ser 3.14 flotante, esto se soluciono moviendo el condicional cambiando la prioridad de este, otro problema que se presentó era que a la hora de leer los comentarios de una sola linea estaba leyendo estos como dos divisores separados y no como comentario y esto se dio por la misma razon que la de los numeros enteros y flotantes, era porque se estaba evaluando primero los operadores antes que los comentarios, entonces para solucionar esto se movio el condicional de los comentarios a la parte de arriba dandole la prioridad y haciendo que los detecte primero
