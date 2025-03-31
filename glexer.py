# lexer.py
# Este archivo define el analizador léxico (lexer) para el lenguaje Gox.
# El lexer utiliza la biblioteca SLY para dividir el código fuente en tokens,
# que son las unidades básicas de la gramática del lenguaje.

from rich import print
import sly
from dataclasses import dataclass
import sys
from rich.table import Table
from rich.console import Console

@dataclass
class Token:
    """
    Representa un token generado por el lexer.
    Contiene el tipo del token, su valor y el número de línea donde se encontró.
    """
    type: str
    value: any
    lineno: int


class GoxLexer(sly.Lexer):
    """
    Analizador léxico para el lenguaje Gox.
    Convierte el código fuente en una secuencia de tokens que serán procesados por el parser.
    """
    # Lista de tokens reconocidos por el lexer
    tokens = [
        "CONST", "VAR", "FUNC", "IF", "ELSE", "WHILE", "BREAK", "CONTINUE",
        "RETURN", "PRINT", "IMPORT", "INT_TYPE", "FLOAT_TYPE", "CHAR_TYPE", "BOOL_TYPE",
        "LE", "GE", "EQ", "NE", "LAND", "LOR", "LT", "GT",
        "ID", "FLOAT", "INTEGER", "CHAR", "BOOL",
    ]

    # Caracteres literales que se reconocen directamente
    literals = "+-*/%=<>(){};,^"

    # Ignorar espacios y tabulaciones
    ignore = " \t"

    # Ignorar saltos de línea y actualizar el número de línea
    @_(r"\n+")
    def ignore_newline(self, t):
        """
        Ignora los saltos de línea y actualiza el número de línea.
        """
        self.lineno += t.value.count("\n")

    # Ignorar comentarios de una sola línea
    @_(r"//.*")
    def ignore_linecomment(self, t):
        """
        Ignora los comentarios de una sola línea que comienzan con '//'.
        """
        pass

    # Ignorar comentarios de múltiples líneas
    @_(r"/\*(.|\n)*?\*/")
    def ignore_comment(self, t):
        """
        Ignora los comentarios de múltiples líneas delimitados por '/*' y '*/'.
        """
        self.lineno += t.value.count("\n")

    # Operadores relacionales y lógicos
    LE = r"<="
    GE = r">="
    EQ = r"=="
    NE = r"!="
    LAND = r"&&"
    LOR = r"\|\|"
    LT = r"<"
    GT = r">"

    # Identificadores y palabras clave
    ID = r"[a-zA-Z_]\w*"

    # Palabras clave del lenguaje Gox
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

    # Literales de caracteres
    CHAR = r"'(\\[nrt'\"\\]|x[0-9a-fA-F]{2}|[^'\\])'"

    # Literales de números flotantes
    @_(r"(\d+\.\d*)|(\d*\.\d+)")
    def FLOAT(self, t):
        """
        Reconoce literales de números flotantes y los convierte a tipo float.
        """
        t.value = float(t.value)
        return t

    # Literales de números enteros
    @_(r"\d+")
    def INTEGER(self, t):
        """
        Reconoce literales de números enteros y los convierte a tipo int.
        """
        t.value = int(t.value)
        return t

    # Manejo de errores
    def error(self, t):
        """
        Maneja caracteres ilegales encontrados en el código fuente.
        """
        print(f"[bold red]Error en línea {self.lineno}:[/bold red] Carácter ilegal '{t.value[0]}'")
        self.index += 1  # Salta al siguiente token


def analizar_archivo(file_path):
    """
    Función para analizar un archivo de código fuente de Gox.
    Genera y muestra una tabla con los tokens encontrados.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
        
        lexer = GoxLexer()
        tokens = lexer.tokenize(code)

        # Crear una tabla para mostrar los tokens
        table = Table(title=f"Análisis Léxico - {file_path}")
        table.add_column("Tipo", style="cyan")
        table.add_column("Valor", style="magenta")
        table.add_column("Línea", justify="right", style="yellow")

        # Agregar los tokens a la tabla
        for tok in tokens:
            value = tok.value if isinstance(tok.value, str) else str(tok.value)
            table.add_row(tok.type, value, str(tok.lineno))

        # Mostrar la tabla en la consola
        console = Console()
        console.print(table)

    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{file_path}'")
        sys.exit(1)


def main():
    """
    Función principal del programa.
    Verifica los argumentos de línea de comandos y analiza el archivo proporcionado.
    """
    if len(sys.argv) != 2:
        print("Uso: python3 glexer.py <archivo.gox>")
        sys.exit(1)

    file_path = sys.argv[1]
    analizar_archivo(file_path)


if __name__ == "__main__":
    main()