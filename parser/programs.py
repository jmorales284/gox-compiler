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
from gmodel import *

# ---------------------------------------------------------------------
# Expression Simple
#
# Esto se le da a usted como un ejemplo

expr_source = "2 + 3 * 4"

expr_model = BinaryOp('+', Integer(2),
                        BinaryOp('*', Integer(3),
                        Integer(4)))

print(expr_model)
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
    Print(BinaryOp('+', Integer(2), BinaryOp('*', Integer(3), UnaryOp('-', Integer(4))))),
    Print(BinaryOp('-', Float(2.0), BinaryOp('/', Float(3.0), UnaryOp('-', Float(4.0))))),
    Print(BinaryOp('+', UnaryOp('-', Integer(2)), Integer(3)))
])


print(model1)


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
    ConstDeclaration('pi', Float(3.14159)),  # Ahora infiere que es float automáticamente
    VariableDeclaration('tau', 'float'),
    Assignment(VariableReference('tau'), BinaryOp('*', Float(2.0), ConstantReference('pi'))),
    Print(VariableReference('tau'))
])



print(model2)

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
model3 = Program([
    VariableDeclaration('a', 'int', Integer(2)),
    VariableDeclaration('b', 'int', Integer(3)),
    If(
        BinaryOp('<', VariableReference('a'), VariableReference('b')),
        Print(VariableReference('a')),
        Print(VariableReference('b'))
    )
])


print(model3)




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
    ConstDeclaration('n', Integer(10)),
    VariableDeclaration('x', 'int', Integer(1)),
    VariableDeclaration('fact', 'int', Integer(1)),

    While(
        BinaryOp('<', VariableReference('x'), ConstantReference('n')),
        [
            Assignment('fact', BinaryOp('*', VariableReference('fact'), VariableReference('x'))),
            Print(VariableReference('fact')),
            Assignment('x', BinaryOp('+', VariableReference('x'), Integer(1)))
        ]
    )
])

print(model4)

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
    FunctionDefinition('square', [Parameter('x', 'int')], 'int',
                        Return(BinaryOp('*', VariableReference('x'), VariableReference('x')))),
    Print(FunctionCall('square', [Integer(4)])),
    Print(FunctionCall('square', [Integer(10)]))
])

print(model5)

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

model6 = Program([
    FunctionDefinition('fact', [Parameter('n', 'int')], 'int', [
        VariableDeclaration('x', 'int', Integer(1)),
        VariableDeclaration('result', 'int', Integer(1)),

        While(
            BinaryOp('<', VariableReference('x'), VariableReference('n')),
            [
                Assignment('result', BinaryOp('*', VariableReference('result'), VariableReference('x'))),
                Assignment('x', BinaryOp('+', VariableReference('x'), Integer(1)))
            ]
        ),

        Return(VariableReference('result'))
    ]),

    Print(FunctionCall('fact', [Integer(10)]))
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
    VariableDeclaration('pi', 'float', Float(3.14159)),
    VariableDeclaration('spam', 'int', Integer(42)),

    Print(BinaryOp('*', VariableReference('spam'), TypeCast('int', VariableReference('pi')))),
    Print(BinaryOp('*', TypeCast('float', VariableReference('spam')), VariableReference('pi'))),
    Print(BinaryOp('*', TypeCast('int', VariableReference('spam')), TypeCast('int', VariableReference('pi'))))
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
    VariableDeclaration('x', 'int', Memory(8192)),  # Reserva memoria
    VariableDeclaration('addr', 'int', Integer(1234)),  # Variable addr con valor inicial
    MemoryAssignmentLocation('addr', Integer(5678)),  # `addr = 5678;
    Print(BinaryOp('+', MemoryReadLocation('addr'), Integer(8)))  # print(`addr + 8);
])



print(model8)