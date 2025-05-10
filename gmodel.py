"""
Este archivo define el modelo del Árbol de Sintaxis Abstracta (AST) para el compilador GOX.

Cada clase en este archivo representa un tipo de nodo en el AST, como declaraciones de variables, 
funciones, estructuras de control (if, while), operaciones binarias, y más. 

El modelo utiliza un patrón de visitante (Visitor Pattern) para permitir que diferentes componentes 
del compilador (como el analizador semántico) recorran y procesen el AST de manera uniforme.

Clases principales:
- Node: Clase base para todos los nodos del AST.
- Program: Nodo raíz que representa el programa completo.
- VariableDeclaration, FunctionDefinition: Representan declaraciones de variables y funciones.
- WhileLoop, Conditional: Representan estructuras de control.
- BinaryOperation, UnaryOperation: Representan operaciones aritméticas y lógicas.
- Otros nodos específicos como Return, Break, Continue, y más.

Cada nodo incluye información relevante como el tipo de nodo, sus hijos, y la línea del código fuente 
donde se encuentra, para facilitar la generación de errores y el análisis semántico.
"""

class Visitor:
    def visit(self,node,env):
        method_name = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node, env)
    
def generic_visit(self, node, env):
    raise Exception(f'No visit_{node.__class__.__name__} method')


class Node:
    def __init__(self, node_type, value=None,lineno=None):
        self.node_type = node_type
        self.value = value
        self.children = []
        self.lineno = lineno

    def add_child(self, node):
        self.children.append(node)

    def accept(self, visitor, env):
        return visitor.visit(self, env)

    def __repr__(self):
        return f"Node({self.node_type}, {repr(self.value)}, children={self.children})"


class Program(Node):
    def __init__(self, stmts):
        """
        Nodo raíz del AST que representa un programa completo.
        :param stmts: Lista de sentencias o declaraciones del programa.
        """
        super().__init__("Program")
        self.stmts = stmts  # Lista de sentencias o declaraciones
        for stmt in stmts:
            self.add_child(stmt)

    def __repr__(self):
        return f"Program(statements={self.stmts})"
    
    def __len__(self):
        return len(self.stmts)

    
class Assignment:
    def __init__(self, location, expression):
        self.location = location  # Identificador de la variable
        self.expression = expression # Expresión a asignar

    def __repr__(self): #Devuelve una representación en texto del objeto para que podamos imprimirlo y ver su contenido fácilmente.

        return f'Assignment({self.location}, {self.expression})'




class Print(Node):
    def __init__(self, expression, lineno=None):
        super().__init__("Print", lineno=lineno)  # Llama al constructor de Node con el tipo "Print"
        self.add_child(Node("Expression", expression))  # Agregamos la expresión como nodo hijo
        self.expression = expression  # Guardamos la expresión para uso posterior
    def __repr__(self):
        return f'Print({self.children[0].value})'  # Tomamos el valor del primer hijo




class Conditional(Node):
    def __init__(self, condition, true_branch, false_branch=None, lineno=None):
        super().__init__("Conditional",lineno=lineno)  # Tipo de nodo: "Conditional"
        self.condition = condition  # Expresión que se evalúa
        self.true_branch = true_branch
        self.false_branch = false_branch  # Rama falsa (opcional)

        # Agregar nodos hijos para manejar la estructura del árbol
        self.add_child(Node("Condition", condition))  # Nodo hijo que representa la condición
        self.add_child(Node("True", true_branch))  # Nodo hijo para la rama verdadera
        if false_branch:
            self.add_child(Node("False", false_branch))  # Nodo hijo para la rama falsa (opcional)

    def __repr__(self):
        if len(self.children) == 3:
            return f'Conditional(If {self.children[0].value}, Then {self.children[1].value}, Else {self.children[2].value})'
        else:
            return f'Conditional(If {self.children[0].value}, Then {self.children[1].value})'



