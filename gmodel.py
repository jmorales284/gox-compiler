#Definicion AST para la gramatica de Gox# program <- statement* EOF
#
# statement <- assignment
#           /  vardecl
#           /  funcdel
#           /  if_stmt
#           /  while_stmt
#           /  break_stmt
#           /  continue_stmt
#           /  return_stmt
#           /  print_stmt
#
# assignment <- location '=' expression ';'
#
# vardecl <- ('var'/'const') ID type? ('=' expression)? ';'
#
# funcdecl <- 'import'? 'func' ID '(' parameters ')' type '{' statement* '}'
#
# if_stmt <- 'if' expression '{' statement* '}'
#         /  'if' expression '{' statement* '}' else '{' statement* '}'
#
# while_stmt <- 'while' expression '{' statement* '}'
#
# break_stmt <- 'break' ';'
#
# continue_stmt <- 'continue' ';'
#
# return_stmt <- 'return' expression ';'
#
# print_stmt <- 'print' expression ';'
#
# parameters <- ID type (',' ID type)*
#            /  empty
#
# type <- 'int' / 'float' / 'char' / 'bool'
#
# location <- ID
#          /  '`' expression
#
# expression <- orterm ('||' orterm)*
#
# orterm <- andterm ('&&' andterm)*
#
# andterm <- relterm (('<' / '>' / '<=' / '>=' / '==' / '!=') reltime)*
#
# relterm <- addterm (('+' / '-') addterm)*
#
# addterm <- factor (('*' / '/') factor)*
#
# factor <- literal
#        / ('+' / '-' / '^') expression
#        / '(' expression ')'
#        / type '(' expression ')'
#        / ID '(' arguments ')'
#        / location
#
# arguments <- expression (',' expression)*
#          / empty
#
# literal <- INTEGER / FLOAT / CHAR / bool
#
# bool <- 'true' / 'false'

# Este archivo define el modelo del Árbol de Sintaxis Abstracta (AST) para el lenguaje Gox.
# El AST es una representación estructurada de los programas escritos en Gox, basada en
# la gramática definida al inicio del archivo.


from typing import List, Union, Optional
from dataclasses import dataclass

from typing import List, Optional
from dataclasses import dataclass

# Clase base para todos los nodos del AST
@dataclass
class Node:
    """
    Clase base para todos los nodos del AST.
    Sirve como punto de partida para heredar las demás clases.
    """
    pass

# 1. Program
@dataclass
class Program(Node):
    """
    Representa un programa completo en Gox.
    Contiene una lista de sentencias (statements) que forman el cuerpo del programa.
    """
    statements: List["Statement"]

# Clase base para todas las sentencias
@dataclass
class Statement(Node):
    """
    Clase base para todas las sentencias en Gox.
    Las sentencias incluyen asignaciones, declaraciones, control de flujo, etc.
    """
    pass

# Clase base para todas las expresiones
@dataclass
class Expression(Node):
    """
    Clase base para todas las expresiones en Gox.
    Las expresiones producen valores y pueden incluir operaciones aritméticas, lógicas, etc.
    """
    pass
    

    
# Clase base para declaraciones
@dataclass
class Declaration(Statement):
    """
    Clase base para todas las declaraciones en Gox.
    Incluye declaraciones de variables y funciones.
    """
    pass
    

# Clase base para ubicaciones
@dataclass
class Location(Node):
    """
    Clase base para ubicaciones en Gox.
    Una ubicación representa un lugar donde se almacena un valor, como una variable o una dirección de memoria.
    """
    pass

# Parte 1. Statements
#
# Los programas en goxlang consisten en sentencias. Estas incluyen
# operaciones como asignación, I/O (imprimir), control de flujo, entre otras.
#


@dataclass
class Assignment(Statement):
    """
    Representa una asignación en Gox.
    location = expression;
    """
    location: Location
    expression: Expression

@dataclass
class Print(Statement):
    """
    Representa una sentencia de impresión en Gox.
    print expression;
    """
    expression: Expression

@dataclass
class If(Statement):
    """
    Representa una sentencia condicional (if) en Gox.
    if test { consequence } [else { alternative }]
    """
    test: Expression
    consequence: List[Statement]
    alternative: Optional[List[Statement]] = None

