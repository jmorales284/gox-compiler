import sys
from lexer import Lexer 

def main():
    if len(sys.argv) != 2:
        print("Uso: python3 main.py <archivo.gox>")
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
        
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        for token in tokens:
            print(token)

    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{file_path}'")
        sys.exit(1)

if __name__ == "__main__":
    main()