class WhileLoop(Node):
    def __init__(self, condition, body, lineno=None):
        super().__init__("While",lineno=lineno)  # Llama al constructor de Node con el tipo "While"
        self.condition = condition  # Expresión que se evalúa en cada iteración
        self.body = body  # Bloque de código que se ejecuta dentro del while

    def __repr__(self):
        return f'While({self.condition}, {self.body})'



class Break(Node):
    def __init__(self,lineno=None):
        super().__init__("Break",lineno=lineno)  # Llama al constructor de Node con el tipo "Break"

    def __repr__(self):
        return "Break()"


class Continue(Node):
    def __init__(self, lineno=None):
        super().__init__("Continue",lineno=lineno)  # Llama al constructor de Node con el tipo "Continue"

    def __repr__(self):
        return "Continue()"


class Return(Node):
    def __init__(self, expression,lineno=None):
        super().__init__("Return",lineno=lineno)  # Llama al constructor de Node con el tipo "Return"
        self.expression = Node("Expression", expression)  # Crear nodo hijo para la expresión
        self.add_child(self.expression)  # Agregarlo al árbol

    def __repr__(self):
        return f'Return({self.expression.value})'






class VariableDeclaration(Node):
    def __init__(self, name, var_type=None, value=None, is_constant=False, lineno=None):
        super().__init__("VariableDeclaration", lineno=lineno)  # Llama al constructor de Node con el tipo "VariableDeclaration"
        self.name = name  # Nombre de la variable
        self.var_type = var_type  # Tipo de la variable (opcional si se infiere)
        self.value = value  # Valor de la variable (opcional)
        self.is_constant = is_constant  # Si es `const` o `var`

        # Agregar nodos hijos si existen
        self.add_child(Node("Name", name))
        if var_type:
            self.add_child(Node("Type", var_type))
        if value:
            self.add_child(Node("Value", value))

    def __repr__(self):
        return f'VariableDeclaration(name={self.name}, type={self.var_type}, value={self.value}, constant={self.is_constant})'



class FunctionDefinition(Node):
    def __init__(self, name, parameters, return_type, body,lineno=None):
        super().__init__("FunctionDefinition", lineno=lineno)  # Llama al constructor de Node con el tipo "FunctionDefinition"
        self.name = name
        self.parameters = parameters  # Lista de parámetros (nombre, tipo)
        self.return_type = return_type
        self.body = body  # Lista de sentencias en el cuerpo de la función
        
        self.add_child(Node("Name", name))
        self.add_child(Node("ReturnType", return_type))
        
        param_node = Node("Parameters")
        for param in parameters:
            param_node.add_child(Node("Parameter", param))
        self.add_child(param_node)
        
        body_node = Node("Body")
        for statement in body:
            body_node.add_child(statement)
        self.add_child(body_node)

    def __repr__(self):
        return f'FunctionDefinition(name={self.name}, parameters={self.parameters}, return_type={self.return_type}, body={self.body})'


class FunctionImport(Node):
    def __init__(self, name, parameters, return_type,lineno=None):
        super().__init__("FunctionImport", lineno=lineno)  # Llama al constructor de Node con el tipo "FunctionImport"
        self.name = name
        self.parameters = parameters
        self.return_type = return_type
        
        self.add_child(Node("Name", name))
        self.add_child(Node("ReturnType", return_type))
        
        param_node = Node("Parameters")
        for param in parameters:
            param_node.add_child(Node("Parameter", param))
        self.add_child(param_node)

    def __repr__(self):
        return f'FunctionImport(name={self.name}, parameters={self.parameters}, return_type={self.return_type})'


class Parameter(Node):
    def __init__(self, name, type):
        super().__init__("Parameter")
        self.name = name
        self.type = type

    def __repr__(self):
        return f'Parameter({self.name}, {self.type})'



class Literal(Node):
    def __init__(self, type, value):
        super().__init__("Literal")
        self.type = type  # Tipo de dato (int, float, bool, char)
        self.value = value  # Valor del literal
        self.name = value  # Nombre del literal (si aplica)

    def __repr__(self):
        return f'Literal({self.type}, {self.value})'



