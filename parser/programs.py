# programs.py
# 
# En las entrañas de su compilador, debe representar programas
# como estructuras de datos. En este archivo, codificará manualmente
# algunos programas goxlang simples usando el modelo de datos que
# se ha desarrollado en el archivo goxlang/model.py
#
# El propósito de este ejercicio es doble:
#
# 1. Asegúrese de comprender el modelo de datos de su compilador.
# 2. Tenga algunas estructuras de programas que pueda usar para pruebas
# y experimentación posteriores.
#
# Este archivo está dividido en secciones. Siga las instrucciones para
# cada parte. Es posible que se haga referencia a partes de este archivo 
# en partes posteriores del proyecto. Planifique tener muchos debates.
#
from model import *

# ---------------------------------------------------------------------
# Expression Simple
#
# Esto se le da a usted como un ejemplo

expr_source = "2 + 3 * 4"

expr_model = BinaryOp('+', int(2),
                        BinaryOp('*', int(3),
                        int(4)))

# ---------------------------------------------------------------------
# Programa 1: Printing
#
# Codifique el siguiente programa el cual prueba la impresión y expresion simple
#
source1 = '''
    print 2 + 3 * -4;
    print 2.0 - 3.0 / -4.0;
    print -2 + 3;
'''

model1 = Program([
    Print(BinaryOp('+', int(2), BinaryOp('*', int(3), UnaryOp('-', int(4))))),
    Print(BinaryOp('-', float(2.0), BinaryOp('/', float(3.0), UnaryOp('-', float(4.0))))),
    Print(BinaryOp('+', UnaryOp('-', int(2)), int(3)))
])




# ---------------------------------------------------------------------
# Programa 2: Declaración de Variables y Constantes.
#            Expresiones y Asignaciones
#
# Codifique la siguiente sentencia.

source2 = '''
    const pi = 3.14159;
    var tau float;
    tau = 2.0 * pi;
    print(tau);
'''

model2 = Program([
    ConstDeclaration('pi', float, Literal(3.14159)),
    VarDeclaration('tau', float),
    Assignment('tau', BinaryOp('*', Literal(2.0), Constant('pi'))),
    Print(Variable('tau'))
])


# ---------------------------------------------------------------------
# Programa 3: Condicionales. Este programa imprime el mínimo de 
#            dos valores
#
# Codifique la siguiente sentencia.

source3 = '''
    var a int = 2;
    var b int = 3;
    if a < b {
        print a;
    } else {
        print b;
    }
'''
model3= Program([
    VarDeclaration('a', int, Literal(2)),
    VarDeclaration('b', int, Literal(3)),
    Conditional(BinaryOp('<', Variable('a'), Variable('b')),
                Print(Variable('a')),
                Print(Variable('b')))
])





# ---------------------------------------------------------------------
# Programa 4: Ciclos.  Este programa imprime los primeros 10 factoriales.
#
source4 = '''
    const n = 10;
    var x int = 1;
    var fact int = 1;

    while x < n {
        fact = fact * x;
        print fact;
        x = x + 1;
    }
'''

model4 = Program([
    ConstDeclaration('n', int, Literal(10)),
    VarDeclaration('x', int, Literal(1)),
    VarDeclaration('fact', int, Literal(1)),
    WhileLoop(BinaryOp('<', Variable('x'), Constant('n')),
            [
                Assignment('fact', BinaryOp('*', Variable('fact'), Variable('x'))),
                Print(Variable('fact')),
                Assignment('x', BinaryOp('+', Variable('x'), Literal(1)))
            ])
])



# ---------------------------------------------------------------------
# Programa 5: Funciones (simple)
#
source5 = '''
    func square(x int) int {
        return x*x;
    }

    print square(4);
    print square(10);
'''

model5 = Program([
    Function('square', [Parameter('x', int)], int, Return(BinaryOp('*', Variable('x'), Variable('x')))),
    Print(FunctionCall('square', [Literal(4)])),
    Print(FunctionCall('square', [Literal(10)]))
])

# ---------------------------------------------------------------------
# Programa 6: Funciones (complejas)
#
source6 = '''
    func fact(n int) int {
        var x int = 1;
        var result int = 1;
        while x < n {
            result = result * x;
            x = x + 1;
        }
        return result;
    }

    print(fact(10));
'''
Return

model6 = Program([
    Function('fact', [Parameter('n', int)], int, [
        VarDeclaration('x', int, Literal(1)),
        VarDeclaration('result', int, Literal(1)),
        WhileLoop(BinaryOp('<', Variable('x'), Variable('n')),
            [
                Assignment('result', BinaryOp('*', Variable('result'), Variable('x'))),
                Assignment('x', BinaryOp('+', Variable('x'), Literal(1)))
            ]),
        Return(Variable('result'))
    ]),
    Print(FunctionCall('fact', [Literal(10)]))
])
        

print(model6)

# ---------------------------------------------------------------------
# Programa 7: Conversión de tipos
#
source7 = '''
    var pi = 3.14159;
    var spam = 42;

    print(spam * int(pi));
    print(float(spam) * pi;)
    print(int(spam) * int(pi));
'''

model7 = Program([
    VarDeclaration('pi', float, Literal(3.14159)),
    VarDeclaration('spam', int, Literal(42)),
    Print(BinaryOp('*', Variable('spam'), FunctionCall('int', [Variable('pi')]))),
    Print(BinaryOp('*', FunctionCall('float', [Variable('spam')]), Variable('pi'))),
    Print(BinaryOp('*', FunctionCall('int', [Variable('spam')]), FunctionCall('int', [Variable('pi')]))
    )
])

print(model7)

# ---------------------------------------------------------------------
# Programa 8: Acceso a memoria
#
source8 = '''
    var x int = ^8192;      // Incrementa memoria por 8192 bytes
    var addr int = 1234;
    `addr = 5678;           // Almacena 5678 en addr
    print(`addr + 8);
'''

model8 = Program([
    VarDeclaration('x', int, Memory(8192)),
    VarDeclaration('addr', int, Literal(1234)),
    MemoryAssignmentLocation('addr', Literal(5678)),
    Print(BinaryOp('+', Memory('addr'), Literal(8)))
])

print(model8)