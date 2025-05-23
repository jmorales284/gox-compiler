# ircode.py
# Juan Manuel Morales
# Camilo Muñoz Albornoz
'''
Una Máquina Intermedia "Virtual"
================================

Una CPU real generalmente consta de registros y un pequeño conjunto de
códigos de operación básicos para realizar cálculos matemáticos,
cargar/almacenar valores desde memoria y controlar el flujo básico
(ramas, saltos, etc.). Aunque puedes hacer que un compilador genere
instrucciones directamente para una CPU, a menudo es más sencillo
dirigirse a un nivel de abstracción más alto. Una de esas abstracciones
es la de una máquina de pila (stack machine).

Por ejemplo, supongamos que deseas evaluar una operación como esta:

    a = 2 + 3 * 4 - 5

Para evaluar la expresión anterior, podrías generar pseudo-instrucciones
como esta:

    CONSTI 2      ; stack = [2]
    CONSTI 3      ; stack = [2, 3]
    CONSTI 4      ; stack = [2, 3, 4]
    MULI          ; stack = [2, 12]
    ADDI          ; stack = [14]
    CONSTI 5      ; stack = [14, 5]
    SUBI          ; stack = [9]
    LOCAL_SET "a" ; stack = []

Observa que no hay detalles sobre registros de CPU ni nada por el estilo
aquí. Es mucho más simple (un módulo de nivel inferior puede encargarse
del mapeo al hardware más adelante si es necesario).

Las CPUs usualmente tienen un pequeño conjunto de tipos de datos como
enteros y flotantes. Existen instrucciones dedicadas para cada tipo. El
código IR seguirá el mismo principio, admitiendo operaciones con enteros
y flotantes. Por ejemplo:

    ADDI   ; Suma entera
    ADDF   ; Suma flotante

Aunque el lenguaje de entrada podría tener otros tipos como `bool` y
`char`, esos tipos deben ser mapeados a enteros o flotantes. Por ejemplo,
un bool puede representarse como un entero con valores {0, 1}. Un char
puede representarse como un entero cuyo valor sea el mismo que el código
del carácter (es decir, un código ASCII o código Unicode).

Con eso en mente, aquí hay un conjunto básico de instrucciones para
nuestro Código IR:

    ; Operaciones enteras
    CONSTI value             ; Apilar un literal entero
    ADDI                     ; Sumar los dos elementos superiores de la pila
    SUBI                     ; Restar los dos elementos superiores de la pila
    MULI                     ; Multiplicar los dos elementos superiores de la pila
    DIVI                     ; Dividir los dos elementos superiores de la pila
    ANDI                     ; AND bit a bit
    ORI                      ; OR bit a bit
    LTI                      : <
    LEI                      : <=
    GTI                      : >
    GEI                      : >=
    EQI                      : ==
    NEI                      : !=
    PRINTI                   ; Imprimir el elemento superior de la pila
    PEEKI                    ; Leer entero desde memoria (dirección en la pila)
    POKEI                    ; Escribir entero en memoria (valor, dirección en la pila)
    ITOF                     ; Convertir entero a flotante

    ; Operaciones en punto flotante
    CONSTF value             ; Apilar un literal flotante
    ADDF                     ; Sumar los dos elementos superiores de la pila
    SUBF                     ; Restar los dos elementos superiores de la pila
    MULF                     ; Multiplicar los dos elementos superiores de la pila
    DIVF                     ; Dividir los dos elementos superiores de la pila
    LTF                      : <
    LEF                      : <=
    GTF                      : >
    GEF                      : >=
    EQF                      : ==
    NEF                      : !=
    PRINTF                   ; Imprimir el elemento superior de la pila
    PEEKF                    ; Leer flotante desde memoria (dirección en la pila)
    POKEF                    ; Escribir flotante en memoria (valor, dirección en la pila)
    FTOI                     ; Convertir flotante a entero

    ; Operaciones orientadas a bytes (los valores se presentan como enteros)
    PRINTB                   ; Imprimir el elemento superior de la pila
    PEEKB                    ; Leer byte desde memoria (dirección en la pila)
    POKEB                    ; Escribir byte en memoria (valor, dirección en la pila)

    ; Carga/almacenamiento de variables.
    ; Estas instrucciones leen/escriben variables locales y globales. Las variables
    ; son referenciadas por algún tipo de nombre que las identifica. La gestión
    ; y declaración de estos nombres también debe ser manejada por tu generador de código.
    ; Sin embargo, las declaraciones de variables no son una instrucción normal. En cambio,
    ; es un tipo de dato que debe asociarse con un módulo o función.
    LOCAL_GET name           ; Leer una variable local a la pila
    LOCAL_SET name           ; Guardar una variable local desde la pila
    GLOBAL_GET name          ; Leer una variable global a la pila
    GLOBAL_SET name          ; Guardar una variable global desde la pila

    ; Llamadas y retorno de funciones.
    ; Las funciones se referencian por nombre. Tu generador de código deberá
    ; encontrar alguna manera de gestionar esos nombres.
    CALL name                ; Llamar función. Todos los argumentos deben estar en la pila
    RET                      ; Retornar de una función. El valor debe estar en la pila

    ; Control estructurado de flujo
    IF                       ; Comienza la parte "consecuencia" de un "if". Prueba en la pila
    ELSE                     ; Comienza la parte "alternativa" de un "if"
    ENDIF                    ; Fin de una instrucción "if"

    LOOP                     ; Inicio de un ciclo
    CBREAK                   ; Ruptura condicional. Prueba en la pila
    CONTINUE                 ; Regresa al inicio del ciclo
    ENDLOOP                  ; Fin del ciclo

    ; Memoria
    GROW                     ; Incrementar memoria (tamaño en la pila) (retorna nuevo tamaño)

Una palabra sobre el acceso a memoria... las instrucciones PEEK y POKE
se usan para acceder a direcciones de memoria cruda. Ambas instrucciones
requieren que una dirección de memoria esté en la pila *primero*. Para
la instrucción POKE, el valor a almacenar se apila después de la dirección.
El orden es importante y es fácil equivocarse. Así que presta mucha
atención a eso.

Su tarea
=========
Su tarea es la siguiente: Escribe código que recorra la estructura del
programa y la aplane a una secuencia de instrucciones representadas como
tuplas de la forma:

       (operation, operands, ...)

Por ejemplo, el código del principio podría terminar viéndose así:

    code = [
       ('CONSTI', 2),
       ('CONSTI', 3),
       ('CONSTI', 4),
       ('MULI',),
       ('ADDI',),
       ('CONSTI', 5),
       ('SUBI',),
       ('LOCAL_SET', 'a'),
    ]

Funciones
=========
Todo el código generado está asociado con algún tipo de función. Por
ejemplo, con una función definida por el usuario como esta:

    func fact(n int) int {
        var result int = 1;
        var x int = 1;
        while x <= n {
            result = result * x;
            x = x + 1;
        }
     }

Debes crear un objeto `Function` que contenga el nombre de la función,
los argumentos, el tipo de retorno, las variables locales y un cuerpo
que contenga todas las instrucciones de bajo nivel. Nota: en este nivel,
los tipos representarán tipos IR de bajo nivel como Integer (I) y Float (F).
No son los mismos tipos usados en el código GoxLang de alto nivel.

Además, todo el código que se define *fuera* de una función debe ir
igualmente en una función llamada `_init()`. Por ejemplo, si tienes
declaraciones globales como esta:

     const pi = 3.14159;
     const r = 2.0;
     print pi*r*r;

Tu generador de código debería en realidad tratarlas así:

     func _init() int {
         const pi = 3.14159;
         const r = 2.0;
         print pi*r*r;
         return 0;
     }

En resumen: todo el código debe ir dentro de una función.

Módulos
=======
La salida final de la generación de código debe ser algún tipo de
objeto `Module` que contenga todo. El módulo incluye objetos de función,
variables globales y cualquier otra cosa que puedas necesitar para
generar código posteriormente.
'''
from rich   import print
from typing import List, Union
from typesys import dict_equivalence
from gmodel  import *
#from symtab import Symtab # Se puede obviar por ahora

