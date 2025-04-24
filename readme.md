# GOX Compiler
# Estudiantes
- Juan Manuel Morales
- Camilo Eduardo Muñoz Albornoz

Este proyecto implementa un compilador para el lenguaje **GOX**, que incluye un analizador léxico, un analizador sintáctico y un analizador semántico. El compilador procesa un archivo fuente escrito en GOX y genera un árbol de sintaxis abstracta (AST), además de realizar verificaciones semánticas.

## Estructura del Proyecto

El proyecto está dividido en varios módulos, cada uno con una responsabilidad específica:

- **`glexer.py`**: Implementa el analizador léxico, que convierte el código fuente en una lista de tokens.
- **`gparser.py`**: Implementa el analizador sintáctico, que convierte los tokens en un árbol de sintaxis abstracta (AST).
- **`gmodel.py`**: Define las clases de nodos del AST y el patrón de visitante para recorrerlo.
- **`checkNew.py`**: Implementa el analizador semántico, que verifica la validez del programa (tipos, declaraciones, etc.).
- **`symtab.py`**: Implementa la tabla de símbolos, que almacena información sobre variables, funciones y otros elementos del programa.
- **`typesys.py`**: Define el sistema de tipos y las reglas para operaciones binarias y unarias.
- **`errors.py`**: Maneja los errores detectados durante las fases de análisis.
- **`pruebaChecker.py`**: Archivo principal para ejecutar el compilador con un archivo fuente de prueba.

---

## Requisitos Previos

Antes de ejecutar el compilador, asegúrate de tener instalado lo siguiente:

- **Python 3.8 o superior**
- Biblioteca `rich` para la visualización de tablas y mensajes de error:
  ```bash
  pip install rich
  ```

---

## Cómo Ejecutar el Compilador

### 1. Preparar el Archivo Fuente

Escribe tu programa en GOX en un archivo con extensión `.gox`. Por ejemplo, crea un archivo llamado prueba.gox con el siguiente contenido:

```gox
func mod(x int, y int) int {
    return x - (x / y) * y;
}

func isprime(n int) bool {
    if n < 2 {
        return false;
    }
    var i int = 2;
    while i * i <= n {
        if mod(n, i) == 0 {
            return false;
        }
        i = i + 1;
    }
    return true;
}
```

### 2. Ejecutar el Compilador

Ejecuta el archivo pruebaChecker.py para analizar el archivo fuente:

```bash
python pruebaChecker.py
```

### 3. Salida del Compilador

El compilador realiza las siguientes tareas y genera la salida correspondiente:

1. **Análisis Léxico**:
   - Convierte el código fuente en una lista de tokens.
   - Ejemplo de salida:
     ```
     func: func Línea 1
     ID: mod Línea 1
     LPAREN: ( Línea 1
     ID: x Línea 1
     int: int Línea 1
     ...
     ```

2. **Análisis Sintáctico**:
   - Genera un árbol de sintaxis abstracta (AST) a partir de los tokens.
   - Ejemplo de salida:
     ```
     AST generado:
     Program(statements=[FunctionDefinition(name=mod, parameters=[Parameter(x, int), Parameter(y, int)], return_type=int, body=[Return(Expression(...))]), ...])
     ```

3. **Análisis Semántico**:
   - Verifica la validez del programa, como tipos de datos, declaraciones de variables y funciones, y estructuras de control.
   - Si hay errores, los muestra con el número de línea:
     ```
     7: Error: Tipo de retorno 'float' no coincide con el tipo de la función 'isprime' que es 'bool'.
     ```

---

## Estructura del Código

### 1. **Análisis Léxico (`glexer.py`)**

El analizador léxico convierte el código fuente en una lista de tokens. Cada token incluye:

- Tipo (`type`): Identifica el tipo del token (e.g., `ID`, `INTEGER`, `PLUS`).
- Valor (`value`): El valor literal del token.
- Línea (`lineno`): La línea del código fuente donde se encuentra el token.

Ejemplo de token:
```python
Token(type='ID', value='mod', lineno=1)
```

### 2. **Análisis Sintáctico (`gparser.py`)**

El analizador sintáctico convierte los tokens en un árbol de sintaxis abstracta (AST). Utiliza métodos como `statement`, `expression`, y `funcdecl` para construir nodos del AST.

Ejemplo de nodo AST:
```python
FunctionDefinition(
    name="mod",
    parameters=[Parameter(name="x", type="int"), Parameter(name="y", type="int")],
    return_type="int",
    body=[Return(Expression(...))]
)
```

### 3. **Análisis Semántico (`checkNew.py`)**

El analizador semántico recorre el AST y verifica:

- Declaraciones de variables y funciones.
- Tipos de datos en operaciones y asignaciones.
- Uso correcto de estructuras de control (`if`, `while`, etc.).
- Retornos en funciones con tipos de retorno.

Ejemplo de verificación:
```python
def visit_Return(self, node: Return, env: Symtab):
    func = env.get('$func')
    if not func:
        error(f"Línea {node.lineno}: 'return' fuera de una función.")
        return

    if node.expression:
        return_type = node.expression.accept(self, env)
        if return_type != func.return_type:
            error(f"Línea {node.lineno}: Tipo de retorno '{return_type}' no coincide con el tipo de la función '{func.name}' que es '{func.return_type}'.")
```

### 4. **Tabla de Símbolos (`symtab.py`)**

La tabla de símbolos almacena información sobre variables, funciones y otros elementos del programa. Soporta entornos anidados para manejar funciones y bloques.

Ejemplo de tabla de símbolos:
```
Symbol Table: 'global'
┌──────────┬───────────────────────────┐
│ key      │ value                     │
├──────────┼───────────────────────────┤
│ mod      │ FunctionDefinition(...)   │
│ isprime  │ FunctionDefinition(...)   │
└──────────┴───────────────────────────┘
```

---

## Cómo Personalizar el Compilador

1. **Agregar Nuevas Funcionalidades**:
   - Modifica `gparser.py` para soportar nuevas construcciones del lenguaje.
   - Actualiza `checkNew.py` para verificar las nuevas construcciones.

2. **Extender el Sistema de Tipos**:
   - Agrega nuevos tipos o reglas de operadores en `typesys.py`.

3. **Manejo de Errores**:
   - Personaliza los mensajes de error en `errors.py`.

---

## Ejemplo de Errores Detectados

1. **Variable no declarada**:
   ```
   Línea 10: Error: La variable 'i' no está definida.
   ```

2. **Tipo de retorno incorrecto**:
   ```
   Línea 7: Error: Tipo de retorno 'float' no coincide con el tipo de la función 'isprime' que es 'bool'.
   ```

3. **Uso incorrecto de estructuras de control**:
   ```
   Línea 15: Error: 'break' fuera de un bucle while.
   ```
