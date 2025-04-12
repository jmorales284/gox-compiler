from typing import List
from dataclasses import dataclass
from goxlex import Lexer
from goxats import *

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

    def parse(self) -> List[Node]:
        statements = []
        while self.current < len(self.tokens) and self.tokens[self.current].type != "EOF":
            statements.append(self.statement())
        return statements

    def statement(self) -> Node:
        if self.peek().type == "ID":
            # Guardamos posición por si necesitamos retroceder
            current_pos = self.current
            name_token = self.advance()
            
            # Verificamos si es llamada a función
            if self.peek() and self.peek().type == "LPAREN":
                self.consume("LPAREN", "Se esperaba '(' después del nombre de función")
                args = []
                if not self.match("RPAREN"):
                    args.append(self.expression())
                    while self.match("COMMA"):
                        args.append(self.expression())
                    self.consume("RPAREN", "Se esperaba ')' después de los argumentos")
                self.consume("SEMI", "Se esperaba ';' después de la llamada")
                return FunctionCall(name_token.value, args)
            else:
                # No era llamada a función, retrocedemos y parseamos como asignación
                self.current = current_pos
                return self.assignment()
        
        elif self.peek().type in ("VAR", "CONST"):
            return self.vardecl()
        elif self.peek().type == "FUNC":
            return self.funcdecl()
        elif self.peek().type == "IF":
            return self.if_stmt()
        elif self.peek().type == "WHILE":
            return self.while_stmt()
        elif self.peek().type == "BREAK":
            self.advance()
            return Break()
        elif self.peek().type == "CONTINUE":
            self.advance()
            return Continue()
        elif self.peek().type == "RETURN":
            return self.return_stmt()
        elif self.peek().type == "PRINT":
            return self.print_stmt()
        else:
            raise SyntaxError(f"Línea {self.peek().lineno}: Declaración inesperada '{self.peek().value}'")

    def assignment(self) -> Node:
        name_token = self.consume("ID", "Se esperaba identificador")
        self.consume("ASSIGN", "Se esperaba '=' después del identificador")
        expr = self.expression()
        self.consume("SEMI", "Se esperaba ';' después de la expresión")

        if name_token.value.startswith("`"):
            return MemoryAssignmentLocation(name_token.value[1:], expr)
        return PrimitiveAssignmentLocation(name_token.value, expr)




    def vardecl(self) -> VariableDeclaration:
        
        
        is_constant = self.match("CONST")
        if not is_constant:
            self.consume("VAR", "Se esperaba 'var' o 'const'")
        
        # Obtener el nombre de la variable
        name_token = self.consume("ID", "Se esperaba nombre de variable después de var/const")
        
        # Manejar tipo explícito (opcional)
        var_type = None
        if self.peek() and self.peek().type in {"INT", "FLOAT", "BOOL", "CHAR", "STRING"}:
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
        
        return VariableDeclaration(
            name=name_token.value,
            var_type=var_type,  # Ahora incluye el tipo si fue especificado
            value=value,
            is_constant=is_constant
        )



    def funcdecl(self) -> FunctionDefinition:
        self.consume("FUNC", "Se esperaba 'func'")
        name_token = self.consume("ID", "Se esperaba nombre de función")
        self.consume("LPAREN", "Se esperaba '(' después del nombre")
        
        params = []
        while self.peek().type != "RPAREN":
            param_token = self.consume("ID", "Se esperaba nombre de parámetro")
            
            if self.peek().type not in {"INT", "FLOAT", "BOOL", "CHAR", "STRING"}:
                raise SyntaxError(f"Línea {self.peek().lineno}: Se esperaba tipo de parámetro")
            
            param_type = self.advance().value
            params.append(Parameter(param_token.value, param_type))
            
            if self.peek().type == "COMMA":
                self.advance()

        self.consume("RPAREN", "Se esperaba ')'")

        # Cambio clave: Hacer el tipo de retorno opcional (default void)
        return_type = "VOID"  # Valor por defecto
        if self.peek() and self.peek().type in {"INT", "FLOAT", "BOOL", "CHAR", "STRING", "VOID"}:
            return_type = self.advance().value
        
        self.consume("LBRACE", f"Se esperaba '{{' (línea {self.peek().lineno})")
        
        body = []
        while not self.match("RBRACE"):
            body.append(self.statement())

        return FunctionDefinition(
            name=name_token.value,
            parameters=params,
            return_type=return_type,
            body=body
        )

    def if_stmt(self) -> Conditional:
        self.consume("IF", "Se esperaba 'if'")
        
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
            
            if self.match("ELSE"):
                false_branch = [self.statement()]
                
            return Conditional(condition, true_branch, false_branch)
        
        # 3. Cuerpo del if con llaves
        true_branch = []
        while not self.match("RBRACE"):
            true_branch.append(self.statement())
        
        # 4. ELSE opcional
        false_branch = None
        if self.match("ELSE"):
            if not self.match("LBRACE"):
                # Else de una sola línea
                false_branch = [self.statement()]
            else:
                false_branch = []
                while not self.match("RBRACE"):
                    false_branch.append(self.statement())
        
        return Conditional(condition, true_branch, false_branch)

    def while_stmt(self) -> WhileLoop:
        self.consume("WHILE", "Se esperaba 'while'")
        condition = self.expression()
        self.consume("LBRACE", "Se esperaba '{' después de while")
        
        body = []
        while not self.match("RBRACE"):
            body.append(self.statement())

        return WhileLoop(condition, body)

    def return_stmt(self) -> Return:
        self.consume("RETURN", "Se esperaba 'return'")
        
        if self.match("SEMI"):
            return Return(None)
        
        expr = self.expression()
        self.consume("SEMI", "Se esperaba ';' después de return")
        return Return(expr)

    def print_stmt(self) -> Print:
        self.consume("PRINT", "Se esperaba 'print'")
        expr = self.expression()
        self.consume("SEMI", "Se esperaba ';' después de print")
        return Print(expr)
    






    

    # Métodos de análisis de expresiones
    def factor(self):

        if self.match("TRUE"):
            return Literal("true", 'bool')  # Valor normalizado a minúsculas
    
        elif self.match("FALSE"):
            return Literal("false", 'bool')  # Valor normalizado a minúsculas

        if self.match("INTEGER"):
            return Literal(self.tokens[self.current - 1].value, 'int')
        
        elif self.match("FLOAT_LITERAL"):
            return Literal(self.tokens[self.current - 1].value, 'float')
        
        # Literales de caracteres y strings
        elif self.match("CHAR_LITERAL"):
            char_value = self.tokens[self.current - 1].value
            # Remover las comillas simples y manejar secuencias de escape
            processed_char = char_value[1:-1].encode().decode('unicode_escape')
            return Literal(processed_char, 'char')
        
        elif self.match("STRING_LITERAL"):
            string_tokens = []
            # Consumir tokens hasta encontrar el cierre de comillas
            while self.peek() and self.peek().type != "STRING_LITERAL":
                string_tokens.append(self.advance().value)
            self.consume("STRING_LITERAL", "Se esperaba cierre de comillas")
            # Unir todos los tokens intermedios para formar el string completo
            string_value = "".join(string_tokens)
            return Literal(string_value, 'string')
        
        # Literales booleanos
        elif self.match("BOOLEAN"):
            return Literal(self.tokens[self.current - 1].value.lower(), 'bool')
        
        # Operadores unarios
        elif self.match("PLUS") or self.match("MINUS") or self.match("GROW"):
            op = self.tokens[self.current - 1].type
            return UnaryOperation(op, self.factor())
        
        # Expresiones entre paréntesis
        elif self.match("LPAREN"):
            expr = self.expression()
            self.consume("RPAREN", "Se esperaba ')'")
            return expr
        
        # Type casting
        elif self.match("INT") or self.match("FLOAT") or self.match("BOOL") or self.match("CHAR"):
            type_name = self.tokens[self.current - 1].value.lower()
            self.consume("LPAREN", f"Se esperaba '(' después de {type_name}")
            expr = self.expression()
            self.consume("RPAREN", "Se esperaba ')'")
            return TypeConversion(type_name, expr)
        
        # Llamadas a funciones
        elif self.match("ID"):
            id_name = self.tokens[self.current - 1].value
            if self.peek() and self.peek().type == "LPAREN":
                self.consume("LPAREN", "Se esperaba '('")
                args = self.parameters() if not self.match("RPAREN") else []
                if not self.tokens[self.current - 1].type == "RPAREN":
                    self.consume("RPAREN", "Se esperaba ')'")
                return FunctionCall(id_name, args)
            else:
                if id_name.startswith("`"):
                    return MemoryReadLocation(id_name[1:])
                return PrimitiveReadLocation(id_name)
        
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
                left = BinaryOperation(left, op, right)
            return left
        except Exception as e:
            raise SyntaxError(f"Línea {self.peek().lineno if self.peek() else '?'}: Error en operación binaria: {str(e)}")






    def expression(self) -> Node:
        
        left = self.orterm()  # Primero parseamos el primer orterm
        
        # Mientras encontremos operadores OR (||)
        while self.peek() and self.peek().type == 'OR':
            op = self.advance().type  # Consumimos el operador
            right = self.orterm()     # Parseamos el siguiente orterm
            left = BinaryOperation(left, op, right)  # Construimos el nodo
        
        return left
    


    def orterm(self) -> Node:
        
        left = self.andterm()
        while self.match("OR"):
            right = self.andterm()
            left = BinaryOperation(left, "OR", right)
        return left

    def andterm(self) -> Node:
        
        left = self.relterm()
        while self.match("AND"):
            right = self.relterm()
            left = BinaryOperation(left, "AND", right)
        return left

    def relterm(self) -> Node:
        
        left = self.addterm()
        while self.peek() and self.peek().type in ('LT', 'GT', 'LE', 'GE', 'EQ', 'NE'):
            op = self.advance().type
            right = self.addterm()
            left = BinaryOperation(left, op, right)
        return left

    def addterm(self) -> Node:
        
        left = self.term()
        while self.peek() and self.peek().type in ('PLUS', 'MINUS'):
            op = self.advance().type
            right = self.term()
            left = BinaryOperation(left, op, right)
        return left
    
    def term(self) -> Node:

        left = self.factor()
        while self.peek() and self.peek().type in ('TIMES', 'DIVIDE', 'MODULO'):
            op = self.advance().type
            right = self.factor()
            left = BinaryOperation(left, op, right)
        return left



    def parameters(self) -> List[Parameter]:
        
        params = []
        
        # Caso empty (no hay parámetros)
        if not self.peek() or self.peek().type == 'RPAREN':
            return params
        
        # Primer parámetro obligatorio
        name = self.consume('ID', 'Se esperaba nombre del parámetro').value
        
        if not self.peek() or self.peek().type not in {'INT', 'FLOAT', 'BOOL', 'CHAR', 'STRING'}:
            raise SyntaxError(f"Línea {self.peek().lineno}: Se esperaba tipo de parámetro")
        
        param_type = self.advance().value
        params.append(Parameter(name, param_type))
        
        # Parámetros adicionales
        while self.match('COMMA'):
            name = self.consume('ID', 'Se esperaba nombre del parámetro después de coma').value
            
            if not self.peek() or self.peek().type not in {'INT', 'FLOAT', 'BOOL', 'CHAR', 'STRING'}:
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








