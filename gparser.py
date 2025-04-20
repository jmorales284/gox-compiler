from typing import List
from dataclasses import dataclass
from glexer import Lexer
from gmodel import *
from rich import print_json

import json
import os

@dataclass
class Token:
    type: str
    value: str
    lineno: int

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0

    def parse(self) -> Program:
        statements = []
        while self.current < len(self.tokens) and self.tokens[self.current].type != "EOF":
            statements.append(self.statement())
        return Program(statements)

    # def statement(self) -> Node:
    #     if self.is_function_call():
    #         name_token = self.advance()  # ID
    #         self.consume("LPAREN", "Se esperaba '(' después del nombre de función")
    #         args = []
    #         if not self.match("RPAREN"):
    #             args.append(self.expression())
    #             while self.match("COMMA"):
    #                 args.append(self.expression())
    #             self.consume("RPAREN", "Se esperaba ')' después de los argumentos")
    #         self.consume("SEMI", "Se esperaba ';' después de la llamada")
    #         return FunctionCall(name_token.value, args)


    #     elif self.peek().type == "ID":
    #         # Asignación
    #         return self.assignment()
        
    #     elif self.peek().type in ("var", "const"):
    #         return self.vardecl()
    #     elif self.peek().type == "if":
    #         return self.if_stmt()
    #     elif self.peek().type == "while":
    #         return self.while_stmt()
    #     elif self.peek().type == "break":
    #         self.advance()
    #         return Break()
    #     elif self.peek().type == "continue":
    #         self.advance()
    #         return Continue()
    #     elif self.peek().type == "return":
    #         return self.return_stmt()
    #     elif self.peek().type == "print":
    #         return self.print_stmt()
    #     else:
    #         raise SyntaxError(f"Línea {self.peek().lineno}: Declaración inesperada '{self.peek().value}'")


    def statement(self) -> Node:
            if self.peek().type == "ID":
                # Guardamos posición por si necesitamos retroceder
                current_pos = self.current
                name_token = self.advance()

                # Verificamos si es llamada a función
                if self.peek() and self.peek().type == "LPAREN":
                    self.consume("LPAREN", "Se esperaba '(' después del nombre de función")
                    args = self.arguments()
                    self.consume("RPAREN", "Se esperaba ')' después de los argumentos")
                    self.consume("SEMI", "Se esperaba ';' después de la llamada")
                    return FunctionCall(name_token.value, args,lineno=self.get_lineno())
                else:
                    # Si no es llamada a función, retrocedemos
                    self.current = current_pos
                    return self.assignment()

            elif self.peek().type in ("var", "const"):
                return self.vardecl()
            elif self.peek().type == "func":
                return self.funcdecl()
            elif self.peek().type == "if":
                return self.if_stmt()
            elif self.peek().type == "while":
                return self.while_stmt()
            elif self.peek().type == "break":
                self.advance()
                self.consume("SEMI", "Se esperaba ';' después de break")
                return Break(lineno=self.get_lineno())
            elif self.peek().type == "continue":
                self.advance()
                self.consume("SEMI", "Se esperaba ';' después de continue")
                return Continue(lineno=self.get_lineno())
            elif self.peek().type == "return":
                return self.return_stmt()
            elif self.peek().type == "print":
                return self.print_stmt()
            else:
                raise SyntaxError(f"Línea {self.peek().lineno}: Declaración inesperada '{self.peek().value}'")
   
   
    def arguments(self) -> List[Node]:
        args = []
        if self.peek().type == "RPAREN":
            return args
        args.append(self.expression())
        while self.match("COMMA"):
            args.append(self.expression())
        return args
    
    def parameters(self) -> List[Parameter]:
        """Parse parameters in function declarations (with types)"""
        params = []
        if self.peek().type == "RPAREN":
            return params  # No parameters
        
        while True:
            param_token = self.consume("ID", "Se esperaba nombre de parámetro")
            
            if self.peek().type not in {"int", "float", "bool", "char"}:
                raise SyntaxError(f"Línea {self.peek().lineno}: Se esperaba tipo de parámetro")
            
            param_type = self.advance().value
            params.append(Parameter(param_token.value, param_type))
            
            if not self.match("COMMA"):
                break
        
        return params

    def assignment(self) -> Node:
        name_token = self.consume("ID", "Se esperaba identificador")
        self.consume("ASSIGN", "Se esperaba '=' después del identificador")
        expr = self.expression()
        self.consume("SEMI", "Se esperaba ';' después de la expresión")

        if name_token.value.startswith("`"):
            return MemoryAssignmentLocation(name_token.value[1:], expr)
        return PrimitiveAssignmentLocation(name_token.value, expr,lineno=self.get_lineno())




    def vardecl(self) -> VariableDeclaration:
        
        is_constant = self.match("const")
        if not is_constant:
            self.consume("var", "Se esperaba 'var' o 'const'")
        
        # Obtener el nombre de la variable
        name_token = self.consume("ID", "Se esperaba nombre de variable después de var/const")
        
        # Manejar tipo explícito (opcional)
        var_type = None
        if self.peek() and self.peek().type in {"int", "float", "bool", "char"}:
            var_type = self.advance().value

        
        # Manejar asignación (opcional)
        value = None
        if self.match("ASSIGN"):

            value = self.expression()
        
        # Consumir el punto y coma final
        try:
            self.consume("SEMI", "Se esperaba ';' al final de la declaración")
        except SyntaxError as e:
            # Mensaje de error más descriptivo
            current_token = self.peek()
            raise SyntaxError(
                f"Línea {current_token.lineno if current_token else '?'}: "
                f"Error en declaración de variable '{name_token.value}'. "
                f"Se esperaba ';' pero se encontró '{current_token.value if current_token else 'EOF'}'"
            ) from e
        
        
        declaration=VariableDeclaration(
            name=name_token.value,
            var_type=var_type,  # Ahora incluye el tipo si fue especificado
            value=value,
            is_constant=is_constant,
            lineno=name_token.lineno  # Agregar número de línea
        )

        return declaration



    def funcdecl(self) -> FunctionDefinition:
        self.consume("func", "Se esperaba 'func'")
        name_token = self.consume("ID", "Se esperaba nombre de función")
        self.consume("LPAREN", "Se esperaba '(' después del nombre")
        
        params = self.parameters()
        self.consume("RPAREN", "Se esperaba ')' después de los parámetros")
        return_type = "VOID"
        if self.peek() and self.peek().type in {"int", "float", "bool", "char"}:
            return_type = self.advance().value
        self.consume("LBRACE", "Se esperaba '{' después de la declaración de función")
        body = []
        while not self.match("RBRACE"):
            body.append(self.statement())

        return FunctionDefinition(
            name=name_token.value,
            parameters=params,
            return_type=return_type,
            body=body,
            lineno=name_token.lineno  # Agregar número de línea
        )

    def if_stmt(self) -> Conditional:
        self.consume("if", "Se esperaba 'if'")
        old_lineno = self.get_lineno()
        
        # 1. Parsear la condición
        condition = self.expression()
        
        # 2. Verificar y consumir el '{'
        if not self.match("LBRACE"):
            # Si no hay '{', verificar si es un if de una sola línea
            if self.peek().type in ["SEMI", "NEWLINE"]:
                raise SyntaxError(f"Línea {self.peek().lineno}: Cuerpo del if no puede estar vacío")
            # Permitir if de una sola línea sin llaves
            true_branch = [self.statement()]
            false_branch = None
            
            if self.match("else"):
                false_branch = [self.statement()]
                
            return Conditional(condition, true_branch, false_branch,lineno=self.old_lineno)
        
        # 3. Cuerpo del if con llaves
        true_branch = []
        while not self.match("RBRACE"):
            true_branch.append(self.statement())
        
        # 4. else opcional
        false_branch = None
        if self.match("else"):
            if not self.match("LBRACE"):
                # Else de una sola línea
                false_branch = [self.statement()]
            else:
                false_branch = []
                while not self.match("RBRACE"):
                    false_branch.append(self.statement())
        
        return Conditional(condition, true_branch, false_branch,lineno=old_lineno)

    def while_stmt(self) -> WhileLoop:
        self.consume("while", "Se esperaba 'while'")
        condition = self.expression()
        old_lineno = self.get_lineno()
        self.consume("LBRACE", "Se esperaba '{' después de while")
        
        body = []
        while not self.match("RBRACE"):
            body.append(self.statement())

        return WhileLoop(condition, body,old_lineno)

    def return_stmt(self) -> Return:
        self.consume("return", "Se esperaba 'return'")
        
        if self.match("SEMI"):
            return Return(None, lineno=self.get_lineno())
        
        expr = self.expression()
        self.consume("SEMI", "Se esperaba ';' después de return")
        return Return(expr,lineno=self.get_lineno())

    def print_stmt(self) -> Print:
        self.consume("print", "Se esperaba 'print'")
        expr = self.expression()
        self.consume("SEMI", "Se esperaba ';' después de print")
        return Print(expr)
    
    # Métodos de análisis de expresiones
    def factor(self):
        if self.match("true"):
            return Literal("bool", 'true')
        
        elif self.match("false"):
            return Literal("bool", 'false')
    
        elif self.match("INTEGER"):
            return Literal('int',self.tokens[self.current - 1].value)
        
        elif self.match("FLOAT"):
            return Literal('float',self.tokens[self.current - 1].value)
        
        elif self.match("CHAR_LITERAL"):
            char_value = self.tokens[self.current - 1].value
            processed_char = char_value[1:-1].encode().decode('unicode_escape')
            return Literal('char',processed_char)
        
        elif self.match("STRING_LITERAL"):
            string_tokens = []
            while self.peek() and self.peek().type != "STRING_LITERAL":
                string_tokens.append(self.advance().value)
            self.consume("STRING_LITERAL", "Se esperaba cierre de comillas")
            string_value = "".join(string_tokens)
            return Literal('string',string_value)
        
        elif self.match("BOOLEAN"):
            return Literal('bool',self.tokens[self.current - 1].value.lower())
        
        elif self.match("PLUS") or self.match("MINUS") or self.match("GROW"):
            op = self.tokens[self.current - 1].type
            return UnaryOperation(op, self.factor())
        
        elif self.match("LPAREN"):
            expr = self.expression()
            self.consume("RPAREN", "Se esperaba ')'")
            return expr
        
        elif self.match("int") or self.match("float") or self.match("bool") or self.match("char"):
            type_name = self.tokens[self.current - 1].value.lower()
            self.consume("LPAREN", f"Se esperaba '(' después de {type_name}")
            expr = self.expression()
            self.consume("RPAREN", "Se esperaba ')'")
            return TypeConversion(type_name, expr)
        
        elif self.match("ID"):
            id_name = self.tokens[self.current - 1].value
            if self.peek() and self.peek().type == "LPAREN":
                self.consume("LPAREN", "Se esperaba '('")
                args = []
                if not self.match("RPAREN"):  # Si no encontramos inmediatamente ')'
                    args.append(self.expression())  # Parsear primer argumento
                    while self.match("COMMA"):  # Mientras haya comas
                        args.append(self.expression())  # Parsear siguiente argumento
                    self.consume("RPAREN", "Se esperaba ')' después de los argumentos")
                return FunctionCall(id_name, args,lineno=self.get_lineno())
            else:
                if id_name.startswith("`"):
                    return MemoryReadLocation(id_name[1:])
                return PrimitiveReadLocation(id_name, lineno=self.tokens[self.current - 1].lineno)
        
        else:
            raise SyntaxError(f"Línea {self.peek().lineno}: Factor inesperado '{self.peek().value}'")
    



    def binary_op(self, operators: list, next_rule: callable) -> Node:

        try:
            left = next_rule()
            while self.peek() and self.peek().type in operators:
                op = self.advance().type
                right = next_rule()
                if not right:
                    raise SyntaxError(f"Línea {self.peek().lineno}: Falta expresión después del operador '{op}'")
                left = BinaryOperation(left, op, right,lineno=self.get_lineno())
            return left
        except Exception as e:
            raise SyntaxError(f"Línea {self.peek().lineno if self.peek() else '?'}: Error en operación binaria: {str(e)}")






    def expression(self) -> Node:
        
        left = self.orterm()  # Primero parseamos el primer orterm
        
        # Mientras encontremos operadores OR (||)
        while self.peek() and self.peek().type == 'OR':
            op = self.advance().type  # Consumimos el operador
            right = self.orterm()     # Parseamos el siguiente orterm
            left = BinaryOperation(left, op, right,lineno=self.get_lineno())  # Construimos el nodo
        
        return left
    


    def orterm(self) -> Node:
        
        left = self.andterm()
        while self.match("OR"):
            right = self.andterm()
            left = BinaryOperation(left, "OR", right,lineno=self.get_lineno())
        return left

    def andterm(self) -> Node:
        
        left = self.relterm()
        while self.match("AND"):
            right = self.relterm()
            left = BinaryOperation(left, "AND", right,lineno=self.get_lineno())
        return left

    def relterm(self) -> Node:
        
        left = self.addterm()
        while self.peek() and self.peek().type in ('LT', 'GT', 'LE', 'GE', 'EQ', 'NE'):
            op = self.advance().type
            right = self.addterm()
            left = BinaryOperation(left, op, right,lineno=self.get_lineno())
        return left

    def addterm(self) -> Node:
        
        left = self.term()
        while self.peek() and self.peek().type in ('PLUS', 'MINUS'):
            op = self.advance().type
            right = self.term()
            left = BinaryOperation(left, op, right,lineno=self.get_lineno())
        return left
    
    def term(self) -> Node:

        left = self.factor()
        while self.peek() and self.peek().type in ('TIMES', 'DIVIDE', 'MODULO'):
            op = self.advance().type
            right = self.factor()
            left = BinaryOperation(left, op, right,lineno=self.get_lineno())
        return left



    def parameters(self) -> List[Parameter]:
        
        params = []
        
        # Caso empty (no hay parámetros)
        if not self.peek() or self.peek().type == 'RPAREN':
            return params
        
        # Primer parámetro obligatorio
        name = self.consume('ID', 'Se esperaba nombre del parámetro').value
        
        if not self.peek() or self.peek().type not in {'int', 'float', 'bool', 'char'}:
            raise SyntaxError(f"Línea {self.peek().lineno}: Se esperaba tipo de parámetro")
        
        param_type = self.advance().value
        params.append(Parameter(name, param_type))
        
        # Parámetros adicionales
        while self.match('COMMA'):
            name = self.consume('ID', 'Se esperaba nombre del parámetro después de coma').value
            
            if not self.peek() or self.peek().type not in {'int', 'float', 'bool', 'char'}:
                raise SyntaxError(f"Línea {self.peek().lineno}: Se esperaba tipo de parámetro")
            
            param_type = self.advance().value
            params.append(Parameter(name, param_type))
        
        return params
    









    # Métodos auxiliares
    def peek(self) -> Token:
        return self.tokens[self.current] if self.current < len(self.tokens) else None
        
    def advance(self) -> Token:
        if self.current < len(self.tokens):
            token = self.tokens[self.current]
            self.current += 1
            return token
        return None
        
    def match(self, token_type: str) -> bool:
        if self.peek() and self.peek().type == token_type:
            self.advance()
            return True
        return False
        
    def consume(self, token_type: str, message: str) -> Token:
        if self.match(token_type):
            return self.tokens[self.current - 1]
        raise SyntaxError(f"Línea {self.peek().lineno}: {message}")

    def get_lineno(self) -> int:
        return self.tokens[self.current - 1].lineno if self.current > 0 else -1








