import sly
from glexer import GoxLexer
from gmodel import *

class GoxParser(sly.Parser):
    """
    Parser para el lenguaje Gox. Convierte una lista de tokens generada por el lexer
    en un Árbol de Sintaxis Abstracta (AST) basado en la gramática definida.
    """

    tokens = GoxLexer.tokens

    debugfile = 'debug.txt'

    precedence = (
        ('right', '='),                 # Asignación
        ('left', 'LOR'),                # OR lógico (más baja precedencia)
        ('left', 'LAND'),               # AND lógico
        ('nonassoc', 'EQ', 'NE'),       # Comparación de igualdad (no asociativos)
        ('nonassoc', 'LT', 'GT', 'LE', 'GE'),  # Operadores relacionales
        ('left', '+', '-'),             # Suma y resta
        ('left', '*', '/', '%'),        # Multiplicación, división y módulo
        ('right', 'UMINUS', 'BACKTICK'),   # Operadores unarios
        ('nonassoc', '(' , ')'),          # Agrupación y acceso
        ('left', 'CALL'),               # Llamadas a funciones
    )


    # Reglas de la gramática



    # Reglas de la gramática

    # program <- statement* EOF
    @_('statement_list')
    def program(self, p):
        """
        Representa un programa completo en Gox.
        Contiene una lista de sentencias (statements).
        """
        return Program(p.statement_list)

    # statement_list <- statement_list statement
    @_('statement_list statement')
    def statement_list(self, p):
        """
        Lista de sentencias. Permite múltiples sentencias en el programa.
        """
        return p.statement_list + [p.statement]

    # statement_list <- statement
    @_('statement')
    def statement_list(self, p):
        """
        Lista de sentencias con una sola sentencia.
        """
        return [p.statement]