# 1. Cargar código fuente
SOURCE_FILE = "factorize.gox"  # Nombre del archivo de entrada
OUTPUT_FILE = "ast_output.json"  # Nombre del archivo de salida

try:
    # 2. Leer y tokenizar
    with open(SOURCE_FILE, "r", encoding="utf-8") as f:
        source_code = f.read()
    
    lexer = Lexer()
    raw_tokens = list(lexer.tokenize(source_code))
    tokens = [Token(type=type, value=value, lineno=lineno) for (type, value, lineno) in raw_tokens] 
    
    # 3. Parsear
    parser = Parser(tokens)
    ast = parser.parse()
    
    # 4. Convertir a JSON (versión mejorada de tu función)
    def ast_to_dict(node):
        if isinstance(node, list):
            return [ast_to_dict(item) for item in node]
        elif hasattr(node, "__dict__"):
            result = {"_type": node.__class__.__name__}  # Agrega tipo de nodo
            result.update({k: ast_to_dict(v) for k, v in node.__dict__.items()})
            return result
        return node

    # 5. Guardar resultados
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(ast_to_dict(ast), f, indent=4, ensure_ascii=False)
    
    # 6. Feedback al usuario
    print(f"✓ Análisis completado: {len(tokens)} tokens procesados")
    print(f"• AST guardado en: {os.path.abspath(OUTPUT_FILE)}")
    print(f"• Tamaño del AST: {len(ast)} nodos principales")

except FileNotFoundError:
    print(f"Error: No se encontró el archivo '{SOURCE_FILE}'")
except Exception as e:
    print(f"Error durante el análisis: {str(e)}")