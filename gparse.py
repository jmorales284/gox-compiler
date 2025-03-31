import sly
from glexer import GoxLexer
from gmodel import *

class GoxParser(sly.Parser):
    tokens = GoxLexer.tokens

    debugfile = 'debug.txt'

    precedence = (
        ('right', '='),                 # Asignación (mayor precedencia)
        ('left', 'LOR'),                # OR lógico
        ('left', 'LAND'),               # AND lógico
        ('nonassoc', 'EQ', 'NE'),       # Comparación de igualdad
        ('nonassoc', 'LT', 'GT', 'LE', 'GE'),  # Comparaciones
        ('left', '+', '-'),             # Suma/resta
        ('left', '*', '/'),             # Multiplicación/división
        ('right', 'UMINUS'),   # Operadores unarios
        ('nonassoc', '(')     # Agrupación y acceso
    )


    # Reglas de la gramática

    @_('statement_list')
    def program(self, p):
        return Program(p.statement_list)

    @_('statement_list statement')
    def statement_list(self, p):
        return p.statement_list + [p.statement]


    @_('statement')
    def statement_list(self, p):
        return [p.statement]

    # Declaraciones y sentencias
    @_('vardecl')
    def statement(self, p):
        return p.vardecl
    

    @_('assignment')
    def statement(self, p):
        return p.assignment

    @_('funcdecl')
    def statement(self, p):
        return p.funcdecl

    @_('if_stmt')
    def statement(self, p):
        return p.if_stmt

    @_('while_stmt')
    def statement(self, p):
        return p.while_stmt

    @_('BREAK ";"')
    def statement(self, p):
        return Break()

    @_('CONTINUE ";"')
    def statement(self, p):
        return Continue()

    @_('RETURN expression ";"')
    def statement(self, p):
        return Return(p.expression)

    @_('PRINT expression ";"')
    def statement(self, p):
        return Print(p.expression)

    # Declaración de variables
    @_('VAR ID opt_type opt_init ";"')
    def vardecl(self, p):
        return VarDeclaration(p.ID, p.opt_type, p.opt_init, is_const=False)

    @_('CONST ID type opt_init ";"')
    def vardecl(self, p):
        return VarDeclaration(p.ID, p.type, p.opt_init, is_const=True)
    
    @_(' "=" expression')
    def opt_init(self, p):
        return p.expression
    
    @_('')
    def opt_init(self, p):
        return None
    
    @_('type')
    def opt_type(self, p):
        return p.type

    @_('')
    def opt_type(self, p):
        return None


    # Asignación
    @_('location "=" expression ";"')
    def assignment(self, p):
        return Assignment(p.location, p.expression)

    # Declaración de funciones
    @_('FUNC ID "(" parameters_opt ")" type_opt "{" statement_list "}"')
    def funcdecl(self, p):
        return FunctionDef(p.ID, p.parameters_opt, p.type_opt, p.statement_list)

    @_('opt_import FUNC ID "(" parameters_opt ")" type_opt "{" statement_list "}"')
    def funcdecl(self, p):
        if p.opt_import:
            return ImportFunction(p.ID, p.parameters_opt, p.type_opt)
        return FunctionDef(p.ID, p.parameters_opt, p.type_opt, p.statement_list)
    
        
    
    @_('IMPORT')
    def opt_import(self, p):
        return True
    
    @_('')
    def opt_import(self, p):
        return False
    
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
    

    # Sentencias if
    @_('IF expression "{" statement_list "}" ELSE "{" statement_list "}"')
    def if_stmt(self, p):
        return If(p.expression, p.statement_list0, p.statement_list1)
    
    @_('IF expression "{" statement_list "}"')
    def if_stmt(self, p):
        return If(p.expression, p.statement_list, None)

    # Sentencias while
    @_('WHILE expression "{" statement_list "}"')
    def while_stmt(self, p):
        return While(p.expression, p.statement_list)
    

    @_('PRINT "(" expression ")" ";"') 
    def statement(self, p):
        return Print(p.expression)

    #Ubicaciones
    @_('ID')
    def location(self, p):
        return VarLocation(p.ID)

    @_('"`" expression')
    def location(self, p):
        return MemoryAddress(p.expression)
    

    # Expresiones
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

    @_('"-" expression %prec UMINUS')
    def expression(self, p):
        return UnaryOp('-', p.expression)
    
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
    
    @_("expression EQ expression")
    def expression(self, p):
        return BinaryOp("==", p.expression0, p.expression1)
    
    @_("expression NE expression")
    def expression(self, p):
        return BinaryOp("!=", p.expression0, p.expression1)
    
    @_("expression LAND expression")
    def expression(self, p):
        return BinaryOp("&&", p.expression0, p.expression1)
    
    @_("expression LOR expression")
    def expression(self, p):
        return BinaryOp("||", p.expression0, p.expression1)


    @_('"(" expression ")"')
    def expression(self, p):
        return p.expression

    @_('type "(" expression ")"')
    def expression(self, p):
        return TypeConversion(p.type, p.expression)

    @_('ID "(" arguments_opt ")"')
    def expression(self, p):
        return FunctionCall(p.ID, p.arguments_opt)

    @_('location')
    def expression(self, p):
        return LocationExpr(p.location)

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
    @_('expression { "," expression }')
    def arguments(self, p):
        return [p.expression0] + p.expression1

    @_('arguments')
    def arguments_opt(self, p):
        return p.arguments

    @_('')
    def arguments_opt(self, p):
        return []
    

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
var x int = 10;
const y float = 3.14;
func add(a int, b int) int { return a + b; }
if x > 10 { print x; } else { print y; }
'''
tokens = list(GoxLexer().tokenize(data))
ast = GoxParser().parse(iter(tokens))
save_ast_to_json(ast, "ast_output.json")


# ----------------------------------------------
# 1. Prueba de asignación
# ----------------------------------------------
tokens = list(GoxLexer().tokenize("x = 3 + 4 * 2;"))
ast = GoxParser().parse(iter(tokens))
save_ast_to_json(ast, "test_assignment.json")

# ----------------------------------------------
# 2. Prueba de declaración de variable
# ----------------------------------------------
tokens = list(GoxLexer().tokenize("var x int = 5;"))
ast = GoxParser().parse(iter(tokens))
save_ast_to_json(ast, "test_var_decl.json")


# # ----------------------------------------------
# # 3. Prueba de declaración de constante
# # ----------------------------------------------
tokens = list(GoxLexer().tokenize("const y float = 3.14;"))
ast = GoxParser().parse(iter(tokens))
save_ast_to_json(ast, "test_const_decl.json")

# text = '''

# func simple() {
#     print (hola);
# }

# simple();
# '''
# tokens = list(GoxLexer().tokenize(text))
# ast = GoxParser().parse(iter(tokens))
# save_ast_to_json(ast, "test_var_decl.json")