# statement <- assignment / vardecl / funcdecl / if_stmt / while_stmt / break_stmt / continue_stmt / return_stmt / print_stmt
    @_('vardecl')
    def statement(self, p):
        """
        Declaración de variables.
        """
        return p.vardecl

    @_('assignment')
    def statement(self, p):
        """
        Asignación de valores a variables.
        """
        return p.assignment

    @_('funcdecl')
    def statement(self, p):
        """
        Declaración de funciones.
        """
        return p.funcdecl
    

    @_('if_stmt')
    def statement(self, p):
        """
        Sentencia condicional (if-else).
        """
        return p.if_stmt

    @_('while_stmt')
    def statement(self, p):
        """
        Sentencia de bucle (while).
        """
        return p.while_stmt

    @_('BREAK ";"')
    def statement(self, p):
        """
        Sentencia break.
        """
        return Break()

    @_('CONTINUE ";"')
    def statement(self, p):
        """
        Sentencia continue.
        """
        return Continue()

    @_('RETURN expression ";"')
    def statement(self, p):
        """
        Sentencia return con una expresión.
        """
        return Return(p.expression)

    @_('print_stmt')
    def statement(self, p):
        """
        Sentencia print para imprimir una expresión.
        """
        return p.print_stmt

    # vardecl <- ('var'/'const') ID type? ('=' expression)? ';'
    @_('VAR ID opt_type opt_init ";"')
    def vardecl(self, p):
        """
        Declaración de variables con la palabra clave 'var'.
        """
        return VarDeclaration(p.ID, p.opt_type, p.opt_init, is_const=False)

    @_('CONST ID type opt_init ";"')
    def vardecl(self, p):
        """
        Declaración de constantes con la palabra clave 'const'.
        """
        return VarDeclaration(p.ID, p.type, p.opt_init, is_const=True)

    @_(' "=" expression')
    def opt_init(self, p):
        """
        Inicialización opcional de una variable o constante.
        """
        return p.expression

    @_('')
    def opt_init(self, p):
        """
        Sin inicialización.
        """
        return None

    @_('type')
    def opt_type(self, p):
        """
        Tipo opcional de una variable o constante.
        """
        return p.type

    @_('')
    def opt_type(self, p):
        """
        Sin tipo especificado.
        """
        return None


    # Asignación
    @_('location "=" expression ";"')
    def assignment(self, p):
        return Assignment(p.location, p.expression)

    @_('IMPORT FUNC ID "(" parameters_opt ")" type_opt ";"',
       'FUNC ID "(" parameters_opt ")" type_opt "{" statement_list "}"')
    def funcdecl(self, p):
        if len(p) == 8:  # Versión con cuerpo
            return FunctionDef(p[1], p[3], p[5], p[7])
        else:  # Versión importada
            return ImportFunction(p[2], p[4], p[6])

    @_('parameters')
    def parameters_opt(self, p):
        return p.parameters

    @_('')
    def parameters_opt(self, p):
        return []

    @_('type')
    def type_opt(self, p):
        return p.type

    @_('')
    def type_opt(self, p):
        return None

    # Parámetros
    @_('param')
    def parameters(self, p):
        return [p.param]
    
    @_('parameters "," param')
    def parameters(self, p):
        return p.parameters + [p.param]

    @_('ID type')
    def param(self, p):
        return Parameter(p.ID, p.type)


    # Tipos
    @_('INT_TYPE')
    def type(self, p):
        return 'int'
    
    @_('FLOAT_TYPE')
    def type(self, p):
        return 'float'
    
    @_('CHAR_TYPE')
    def type(self, p):
        return 'char'
    
    @_('BOOL_TYPE')
    def type(self, p):
        return 'bool'
    

    @_('"{" statement_list "}"')
    def block(self, p):
        """
        Bloque de código delimitado por llaves.
        """
        return p.statement_list
    

    # Sentencias if
    @_('IF expression block')
    def if_stmt(self, p):
        return If(p.expression, p.block, None)
    
    @_('IF expression block ELSE block')
    def if_stmt(self, p):
        return If(p.expression, p.block0, p.block1)

    # Sentencias while

    @_('WHILE expression block')
    def while_stmt(self, p):
        return While(p.expression, p.block)
    

    @_('PRINT expression ";"') 
    def print_stmt(self, p):
        return Print(p.expression)

    #Ubicaciones
    @_('ID')
    def location(self, p):
        return VarLocation(p.ID)

    @_('BACKTICK primary')
    def location(self, p):
        return MemoryAddress(p.primary)
        
    # Expresiones
    @_("expression LOR expression")
    def expression(self, p):
        return BinaryOp("||", p.expression0, p.expression1)

    @_("expression LAND expression")
    def expression(self, p):
        return BinaryOp("&&", p.expression0, p.expression1)

    # Operadores de comparación (igualdad)
    @_("expression EQ expression")
    def expression(self, p):
        return BinaryOp("==", p.expression0, p.expression1)

    @_("expression NE expression")
    def expression(self, p):
        return BinaryOp("!=", p.expression0, p.expression1)

    # Operadores relacionales
    @_("expression LT expression")
    def expression(self, p):
        return BinaryOp("<", p.expression0, p.expression1)

    @_("expression GT expression")
    def expression(self, p):
        return BinaryOp(">", p.expression0, p.expression1)

    @_("expression LE expression")
    def expression(self, p):
        return BinaryOp("<=", p.expression0, p.expression1)

    @_("expression GE expression")
    def expression(self, p):
        return BinaryOp(">=", p.expression0, p.expression1)

    # Operadores aritméticos
    @_('expression "+" expression')
    def expression(self, p):
        return BinaryOp('+', p.expression0, p.expression1)

    @_('expression "-" expression')
    def expression(self, p):
        return BinaryOp('-', p.expression0, p.expression1)

    @_('expression "*" expression')
    def expression(self, p):
        return BinaryOp('*', p.expression0, p.expression1)

    @_('expression "/" expression')
    def expression(self, p):
        return BinaryOp('/', p.expression0, p.expression1)

    @_('expression "%" expression')
    def expression(self, p):
        return BinaryOp('%', p.expression0, p.expression1)

    # Operador unario (manteniendo tu sintaxis)
    @_('"-" expression %prec UMINUS')
    def expression(self, p):
        return UnaryOp('-', p.expression)

    # Expresiones primarias (debes mantener estas también)
    @_('function_call')
    def expression(self, p):
        """
        Llamada a una función.
        """
        return p.function_call

    @_('"(" expression ")"')
    def primary(self, p):
        return p.expression
    
    @_('location')
    def primary(self, p):
        return p.location
    
    @_('primary')
    def expression(self, p):
        return p.primary

    @_('ID "(" arguments_opt ")" %prec CALL')
    def function_call(self, p):
        return FunctionCall(p.ID, p.arguments_opt)

    @_('INTEGER')
    def expression(self, p):
        return LiteralInteger(p.INTEGER)

    @_('FLOAT')
    def expression(self, p):
        return LiteralFloat(p.FLOAT)

    @_('CHAR')
    def expression(self, p):
        return LiteralChar(p.CHAR)

    @_('BOOL')
    def expression(self, p):
        return LiteralBool(p.BOOL)

    # Argumentos

    @_('arguments')
    def arguments_opt(self, p):
        return p.arguments
    
    @_('')
    def arguments_opt(self, p):
        return []
    
    @_('expression')
    def arguments(self, p):
        return [p.expression]
    
    @_('arguments "," expression')
    def arguments(self, p):
        return p.arguments + [p.expression]
        
    

    # Manejo de errores
    def error(self, p):
        if p:
            print(f"Syntax error at line {p.lineno}, token: {p.type}: {p.value}")
        else:
            print("Syntax error at EOF")


