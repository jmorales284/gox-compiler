# lexer.py
from rich import print
import sly
from dataclasses import dataclass

@dataclass
class Token:
    type: str
    value: any
    lineno: int


class Lexer(sly.Lexer):
    tokens = [
        "CONST", "VAR", "FUNC", "IF", "ELSE", "WHILE", "BREAK", "CONTINUE",
        "RETURN", "PRINT", "IMPORT",
        "LE", "GE", "EQ", "NE", "LAND", "LOR",
        "ID", "FLOAT", "INTEGER", "CHAR", "BOOL"
    ]
    literals = "+-*/=<>(){};,^"

    # Ignore spaces and tabs
    ignore = " \t"

    # Ignore newlines
    @_(r"\n+")
    def ignore_newline(self, t):
        self.lineno += t.value.count("\n")

    # Ignore single-line comments
    @_(r"//.*")
    def ignore_linecomment(self, t):
        pass

    # Ignore multi-line comments
    @_(r"/\*(.|\n)*?\*/")
    def ignore_comment(self, t):
        self.lineno += t.value.count("\n")

    # Operators
    LE = r"<="
    GE = r">="
    EQ = r"=="
    NE = r"!="
    LAND = r"&&"
    LOR = r"\|\|"

    # Identifiers & Keywords
    ID = r"[a-zA-Z_]\w*"
    ID["const"] = CONST
    ID["var"] = VAR
    ID["func"] = FUNC
    ID["if"] = IF
    ID["else"] = ELSE
    ID["while"] = WHILE
    ID["break"] = BREAK
    ID["continue"] = CONTINUE
    ID["return"] = RETURN
    ID["print"] = PRINT
    ID["import"] = IMPORT
    ID["false"] = BOOL
    ID["true"] = BOOL

    # Character literals
    CHAR = r"'(\\[nrt'\"\\]|x[0-9a-fA-F]{2}|[^'\\])'"

    # Float literals
    @_(r"(\d+\.\d*)|(\d*\.\d+)")
    def FLOAT(self, t):
        t.value = float(t.value)
        return t

    # Integer literals
    @_(r"\d+")
    def INTEGER(self, t):
        t.value = int(t.value)
        return t

    # Error handling
    def error(self, t):
        print(f"[bold red]Error en línea {self.lineno}:[/bold red] Carácter ilegal '{t.value[0]}'")
        self.index += 1  # Salta al siguiente token
