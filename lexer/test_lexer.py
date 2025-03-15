import unittest
from lexer import Lexer, Token

class TestLexer(unittest.TestCase):
    def test_keywords(self):
        lexer = Lexer("var int float bool char func return if else while print true false")
        tokens = lexer.tokenize()
        expected_types = ['var', 'int', 'float', 'bool', 'char', 'func', 'return', 'if', 'else', 'while', 'print', 'true', 'false']
        self.assertEqual([t.type for t in tokens], expected_types)
    
    def test_identifiers(self):
        lexer = Lexer("x y variable foo bar")
        tokens = lexer.tokenize()
        expected_types = ['ID', 'ID', 'ID', 'ID', 'ID']
        self.assertEqual([t.type for t in tokens], expected_types)
    
    def test_numbers(self):
        lexer = Lexer("123 45.67 .89 0 1000")
        tokens = lexer.tokenize()
        expected_types = ['INTEGER', 'FLOAT', 'FLOAT', 'INTEGER', 'INTEGER']
        self.assertEqual([t.type for t in tokens], expected_types)
    
    def test_operators(self):
        lexer = Lexer("+ - * / <= >= == != && || < > =")
        tokens = lexer.tokenize()
        expected_types = ['PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'LE', 'GE', 'EQ', 'NE', 'LAND', 'LOR', 'LT', 'GT', 'ASSIGN']
        self.assertEqual([t.type for t in tokens], expected_types)
    
    def test_symbols(self):
        lexer = Lexer("( ) { } , ; `")
        tokens = lexer.tokenize()
        expected_types = ['LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'COMMA', 'SEMI', 'DEREF']
        self.assertEqual([t.type for t in tokens], expected_types)
    
    def test_comments(self):
        lexer = Lexer("// This is a comment\nvar x = 5; /* Block comment */ y = 10;")
        tokens = lexer.tokenize()
        expected_types = ['var', 'ID', 'ASSIGN', 'INTEGER', 'SEMI', 'ID', 'ASSIGN', 'INTEGER', 'SEMI']
        self.assertEqual([t.type for t in tokens], expected_types)

    def test_invalid_char(self):
        lexer = Lexer("$")
        with self.assertRaises(ValueError):
            lexer.tokenize()

if __name__ == "__main__":
    unittest.main()
