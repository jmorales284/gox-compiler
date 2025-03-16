from rich import print
from model import *
import graphviz as gpv


class RenderAST(Visitor):
    node_default = {
        'shape' : 'box',
        'color' : 'blue',
        'style' : 'filled',
        'fillcolor' : 'lightblue'
    }
    edge_default = {
        'arrowhead' : 'none',
    }

    def __init__(self):
        self.dot = gpv.Digraph('AST', comment='Sintaxis tree')
        self.dot.attr('node', **self.node_default)
        self.dot.attr('edge', **self.edge_default)
        self.seq = 0

    def name(self):
        self.seq += 1
        return f'n{self.seq:02d}'
    
    @classmethod
    def render(cls, n:Node):
        dot = cls()
        n.accept(dot)
        return dot.dot
    

    def visit(self, n:Program):
        name = self.name()
        self.dot.node(name, label='Program')
        for s in n.statements:
            self.dot.edge(name, s.accept(self))
        return name
    
    def visit(self, n:Assignment):
        name = self.name()
        self.dot.node(name, label='Assign\\nlocation={n.location}')
        self.dot.edge(name, n.expression.accept(self), label='expression')

        return name
    
    def visit(self, n:Print):
        name = self.name()
        self.dot.node(name, label='Print')
        self.dot.edge(name, n.expression.accept(self), label='expression')

        return name
    
    def visit(self, n:If):
        name = self.name()
        self.dot.node(name, label='If')
        self.dot.edge(name, n.test.accept(self), label='test')
        self.dot.edge(name, n.consequence.accept(self), label='consequence')

        if n.alternative:
            self.dot.edge(name, n.alternative.accept(self), label='alternative')
        
        return name
    
    def visit(self, n:While):
        name = self.name()
        self.dot.node(name, label='While')
        self.dot.edge(name, n.test.accept(self), label='test')
        self.dot.edge(name, n.body.accept(self), label='body')

        return name
    
    def visit(self, n:Break):
        name = self.name()
        self.dot.node(name, label='Break')
        return name
    
    def visit(self, n:Continue):
        name = self.name()
        self.dot.node(name, label='Continue')
        return name
    
    def visit(self, n:Return):
        name = self.name()
        self.dot.node(name, label='Return')
        if n.expr:
            self.dot.edge(name, n.expression.accept(self), label='expression')
        return name
    

    def visit(self, n:VariableDeclaration):
        name = self.name()
        label = f'VariableDeclaration\\nname={n.name}\\ntype={n.type}'
        if n.is_const:
            label += '\\nconst=True'
        self.dot.node(name, label=label)
        if n.value:
            self.dot.edge(name, n.value.accept(self), label='value')
        return name
    
    def visit(self, n:FunctionCall):
        name = self.name()
        self.dot.node(name, label=f'FunctionCall\\nname={n.name}')
        for a in n.arguments:
            self.dot.edge(name, a.accept(self), label='arguments')
        return name
    
    def visit(self, n:FunctionDefinition):
        name = self.name()
        label = f'FunctionDefinition\\nname={n.name}\\nreturn_type={n.return_type}'
        if n.is_imported:
            label += '\\nis_imported=True'
        self.dot.node(name, label=label)

        params_name = self.name()
        self.dot.node(params_name, label='Params')
        for param in n.parameters:
            self.dot.edge(params_name, param.accept(self))
        self.dot.edge(name, params_name, label='parameters')

        body_name = self.name()
        self.dot.node(body_name, label='Body')
        for stmt in n.body:
            self.dot.edge(body_name, stmt.accept(self))
        self.dot.edge(name, body_name, label='body')

        return name

    def visit(self, n:Parameter):
        name = self.name()
        label = f'Parameter\\nname={n.name}\\ntype={n.type}'
        self.dot.node(name, label=label)
        return name
    
    def visit(self, n:VariableLocation):
        name = self.name()
        label = f'VariableLocation\\nname={n.name}'
        self.dot.node(name, label=label)
        return name
    
    def visit(self, n:Integer):
        name = self.name()
        self.dot.node(name, label=f'Integer\\nvalue={n.value}')
        return name
    
    def visit(self, n:Float):
        name = self.name()
        self.dot.node(name, label=f'Float\\nvalue={n.value}')
        return name
    
    def visit(self, n:Char):
        name = self.name()
        self.dot.node(name, label=f'Char\\nvalue={n.value}')
        return name 
    
    def visit(self, n:Boolean):
        name = self.name()
        self.dot.node(name, label=f'Boolean\\nvalue={n.value}')
        return name 
    
    def visit(self, n:BinaryOp):
        name = self.name()
        self.dot.node(name, label=f'BinaryOp\\noperator={n.operator}')
        self.dot.edge(name, n.left.accept(self), label='left')
        self.dot.edge(name, n.right.accept(self), label='right')
        return name
    
    def visit(self, n:UnaryOp):
        name = self.name()
        self.dot.node(name, label=f'UnaryOp\\noperator={n.operator}')
        self.dot.edge(name, n.expr.accept(self), label='expr')
        return name