from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional, Dict, Set
import re


class TokenType(Enum):
    AZ = auto()              # азъ
    RECHE = auto()           # рече
    YESM = auto()            # есмь
    TOGDA = auto()           # тогда
    ILIZHE = auto()          # илиже
    INACHE = auto()          # иначе
    POKONCHI = auto()        # покончи
    DOKOLE = auto()          # доколе
    TVORI = auto()           # твори
    DLYA = auto()            # для
    DO = auto()              # до
    SHAG = auto()            # шаг
    VOZVRATI = auto()        # возврати
    GLAGOLI = auto()         # глаголи
    VNEMLI = auto()          # внемли
    VKLUCHI = auto()         # включи
    POMILUY = auto()         # помилуй
    
    # Типы данных
    CHISLO = auto()          # число
    DROB = auto()            # дробь
    SLOVO = auto()           # слово
    ISTINA = auto()          # истина
    LOZH = auto()            # ложь
    NICHTO = auto()          # ничто
    
    # Операторы (церковные)
    RAVNO = auto()           # равно
    NERAVNO = auto()         # неравно
    BOLEE = auto()           # более
    MENEE = auto()           # менее
    I = auto()               # и
    ILI = auto()             # или
    NE = auto()              # не
    
    # Символы и операторы
    PLUS = auto()            # +
    MINUS = auto()           # -
    STAR = auto()            # *
    SLASH = auto()           # /
    ASSIGN = auto()          # :=
    EQ = auto()              # ==
    NEQ = auto()             # !=
    GT = auto()              # >
    LT = auto()              # <
    AND = auto()             # &&
    OR = auto()              # ||
    NOT = auto()             # !
    LPAREN = auto()          # (
    RPAREN = auto()          # )
    LBRACE = auto()          # {
    RBRACE = auto()          # }
    COMMA = auto()           # ,
    SEMICOLON = auto()       # ;
    DOT = auto()             # .
    
    # Литералы
    INTEGER = auto()         # 123
    FLOAT = auto()           # 123.45
    STRING = auto()          # "текст"
    IDENTIFIER = auto()      # имя_переменной
    
    # Специальные
    COMMENT = auto()         # // комментарий или # комментарий
    WHITESPACE = auto()      # пробелы (игнорируются)
    NEWLINE = auto()         # перевод строки
    EOF = auto()             # конец файла


@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int
    length: int
    
    def __repr__(self):
        return f"Token({self.type.name}, '{self.value}', line={self.line}, col={self.column})"


class LexerError(Exception):
    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Лексическая ошибка в строке {line}, позиция {column}: {message}")