# # 1. Cargar código fuente
# SOURCE_FILE = "factorize.gox"  # Nombre del archivo de entrada
# OUTPUT_FILE = "ast_output.json"  # Nombre del archivo de salida

# try:
#     # 2. Leer y tokenizar
#     with open(SOURCE_FILE, "r", encoding="utf-8") as f:
#         source_code = f.read()
    
#     lexer = Lexer(source_code)
#     tokens = list(lexer.tokenize())
#     for token in tokens:
#         print(f"{token.type}: {token.value} Línea {token.lineno}")
#     # 3. Parsear
#     parser = Parser(tokens)
#     ast = parser.parse()
#     print("AST generado:")
#     print(ast)
    
#     # 4. Convertir a JSON 
#     def ast_to_dict(node):
#         if isinstance(node, list):
#             return [ast_to_dict(item) for item in node]
#         elif hasattr(node, "__dict__"):
#             result = {"_type": node.__class__.__name__}  # Agrega tipo de nodo
#             result.update({k: ast_to_dict(v) for k, v in node.__dict__.items()})
#             return result
#         return node

#     # 5. Guardar resultados
#     with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
#         json.dump(ast_to_dict(ast), f, indent=4, ensure_ascii=False)
    
#     # 6. Feedback al usuario
#     print(f"✓ Análisis completado: {len(tokens)} tokens procesados")
#     print(f"• AST guardado en: {os.path.abspath(OUTPUT_FILE)}")
#     print(f"• Tamaño del AST: {len(ast)} nodos principales")

# except FileNotFoundError:
#     print(f"Error: No se encontró el archivo '{SOURCE_FILE}'")
# except Exception as e:
#     print(f"Error durante el análisis: {str(e)}")