import json

def ast_to_dict(node):
    if isinstance(node, list):
        return [ast_to_dict(item) for item in node]
    elif hasattr(node, "__dict__"):
        return {key: ast_to_dict(value) for key, value in node.__dict__.items()}
    else:
        return node


def save_ast_to_json(ast, filename="ast_output.json"):
    ast_json = json.dumps(ast_to_dict(ast), indent=4)
    with open(filename, "w") as f:
        f.write(ast_json)

#Prueba rápida de la gramática
data = '''
/* ******************************************************************* *
 *                                                                     *
 * factorize.gox  (compilador gox)                                     *
 *                                                                     *
 * Dado un numero N, lo descompone en sus factores primos.             *
 * Ejemplo: 21 = 3x7                                                   *
 *                                                                     *
 ********************************************************************* *
 */

func isprime(n int) bool {
    if n < 2 {
        return false;
    }
    var i int = 2;
    while i * i <= n {
        if n * i == 0 {
            return false;
        }
        i = i + 1;
    }
    return true;
}

func factorize(n int) {
    var factor int = 2;
    //print "factores primos de " + n + ": ";

    while n > 1 {
        while n * factor == 0 {  // El error aquí era `n * factor == 0`
            print factor;
            n = n / factor;
        }
        factor = factor + 1;
    }
}


const n int = isprime(2); 
'''
tokens = list(GoxLexer().tokenize(data))
ast = GoxParser().parse(iter(tokens))
save_ast_to_json(ast, "ast_output.json")


# # ----------------------------------------------
# # 1. Prueba de asignación
# # ----------------------------------------------
# tokens = list(GoxLexer().tokenize("x = 3 + 4 * 2;"))
# ast = GoxParser().parse(iter(tokens))
# save_ast_to_json(ast, "test_assignment.json")

# # ----------------------------------------------
# # 2. Prueba de declaración de variable
# # ----------------------------------------------
# tokens = list(GoxLexer().tokenize("var x int = 5;"))
# ast = GoxParser().parse(iter(tokens))
# save_ast_to_json(ast, "test_var_decl.json")


# # # ----------------------------------------------
# # # 3. Prueba de declaración de constante
# # # ----------------------------------------------
# tokens = list(GoxLexer().tokenize("const y float = 3.14;"))
# ast = GoxParser().parse(iter(tokens))
# save_ast_to_json(ast, "test_const_decl.json")

# text = '''

# func simple() {
#     print (hola);
# }

# simple();
# '''
# tokens = list(GoxLexer().tokenize(text))
# ast = GoxParser().parse(iter(tokens))
# save_ast_to_json(ast, "test_var_decl.json")