class BlagoglagolLexer:
    
    def __init__(self, source: str):
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        self.keywords: Dict[str, TokenType] = {
            "азъ": TokenType.AZ,
            "рече": TokenType.RECHE,
            "есмь": TokenType.YESM,
            "тогда": TokenType.TOGDA,
            "илиже": TokenType.ILIZHE,
            "иначе": TokenType.INACHE,
            "покончи": TokenType.POKONCHI,
            "доколе": TokenType.DOKOLE,
            "твори": TokenType.TVORI,
            "для": TokenType.DLYA,
            "до": TokenType.DO,
            "шаг": TokenType.SHAG,
            "возврати": TokenType.VOZVRATI,
            "глаголи": TokenType.GLAGOLI,
            "внемли": TokenType.VNEMLI,
            "включи": TokenType.VKLUCHI,
            "помилуй": TokenType.POMILUY,
            
            # Типы данных
            "число": TokenType.CHISLO,
            "дробь": TokenType.DROB,
            "слово": TokenType.SLOVO,
            "истина": TokenType.ISTINA,
            "ложь": TokenType.LOZH,
            "ничто": TokenType.NICHTO,
            
            # Операторы-слова
            "равно": TokenType.RAVNO,
            "неравно": TokenType.NERAVNO,
            "более": TokenType.BOLEE,
            "менее": TokenType.MENEE,
            "и": TokenType.I,
            "или": TokenType.ILI,
            "не": TokenType.NE,
        }
        
        # Символы-операторы (одиночные)
        self.single_char_tokens: Dict[str, TokenType] = {
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.STAR,
            '/': TokenType.SLASH,
            '(': TokenType.LPAREN,
            ')': TokenType.RPAREN,
            '{': TokenType.LBRACE,
            '}': TokenType.RBRACE,
            ',': TokenType.COMMA,
            ';': TokenType.SEMICOLON,
            '.': TokenType.DOT,
            '>': TokenType.GT,
            '<': TokenType.LT,
            '!': TokenType.NOT,
        }
        
        # Составные операторы
        self.double_char_tokens: Dict[str, TokenType] = {
            ':=': TokenType.ASSIGN,
            '==': TokenType.EQ,
            '!=': TokenType.NEQ,
            '&&': TokenType.AND,
            '||': TokenType.OR,
        }
    
    def tokenize(self) -> List[Token]:
        self.tokens = []
        self.position = 0
        self.line = 1
        self.column = 1
        
        while self.position < len(self.source):
            try:
                self._next_token()
            except LexerError as e:
                self.tokens.append(Token(
                    type=TokenType.EOF,
                    value=f"ERROR: {e.message}",
                    line=e.line,
                    column=e.column,
                    length=0
                ))
                raise
        
        self.tokens.append(Token(
            type=TokenType.EOF,
            value="",
            line=self.line,
            column=self.column,
            length=0
        ))
        
        return self.tokens
    
    def _next_token(self):
        char = self._current_char()
        
        # Пропускаем пробелы
        if char.isspace():
            self._skip_whitespace()
            return
        
        # Комментарии
        if char == '/' and self._peek_char() == '/':
            self._skip_line_comment()
            return
        if char == '#' or (char == ':' and self._peek_char() == ':'):
            self._skip_church_comment()
            return
        
        # Составные операторы
        if self.position < len(self.source) - 1:
            two_chars = self.source[self.position:self.position + 2]
            if two_chars in self.double_char_tokens:
                self._add_token(self.double_char_tokens[two_chars], two_chars, 2)
                return
        
        # Одиночные символы-операторы
        if char in self.single_char_tokens:
            self._add_token(self.single_char_tokens[char], char, 1)
            return
        
        # Строковые литералы
        if char == '"':
            self._read_string()
            return
        
        # Числа
        if char.isdigit():
            self._read_number()
            return
        
        # Идентификаторы и ключевые слова
        if char.isalpha() or char == '_':
            self._read_identifier()
            return
        
        # Если ничего не подошло - ошибка
        raise LexerError(f"Неожиданный символ '{char}'", self.line, self.column)
    
    def _current_char(self) -> str:
        if self.position >= len(self.source):
            return '\0'
        return self.source[self.position]
    
    def _peek_char(self, offset: int = 1) -> str:
        pos = self.position + offset
        if pos >= len(self.source):
            return '\0'
        return self.source[pos]
    
    def _advance(self, count: int = 1):
        for _ in range(count):
            if self._current_char() == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.position += 1
    
    def _add_token(self, token_type: TokenType, value: str, length: int):
        token = Token(
            type=token_type,
            value=value,
            line=self.line,
            column=self.column,
            length=length
        )
        self.tokens.append(token)
        self._advance(length)
    
    def _skip_whitespace(self):
        start_line = self.line
        start_col = self.column
        
        while self.position < len(self.source) and self._current_char().isspace():
            if self._current_char() == '\n':
                pass
            self._advance()
    
    def _skip_line_comment(self):
        comment = ""
        start_line = self.line
        start_col = self.column
        
        # Пропускаем //
        self._advance(2)
        
        while self.position < len(self.source) and self._current_char() != '\n':
            comment += self._current_char()
            self._advance()
        
        self.tokens.append(Token(
            type=TokenType.COMMENT,
            value=comment.strip(),
            line=start_line,
            column=start_col,
            length=len(comment) + 2
        ))
    
    def _skip_church_comment(self):
        comment = ""
        start_line = self.line
        start_col = self.column
        is_double_colon = self._current_char() == ':'
        
        # Пропускаем символы комментария
        self._advance(2 if is_double_colon else 1)
        
        while self.position < len(self.source) and self._current_char() != '\n':
            comment += self._current_char()
            self._advance()
        
        self.tokens.append(Token(
            type=TokenType.COMMENT,
            value=comment.strip(),
            line=start_line,
            column=start_col,
            length=len(comment) + (2 if is_double_colon else 1)
        ))
    
    def _read_string(self):
        start_line = self.line
        start_col = self.column
        string_value = ""
        
        self._advance()
        
        while self.position < len(self.source) and self._current_char() != '"':
            if self._current_char() == '\\':
                self._advance()
                if self._current_char() == 'n':
                    string_value += '\n'
                elif self._current_char() == 't':
                    string_value += '\t'
                elif self._current_char() == '"':
                    string_value += '"'
                elif self._current_char() == '\\':
                    string_value += '\\'
                else:
                    string_value += self._current_char()
            else:
                string_value += self._current_char()
            self._advance()
        
        if self.position >= len(self.source):
            raise LexerError("Незакрытая строка", start_line, start_col)
        
        self._advance()
        
        self.tokens.append(Token(
            type=TokenType.STRING,
            value=string_value,
            line=start_line,
            column=start_col,
            length=len(string_value) + 2
        ))
    
    def _read_number(self):
        start_line = self.line
        start_col = self.column
        num_value = ""
        is_float = False
        
        while self.position < len(self.source):
            char = self._current_char()
            if char.isdigit():
                num_value += char
            elif char == '.' and not is_float:
                if self._peek_char().isdigit():
                    num_value += char
                    is_float = True
                else:
                    break
            else:
                break
            self._advance()
        
        token_type = TokenType.FLOAT if is_float else TokenType.INTEGER
        self.tokens.append(Token(
            type=token_type,
            value=num_value,
            line=start_line,
            column=start_col,
            length=len(num_value)
        ))
    
    def _read_identifier(self):
        start_line = self.line
        start_col = self.column
        identifier = ""
        
        while self.position < len(self.source):
            char = self._current_char()
            if char.isalnum() or char == '_':
                identifier += char
                self._advance()
            else:
                break
        
        token_type = self.keywords.get(identifier.lower(), TokenType.IDENTIFIER)
        
        self.tokens.append(Token(
            type=token_type,
            value=identifier,
            line=start_line,
            column=start_col,
            length=len(identifier)
        ))
    
    def get_token_names(self) -> Dict[TokenType, str]:
        return {
            TokenType.AZ: "АЗЪ",
            TokenType.RECHE: "РЕЧЕ", 
            TokenType.YESM: "ЕСМЬ",
            TokenType.TOGDA: "ТОГДА",
            TokenType.ILIZHE: "ИЛИЖЕ",
            TokenType.INACHE: "ИНАЧЕ",
            TokenType.POKONCHI: "ПОКОНЧИ",
            TokenType.DOKOLE: "ДОКОЛЕ",
            TokenType.TVORI: "ТВОРИ",
            TokenType.DLYA: "ДЛЯ",
            TokenType.DO: "ДО",
            TokenType.SHAG: "ШАГ",
            TokenType.VOZVRATI: "ВОЗВРАТИ",
            TokenType.GLAGOLI: "ГЛАГОЛИ",
            TokenType.VNEMLI: "ВНЕМЛИ",
            TokenType.VKLUCHI: "ВКЛЮЧИ",
            TokenType.POMILUY: "ПОМИЛУЙ",
            TokenType.CHISLO: "ЧИСЛО",
            TokenType.DROB: "ДРОБЬ",
            TokenType.SLOVO: "СЛОВО",
            TokenType.ISTINA: "ИСТИНА",
            TokenType.LOZH: "ЛОЖЬ",
            TokenType.NICHTO: "НИЧТО",
            TokenType.RAVNO: "РАВНО",
            TokenType.NERAVNO: "НЕРАВНО",
            TokenType.BOLEE: "БОЛЕЕ",
            TokenType.MENEE: "МЕНЕЕ",
            TokenType.I: "И",
            TokenType.ILI: "ИЛИ",
            TokenType.NE: "НЕ",
            TokenType.IDENTIFIER: "ИМЯ",
            TokenType.INTEGER: "ЦЕЛОЕ",
            TokenType.FLOAT: "ДРОБНОЕ",
            TokenType.STRING: "СТРОКА",
            TokenType.COMMENT: "ПРИМЕЧАНИЕ",
            TokenType.EOF: "КОНЕЦ",
        }


def print_tokens(tokens: List[Token], lexer: BlagoglagolLexer):
    token_names = lexer.get_token_names()
    
    print("\n" + "=" * 80)
    print(f"{'ТИП':<15} {'ЗНАЧЕНИЕ':<20} {'СТРОКА':<8} {'ПОЗИЦИЯ':<8}")
    print("=" * 80)
    
    for token in tokens:
        type_name = token_names.get(token.type, token.type.name)
        
        if token.type == TokenType.STRING:
            value = f'"{token.value}"'
        elif token.type == TokenType.COMMENT:
            value = f"# {token.value}"
        elif token.type == TokenType.EOF:
            value = "<EOF>"
        else:
            value = token.value
        
        print(f"{type_name:<15} {value:<20} {token.line:<8} {token.column:<8}")
    
    print("=" * 80)


if __name__ == "__main__":
    test_code = """
    глаголи "День первый: Да будет свет!"
    """
    
    lexer = BlagoglagolLexer(test_code)
    
    try:
        tokens = lexer.tokenize()
        print_tokens(tokens, lexer)
        print(f"\n Всего токенов: {len(tokens)}")
    except LexerError as e:
        print(f"\n {e}")