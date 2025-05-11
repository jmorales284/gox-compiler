import sys
from glexer import Lexer
from rich.table import Table
from rich.console import Console

def analizar_archivo(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
        
        lexer = Lexer(code)
        tokens = lexer.tokenize()

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
