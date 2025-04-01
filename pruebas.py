from glexer import GoxLexer
from gparse import GoxParser
import json

def ast_to_dict(node):
    if isinstance(node, list):
        return [ast_to_dict(item) for item in node]
    elif hasattr(node, "__dict__"):
        return {key: ast_to_dict(value) for key, value in node.__dict__.items()}
    else:
        return node


def save_ast_to_json(ast, filename="ast_output.json"):
    ast_json = json.dumps(ast_to_dict(ast), indent=4)
    with open(filename, "w") as f:
        f.write(ast_json)

# Prueba de asignaciones simples
data = '''
x = 10;
y = x + 5;
z = x * y - 3;
'''
tokens = list(GoxLexer().tokenize(data))
ast = GoxParser().parse(iter(tokens))
save_ast_to_json(ast, "test_assignments.json")


# Prueba de declaraciones de variables
data = '''
var x int;
var y float = 3.14;
var z char = 'a';
var flag bool = true;
'''
tokens = list(GoxLexer().tokenize(data))
ast = GoxParser().parse(iter(tokens))
save_ast_to_json(ast, "test_var_declarations.json")

# Prueba de declaraciones de constantes
data = '''
const pi float = 3.14159;
const e float = 2.71828;
const greeting char = 'H';
const is_valid bool = false;
'''
tokens = list(GoxLexer().tokenize(data))
ast = GoxParser().parse(iter(tokens))
save_ast_to_json(ast, "test_const_declarations.json")

# Prueba de funciones
data = '''
func add(a int, b int) int {
    return a + b;
}

func greet() {
    print (x);
}
'''
tokens = list(GoxLexer().tokenize(data))
ast = GoxParser().parse(iter(tokens))
save_ast_to_json(ast, "test_functions.json")

# Prueba de sentencias if-else
data = '''
if x > 10 {
    print (x);
} else {
    print (y);
}
'''
tokens = list(GoxLexer().tokenize(data))
ast = GoxParser().parse(iter(tokens))
save_ast_to_json(ast, "test_if_else.json")

# Prueba de bucles while
data = '''
var i int = 0;
while i < 10 {
    print i;
    i = i + 1;
}
'''
tokens = list(GoxLexer().tokenize(data))
ast = GoxParser().parse(iter(tokens))
save_ast_to_json(ast, "test_while.json")


# Prueba de expresiones aritméticas y lógicas
data = '''
var result int = (3 + 4) * 2 - 5 / (1 + 1);
var is_valid bool = true && false || (3 > 2);
'''
tokens = list(GoxLexer().tokenize(data))
ast = GoxParser().parse(iter(tokens))
save_ast_to_json(ast, "test_expressions.json")

# Prueba de tipos y conversiones
data = '''
var x float = float(10);
var y int = int(3.14);
var z char = char(65);
var flag bool = bool(1);
'''
tokens = list(GoxLexer().tokenize(data))
ast = GoxParser().parse(iter(tokens))
save_ast_to_json(ast, "test_type_conversions.json")

# Prueba de argumentos en funciones
data = '''
func sum(a int, b int, c int) int {
    return a + b + c;
}

var result int = sum(1, 2, 3);
'''
tokens = list(GoxLexer().tokenize(data))
ast = GoxParser().parse(iter(tokens))
save_ast_to_json(ast, "test_function_arguments.json")


# Prueba de literales
data = '''
var x int = 42;
var y float = 3.14;
var z char = 'c';
var flag bool = true;
'''
tokens = list(GoxLexer().tokenize(data))
ast = GoxParser().parse(iter(tokens))
save_ast_to_json(ast, "test_literals.json")

# Prueba de importación de funciones
data = '''
import func external_func(a int) int {
    return a * 2;
}

var result int = external_func(5);
'''
tokens = list(GoxLexer().tokenize(data))
ast = GoxParser().parse(iter(tokens))
save_ast_to_json(ast, "test_import_functions.json")

# Prueba de expresiones complejas
data = '''
var result int = (3 + 4 * 2) - (10 / (5 - 3)) % 2;
var is_valid bool = (true || false) && (3 > 2) && (5 < 4);
'''
tokens = list(GoxLexer().tokenize(data))
ast = GoxParser().parse(iter(tokens))
save_ast_to_json(ast, "test_complex_expressions.json")

# Prueba de un programa completo
data = '''
func main() {
    var x int = 10;
    var y int = 20;
    var result int = x + y;

    if result > 15 {
        print (15);
    } else {
        print ( result );
    }

    while x > 0 {
        print x;
        x = x - 1;
    }
}

'''
tokens = list(GoxLexer().tokenize(data))
ast = GoxParser().parse(iter(tokens))
save_ast_to_json(ast, "test_full_program.json")