@dataclass
class While(Statement):
    """
    Representa un bucle while en Gox.
    while test { body }
    """
    test: Expression
    body: List[Statement]

@dataclass
class Break(Statement):
    """
    Representa una sentencia break en Gox.
    break;
    """
    pass

@dataclass
class Continue(Statement):
    """
    Representa una sentencia continue en Gox.
    continue;
    """
    pass

@dataclass
class Return(Statement):
    """
    Representa una sentencia return en Gox.
    return expression;
    """
    expression: Expression

# Parte 2. Definictions/Declarations
#
# goxlang requiere que todas las variables y funciones se declaren antes de 
# ser utilizadas.  Todas las definiciones tienen un nombre que las identifica.
# Estos nombres se definen dentro de un entorno que forma lo que se denomina
# un "ámbito".  Por ejemplo, ámbito global o ámbito local.


@dataclass
class VarDeclaration(Declaration):
    """
    Representa una declaración de variable en Gox.
    var/const name: type = value;
    """
    name: str
    type: str
    value: Optional[Expression] = None
    is_const: bool = False

@dataclass
class Parameter(Node):
    """
    Representa un parámetro de una función en Gox.
    name: type
    """
    name: str
    type: str

@dataclass
class FunctionDef(Declaration):
    """
    Representa una definición de función en Gox.
    func name(parameters) -> return_type { body }
    """
    name: str
    parameters: List[Parameter]
    return_type: str
    body: List[Statement]

@dataclass
class ImportFunction(Declaration):
    """
    Representa una función importada en Gox.
    import func name(parameters) -> return_type;
    """
    name: str
    parameters: List[Parameter]
    return_type: str
    body: List[Statement]

# Parte 3. Expressions
# Las expresiones representan elementos que se evalúan y producen un valor concreto.
# Incluyen literales, operaciones binarias, unarias, conversiones de tipo, etc.

@dataclass
class LiteralInteger(Expression):
    """
    Representa un literal entero en Gox.
    """
    value: int

@dataclass
class LiteralFloat(Expression):
    """
    Representa un literal flotante en Gox.
    """
    value: float

@dataclass
class LiteralBool(Expression):
    """
    Representa un literal booleano en Gox.
    true / false
    """
    value: bool

@dataclass
class LiteralChar(Expression):
    """
    Representa un literal de carácter en Gox.
    """
    value: str

@dataclass
class BinaryOp(Expression):
    """
    Representa una operación binaria en Gox.
    left operator right
    """
    operator: str
    left: Expression
    right: Expression

@dataclass
class UnaryOp(Expression):
    """
    Representa una operación unaria en Gox.
    operator operand
    """
    operator: str
    operand: Expression

@dataclass
class TypeConversion(Expression):
    """
    Representa una conversión de tipo en Gox.
    type(expression)
    """
    type: str
    expression: Expression

@dataclass
class FunctionCall(Expression):
    """
    Representa una llamada a función en Gox.
    name(arguments)
    """
    name: str
    arguments: List[Expression]

# Parte 4: Locations
#
# Una ubicación representa un lugar donde se almacena un valor. Lo complicado
# de las ubicaciones es que se usan de dos maneras diferentes.
# Primero, una ubicación podría aparecer en el lado izquierdo de una asignación
# de esta manera:
#
#     location = expression;        // Almacena un valor dentro de location
#
# Sin embargo, una ubicación podria aparecer como parte de una expresión:
#
#     print location + 10;          // Lee un valor desde location
#
# Una ubicación no es necesariamente simple nombre de variable. Por ejemplo,
# considere el siguiente ejemplo en Python:
#
#     >>> a = [1,2,3,4] 
#     >>> a[2] = 10                 // Almacena en ubicación "a[2]"
#     >>> print(a[2])               // Lee desde ubicación "a[2]" 
#


@dataclass
class VarLocation(Location):
    """
    Representa una ubicación de variable en Gox.
    """
    name: str

@dataclass
class MemoryAddress(Location):
    """
    Representa una dirección de memoria en Gox.
    `expression
    """
    address: Expression

@dataclass
class LocationExpr(Expression):
    """
    Representa una ubicación utilizada como expresión en Gox.
    """
    location: Location