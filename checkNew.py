from typing import List
from gmodel import *
from symtab import Symtab
from errors import error
from typesys import check_binop

class Checker(Visitor):
    @classmethod
    def check(cls, node: Node):
        '''
        Punto de entrada para iniciar la verificación semántica.
        1. Crea una nueva tabla de símbolos global.
        2. Inicia la visita al nodo raíz.
        '''
        checker = cls()
        env = Symtab("global")
        node.accept(checker, env)
        return checker

    # ----------------------
    # NODOS DE DECLARACIÓN
    # ----------------------

    def visit_Program(self, node: Program, env: Symtab):
        '''
        Verifica el nodo raíz del programa.
        Recorre cada sentencia en el programa y las verifica.
        '''
        for stmt in node.stmts:
            stmt.accept(self, env)
        env.print()
        print("___________________________________")

    def visit_VariableDeclaration(self, node: VariableDeclaration, env: Symtab):
        '''
        Verifica una declaración de variable.
        1. Revisa si ya existe una variable con el mismo nombre.
        2. Si hay un valor inicial, revisa que su tipo coincida con el tipo declarado.
        3. Agrega la variable a la tabla de símbolos.
        '''
        if env.get(node.name):
            error(f"Error: La variable '{node.name}' ya está definida.",node.lineno)
            return

        # Si hay valor inicial, verificar su tipo
        if node.value:
            var_decl_type = node.var_type
            value_type = node.value.accept(self, env)
            if var_decl_type != value_type:
                error(f"Error: Tipo de variable '{node.name}' no coincide con el tipo de valor inicial.",node.lineno)

        # Registrar variable en el entorno actual
        env.add(node.name, node)

    def visit_FunctionDefinition(self, node: FunctionDefinition, env: Symtab):
        '''
        Verifica una definición de función:
        1. Verifica si la función ya está definida.
        2. Verifica que no haya funciones anidadas.
        3. Crea un nuevo entorno para el cuerpo de la función.
        4. Agrega los parámetros al entorno.
        5. Verifica el cuerpo de la función.
        6. Verifica que si hay un tipo de retorno diferente de void, haya un return.
        '''
        # Verifica si la función ya está definida
        if env.get(node.name):
            error(f"Error: La función '{node.name}' ya está definida.",node.lineno)
            return

        # Verificar si ya estamos dentro de una función
        if env.get('$func'):
            error(f"Error: las funciones anidadas no están permitidas.",node.lineno)
            return

        env.add(node.name, node)

        # Nuevo entorno para el cuerpo
        local_env = Symtab("function:" + node.name, env)

        # Agregar variable para referenciar la función misma 
        local_env.add('$func', node)

        
        for param in node.parameters:
            name_param= param.name
            local_env.add(name_param, param)

        # Verificar el cuerpo de la función
        has_return = False
        for stmt in node.body:
            if isinstance(stmt, Return):
                has_return = True
            stmt.accept(self, local_env)

        # Verificar si la función tiene un tipo de retorno diferente de void
        if node.return_type != 'VOID' and not has_return:
            error(f"Error: La función '{node.name}' debe tener un 'return' para el tipo de retorno '{node.return_type}'.",node.lineno)
        
        

    def visit_FunctionImport(self, node: FunctionImport, env: Symtab):
        '''
        Registra una función importada (declaración externa) en la tabla de símbolos.
        '''
        if env.get(node.name):
            error(f"Error: La función '{node.name}' ya está definida.",node.lineno)
            return

        env.add(node.name, node)

    # ----------------------
    # NODOS DE EXPRESIÓN
    # ----------------------

    def visit_Literal(self, node: Literal, env: Symtab):
        '''
        Retorna el tipo de dato del literal.
        '''
        return node.type

    def visit_PrimitiveReadLocation(self, node: PrimitiveReadLocation, env: Symtab):
        symbol = env.get(node.name)
        if not symbol:
            error(f"La variable '{node.name}' no está declarada.", node.lineno)
            return 'error'
        if isinstance(symbol, Parameter):
            node.type = symbol.type  # Asignar el tipo al nodo
            return symbol.type
        elif isinstance(symbol, VariableDeclaration):
            node.type = symbol.var_type  # Asignar el tipo al nodo
            return symbol.var_type
        else:
            error(f"Tipo desconocido para la variable '{node.name}'.", node.lineno)
            return 'error'

    def visit_BinaryOperation(self, node: BinaryOperation, env: Symtab):
        left_type = node.left.accept(self, env)
        right_type = node.right.accept(self, env)

        # Intentar conversión implícita si los tipos no coinciden
        if left_type != right_type:
            if left_type == 'int' and right_type == 'float':
                node.left = TypeConversion('float', node.left)
                left_type = 'float'
            elif left_type == 'float' and right_type == 'int':
                node.right = TypeConversion('float', node.right)
                right_type = 'float'

        result_type = check_binop(node.operator, left_type, right_type)
        if result_type == 'error' or result_type is None:
            error(f"Error en operación binaria: tipos incompatibles '{left_type}' {node.operator} '{right_type}'", node.lineno)
            node.type = 'error'
        else:
            node.type = result_type
        return result_type

    def visit_UnaryOperation(self, node: UnaryOperation, env: Symtab):
        '''
        Verifica una operación unaria.
        1. Evalúa el tipo del operando.
        2. Retorna el tipo resultante (dependiendo del operador).
        '''
        operand_type = node.operand.accept(self, env)
        if node.operator == 'HAT':
            if operand_type != 'int':
                error(f"Error: El operador '{node.operator}' solo es válido para enteros, pero se encontró '{operand_type}'.",node.lineno)
                node.type = 'error'
            return 'int'
        
        elif node.operator == 'NOT':
            if operand_type != 'bool':
                error(f"Error: El operador '{node.operator}' solo es válido para booleanos, pero se encontró '{operand_type}'.",node.lineno)
                node.type = 'error'
            return 'bool'
        
        elif node.operator in ('PLUS', 'MINUS'):
            if operand_type not in ('int', 'float'):
                error(f"Error: El operador '{node.operator}' solo es válido para enteros o flotantes, pero se encontró '{operand_type}'.",node.lineno)
                node.type = 'error'
            return operand_type
        else:
            error(f"Error: Operador unario desconocido '{node.operator}'.",node.lineno)
            node.type = 'error'
            return 'error'
        


    def visit_FunctionCall(self, node: FunctionCall, env: Symtab):
        '''
        Verifica una llamada a función:
        1. Verifica que la función esté declarada.
        2. Verifica el número de argumentos y sus tipos.
        '''
        func = env.get(node.name)
        if not func:
            error(f"Error: La función '{node.name}' no está declarada.",node.lineno)
            return 'error'

        if len(func.parameters) != len(node.arguments):
            error(f"Error: Número incorrecto de argumentos para función '{node.name}'.",node.lineno)
            return 'error'
        
        #Visitar argumentos(si están definidos) y verificar que cada argumento sea compatible con cada parámetro de la función
        node_arguments= node.arguments
        func_parameters= func.parameters
        for param, arg in zip(func_parameters,node_arguments):
            arg_type = arg.accept(self, env)
            param_type = param.type
            if param_type != arg_type:
                error(f"Error: Tipo de argumento '{arg.name}' no coincide con el tipo de parámetro '{param.name}'. Esperado {param_type}, recibido {arg_type}.",node.lineno)

        return func.return_type

    def visit_TypeConversion(self, node: TypeConversion, env: Symtab):
        '''
        Verifica una conversión de tipo. Se asume que cualquier conversión es válida.
        '''
        expr_type = node.expression.accept(self, env)
        node.type = node.target_type
        return node.target_type

    # ----------------------
    # NODOS DE ASIGNACIÓN
    # ----------------------

    def visit_Assignment(self, node: Assignment, env: Symtab):
        '''
        Verifica una asignación.
        1. Visita la ubicación (location).
        2. Evalúa la expresión.
        3. Verifica que ambos tipos sean compatibles.
        '''
        return node.location.accept(self, env)

    def visit_PrimitiveAssignmentLocation(self, node: PrimitiveAssignmentLocation, env: Symtab):
        '''
        Verifica la asignación a una variable primitiva:
        1. Revisa que la variable exista.
        2. Verifica que no sea constante.
        3. Evalúa la expresión asignada.
        4. Compara tipos.
        '''
        symbol = env.get(node.name)
        if not symbol:
            error(f"Error: La variable '{node.name}' no está definida.",node.lineno)
            return

        if hasattr(symbol,'is_constant') and symbol.is_constant:
            error(f"Error: La variable '{node.name}' es constante y no se puede modificar.",node.lineno)
            return
        
        expr_type = node.expression.accept(self, env)
        declared_type = None
        if isinstance(symbol, Parameter):
            declared_type = symbol.type
        elif isinstance(symbol, VariableDeclaration):
            declared_type = symbol.var_type

        if declared_type != expr_type:
            error(f"Error: Tipo incompatible en asignación a '{node.name}'. Esperado {declared_type}, recibido {expr_type}.",node.lineno)

    # ----------------------
    # NODOS DE CONTROL
    # ----------------------

    def visit_Conditional(self, node: Conditional, env: Symtab):
        '''
        Verifica una estructura condicional if-else.
        1. Evalúa la condición.
        2. Verifica el bloque "then".
        3. Verifica el bloque "else" si existe.
        '''
        # Verifica el tipo de la condición
        condition_type = node.children[0].value.accept(self, env)
        if condition_type != 'bool':
            error(f"Error: La condición debe ser de tipo booleano, pero se encontró '{condition_type}'.",node.lineno)

        
        for stmt in node.true_branch:
            stmt.accept(self, env)

        # Verifica el bloque "else" si existe
        if node.false_branch:
            for stmt in node.false_branch:
                stmt.accept(self, env)

    def visit_WhileLoop(self, node: WhileLoop, env: Symtab):
        '''
        Verifica un bucle while:
        1. Evalúa que la condición sea booleana.
        2. Verifica el cuerpo del bucle.
        '''
        # Verifica la condición
        condition_type = node.condition.accept(self, env)
        if condition_type != 'bool':
            error(f"Error: La condición del bucle while debe ser de tipo booleano, pero se encontró '{condition_type}'.",node.lineno)
        

        # Verifica el cuerpo del bucle si hay un break o continue
        env.add('$loop', True)  # Marca que estamos dentro de un bucle

        # Verifica el cuerpo del bucle
        stmts = node.body
        for stmt in stmts:
            stmt.accept(self, env)
        
        # Elimina la bandera al salir del bucle
        env.__setitem__('$loop', False)

    def visit_Break(self, node: Break, env: Symtab):
        '''
        Verifica que el break esté dentro de un bucle while.
        Si no está dentro de un bucle, lanza un error.
        '''
        if not env.get('$loop'):
            error(f"Error: 'break' fuera de un bucle while.",node.lineno)
            return
        # Si está dentro de un bucle, no se necesita hacer nada
        # ya que el break es válido.
        pass

    def visit_Continue(self, node: Continue, env: Symtab):
        '''
        verifica que el continue esté dentro de un bucle while.
        Si no está dentro de un bucle, lanza un error.
        '''
        if not env.get('$loop'):
            error(f"Error: 'continue' fuera de un bucle while.",node.lineno)
            return
        pass

    def visit_Return(self, node: Return, env: Symtab):
        '''
        Verifica la expresión de retorno (si existe).
        verificar que este dentro de una función.
        Verifica que el tipo de retorno coincida con el tipo de la función.
        '''
        func = env.get('$func')
        if not env.get('$func'):
            error(f"Error: 'return' fuera de una función.",node.lineno)
            return
        if node.expression:
            return_type=node.expression.value.accept(self, env)
            func_type = func.return_type
            if return_type != func_type:
                error(f"Error: Tipo de retorno '{return_type}' no coincide con el tipo de la función '{func.name}' que es '{func_type}'.",node.lineno)

    def visit_Print(self, node: Print, env: Symtab):
        '''
        Verifica la expresión dentro del print.
        '''
        node.children[0].value.accept(self, env)

    # ----------------------
    # MANEJO DE MAMORIA
    # ----------------------
    def visit_MemoryAssignmentLocation(self, node: MemoryAssignmentLocation, env):
        addr_type = node.address.accept(self, env)
        if addr_type != 'int':
            error(f"Error: La dirección de memoria debe ser de tipo entero, pero se encontró '{addr_type}'.", node.lineno)
            return 'error'

        value_type = node.value.accept(self, env)
        node.type = value_type
        return value_type

    def visit_MemoryReadLocation(self, node: MemoryReadLocation, env):
        addr_type = node.address.accept(self, env)
        if addr_type != 'int':
            error(f"Error: La dirección de memoria debe ser de tipo entero, pero se encontró '{addr_type}'.", node.lineno)
            return 'error'

        node.type = 'int'
        return 'int'

    # ----------------------
    # GENERIC VISIT
    # ----------------------

    def generic_visit(self, node, env):
        '''
        Lanza una advertencia si no hay un método específico para el nodo.
        '''
        print(f"Warning: No visit method for {node.__class__.__name__}")
