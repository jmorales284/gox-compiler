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

from typing import List, Union, Optional
from dataclasses import dataclass
from multimethod import multimethod

from typing import List, Optional
from dataclasses import dataclass

@dataclass
class Node:
    pass

# 1. Program
@dataclass
class Program(Node):
    statements: List["Statement"]

@dataclass
class Statement(Node):
    pass

@dataclass
class Expression(Node):
    pass
    

    
@dataclass
class Declaration(Statement):
    pass
    

@dataclass
class Location(Node):
    pass

# Parte 1. Statements
#
# Los programas en goxlang consisten en sentencias. Estas incluyen
# operaciones como asignación, I/O (imprimir), control de flujo, entre otras.
#


@dataclass
class Assignment(Statement):
    location: Location
    expression: Expression

@dataclass
class Print(Statement):
    expression: Expression

@dataclass
class If(Statement):
    test: Expression
    consequence: List[Statement]
    alternative: Optional[List[Statement]] = None

@dataclass
class While(Statement):
    test: Expression
    body: List[Statement]

@dataclass
class Break(Statement):
    pass

@dataclass
class Continue(Statement):
    pass

@dataclass
class Return(Statement):
    expression: Expression

# Parte 2. Definictions/Declarations
#
# goxlang requiere que todas las variables y funciones se declaren antes de 
# ser utilizadas.  Todas las definiciones tienen un nombre que las identifica.
# Estos nombres se definen dentro de un entorno que forma lo que se denomina
# un "ámbito".  Por ejemplo, ámbito global o ámbito local.


@dataclass
class VarDeclaration(Declaration):
    name: str
    type: str
    value: Optional[Expression] = None
    is_const: bool = False

@dataclass
class Parameter(Node):
    name: str
    type: str

@dataclass
class FunctionDef(Declaration):
    name: str
    parameters: List[Parameter]
    return_type: str
    body: List[Statement]

@dataclass
class ImportFunction(Declaration):
    name: str
    parameters: List[Parameter]
    return_type: str



# Parte 3. Expressions
# Las expresiones representan elementos que se evalúan y producen un valor concreto.
#
# goxlang define las siguientes expressiones y operadores
#


@dataclass
class LiteralInteger(Expression):
    value: int

@dataclass
class LiteralFloat(Expression):
    value: float

@dataclass
class LiteralBool(Expression):
    value: bool

@dataclass
class LiteralChar(Expression):
    value: str

@dataclass
class BinaryOp(Expression):
    operator: str
    left: Expression
    right: Expression

@dataclass
class UnaryOp(Expression):
    operator: str
    operand: Expression

@dataclass
class TypeConversion(Expression):
    type: str
    expression: Expression

@dataclass
class FunctionCall(Expression):
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
    name: str

@dataclass
class MemoryAddress(Location):
    address: Expression

@dataclass
class LocationExpr(Expression):
    location: Location