# GOX Compiler
# Estudiantes
- Juan Manuel Morales
- Camilo Eduardo Muñoz Albornoz

## Descripción

Este proyecto implementa un **compilador para el lenguaje GOX (GoxLang)**. El compilador realiza las siguientes fases:

- **Análisis léxico**: Convierte el código fuente en una lista de tokens.
- **Análisis sintáctico**: Construye un Árbol de Sintaxis Abstracta (AST) a partir de los tokens.
- **Análisis semántico**: Verifica tipos, declaraciones y el uso correcto de variables y funciones.
- **Generación de código intermedio (IR)**: Traduce el AST a instrucciones para una máquina de pila virtual.
- **Ejecución**: Interpreta el código IR en una máquina de pila.

## Estructura del Proyecto

El proyecto está dividido en varios módulos, cada uno con una responsabilidad específica:

- **`glexer.py`**: Implementa el analizador léxico, que convierte el código fuente en una lista de tokens.
- **`gparser.py`**: Implementa el analizador sintáctico, que convierte los tokens en un árbol de sintaxis abstracta (AST).
- **`gmodel.py`**: Define las clases de nodos del AST y el patrón de visitante para recorrerlo.
- **`checkNew.py`**: Implementa el analizador semántico, que verifica la validez del programa (tipos, declaraciones, etc.).
- **`symtab.py`**: Implementa la tabla de símbolos, que almacena información sobre variables, funciones y otros elementos del programa.
- **`typesys.py`**: Define el sistema de tipos y las reglas para operaciones binarias y unarias.
- **`errors.py`**: Maneja los errores detectados durante las fases de análisis.
- **`ircode.py`**: Generador de código intermedio (IR).
- **`stack_machine.py`**: Máquina de pila virtual para ejecutar el IR.
- **`pruebaChecker.py`**: Script principal para ejecutar el compilador.
- **`prueba.gox`**: Ejemplo de archivo fuente en GOX.

---

## Requisitos Previos

Antes de ejecutar el compilador, asegúrate de tener instalado lo siguiente:

- **Python 3.8 o superior**
- Biblioteca `rich` para la visualización de tablas y mensajes de error:
  ```bash
  pip install rich
  ```

---

## Uso

### 1. Escribe tu programa en GOX

Crea un archivo con extensión `.gox`, por ejemplo `prueba.gox`:

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

print isprime(7); // true or 1
```

### 2. Ejecuta el compilador

Para analizar y ejecutar tu archivo fuente:

```bash
python stack_machine.py prueba.gox
```

### 3. Salida esperada

El compilador mostrará:

- El AST generado.
- La tabla de símbolos.
- El código intermedio (IR) generado.
- La ejecución del programa en la máquina de pila.

---

## Ejemplo de Salida

```
Ast generado:
Program(statements=[...])
Symbol Table: 'global'
┌──────────┬───────────────────────────┐
│ key      │ value                     │
├──────────┼───────────────────────────┤
│ mod      │ FunctionDefinition(...)   │
│ isprime  │ FunctionDefinition(...)   │
└──────────┴───────────────────────────┘
Maquina de pila:
MODULE:::
GLOBAL::: ...
FUNCTION::: ...
...
Ejecutando programa:
...
```

---

## Estructura del Código

### 1. **Análisis Léxico (`glexer.py`)**

Convierte el código fuente en tokens.  
Ejemplo de token:
```python
Token(type='ID', value='mod', lineno=1)
```

### 2. **Análisis Sintáctico (`gparser.py`)**

Construye el AST a partir de los tokens.  
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

Verifica tipos, declaraciones y estructuras de control.  
Ejemplo de verificación:
```python
def visit_Return(self, node: Return, env: Symtab):
    func = env.get('$func')
    if not func:
        error(f"Línea {node.lineno}: 'return' fuera de una función.")
        return
    ...
```

### 4. **Tabla de Símbolos (`symtab.py`)**

Almacena información sobre variables y funciones.  
Ejemplo:
```
Symbol Table: 'global'
┌──────────┬───────────────────────────┐
│ key      │ value                     │
├──────────┼───────────────────────────┤
│ mod      │ FunctionDefinition(...)   │
│ isprime  │ FunctionDefinition(...)   │
└──────────┴───────────────────────────┘
```

### 5. **Generación de Código IR (`ircode.py`)**

Traduce el AST a instrucciones para la máquina de pila.

### 6. **Ejecución en Máquina de Pila (`stack_machine.py`)**

Interpreta y ejecuta el código IR.

---

## Personalización

- **Agregar nuevas construcciones**: Modifica `gparser.py` y `gmodel.py`.
- **Extender el sistema de tipos**: Edita `typesys.py`.
- **Mejorar mensajes de error**: Personaliza `errors.py`.
- **Agregar instrucciones IR**: Modifica `ircode.py` y `stack_machine.py`.

---

# Ejemplo de Errores Detectados

- **Variable no declarada**:
  ```
  Línea 10: Error: La variable 'i' no está definida.
  ```
- **Tipo de retorno incorrecto**:
  ```
  Línea 7: Error: Tipo de retorno 'float' no coincide con el tipo de la función 'isprime' que es 'bool'.
  ```
- **Uso incorrecto de estructuras de control**:
  ```
  Línea 15: Error: 'break' fuera de un bucle while.
  ```

---

## Créditos

Este proyecto fue desarrollado como parte del curso de compiladores.

---

## Licencia

Este proyecto es de uso académico y educativo.