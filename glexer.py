import re

class Token:
    def __init__(self, type: str, value: str, lineno: int):
        self.type = type
        self.value = value
        self.lineno = lineno
    
    def __repr__(self):
        return f"Token({self.type}, {self.value}, {self.lineno})"

class Lexer:
    # Palabras clave
    KEYWORDS = {
        'const', 'var', 'print', 'return', 'break', 'continue', 'if', 'else', 'while', 'func', 'import', 'true', 'false',
        'int', 'float', 'char', 'bool'
    }

    # Operadores de dos caracteres
    TWO_CHAR = {
        '<=': 'LE', '>=': 'GE', '==': 'EQ', '!=': 'NE', '&&': 'LAND', '||': 'LOR'
    }

    # Operadores y símbolos de un carácter
    ONE_CHAR = {
        '+': 'PLUS', '-': 'MINUS', '*': 'TIMES', '/': 'DIVIDE', '<': 'LT', '>': 'GT',
        '=': 'ASSIGN', ';': 'SEMI', '(': 'LPAREN', ')': 'RPAREN', '{': 'LBRACE', '}': 'RBRACE', ',': 'COMMA', '`': 'DEREF'
    }

    # Expresiones regulares
    NAME_PAT = re.compile(r'[a-zA-Z_][a-zA-Z_0-9]*')
    INTEGER_PAT = re.compile(r'\d+')
    FLOAT_PAT = re.compile(r'\d+\.\d*|\.\d+')
    CHAR_PAT = re.compile(r"'(\\.|[^\\'])'")

    BOOL_PAT = re.compile(r'\b(true|false)\b')
    COMMENT_LINE_PAT = re.compile(r'//.*')
    COMMENT_BLOCK_PAT = re.compile(r'/\*.*?\*/', re.DOTALL)

    def __init__(self, text):
        self.text = text
        self.index = 0
        self.lineno = 1
        self.tokens = []

    def tokenize(self):
        while self.index < len(self.text):
            char = self.text[self.index]
            if char in ' \t':
                self.index += 1
                continue


            if char == '\n':
                self.lineno += 1
                self.index += 1
                continue


            if self.text[self.index:self.index+2] == "//":
                self.index = self.text.find("\n", self.index)
                if self.index == -1:  
                    self.index = len(self.text)
                continue

   
            if self.text[self.index:self.index+2] == "/*":
                end_index = self.text.find("*/", self.index+2)
                if end_index == -1:
                    raise ValueError(f"{self.lineno}: Comentario no terminado")
                self.lineno += self.text[self.index:end_index].count("\n")  # Contar saltos de línea en el bloque
                self.index = end_index + 2
                continue

   
            if self.text[self.index:self.index+2] in self.TWO_CHAR:
                self.tokens.append(Token(self.TWO_CHAR[self.text[self.index:self.index+2]], self.text[self.index:self.index+2], self.lineno))
                self.index += 2
                continue

     
            if char in self.ONE_CHAR:
                self.tokens.append(Token(self.ONE_CHAR[char], char, self.lineno))
                self.index += 1
                continue

            m = self.NAME_PAT.match(self.text, self.index)
            if m:
                value = m.group(0)
                token_type = value if value in self.KEYWORDS else 'ID'
                self.tokens.append(Token(token_type, value, self.lineno))
                self.index = m.end()
                continue

            m = self.BOOL_PAT.match(self.text, self.index)
            if m:
                self.tokens.append(Token('BOOL', m.group(0), self.lineno))
                self.index = m.end()
                continue

            m = self.FLOAT_PAT.match(self.text, self.index)
            if m:
                self.tokens.append(Token('FLOAT', m.group(0), self.lineno))
                self.index = m.end()
                continue

            m = self.INTEGER_PAT.match(self.text, self.index)
            if m:
                self.tokens.append(Token('INTEGER', m.group(0), self.lineno))
                self.index = m.end()
                continue



            m = self.CHAR_PAT.match(self.text, self.index)
            if m:
                self.tokens.append(Token('CHAR', m.group(1), self.lineno))
                self.index = m.end()
                continue

            raise ValueError(f"{self.lineno}: Caracter ilegal '{char}'")

        return self.tokens