# Todo el código IR se empaquetará en un módulo. Un 
# módulo es un conjunto de funciones.

# Clase IRModule: Contenedor de Todo el codigo IR con funciones y variables globales
class IRModule:
	def __init__(self):
		self.functions = { }       # Dict de funciones IR , para guardar las funciones
		self.globals = { }         # Dict de variables global, para guardar las variables globales
		

	# Metodo de volcado para imprimir el contenido del modulo
	def dump(self):
		print("MODULE:::")
		for glob in self.globals.values():
			glob.dump()
			
		for func in self.functions.values():
			func.dump()
			
# Clase IRGlobal: Representa una variable global en el módulo.
class IRGlobal:
	def __init__(self, name, type):
		self.name = name # Nombre de la variable
		self.type = type # Tipo de la variable
		
	# Metodo de volcado para imprimir el contenido de la variable, aqui ya no hay tipos especiales, solo I de enteros, bool y char y el F de float
	def dump(self):
		print(f"GLOBAL::: {self.name}: {self.type}")

# Las funciones sirven como contenedor de las 
# instrucciones IR de bajo nivel específicas de cada
# función. También incluyen metadatos como el nombre 
# de la función, los parámetros y el tipo de retorno.

# Clase IRFunction: Representa una función en el módulo.
class IRFunction:
	def __init__(self, module, name, parmnames, parmtypes, return_type, imported=False):
		# Agreguemos la lista de funciones del módulo adjunto
		self.module = module # Modulo al que pertenece la funcion
		module.functions[name] = self # Agregamos la funcion al modulo
		self.name = name 
		self.parmnames = parmnames
		self.parmtypes = parmtypes
		self.return_type = return_type
		self.imported = imported
		self.locals = { }    # Variables Locales
		self.code = [ ]      # Lista de Instrucciones IR 
		
	def new_local(self, name, type):
		self.locals[name] = type
		
	def append(self, instr):
		self.code.append(instr)
		
	def extend(self, instructions):
		self.code.extend(instructions)
		
	def dump(self):
		print(f"FUNCTION::: {self.name}, {self.parmnames}, {self.parmtypes} {self.return_type}")
		print(f"locals: {self.locals}")
		for instr in self.code:
			print(instr)
			
