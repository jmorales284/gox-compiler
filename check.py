# check.py
'''
Este archivo contendrá la parte de verificación/validación de tipos
del compilador.  Hay varios aspectos que deben gestionarse para
que esto funcione. Primero, debe tener una noción de "tipo" en su compilador.
Segundo, debe administrar los entornos y el alcance para manejar los
nombres de las definiciones (variables, funciones, etc.).

Una clave para esta parte del proyecto es realizar pruebas adecuadas.
A medida que agregue código, piense en cómo podría probarlo.
'''
from collections import ChainMap
from rich    import print
from typing  import Union, List


from errors   import error, errors_detected
from gmodel   import *
from symtab  import Symtab
from typesys import typenames, check_binop, check_unaryop


class Checker(Visitor):
	@classmethod
	def check(cls, n:Node):
		'''
		1. Crear una nueva tabla de simbolos
		2. Visitar todas las declaraciones
		'''
		check = cls()
		env = Symtab()
		n.accept(check, env)
		return check

	def visit(self, n:Program, env:Symtab):
		'''
		1. recorrer la lista de elementos
		'''
		for stmt in n.stmts:
			stmt.accept(self, env)

	# Statements

	def visit(self, n:Assignment, env:Symtab):
		# Validar n.loc
		loc_type = n.loc.accept(self, env)

		#visitar n.expr
		expr_type = n.expr.accept(self, env)

		# Verificar si son tipos compatibles
		return check_binop('=', loc_type, expr_type)

	def visit(self, n:Print, env:Symtab):
		#visitar n.expr
		return n.expr.accept(self, env)

	def visit(self, n:Conditional, env:Symtab):

		# Visitar n.test (validar tipos)
		n.test.accept(self, env)

		# Visitar Stament por n.then
		for stmt in n.cons:
			stmt.accept(self, env)
		# Si existe opcion n.else_, visitar
			
	def visit(self, n:WhileLoop, env:Symtab):
		# Visitar n.test (validar tipos)
		n.test.accept(self, env)

		#
		env['$loop'] = True

		# visitar n.body
		for b in n.body:
			b.accept(self, env)
		env['$loop'] = False


		
	def visit(self, n:Union[Break, Continue], env:Symtab):
		# Verificar que esta dentro de un ciclo while
		if not env['$loop']:
			error(f"'{n} por fuera de un ciclo while'", n.lineno)
			


			
	def visit(self, n:Return, env:Symtab):
		'''
		1. Si se ha definido n.expr, validar que sea del mismo tipo de la función
		'''
		# Revisar que se esta dentro de una funcion
		
		# Si se ha definido n.expr, validar que sea del mismo tipo de la función

		# Visitar Expression
		n.expr.accept(self, env)
	


	# Declarations

	def visit(self, n:VariableDeclaration, env:Symtab):
		# Asignar tipo a la constante
		n.type = n.value.accept(self, env)

		# Agregar a la tabla de simbolos
		env.add(n.name, n)

	def visit(self, n:VariableDeclaration, env:Symtab):
		# Agregar n.name a la TS actual
		env.add(n.name, n)
		if n.value:
			dtype = n.value.accept(self, env)
			return check_binop('=', n.type, dtype)
		

	def visit(self, n:FunctionDefinition, env:Symtab):
		# Guardar la función en la TS actual
		env.add(n.name, n)

		# Crear una nueva TS para la función
		env = Symtab(n.name, env)

		# Variable para referenciar la funcion
		env['$func'] = True

		# Agregar todos los n.params dentro de la TS
		for p in n.params:
			p.accept(self, env)

		# Visitar n.stmts
		for stmt in n.stmts:
			stmt.accept(self, env)
		
		env['$func'] = False


	def visit(self, n:Parameter, env:Symtab):
		# Guardar el parametro (name, type) en TS
		env.add(n.name, n)
		
	# Expressions

	def visit(self, n:Literal, env:Symtab):

		# Retornar el tipo de la literal
		# Los literales primitivos basicos ya tienen un tipo definido en la estructura del ast (model.py)
		return n.type

	def visit(self, n:BinaryOperation, env:Symtab):
		# visitar n.left y luego n.right
		left_type = n.left.accept(self, env)
		right_type = n.right.accept(self, env)

		# Verificar si son tipos compatibles
		return check_binop(n.opr, left_type, right_type)
		
	def visit(self, n:UnaryOperation, env:Symtab):
		'''
		1. visitar n.expr
		2. validar si es un operador unario valido
		'''
		type1 = n.expr.accept(self, env)
		return check_unaryop(n.opr, type1)

	def visit(self, n:TypeConversion, env:Symtab):
		# Visitar n.expr para validar
		n.expr.accept(self, env)

		# Retornar el tipo del cast n.type
		return n.type

	def visit(self, n:FunctionCall, env:Symtab):
		'''
		3. verificar que len(n.args) == len(func.params)
		4. verificar que cada arg sea compatible con cada param de la función
		'''
		# Validar si n.name existe
		func = env.get(n.name)
		if func is None:
			error(f"'{n.name}' no es una funcion definida", n.lineno)
			return
		
		# Verificar que len(n.args) == len(func.params)
		if len(n.args) != len(func.params):
			error(f"El numero de argumentos no coincide con la declaracion de la funcion '{n.name}'", n.lineno)
			return
		
		# Visitar n.args (si estan definidos) y verifica que cada arg sea compatible con cada param de la función
		for param, arg in zip(func.params, n.args):
			arg_type = arg.accept(self, env)
			if param.type != arg_type:
				error(f"El tipo de argumento '{arg.name}' no es compatible con el tipo de parametro '{param.name}'", n.lineno)

	def visit(self, n:NamedLocation, env:Symtab):
		'''
		1. Verificar si n.name existe en TS y obtener el tipo
		2. Retornar el tipo
		'''
		# Verificar si n.name existe en TS y obtener el tipo
		node = env.get(n.name)

		# Retornar el tipo
		if node: return node.type
		error(f"'{n.name}' no es una variable definida", n.lineno)

	def visit(self, n:MemoryLocation, env:Symtab):
		'''
		1. Visitar n.address (expression) para validar
		2. Retornar el tipo de datos
		'''
		pass
