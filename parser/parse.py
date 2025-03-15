# parse.py
#
# El analizador debe construir el modelo de
# datos o un árbol de sintaxis abstracta a
# partir de la entrada de texto. La gramática
# aquí se especifica como PEG (Parsing
# Expression Grammar).
#
# PEG Syntax:
#
#    'quoted'   : Texto literal
#    ( ... )    : Agrupacion
#      e?       : Opcional (0 o 1 coincidencia de e)
#      e*       : Repeticion (0 o mas coincidencias de e)
#      e+       : Repeticion (1 o mas coincidencias)
#     e1 e2     : Coincide e1 luego e2 (secuencia)
#    e1 / e2    : Trata e1. Si falla, trata e2.
#
# Se asume que los nombres en mayúsculas son tokens
# del archivo tokenize.py (su analizador lexico).
# EOF es "Fin del archivo".
#
# program <- statement* EOF
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

from typing import List
from dataclasses import dataclass
from model import (
    Integer, Float, Char, Bool, TypeCast, BinOp, 
    UnaryOp, Assignment, Variable, NamedLocation, 
    Break, Continue, Return, Print, If, While, 
    Function, Parameter,
)

# -------------------------------
# Implementación del Parser
# -------------------------------
class Parser:
	def __init__(self, tokens: List[Token]):
		self.tokens = tokens
		self.current = 0

	def parse(self) -> List:
		statements = []
		while self.peek() and self.peek().type != "EOF":
			statements.append(self.statement())
		return statements

	# -------------------------------
	# Análisis de declaraciones
	# -------------------------------
	def statement(self):
		if self.match("ID"):
			return self.assignment()
		elif self.match("VAR") or self.match("CONST"):
			return self.vardecl()
		elif self.match("FUNC"):
			return self.funcdecl()
		elif self.match("IF"):
			return self.if_stmt()
		elif self.match("WHILE"):
			return self.while_stmt()
		elif self.match("BREAK"):
			return Break()
		elif self.match("CONTINUE"):
			return Continue()
		elif self.match("RETURN"):
			return self.return_stmt()
		elif self.match("PRINT"):
			return self.print_stmt()
		else:
			raise SyntaxError(f"Línea {self.peek().lineno}: Declaración inesperada")
			
	def assignment(self):
		pass
		
	def vardecl(self):
		pass
		
	def funcdecl(self):
		pass
		
	def if_stmt(self):
		pass

	def while_stmt(self):
		pass
		
	def return_stmt(self):
		pass
		
	def print_stmt(self):
		pass
		
	# -------------------------------
	# Análisis de expresiones
	# -------------------------------
	def expression(self):
		pass
		
	def orterm(self):
		pass
		
	def andterm(self):
		pass
		
	def relterm(self):
		pass
		
	def addterm(self):
		pass
		
	def binary_op(self, operators, next_rule):
		pass
		
	def factor(self):
		pass
			
	def parameters(self):
		pass

	# -------------------------------
	# Trate de conservar este codigo
	# -------------------------------

	def peek(self) -> Token:
		return self.tokens[self.current] if self.current < len(self.tokens) else None
		
	def advance(self) -> Token:
		token = self.peek()
		self.current += 1
		return token
		
	def match(self, token_type: str) -> bool:
		if self.peek() and self.peek().type == token_type:
			self.advance()
			return True
		return False
		
	def consume(self, token_type: str, message: str):
		if self.match(token_type):
			return self.tokens[self.current - 1]
		raise SyntaxError(f"Línea {self.peek().lineno}: {message}")
	
	
# -------------------------------
# Prueba del Parser con Tokens
# -------------------------------
tokens = [
	...
]

parser = Parser(tokens)
ast = parser.parse()

# Convertir el AST a una representación JSON para mejor visualización
import json

def ast_to_dict(node):
	if isinstance(node, list):
		return [ast_to_dict(item) for item in node]
	elif hasattr(node, "__dict__"):
		return {key: ast_to_dict(value) for key, value in node.__dict__.items()}
	else:
		return node

ast_json = json.dumps(ast_to_dict(ast), indent=4)

# Guardar el AST como JSON
ast_file_path = "ast_updated.json"
with open(ast_file_path, "w", encoding="utf-8") as f:
	f.write(ast_json)

# Proporcionar el enlace de descarga
ast_file_path