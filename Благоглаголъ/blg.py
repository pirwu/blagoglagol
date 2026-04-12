import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer import BlagoglagolLexer
from parser import BlagoglagolParser
from interpreter import BlagoglagolInterpreter

VERSION = "1.0.0"

def main():
    if len(sys.argv) < 2:
        print(f"Благоглаголъ v{VERSION}")
        print("Использование: blg <файл.blg>")
        print("             blg --version")
        sys.exit(1)
    
    if sys.argv[1] == "--version" or sys.argv[1] == "-v":
        print(f"Благоглаголъ v{VERSION}")
        return
    
    filename = sys.argv[1]
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            source = f.read()
        
        lexer = BlagoglagolLexer(source)
        tokens = lexer.tokenize()
        
        parser = BlagoglagolParser(tokens)
        ast = parser.parse()
        
        interpreter = BlagoglagolInterpreter()
        interpreter.interpret(ast)
        
    except FileNotFoundError:
        print(f"Файл '{filename}' не найден")
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()