class BinaryOperation(Node):
    def __init__(self, left, operator, right,lineno=None,type=None):
        super().__init__("BinaryOperation", lineno=lineno)  # Llama al constructor de Node con el tipo "BinaryOperation"
        self.left = left  # Operando izquierdo
        self.operator = operator  # Operador (+, -, *, /, <, >, etc.)
        self.right = right  # Operando derecho
        if isinstance(left, Literal) and isinstance(right, Literal):
            self.type = left.type if left.type == right.type else None


    def __repr__(self):
        return f'BinaryOperation({self.left}, "{self.operator}", {self.right})'




class UnaryOperation(Node):
    def __init__(self, operator, operand):
        super().__init__("UnaryOperation")
        self.operator = operator  # Operador unario (+, -, !, ^)
        self.operand = operand  # Expresión afectada

    def __repr__(self):
        return f'UnaryOperation("{self.operator}", {self.operand})'

class Location(Node):
    def __init__(self, name):
        super().__init__("Location")
        self.name = name  # Nombre de la variable o estructura

    def __repr__(self):
        return f'Location({self.name})'


class TypeConversion(Node):
    def __init__(self, target_type, expression):
        super().__init__("TypeConversion")
        self.target_type = target_type  # Tipo de conversión (int, float)
        self.expression = expression  # Expresión a convertir

    def __repr__(self):
        return f'TypeConversion({self.target_type}, {self.expression})'



class FunctionCall(Node):
    def __init__(self, name, arguments,lineno=None):
        super().__init__("FunctionCall",lineno=lineno)  # Llama al constructor de Node con el tipo "FunctionCall"
        self.name = name  # Nombre de la función
        self.arguments = arguments  # Lista de argumentos

    def __repr__(self):
        return f'FunctionCall({self.name}, {self.arguments})'


class PrimitiveAssignmentLocation(Node):
    """
    Representa una asignación de valor a una variable en goxlang.

    Ejemplo en goxlang:
        abc = 123;

    Atributos:
        name (str): Nombre de la variable.
        expression: Expresión que se asigna a la variable.
    """
    def __init__(self, name, expression,lineno=None):
        super().__init__("PrimitiveAssignmentLocation", lineno=lineno)  # Llama al constructor de Node con el tipo "PrimitiveAssignmentLocation"
        self.name = name
        self.expression = expression
    
    def __repr__(self):
        return f'PrimitiveAssignmentLocation({self.name}), {self.expression}'
    


class PrimitiveReadLocation(Node):
    """
    Representa la lectura de una variable en goxlang.

    Ejemplo en goxlang:
        print abc;

    Atributos:
        name (str): Nombre de la variable que se lee.
    """
    def __init__(self, name, lineno=None):
        super().__init__("PrimitiveReadLocation", lineno=lineno)  # Llama al constructor de Node con el tipo "PrimitiveReadLocation"
        self.name = name
    
    def __repr__(self):
        return f'PrimitiveReadLocation({self.name})'


class MemoryAssignmentLocation(Node):
    """
    Representa una asignación de valor a una dirección de memoria en goxlang.

    Ejemplo en goxlang:
        `address = 123;

    Atributos:
        address (int): Dirección de memoria donde se almacena el valor.
        expression: Expresión que se asigna a la dirección de memoria.
    """
    def __init__(self, address, expression,lineno=None):
        super().__init__("MemoryAssignmentLocation")
        self.address = address
        self.expression = expression
    
    def __repr__(self):
        return f'MemoryAssignmentLocation({self.address}), {self.expression}'


class MemoryReadLocation(Node):
    """
    Representa la lectura de un valor desde una dirección de memoria en goxlang.

    Ejemplo en goxlang:
        print `address + 10;

    Atributos:
        address (int): Dirección de memoria que se lee.
    """
    def __init__(self, address):
        super().__init__("MemoryReadLocation")
        self.address = address
    
    def __repr__(self):
        return f'MemoryReadLocation({self.address})'