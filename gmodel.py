class Visitor:
    def visit(self,node,env):
        method_name = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node, env)
    
def generic_visit(self, node, env):
    raise Exception(f'No visit_{node.__class__.__name__} method')


class Node:
    def __init__(self, node_type, value=None):
        self.node_type = node_type
        self.value = value
        self.children = []

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
    

class Assignment(Node):
    def __init__(self, location, expression):
        self.location = location
        self.expression = expression

    def __repr__(self):
        return f"Assignment({self.location}, {self.expression})"


class Print(Node):
    def __init__(self, expression):
        super().__init__("Print", expression)
        self.add_child(Node("Expression", expression))

    def __repr__(self):
        return f"Print({self.children[0].value})"


class Conditional(Node):
    def __init__(self, condition, true_branch, false_branch=None):
        super().__init__("Conditional")
        self.add_child(Node("Condition", condition))
        self.add_child(Node("True", true_branch))
        if false_branch:
            self.add_child(Node("False", false_branch))

    def __repr__(self):
        branches = f"Then {self.children[1].value}"
        if len(self.children) == 3:
            branches += f", Else {self.children[2].value}"
        return f"Conditional(If {self.children[0].value}, {branches})"


class WhileLoop(Node):
    def __init__(self, condition, body):
        super().__init__("While")
        self.condition = condition
        self.body = body

    def __repr__(self):
        return f"While({self.condition}, {self.body})"


class Break(Node):
    def __init__(self):
        super().__init__("Break")

    def __repr__(self):
        return "Break()"


class Continue(Node):
    def __init__(self):
        super().__init__("Continue")

    def __repr__(self):
        return "Continue()"


class Return(Node):
    def __init__(self, expression):
        super().__init__("Return", expression)
        self.expression = Node("Expression", expression)
        self.add_child(self.expression)

    def __repr__(self):
        return f"Return({self.expression.value})"


class VariableDeclaration(Node):
    def __init__(self, name, var_type=None, value=None, is_constant=False):
        super().__init__("VariableDeclaration", name)
        self.var_type = var_type
        self.value = value
        self.is_constant = is_constant
        self.add_child(Node("Name", name))
        if var_type:
            self.add_child(Node("Type", var_type))
        if value:
            self.add_child(Node("Value", value))

    def __repr__(self):
        return f"VariableDeclaration(name={self.value}, type={self.var_type}, value={self.value}, constant={self.is_constant})"


class FunctionDefinition(Node):
    def __init__(self, name, parameters, return_type, body):
        super().__init__("FunctionDefinition", name)
        self.return_type = return_type
        self.parameters = parameters
        self.body = body
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
        return f"FunctionDefinition(name={self.value}, parameters={self.parameters}, return_type={self.return_type}, body={self.body})"


class FunctionImport(Node):
    def __init__(self, name, parameters, return_type):
        super().__init__("FunctionImport", name)
        self.parameters = parameters
        self.return_type = return_type
        self.add_child(Node("Name", name))
        self.add_child(Node("ReturnType", return_type))

        param_node = Node("Parameters")
        for param in parameters:
            param_node.add_child(Node("Parameter", param))
        self.add_child(param_node)

    def __repr__(self):
        return f"FunctionImport(name={self.value}, parameters={self.parameters}, return_type={self.return_type})"


class Parameter(Node):
    def __init__(self, name, type):
        super().__init__("Parameter", name)
        self.type = type

    def __repr__(self):
        return f"Parameter({self.value}, {self.type})"


class Literal(Node):
    def __init__(self, type, value):
        super().__init__("Literal", value)
        self.type = type

    def __repr__(self):
        return f"Literal({self.type}, {self.value})"


class BinaryOperation(Node):
    def __init__(self, left, operator, right):
        super().__init__("BinaryOperation")
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self):
        return f"BinaryOperation({self.left}, '{self.operator}', {self.right})"


class UnaryOperation(Node):
    def __init__(self, operator, operand):
        super().__init__("UnaryOperation")
        self.operator = operator
        self.operand = operand

    def __repr__(self):
        return f"UnaryOperation('{self.operator}', {self.operand})"


class Location(Node):
    def __init__(self, name):
        super().__init__("Location", name)

    def __repr__(self):
        return f"Location({self.value})"


class TypeConversion(Node):
    def __init__(self, target_type, expression):
        super().__init__("TypeConversion")
        self.target_type = target_type
        self.expression = expression

    def __repr__(self):
        return f"TypeConversion({self.target_type}, {self.expression})"


class FunctionCall(Node):
    def __init__(self, name, arguments):
        super().__init__("FunctionCall", name)
        self.arguments = arguments

    def __repr__(self):
        return f"FunctionCall({self.value}, {self.arguments})"


class PrimitiveAssignmentLocation(Node):
    def __init__(self, name, expression):
        super().__init__("PrimitiveAssignmentLocation", name)
        self.expression = expression

    def __repr__(self):
        return f"PrimitiveAssignmentLocation({self.value}), {self.expression}"


class PrimitiveReadLocation(Node):
    def __init__(self, name):
        super().__init__("PrimitiveReadLocation", name)

    def __repr__(self):
        return f"PrimitiveReadLocation({self.value})"


class MemoryAssignmentLocation(Node):
    def __init__(self, address, expression):
        super().__init__("MemoryAssignmentLocation", address)
        self.expression = expression

    def __repr__(self):
        return f"MemoryAssignmentLocation({self.value}), {self.expression}"


class MemoryReadLocation(Node):
    def __init__(self, address):
        super().__init__("MemoryReadLocation", address)

    def __repr__(self):
        return f"MemoryReadLocation({self.value})"
