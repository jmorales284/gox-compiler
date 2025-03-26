from typing import List, Optional
from dataclasses import dataclass
from multimethod import multimeta


@dataclass
class Node:
    def accept(self, v:Visitor, *args, **kwargs):
        return v.visit(self, *args, **kwargs)

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
# 1.1 Assignment
#
#     location = expression ;

@dataclass
class Assignment(Statement):
    location : Location
    expression : Expression

    
# 1.2 Printing
#     print expression ;

@dataclass
class Print(Statement):
    expression: Expression


    
# 1.3 Conditional
#     if test { consequence } else { alternative }
@dataclass
class If(Statement):
    test: Expression
    consequence: List[Statement]
    alternative: List[Statement]



#
# 1.4 While Loop
#     while test { body }
@dataclass
class While(Statement):
    test: Expression
    body: List[Statement]




# 1.5 Break y Continue
#     while test {
#         ...
#         break;   // continue
#     }

@dataclass
class Break(Node):
    pass

@dataclass
class Continue(Node):
    pass


# 1.6 Return un valor
#     return expresion ;
@dataclass
class Return(Statement):
    expression: Expression




    

# ----------------------------------------------------------------------
# Parte 2. Definictions/Declarations
#
# goxlang requiere que todas las variables y funciones se declaren antes de 
# ser utilizadas.  Todas las definiciones tienen un nombre que las identifica.
# Estos nombres se definen dentro de un entorno que forma lo que se denomina
# un "ámbito".  Por ejemplo, ámbito global o ámbito local.

# 2.1 Variables.  Las Variables pueden ser declaradas de varias formas.
#
#     const name = value;
#     const name [type] = value;
#     var name type [= value];
#     var name [type] = value;
#
# Las Constantes son inmutable. Si un valor está presente, el tipo puede ser 
# omitido e inferir desde el tipo del valor.

@dataclass
class VarDeclaration(Declaration):
    name: str
    type: str
    value: Optional[Expression]

@dataclass
class ConstDeclaration(Declaration):
    name: str
    type: Optional[str]
    value: Expression

# ----------------------------------------------------------------------
# Parte 2.3 Function Parameters
# 2.2 Function Parameters
#
#     func square(x int) int { return x*x; }
#
# Un parametro de función (p.ej., "x int") es una clase de variable especial.
# Tiene un nombre y un tipo como una variable, pero es declarada como parte
# de la definición de una función, no como una declaración "var" separada.

@dataclass
class Parameter(Declaration):
    name: str
    type: str



    
# 2.3 Function definitions.
#
#     func name(parameters) return_type { statements }
#
# Una función externa puede ser importada usando una sentencia especial:
#
#     import func name(parameters) return_type;

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




# ----------------------------------------------------------------------

# Parte 3. Expressions
#
# Las expresiones representan elementos que se evalúan y producen un valor concreto.
#
# goxlang define las siguientes expressiones y operadores
#
# 3.1 Literals
#     23           (Entero)
#     4.5          (Flotante)
#     true,false   (Booleanos)
#     'c'          (Carácter)


    
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
    
# 3.2 Binary Operators
#     left + right   (Suma)
#     left - right   (Resta)
#     left * right   (Multiplicación)
#     left / right   (División)
#     left < right   (Menor que)
#     left <= right  (Menor o igual que)
#     left > right   (Mayor que)
#     left >= right  (Mayor o igual que)
#     left == right  (Igual a)
#     left != right  (Diferente de)
#     left && right  (Y lógico)
#     left || right  (O lógico)

@dataclass
class BinaryOp(Expression):
    operator: str
    left: Expression
    right: Expression


# 3.3 Unary Operators
#     +operand  (Positivo)
#     -operand  (Negación)
#     !operand  (Negación lógica)
#     ^operand  (Expandir memoria)

@dataclass
class UnaryOp(Expression):
    operator: str
    operand: Expression


    
# 3.4 Lectura de una ubicación (vea mas adelante)
#     location

#Se  implementa mas bajo
    
# 3.5 Conversiones de tipo
#     int(expr)  
#     float(expr)

@dataclass
class TypeConversion(Expression):
    type: str
    expression: Expression


    
# 3.6 Llamadas a función
#     func(arg1, arg2, ..., argn)

@dataclass 
class FunctionCall(Expression):
    name: str
    arguments: List[Expression]






    
# ----------------------------------------------------------------------
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
# goxlang tiene dos tipos de locations (ubicaciones):
#
# 4.1 Ubicaciones primitivas
#
#     abc = 123;
#     print abc;
#
#     Cualquier nombre usado debe referirse a una definición de variable existente.
#     Por ejemplo, "abc" en este ejmeplo debe tener una declaración correspondiente
#     tal como
#
#     var abc int;

#     location = expression;        // Almacena un valor dentro de location


@dataclass
class VarLocation(Location):
    """Ubicación de una variable normal."""
    name: str


    
# 4.2 Direcciones de memoria. Un número entero precedido por una comilla invertida (``)
#
#     `address = 123;
#     print `address + 10;


@dataclass
class MemoryAddress(Location):
    """Ubicación de una dirección de memoria (` `address`)."""
    address: Expression  # Puede ser un entero o una expresión que lo evalúe


@dataclass
class LocationExpr(Expression):
    """Permite usar una ubicación dentro de expresiones."""
    location: Location
