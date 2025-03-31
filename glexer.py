# lexer.py
from rich import print
import sly
from dataclasses import dataclass
import sys
from rich.table import Table
from rich.console import Console

@dataclass
class Token:
    type: str
    value: any
    lineno: int


class GoxLexer(sly.Lexer):
    tokens = [
        "CONST", "VAR", "FUNC", "IF", "ELSE", "WHILE", "BREAK", "CONTINUE",
        "RETURN", "PRINT", "IMPORT", "INT_TYPE", "FLOAT_TYPE", "CHAR_TYPE", "BOOL_TYPE",
        "LE", "GE", "EQ", "NE", "LAND", "LOR", "LT", "GT",
        "ID", "FLOAT", "INTEGER", "CHAR", "BOOL",
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
    LT = r"<"
    GT = r">"

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
    ID["int"] = INT_TYPE
    ID["float"] = FLOAT_TYPE
    ID["char"] = CHAR_TYPE
    ID["bool"] = BOOL_TYPE



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


def analizar_archivo(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
        
        lexer = GoxLexer()
        tokens = lexer.tokenize(code)

        table = Table(title=f"Análisis Léxico - {file_path}")
        table.add_column("Tipo", style="cyan")
        table.add_column("Valor", style="magenta")
        table.add_column("Línea", justify="right", style="yellow")

        for tok in tokens:
            value = tok.value if isinstance(tok.value, str) else str(tok.value)
            table.add_row(tok.type, value, str(tok.lineno))

        console = Console()
        console.print(table)

    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{file_path}'")
        sys.exit(1)

def main():
    if len(sys.argv) != 2:
        print("Uso: python3 main.py <archivo.gox>")
        sys.exit(1)

    file_path = sys.argv[1]
    analizar_archivo(file_path)

if __name__ == "__main__":
    main()