# Mapeo de tipos de GoxLang a tipos de IR 
_typemap = {
	'int'  : 'I',
	'float': 'F',
	'bool' : 'I',
	'char' : 'I',
}

# Generar un nombre de variable temporal único
def new_temp(n=[0]):
	n[0] += 1
	return f'$temp{n[0]}'

# Una función de nivel superior que comenzará a generar IRCode
# Clase IRCode: Generador de codigo IR recorriendo el arbol de sintaxis
class IRCode(Visitor):
	# Diccion de operadores binarios y sus instrucciones IR correspondientes
	_binop_code = {
		('int', '+', 'int')  : 'ADDI',
		('int', '-', 'int')  : 'SUBI',
		('int', '*', 'int')  : 'MULI',
		('int', '/', 'int')  : 'DIVI',
		('int', '<', 'int')  : 'LTI',
		('int', '<=', 'int') : 'LEI',
		('int', '>', 'int')  : 'GTI',
		('int', '>=', 'int') : 'GEI',
		('int', '==', 'int') : 'EQI',
		('int', '!=', 'int') : 'NEI',
		
		('float', '+',  'float') : 'ADDF',
		('float', '-',  'float') : 'SUBF',
		('float', '*',  'float') : 'MULF',
		('float', '/',  'float') : 'DIVF',
		('float', '<',  'float') : 'LTF',
		('float', '<=', 'float') : 'LEF',
		('float', '>',  'float') : 'GTF',
		('float', '>=', 'float') : 'GEF',
		('float', '==', 'float') : 'EQF',
		('float', '!=', 'float') : 'NEF',
		
		('char', '<', 'char')  : 'LTI',
		('char', '<=', 'char') : 'LEI',
		('char', '>', 'char')  : 'GTI',
		('char', '>=', 'char') : 'GEI',
		('char', '==', 'char') : 'EQI',
		('char', '!=', 'char') : 'NEI',

	#Añadidos ya que no existen en el lenguaje
		('bool', '&&', 'bool') : 'ANDI',
		('bool', '||', 'bool') : 'ORI',
		('bool', '<',  'bool') : 'LTI',
		('bool', '<=', 'bool') : 'LEI',
		('bool', '>',  'bool') : 'GTI',
		('bool', '>=', 'bool') : 'GEI',
		('bool', '==', 'bool') : 'EQI',
		('bool', '!=', 'bool') : 'NEI',
	}

	# Diccion de operadores unarios y sus instrucciones IR correspondientes
	_unaryop_code = {
		('+', 'int')   : [],
		('+', 'float') : [],
		('-', 'int')   : [('CONSTI', -1), ('MULI',)],
		('-', 'float') : [('CONSTF', -1.0), ('MULF',)],
		('!', 'bool')  : [('CONSTI', -1), ('MULI',)],
		('^', 'int')   : [ ('GROW',) ]
	}
	# Diccion de conversiones de tipo y sus instrucciones IR correspondientes
	_typecast_code = {
		# (from, to) : [ ops ]
		('int', 'float') : [ ('ITOF',) ],
		('float', 'int') : [ ('FTOI',) ],
	}

	# Diccion de operadores y sus equivalentes en el lenguaje
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
		'PRINT': 'print',
		'CARET': '^'
	}

	# --- Constructor: Generador de codigo IR
	@classmethod
	def gencode(cls, node:Program):
		'''
		El nodo es el nodo superior del árbol de 
		modelo/análisis.
		La función inicial se llama "_init". No acepta 
		argumentos. Devuelve un entero.
		'''
		ircode = cls() # Se crea un codigo de este tipo
		
		module = IRModule()
		func = IRFunction(module, 'main', [], [], 'I') # Se crea la funcion principal no acepta argumentos y devuelve un entero 
		for item in node.stmts:# Por cada elemento del nodo
			item.accept(ircode, func)
		if '_actual_main' in module.functions:
			func.append(('CALL', '_actual_main'))
		else:
			func.append(('CONSTI', 0))
		func.append(('RET',))
		return module
	
	# --- Statements

	# Metodos visit_* Procesan los nodos del arbol de sintaxis y generan instrucciones IR


	# Asignacion de variables
	def visit_PrimitiveAssignmentLocation(self, n:PrimitiveAssignmentLocation, func:IRFunction):
		#Visitar la expresion
		n.expression.accept(self, func) # Se le asigna el valor a la expresion
		#Añadir la instruccion al codigo IR
		if n.name in func.locals: # Se decide si la variable es local o global
			func.append(('LOCAL_SET', n.name))
		elif n.name in func.module.globals:
			func.append(('GLOBAL_SET', n.name))
		else:
			raise RuntimeError(f"Variable no definida: {n.name}")

	# Condicional IF
	def visit_Conditional(self, n:Conditional, func:IRFunction):
		n.condition.accept(self, func) # Evaluar la condicion -> pila
		func.append(('IF',)) # Iniciar la parte "consecuencia" de un "if"
		for stmt in n.true_branch:
			stmt.accept(self, func) # Visitar la parte "consecuencia"
		if n.false_branch: # Si hay una parte "alternativa"
			func.append(('ELSE',))
			for stmt in n.false_branch:
				stmt.accept(self, func) # Visitar la parte "alternativa"
		func.append(('ENDIF',)) # Fin de la instruccion "if"

	# Ciclo WHILE
	def visit_WhileLoop(self, n:WhileLoop, func:IRFunction):
		func.append(('LOOP',)) # Iniciar el ciclo
		n.condition.accept(self, func) # Se le asigna el valor a la condicion
		func.append(('CBREAK',)) # Iniciar la parte "consecuencia" de un "if"
		for stmt in n.body:
			stmt.accept(self, func)
		func.append(('ENDLOOP',))
		
	# Break, Continue y Return
	def visit_break(self, n:Break, func:IRFunction):
		func.append(('CONSTI',1))
		func.append(('CBREAK',))


	def visit_Continue(self, n:Continue, func:IRFunction):
		func.append(('CONTINUE',))
		pass

	def visit_Return(self, n:Return, func:IRFunction):
		if n.expression:
			n.expression.accept(self, func)
		func.append(('RET',))


	# Declaracion de variables
	def visit_VariableDeclaration(self, n:VariableDeclaration, func:IRFunction):
		ir_type = _typemap.get(n.var_type, 'I') 
		# Registrar la variable en el ambito correcto
		# Contexto global
		if func.name == 'main':
			func.module.globals[n.name] = IRGlobal(n.name, ir_type)
		# Contexto local
		else:
			func.new_local(n.name, ir_type)
		
		if n.value is not None:
			n.value.accept(self, func)
			if isinstance(n.value, UnaryOperation) and n.value.operator == 'HAT':
				func.append(('GROW',)) # Maneja '^' como un operador reserva de memoria
			if func.name == 'main':
				func.append(('GLOBAL_SET', n.name))
			else:
				func.append(('LOCAL_SET', n.name))

	# Declaracion de funciones
	def visit_FunctionDefinition(self, n:FunctionDefinition, func:IRFunction):
		parmtypes = [ _typemap.get(p.type, 'I') for p in n.parameters ]
		return_type = _typemap.get(n.return_type, 'I')
		new_func = IRFunction(func.module, n.name, [p.name for p in n.parameters], parmtypes, return_type)

		# Parametros de la funcion se añaden como variables locales
		for param in n.parameters:
			new_func.new_local(param.name, _typemap.get(param.type, 'I'))
		# Generar cuerpo de la funcion
		for stmt in n.body:
			stmt.accept(self, new_func)

		# Si la funcion no tiene un return, se añade uno
		if not any(instr[0] == 'RET' for instr in new_func.code):
			if return_type != 'void':
				new_func.append(('CONSTI', 0))
			new_func.append(('RET',))
		
	
	def visit_FunctionImport(self, n: FunctionImport, func: IRFunction):
		IRFunction(func.module, n.name, [p.name for p in n.parameters],
                 [_typemap.get(p.type, 'I') for p in n.parameters],
                 _typemap.get(n.return_type, 'I'), imported=True)
		
	# Expresiones y literales
	def visit_Literal(self, n:Literal, func:IRFunction):
		# Colocar el valor en la pila la instruccion IR del literal
		if n.type == 'int':
			func.append(('CONSTI', int(n.value)))
		elif n.type == 'float':
			func.append(('CONSTF', float(n.value)))
		elif n.type == 'char':
			func.append(('CONSTI', ord(n.value)))
		elif n.type == 'bool':
			#Mapear el booleano a un entero
			if n.value.lower() == 'true':
				func.append(('CONSTI', 1))
			elif n.value.lower() == 'false':
				func.append(('CONSTI', 0))
			else:
				raise RuntimeError(f"Valor booleano no valido: {n.value}")
		else:
			raise RuntimeError(f"Tipo de dato no soportado: {n.type}")

	# Operaciones binarias y unarias
	def visit_BinaryOperation(self, n:BinaryOperation, func:IRFunction):
		if n.operator == '&&': # Si el operador es AND
			n.left.accept(self, func)
			func.append(('IF',))
			n.right.accept(self, func)
			func.append(('ELSE',))
			func.append(('CONSTI', 0))
			func.append(('ENDIF',))
		elif n.operator == '||':
			n.left.accept(self, func)
			func.append(('IF',))
			func.append(('CONSTI', 1))
			func.append(('ELSE',))
			n.right.accept(self, func)
			func.append(('ENDIF',))
		else: # de lo contrario visitar el hijo izquierdo y derecho
			n.left.accept(self, func)
			n.right.accept(self, func)
			# Obtener los tipos de los hijos izquierdo y derecho y el operador
			
			left_type = n.left.type
			right_type = n.right.type
			# Convertir el operador a un operador de un carácter
			op = dict_equivalence.get(n.operator, n.operator) # Convertir a un operador de un carácter

			# Verificar si se necesita una conversion de tipo
			if left_type != right_type:
				if left_type == 'int' and right_type == 'float':
					func.append(('ITOF',))
					left_type = 'float'
				elif left_type == 'float' and right_type == 'int':
					func.append(('FTOI',))
					right_type = 'float'

			# Obtener el tipo de la operacion
			op_code = self._binop_code.get((left_type, op, right_type), None)
			# Agregar la instruccion al codigo IR
			if op_code:
				func.append((op_code,))
			else:
				raise RuntimeError(f"Operador no soportado: {op} para tipos {left_type} y {right_type}")
		
	def visit_UnaryOperation(self, n:UnaryOperation, func:IRFunction):
		n.operand.accept(self, func)
		operator = dict_equivalence.get(n.operator, n.operator) # Convertir a un operador de un carácter
		ops = self._unaryop_code.get((operator, n.operand.type), None)
		if ops:
			func.extend(ops)
		n.type = n.operand.type # Asignar el tipo de la operacion al nodo
		


	# Conversion de tipos
	def visit_TypeConversion(self, n: TypeConversion, func: IRFunction):
	  # Procesar la expresión que se va a convertir
		n.expression.accept(self, func)

		# Obtener las instrucciones de conversión
		ops = self._typecast_code.get((n.expression.type, n.target_type), None)
		if ops:
			func.extend(ops)
    
    	# Asignar el tipo resultante al nodo
		n.type = n.target_type
		
	def visit_FunctionCall(self, n:FunctionCall, func:IRFunction):
		# Procesar los argumentos de la llamada a la función
		for arg in reversed(n.arguments):
			arg.accept(self, func)
		func.append(('CALL', n.name))

		# Asignar el tipo de retorno de la función al nodo
		if n.name in func.module.functions:
			n.type = func.module.functions[n.name].return_type
		else:
			raise RuntimeError(f"Función no definida: {n.name}")
	

	# Lectura y escritura de variables

	# Lectura de variables
	def visit_PrimitiveReadLocation(self, n:PrimitiveReadLocation, func:IRFunction):
		if n.name in func.locals: # si la variable es local
			n.node_type = func.locals[n.name] # asignar el tipo de la variable
			func.append(('LOCAL_GET', n.name)) # agregar la instruccion al codigo IR
		elif n.name in func.module.globals: # si la variable es global
			n.node_type = func.module.globals[n.name].type # asignar el tipo de la variable
			func.append(('GLOBAL_GET', n.name)) # agregar la instruccion al codigo IR
		else:
			raise RuntimeError(f"Variable no definida: {n.name}")
		
	# Lectura de un valor desde una direccion de memoria
	def visit_MemoryReadLocation(self, n: MemoryReadLocation, func: IRFunction):
		# Procesar la dirección de memoria
		n.address.accept(self, func)

		# Determinar el tipo de dato y generar la instrucción correspondiente
		if n.type == 'int':
			func.append(('PEEKI',))  # Leer entero desde memoria
		elif n.type == 'float':
			func.append(('PEEKF',))  # Leer flotante desde memoria
		elif n.type == 'char':
			func.append(('PEEKB',))  # Leer byte desde memoria
		else:
			raise RuntimeError(f"Tipo de dato no soportado para lectura de memoria: {n.type}")
		
	# Escritura de un valor en una direccion de memoria
	def visit_MemoryAssignmentLocation(self, n: MemoryAssignmentLocation, func: IRFunction):
		# Procesar la dirección de memoria primero
		n.address.accept(self, func)

		# Procesar el valor a escribir
		n.value.accept(self, func)

		# Determinar el tipo de dato y generar la instrucción correspondiente
		if n.value.type == 'int':
			func.append(('POKEI',))  # Escribir entero en memoria
		elif n.value.type == 'float':
			func.append(('POKEF',))  # Escribir flotante en memoria
		elif n.value.type == 'char':
			func.append(('POKEB',))  # Escribir byte en memoria
		else:
			raise RuntimeError(f"Tipo de dato no soportado para escritura en memoria: {n.value.type}")

	# Instruccion de impresion
	def visit_Print(self, n: Print, func: IRFunction):
		n.expression.accept(self, func)  # Procesar la expresión a imprimir

	  # Determinar el tipo de dato y generar la instrucción correspondiente
		if n.expression.type == 'int' or n.expression.type == 'I':
			func.append(('PRINTI',))  # Imprimir entero
		elif n.expression.type == 'float' or n.expression.type == 'F':
			func.append(('PRINTF',))  # Imprimir flotante
		elif n.expression.type == 'char' or n.expression.type == 'C':
			func.append(('PRINTB',))  # Imprimir byte
		elif n.expression.type == 'bool' or n.expression.type == 'B':
			func.append(('PRINTI',))
		else:
			raise RuntimeError(f"Tipo de dato no soportado para impresión: {n.expression.type}")

	#Generic Visit

	def generic_visit(self, node, func:IRFunction):
		# Si el nodo no tiene un metodo de visita especifico, se llama al metodo de visita generico
		for child in node.children:
			if isinstance(child, Node):
				child.accept(self, func)
			else:
				print(f"Unknown child type: {type(child)}")


if __name__ == '__main__':
	import sys
	
	from errors import error, errors_detected
	from glexer import Lexer
	from gparser import Parser

	from checkNew import Checker

	if len(sys.argv) != 2:
		raise SystemExit("Usage: python ircode.py <filename>")
	
	filename = sys.argv[1]

	with open(filename, "r", encoding="utf-8") as f:
		source_code = f.read()

	lexer = Lexer(source_code)
	tokens = list(lexer.tokenize())
	parser = Parser(tokens)
	top = parser.parse()
	print('AST generado:')
	print(top)
	env = Checker.check(top)

		
	if not errors_detected():
		module = IRCode.gencode(top)
		module.dump()
