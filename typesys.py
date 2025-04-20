# typesys.py
'''
Sistema de tipos
================
Este archivo implementa las características básicas del sistema de tipos. Existe 
mucha flexibilidad, pero la mejor estrategia podría ser no darle demasiadas 
vueltas al problema. Al menos no al principio. Estos son los requisitos 
básicos mínimos:

1. Los tipos tienen identidad (p. ej., al menos un nombre como 'int', 'float', 'char').
2. Los tipos deben ser comparables (p. ej., int != float).
3. Los tipos admiten diferentes operadores (p. ej., +, -, *, /, etc.).

Una forma de lograr todos estos objetivos es comenzar con algún tipo de 
enfoque basado en tablas. No es lo más sofisticado, pero funcionará 
como punto de partida. Puede volver a refactorizar el sistema de tipos
más adelante.
'''

typenames = { 'int', 'float', 'char', 'bool' }

# Capabilities
bin_ops = {
	# Integer operations
	('int', '+', 'int') : 'int',
	('int', '-', 'int') : 'int',
	('int', '*', 'int') : 'int',
	('int', '/', 'int') : 'int',

	('int', '<', 'int')  : 'bool',
	('int', '<=', 'int') : 'bool',
	('int', '>', 'int')  : 'bool',
	('int', '>=', 'int') : 'bool',
	('int', '==', 'int') : 'bool',
	('int', '!=', 'int') : 'bool',

	# Float operations
	('float', '+', 'float') : 'float',
	('float', '-', 'float') : 'float',
	('float', '*', 'float') : 'float',
	('float', '/', 'float') : 'float',

	('float', '<', 'float')  : 'bool',
	('float', '<=', 'float') : 'bool',
	('float', '>', 'float')  : 'bool',
	('float', '>=', 'float') : 'bool',
	('float', '==', 'float') : 'bool',
	('float', '!=', 'float') : 'bool',

	# Bools
	('bool', '&&', 'bool') : 'bool',
	('bool', '||', 'bool') : 'bool',
	('bool', '==', 'bool') : 'bool',
	('bool', '!=', 'bool') : 'bool',

	# Char
	('char', '<', 'char')  : 'bool',
	('char', '<=', 'char') : 'bool',
	('char', '>', 'char')  : 'bool',
	('char', '>=', 'char') : 'bool',
	('char', '==', 'char') : 'bool',
	('char', '!=', 'char') : 'bool',
}

# Check if a binary operator is supported. Returns the
# result type or None (if not supported). Type checker
# uses this function.

def check_binop(op, left_type, right_type):
	op = dict_equivalence.get(op, op)  # Convertir a un operador de un carácter
	return bin_ops.get((left_type, op, right_type))

unary_ops = {
	('+', 'int') : 'int',
	('-', 'int') : 'int',
	('^', 'int') : 'int',
    
	('+', 'float') : 'float',
	('-', 'float') : 'float',

	('!', 'bool') : 'bool',
}

def check_unaryop(op, operand_type):
	op = dict_equivalence.get(op, op)  # Convertir a un operador de un carácter
	return unary_ops.get((op, operand_type))

# Operadores de dos caracteres
TWO_CHAR = {
		'<=': 'LE', '>=': 'GE', '==': 'EQ', '!=': 'NE', '&&': 'LAND', '||': 'LOR'
}

# Operadores y símbolos de un carácter
ONE_CHAR = {
		'+': 'PLUS', '-': 'MINUS', '*': 'TIMES', '/': 'DIVIDE', '<': 'LT', '>': 'GT',
		'=': 'ASSIGN', ';': 'SEMI', '(': 'LPAREN', ')': 'RPAREN', '{': 'LBRACE', '}': 'RBRACE', ',': 'COMMA', '`': 'DEREF'
}

dict_equivalence={
	'PLUS': '+',
	'MINUS': '-',
	'TIMES': '*',
	'DIVIDE': '/',
	'LT': '<',
	'GT': '>',
	'ASSIGN': '=',
	'SEMI': ';',
	'LPAREN': '(',
	'RPAREN': ')',
	'LBRACE': '{',
	'RBRACE': '}',
	'COMMA': ',',
	'DEREF': '`',
	'LE': '<=',
	'GE': '>=',
	'EQ': '==',
	'NE': '!=',
	'LAND': '&&',
	'LOR': '||',
}
