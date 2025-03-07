class Node:
    def __init__(self, type, value=None):
        self.type = type
        self.value = value
        self.children = []

    def add_child(self, node):
        self.children.append(node)

    def __repr__(self):
        return f"Node({self.type}, {self.value}, children={self.children})"
    
class Program(Node):
    def __init__(self, decls,stmts):
        super().__init__("Program")
        self.stmts = stmts
        self.decls = decls
    
    def __repr__(self):
        return f'Program({self.stmts}), {self.decls}'
    
# Parte 1. Statements
#
# Los programas en goxlang consisten en sentencias. Estas incluyen
# operaciones como asignación, I/O (imprimir), control de flujo, entre otras.
#
# 1.1 Assignment
#
#     location = expression ;

class Assignment(Node):
    def __init__(self, location, expression):
        self.location = location
        self.expression = expression

    def __repr__(self):
        return f'Assignment({self.location}, {self.expression})'
    
    
# 1.2 Printing
#     print expression ;

class Print(Node):
    def __init__(self, expression):
        super().__init__("Print")
        self.add_child(Node("Expression", expression))
    
    def __repr__(self):
        return f'Print({self.expression})'
    
# 1.3 Conditional
#     if test { consequence } else { alternative }

class Conditional(Node):
    def __init__(self, test, consequence, alternative = None):
        super().__init__("Conditional")
        self.test = test
        self.consequence = consequence
        self.alternative = alternative

    def __repr__(self):
        return f'Conditional({self.test}, {self.consequence}, {self.alternative})'
    
#
# 1.4 While Loop
#     while test { body }
class WhileLoop(Node):
    def __init__(self, test, body):
        super().__init__("WhileLoop")
        self.add_child(Node("Test", test))
        self.add_child(Node("Body", body))
    
    def __repr__(self):
        return f'WhileLoop({self.test}, {self.body})'

# 1.5 Break y Continue
#     while test {
#         ...
#         break;   // continue
#     }

# def Break(Node):
#     def __init__(self):
#         super().__init__("Break")

#     def __repr__(self):
#         return f'Break()'

# 1.6 Return un valor
#     return expresion ;

class Return(Node):
    def __init__(self, expression):
        super().__init__("Return")
        self.expression = expression

    def __repr__(self):
        return f'Return({self.expression})'
    

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

class VarDeclaration(Node):
    def __init__(self, name, type, value = None):
        super().__init__("Variable")
        self.name = name
        self.type = type
        self.value = value

    def __repr__(self):
        return f'Var({self.name}, {self.type}, {self.value})'

class ConstDeclaration(Node):
    def __init__(self, name, type, value):
        super().__init__("Constant")
        self.name = name
        self.type = type
        self.value = value

    def __repr__(self):
        return f'Const({self.name}, {self.type}, {self.value})'
    

    
# 2.2 Function definitions.
#
#     func name(parameters) return_type { statements }
#
# Una función externa puede ser importada usando una sentencia especial:
#
#     import func name(parameters) return_type;

class Function(Node):
    def __init__(self, name, parameters, return_type, body):
        super().__init__("Function")
        self.name = name
        self.parameters = parameters
        self.return_type = return_type
        self.body = body
    
    def __repr__(self):
        return f'Function({self.name}, {self.parameters}, {self.return_type}, {self.body})'
    
class Import(Node):
    def __init__(self, name, parameters, return_type):
        super().__init__("Import")
        self.name = name
        self.parameters = parameters
        self.return_type = return_type

    def __repr__(self):
        return f'Import({self.name}, {self.parameters}, {self.return_type})'
    
# 2.3 Function Parameters
#
#     func square(x int) int { return x*x; }
#
# Un parametro de función (p.ej., "x int") es una clase de variable especial.
# Tiene un nombre y un tipo como una variable, pero es declarada como parte
# de la definición de una función, no como una declaración "var" separada.

class Parameter(Node):
    def __init__(self, name, type):
        super().__init__("Parameter")
        self.name = name
        self.type = type
    
    def __repr__(self):
        return f'Parameter({self.name}, {self.type})'
    
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

class Literal(Node):
    def __init__(self, value):
        super().__init__("Literal")
        self.value = value
    
    def __repr__(self):
        return f'Literal({self.value})'
    
class Variable(Node):
    def __init__(self, name):
        super().__init__("Variable")
        self.name = name
    
    def __repr__(self):
        return f'Variable({self.name})'
    
class Constant(Node):
    def __init__(self, name, va):
        super().__init__("Constant")
        self.name = name
    
    def __repr__(self):
        return f'Constant({self.name})'
    
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

class BinaryOp(Node):
    def __init__(self, operator, left, right):
        super().__init__("BinaryOp")
        self.operator = operator
        self.left = left
        self.right = right
    
    def __repr__(self):
        return f'BinaryOp({self.operator}, {self.left}, {self.right})'
    
# 3.3 Unary Operators
#     +operand  (Positivo)
#     -operand  (Negación)
#     !operand  (Negación lógica)
#     ^operand  (Expandir memoria)

class UnaryOp(Node):
    def __init__(self, operator, operand):
        super().__init__("UnaryOp")
        self.operator = operator
        self.operand = operand
    
    def __repr__(self):
        return f'UnaryOp({self.operator}, {self.operand})'
    
# 3.4 Lectura de una ubicación (vea mas adelante)
#     location

class Location(Node):
    def __init__(self, name):
        super().__init__("Location")
        self.name = name
    
    def __repr__(self):
        return f'Location({self.name})'
    
# 3.5 Conversiones de tipo
#     int(expr)  
#     float(expr)

class TypeCast(Node):
    def __init__(self, type, expression):
        super().__init__("TypeCast")
        self.type = type
        self.expression = expression
    
    def __repr__(self):
        return f'TypeCast({self.type}, {self.expression})'
    
# 3.6 Llamadas a función
#     func(arg1, arg2, ..., argn)

class FunctionCall(Node):
    def __init__(self, name, arguments):
        super().__init__("FunctionCall")
        self.name = name
        self.arguments = arguments
    
    def __repr__(self):
        return f'FunctionCall({self.name}, {self.arguments})'
    
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

class PrimitiveAssignmentLocation(Node):
    def __init__(self, name, expression):
        super().__init__("PrimitiveAssignmentLocation")
        self.name = name
        self.expression = expression
    
    def __repr__(self):
        return f'PrimitiveAssignmentLocation({self.name}), {self.expression}'
    
class PrimitiveReadLocation(Node):
    def __init__(self, name):
        super().__init__("PrimitiveReadLocation")
        self.name = name
    
    def __repr__(self):
        return f'PrimitiveReadLocation({self.name})'
    
# 4.2 Direcciones de memoria. Un número entero precedido por una comilla invertida (``)
#
#     `address = 123;
#     print `address + 10;

class MemoryAssignmentLocation(Node):
    def __init__(self, address, expression):
        super().__init__("MemoryAssignmentLocation")
        self.address = address
        self.expression = expression
    
    def __repr__(self):
        return f'MemoryAssignmentLocation({self.address}), {self.expression}'
    
class MemoryReadLocation(Node):
    def __init__(self, address):
        super().__init__("MemoryReadLocation")
        self.address = address
    
    def __repr__(self):
        return f'MemoryReadLocation({self.address})'
