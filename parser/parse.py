from rich import print
import sly
import json
from lexer.lexer import Lexer
from model import *

class Parser(sly.Parser):
    tokens = Lexer.tokens
    debugfile = 'parser.out'
    
    def __init__(self):
        self.ast = []

    def parse(self, tokens):
        self.ast = super().self.parse(tokens)
        return self.ast

    @_('{ statement }')
    def program(self, p):
        return list(p.statement)

    @_("import_stmt")
    def statement(self, p):
        return p.import_stmt

    @_("assignment")
    def statement(self, p):
        return p.assignment

    @_("vardecl")
    def statement(self, p):
        return p.vardecl

    @_("funcdecl")
    def statement(self, p):
        return p.funcdecl

    @_("if_stmt")
    def statement(self, p):
        return p.if_stmt

    @_("while_stmt")
    def statement(self, p):
        return p.while_stmt

    @_("return_stmt")
    def statement(self, p):
        return p.return_stmt

    @_("print_stmt")
    def statement(self, p):
        return p.print_stmt

    @_("break_stmt")
    def statement(self, p):
        return p.break_stmt

    @_("continue_stmt")
    def statement(self, p):
        return p.continue_stmt

    @_("location '=' expression ';'")
    def assignment(self, p):
        return Assignment(p.location, p.expression)

    @_("VAR ID type? ['=' expression ] ';'")
    def vardecl(self, p):
        return VarDeclaration(p.ID, p.type if hasattr(p, 'type') else None, p.expression if hasattr(p, 'expression') else None)

    @_("FUNC ID '(' parameters ')' type '{' { statement } '}'")
    def funcdecl(self, p):
        return FunctionDef(p.ID, p.parameters, p.type, list(p.statement))

    @_("IF expression '{' { statement } '}' [ELSE '{' { statement } '}']")
    def if_stmt(self, p):
        return If(p.expression, list(p.statement0), list(p.statement1) if hasattr(p, 'statement1') else [])

    @_("WHILE expression '{' { statement } '}'")
    def while_stmt(self, p):
        return While(p.expression, list(p.statement))

    @_("RETURN expression ';'")
    def return_stmt(self, p):
        return Return(p.expression)

    @_("PRINT expression ';'")
    def print_stmt(self, p):
        return Print(p.expression)

    @_("BREAK ';'")
    def break_stmt(self, p):
        return Break()

    @_("CONTINUE ';'")
    def continue_stmt(self, p):
        return Continue()

    @_("IMPORT STRING ';'")
    def import_stmt(self, p):
        return Import(p.STRING)

    @_("ID '(' arguments? ')'")
    def function_call(self, p):
        return FunctionCall(p.ID, p.arguments if hasattr(p, 'arguments') else [])

    @_("parameters | empty")
    def parameters(self, p):
        return p.parameters if hasattr(p, 'parameters') else []

    @_("ID type (',' ID type)*")
    def parameters(self, p):
        params = [(p.ID, p.type)]
        for i in range(2, len(p), 2):
            params.append((p[i], p[i+1]))
        return params

    @_("arguments | empty")
    def arguments(self, p):
        return p.arguments if hasattr(p, 'arguments') else []

    @_("expression (',' expression)*")
    def arguments(self, p):
        args = [p.expression]
        for i in range(2, len(p), 2):
            args.append(p[i])
        return args

    @_("ID | '`' expression '")
    def location(self, p):
        return p.ID if hasattr(p, 'ID') else p.expression

    @_("('int' | 'float' | 'char' | 'bool')")
    def type(self, p):
        return p[0]

    @_("factor (('*' | '/') factor)*")
    def addterm(self, p):
        result = p.factor
        for i in range(1, len(p), 2):
            result = BinaryOp(p[i], result, p[i + 1])
        return result

    @_("addterm (('+' | '-') addterm)*")
    def relterm(self, p):
        result = p.addterm
        for i in range(1, len(p), 2):
            result = BinaryOp(p[i], result, p[i + 1])
        return result

    @_("relterm (('<' | '>' | '<=' | '>=') relterm)*")
    def andterm(self, p):
        result = p.relterm
        for i in range(1, len(p), 2):
            result = BinaryOp(p[i], result, p[i + 1])
        return result

    @_("andterm ('&&' andterm)*")
    def orterm(self, p):
        result = p.andterm
        for i in range(1, len(p), 2):
            result = BinaryOp(p[i], result, p[i + 1])
        return result

    @_("INTEGER | FLOAT | CHAR | bool")
    def literal(self, p):
        return p[0]

    @_("'true' | 'false'")
    def bool(self, p):
        return p[0] == 'true'

    def save_ast_to_json(self, filename='ast_output.json'):
        with open(filename, 'w') as f:
            json.dump([node.__dict__ for node in self.ast], f, indent=4)
"""

# Declaración de funciones


# Sentencia condicional
if_stmt <- 'if' expression '{' statement* '}'
         / 'if' expression '{' statement* '}' 'else' '{' statement* '}'

# Sentencia de bucle
while_stmt <- 'while' expression '{' statement* '}'

# Sentencias de control de flujo
break_stmt <- 'break' ';'
continue_stmt <- 'continue' ';'
return_stmt <- 'return' expression ';'

# Impresión de valores
print_stmt <- 'print' expression ';'

# Parámetros de funciones
parameters <- ID type (',' ID type)*
            / empty

# Tipos de datos
type <- 'int' / 'float' / 'char' / 'bool'

# Ubicación de valores (variables o direcciones)
location <- ID
          / '`' expression

# Expresiones lógicas y aritméticas
expression <- orterm ('||' orterm)*
orterm <- andterm ('&&' andterm)*
andterm <- relterm (('<' / '>' / '<=' / '>=' / '==' / '!=') relterm)*
relterm <- addterm (('+' / '-') addterm)*
addterm <- factor (('*' / '/') factor)*
factor <- literal  
        / ('+' / '-' / '^') expression
        / '(' expression ')'
        / type '(' expression ')'
        / ID '(' arguments ')'
        / location

# Argumentos de funciones
arguments <- expression (',' expression)*
          / empty

# Valores literales
literal <- INTEGER / FLOAT / CHAR / bool
bool <- 'true' / 'false'
"""