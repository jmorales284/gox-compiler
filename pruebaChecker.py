from gmodel import *
from checkNew import Checker
from glexer import Lexer
from gparser import Parser
import os

os.system('cls' if os.name == 'nt' else 'clear')

# 1. Cargar código fuente
SOURCE_FILE = "prueba.gox"  # Nombre del archivo de entrada
OUTPUT_FILE = "ast_output.json"  # Nombre del archivo de salida

# 2. Leer y tokenizar
with open(SOURCE_FILE, "r", encoding="utf-8") as f:
    source_code = f.read()

lexer = Lexer(source_code)
tokens = list(lexer.tokenize())
# for token in tokens:
#     print(f"{token.type}: {token.value} Línea {token.lineno}")
# 3. Parsear
parser = Parser(tokens)
ast = parser.parse()


# 6. Feedback al usuario
print(f"✓ Análisis completado: {len(tokens)} tokens procesados")

print("AST generado:")
print(ast)
print("___________________________________")

# Un programa con solo una declaración de variable y una asignación
program = ast
Checker.check(program)