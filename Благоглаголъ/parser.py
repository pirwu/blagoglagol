from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union
from lexer import BlagoglagolLexer, Token, TokenType, LexerError

class ASTNodeType(Enum):
    PROGRAM = auto()
    
    # Объявления
    VARIABLE_DECLARATION = auto()
    FUNCTION_DECLARATION = auto()
    PARAMETER = auto()
    
    # Операторы
    BLOCK = auto()
    ASSIGNMENT = auto()
    IF_STATEMENT = auto()
    WHILE_LOOP = auto()
    FOR_LOOP = auto()
    RETURN_STATEMENT = auto()
    PRINT_STATEMENT = auto()
    INPUT_STATEMENT = auto()
    EXPRESSION_STATEMENT = auto()
    
    # Выражения
    BINARY_OPERATION = auto()
    UNARY_OPERATION = auto()
    FUNCTION_CALL = auto()
    VARIABLE = auto()
    
    # Литералы
    INTEGER_LITERAL = auto()
    FLOAT_LITERAL = auto()
    STRING_LITERAL = auto()
    BOOLEAN_LITERAL = auto()
    
    # Специальные
    INCLUDE = auto()
    TYPE_REFERENCE = auto()


@dataclass
class ASTNode:
    type: ASTNodeType
    line: int
    column: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.name,
            "line": self.line,
            "column": self.column
        }


@dataclass
class TypeNode(ASTNode):
    type_name: str
    
    def __init__(self, type_name: str, line: int, column: int):
        super().__init__(ASTNodeType.TYPE_REFERENCE, line, column)
        self.type_name = type_name
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["type_name"] = self.type_name
        return result


@dataclass
class IntegerLiteral(ASTNode):
    value: int
    
    def __init__(self, value: int, line: int, column: int):
        super().__init__(ASTNodeType.INTEGER_LITERAL, line, column)
        self.value = value
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["value"] = self.value
        return result


@dataclass
class FloatLiteral(ASTNode):
    value: float
    
    def __init__(self, value: float, line: int, column: int):
        super().__init__(ASTNodeType.FLOAT_LITERAL, line, column)
        self.value = value
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["value"] = self.value
        return result


@dataclass
class StringLiteral(ASTNode):
    value: str
    
    def __init__(self, value: str, line: int, column: int):
        super().__init__(ASTNodeType.STRING_LITERAL, line, column)
        self.value = value
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["value"] = self.value
        return result


@dataclass
class BooleanLiteral(ASTNode):
    value: bool
    
    def __init__(self, value: bool, line: int, column: int):
        super().__init__(ASTNodeType.BOOLEAN_LITERAL, line, column)
        self.value = value
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["value"] = self.value
        return result


@dataclass
class Variable(ASTNode):
    name: str
    
    def __init__(self, name: str, line: int, column: int):
        super().__init__(ASTNodeType.VARIABLE, line, column)
        self.name = name
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["name"] = self.name
        return result


@dataclass
class BinaryOperation(ASTNode):
    operator: str
    left: ASTNode
    right: ASTNode
    
    def __init__(self, operator: str, left: ASTNode, right: ASTNode, line: int, column: int):
        super().__init__(ASTNodeType.BINARY_OPERATION, line, column)
        self.operator = operator
        self.left = left
        self.right = right
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["operator"] = self.operator
        result["left"] = self.left.to_dict()
        result["right"] = self.right.to_dict()
        return result


@dataclass
class UnaryOperation(ASTNode):
    operator: str
    operand: ASTNode
    
    def __init__(self, operator: str, operand: ASTNode, line: int, column: int):
        super().__init__(ASTNodeType.UNARY_OPERATION, line, column)
        self.operator = operator
        self.operand = operand
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["operator"] = self.operator
        result["operand"] = self.operand.to_dict()
        return result


@dataclass
class FunctionCall(ASTNode):
    name: str
    arguments: List[ASTNode]
    
    def __init__(self, name: str, arguments: List[ASTNode], line: int, column: int):
        super().__init__(ASTNodeType.FUNCTION_CALL, line, column)
        self.name = name
        self.arguments = arguments
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["name"] = self.name
        result["arguments"] = [arg.to_dict() for arg in self.arguments]
        return result


@dataclass
class VariableDeclaration(ASTNode):
    var_type: TypeNode
    name: str
    initializer: Optional[ASTNode] = None
    
    def __init__(self, var_type: TypeNode, name: str, initializer: Optional[ASTNode], 
                 line: int, column: int):
        super().__init__(ASTNodeType.VARIABLE_DECLARATION, line, column)
        self.var_type = var_type
        self.name = name
        self.initializer = initializer
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["var_type"] = self.var_type.to_dict()
        result["name"] = self.name
        if self.initializer:
            result["initializer"] = self.initializer.to_dict()
        return result


@dataclass
class Assignment(ASTNode):
    name: str
    value: ASTNode
    
    def __init__(self, name: str, value: ASTNode, line: int, column: int):
        super().__init__(ASTNodeType.ASSIGNMENT, line, column)
        self.name = name
        self.value = value
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["name"] = self.name
        result["value"] = self.value.to_dict()
        return result


@dataclass
class Block(ASTNode):
    statements: List[ASTNode] = field(default_factory=list)
    
    def __init__(self, statements: List[ASTNode], line: int, column: int):
        super().__init__(ASTNodeType.BLOCK, line, column)
        self.statements = statements
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["statements"] = [stmt.to_dict() for stmt in self.statements]
        return result


@dataclass
class IfStatement(ASTNode):
    condition: ASTNode
    then_branch: ASTNode
    elif_branches: List[tuple[ASTNode, ASTNode]] = field(default_factory=list)
    else_branch: Optional[ASTNode] = None
    
    def __init__(self, condition: ASTNode, then_branch: ASTNode, 
                 elif_branches: List[tuple[ASTNode, ASTNode]], 
                 else_branch: Optional[ASTNode], line: int, column: int):
        super().__init__(ASTNodeType.IF_STATEMENT, line, column)
        self.condition = condition
        self.then_branch = then_branch
        self.elif_branches = elif_branches
        self.else_branch = else_branch
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["condition"] = self.condition.to_dict()
        result["then_branch"] = self.then_branch.to_dict()
        if self.elif_branches:
            result["elif_branches"] = [
                {"condition": cond.to_dict(), "body": body.to_dict()}
                for cond, body in self.elif_branches
            ]
        if self.else_branch:
            result["else_branch"] = self.else_branch.to_dict()
        return result


@dataclass
class WhileLoop(ASTNode):
    condition: ASTNode
    body: ASTNode
    
    def __init__(self, condition: ASTNode, body: ASTNode, line: int, column: int):
        super().__init__(ASTNodeType.WHILE_LOOP, line, column)
        self.condition = condition
        self.body = body
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["condition"] = self.condition.to_dict()
        result["body"] = self.body.to_dict()
        return result


@dataclass
class ForLoop(ASTNode):
    variable: str
    start: ASTNode
    end: ASTNode
    step: Optional[ASTNode]
    body: ASTNode
    
    def __init__(self, variable: str, start: ASTNode, end: ASTNode, 
                 step: Optional[ASTNode], body: ASTNode, line: int, column: int):
        super().__init__(ASTNodeType.FOR_LOOP, line, column)
        self.variable = variable
        self.start = start
        self.end = end
        self.step = step
        self.body = body
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["variable"] = self.variable
        result["start"] = self.start.to_dict()
        result["end"] = self.end.to_dict()
        if self.step:
            result["step"] = self.step.to_dict()
        result["body"] = self.body.to_dict()
        return result


@dataclass
class ReturnStatement(ASTNode):
    value: Optional[ASTNode] = None
    
    def __init__(self, value: Optional[ASTNode], line: int, column: int):
        super().__init__(ASTNodeType.RETURN_STATEMENT, line, column)
        self.value = value
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        if self.value:
            result["value"] = self.value.to_dict()
        return result


@dataclass
class PrintStatement(ASTNode):
    arguments: List[ASTNode]
    
    def __init__(self, arguments: List[ASTNode], line: int, column: int):
        super().__init__(ASTNodeType.PRINT_STATEMENT, line, column)
        self.arguments = arguments
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["arguments"] = [arg.to_dict() for arg in self.arguments]
        return result


@dataclass
class InputStatement(ASTNode):
    prompt: Optional[ASTNode] = None
    
    def __init__(self, prompt: Optional[ASTNode], line: int, column: int):
        super().__init__(ASTNodeType.INPUT_STATEMENT, line, column)
        self.prompt = prompt
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        if self.prompt:
            result["prompt"] = self.prompt.to_dict()
        return result


@dataclass
class Parameter(ASTNode):
    param_type: TypeNode
    name: str
    
    def __init__(self, param_type: TypeNode, name: str, line: int, column: int):
        super().__init__(ASTNodeType.PARAMETER, line, column)
        self.param_type = param_type
        self.name = name
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["param_type"] = self.param_type.to_dict()
        result["name"] = self.name
        return result


@dataclass
class FunctionDeclaration(ASTNode):
    return_type: Optional[TypeNode]
    name: str
    parameters: List[Parameter]
    body: Block
    
    def __init__(self, return_type: Optional[TypeNode], name: str, 
                 parameters: List[Parameter], body: Block, line: int, column: int):
        super().__init__(ASTNodeType.FUNCTION_DECLARATION, line, column)
        self.return_type = return_type
        self.name = name
        self.parameters = parameters
        self.body = body
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        if self.return_type:
            result["return_type"] = self.return_type.to_dict()
        result["name"] = self.name
        result["parameters"] = [param.to_dict() for param in self.parameters]
        result["body"] = self.body.to_dict()
        return result


@dataclass
class IncludeStatement(ASTNode):
    filename: str
    
    def __init__(self, filename: str, line: int, column: int):
        super().__init__(ASTNodeType.INCLUDE, line, column)
        self.filename = filename
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["filename"] = self.filename
        return result


@dataclass
class Program(ASTNode):
    statements: List[ASTNode] = field(default_factory=list)
    
    def __init__(self, statements: List[ASTNode]):
        super().__init__(ASTNodeType.PROGRAM, 1, 1)
        self.statements = statements
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["statements"] = [stmt.to_dict() for stmt in self.statements]
        return result

class ParseError(Exception):
    def __init__(self, message: str, token: Token):
        self.message = message
        self.token = token
        super().__init__(f"Ошибка парсинга в строке {token.line}, позиция {token.column}: {message}")


class BlagoglagolParser:
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0
        self.current_token: Optional[Token] = None
        
    def parse(self) -> Program:
        self.position = 0
        self._advance()
        
        statements = []
        
        while not self._is_at_end():
            try:
                stmt = self._parse_statement()
                if stmt:
                    statements.append(stmt)
            except ParseError as e:
                print(f" {e}")
                self._synchronize()
        
        return Program(statements)
    
    def _advance(self):
        if self.position < len(self.tokens):
            self.current_token = self.tokens[self.position]
            self.position += 1
        else:
            self.current_token = None
    
    def _peek(self) -> Optional[Token]:
        return self.current_token
    
    def _peek_next(self) -> Optional[Token]:
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None
    
    def _is_at_end(self) -> bool:
        return self.current_token is None or self.current_token.type == TokenType.EOF
    
    def _check(self, token_type: TokenType) -> bool:
        if self._is_at_end():
            return False
        return self._peek().type == token_type
    
    def _match(self, *token_types: TokenType) -> bool:
        for token_type in token_types:
            if self._check(token_type):
                self._advance()
                return True
        return False
    
    def _consume(self, token_type: TokenType, error_message: str) -> Token:
        if self._check(token_type):
            token = self._peek()
            self._advance()
            return token
        
        raise ParseError(error_message, self._peek())
    
    def _synchronize(self):
        self._advance()
        
        while not self._is_at_end():
            if self._peek().type == TokenType.SEMICOLON:
                self._advance()
                return
            
            if self._peek().type in [
                TokenType.AZ, TokenType.YESM, TokenType.DOKOLE,
                TokenType.DLYA, TokenType.GLAGOLI, TokenType.VOZVRATI,
                TokenType.POKONCHI
            ]:
                return
            
            self._advance()
    
    def _parse_statement(self) -> Optional[ASTNode]:
        """Парсинг оператора"""
        token = self._peek()
        
        if self._match(TokenType.VKLUCHI):
            return self._parse_include()
        
        if self._match(TokenType.AZ):
            return self._parse_declaration()
        
        if self._check(TokenType.IDENTIFIER) and self._peek_next() and \
           self._peek_next().type == TokenType.ASSIGN:
            return self._parse_assignment()
        
        if self._match(TokenType.YESM):
            return self._parse_if_statement()
        
        if self._match(TokenType.DOKOLE):
            return self._parse_while_loop()
        
        if self._match(TokenType.DLYA):
            return self._parse_for_loop()
        
        if self._match(TokenType.VOZVRATI):
            return self._parse_return()
        
        if self._match(TokenType.GLAGOLI):
            return self._parse_print()
        
        if self._match(TokenType.VNEMLI):
            return self._parse_input()
        
        if self._match(TokenType.LBRACE):
            return self._parse_block()
        
        if self._check(TokenType.IDENTIFIER):
            expr = self._parse_expression()
            self._consume(TokenType.SEMICOLON, "Ожидалась ';' после выражения")
            return expr
        
        if self._match(TokenType.SEMICOLON):
            return None
        
        raise ParseError(f"Неожиданный токен '{token.value}'", token)
    
    def _parse_include(self) -> IncludeStatement:
        token = self._peek()
        filename_token = self._consume(TokenType.STRING, "Ожидалось имя файла в кавычках")
        self._consume(TokenType.SEMICOLON, "Ожидалась ';' после включения")
        
        return IncludeStatement(filename_token.value, token.line, token.column)
    
    def _parse_declaration(self) -> ASTNode:
        self._consume(TokenType.RECHE, "Ожидалось 'рече' после 'азъ'")
        
        token = self._peek()
        
        return_type = None
        if self._check(TokenType.CHISLO) or self._check(TokenType.DROB) or \
           self._check(TokenType.SLOVO) or self._check(TokenType.NICHTO):
            return_type = self._parse_type()
        
        name_token = self._consume(TokenType.IDENTIFIER, "Ожидалось имя переменной или функции")
        
        if self._match(TokenType.LPAREN):
            return self._parse_function_rest(return_type, name_token)
        
        return self._parse_variable_rest(return_type, name_token)
    
    def _parse_variable_rest(self, var_type: TypeNode, name_token: Token) -> VariableDeclaration:
        initializer = None
        
        if self._match(TokenType.ASSIGN) or self._match(TokenType.EQ):
            initializer = self._parse_expression()
        
        self._consume(TokenType.SEMICOLON, "Ожидалась ';' после объявления переменной")
        
        return VariableDeclaration(
            var_type, 
            name_token.value, 
            initializer,
            name_token.line, 
            name_token.column
        )
    
    def _parse_function_rest(self, return_type: Optional[TypeNode], 
                             name_token: Token) -> FunctionDeclaration:
        parameters = []
        
        if not self._check(TokenType.RPAREN):
            parameters = self._parse_parameters()
        
        self._consume(TokenType.RPAREN, "Ожидалась ')' после параметров")
        
        body = self._parse_block()
        
        return FunctionDeclaration(
            return_type,
            name_token.value,
            parameters,
            body,
            name_token.line,
            name_token.column
        )
    
    def _parse_parameters(self) -> List[Parameter]:
        parameters = []
        
        while not self._check(TokenType.RPAREN) and not self._is_at_end():
            param_type = self._parse_type()
            param_name = self._consume(TokenType.IDENTIFIER, "Ожидалось имя параметра")
            
            parameters.append(Parameter(
                param_type,
                param_name.value,
                param_name.line,
                param_name.column
            ))
            
            if not self._match(TokenType.COMMA):
                break
        
        return parameters
    
    def _parse_type(self) -> TypeNode:
        token = self._peek()
        
        if self._match(TokenType.CHISLO, TokenType.DROB, TokenType.SLOVO, TokenType.NICHTO):
            return TypeNode(token.value, token.line, token.column)
        
        raise ParseError("Ожидался тип данных (число, дробь, слово, ничто)", token)
    
    def _parse_assignment(self) -> Assignment:
        name_token = self._consume(TokenType.IDENTIFIER, "Ожидалось имя переменной")
        self._consume(TokenType.ASSIGN, "Ожидалось ':='")
        
        value = self._parse_expression()
        self._consume(TokenType.SEMICOLON, "Ожидалась ';' после присваивания")
        
        return Assignment(name_token.value, value, name_token.line, name_token.column)
    
    def _parse_if_statement(self) -> IfStatement:
        token = self._peek()
        condition = self._parse_expression()
        
        self._consume(TokenType.TOGDA, "Ожидалось 'тогда'")
        
        then_branch = self._parse_statement_or_block()
        
        elif_branches = []
        else_branch = None
        
        while self._match(TokenType.ILIZHE):
            elif_condition = self._parse_expression()
            self._consume(TokenType.TOGDA, "Ожидалось 'тогда'")
            elif_body = self._parse_statement_or_block()
            elif_branches.append((elif_condition, elif_body))
        
        if self._match(TokenType.INACHE):
            else_branch = self._parse_statement_or_block()
        
        self._consume(TokenType.POKONCHI, "Ожидалось 'покончи'")
        
        return IfStatement(
            condition, then_branch, elif_branches, else_branch,
            token.line, token.column
        )
    
    def _parse_while_loop(self) -> WhileLoop:
        token = self._peek()
        condition = self._parse_expression()
        
        self._consume(TokenType.TVORI, "Ожидалось 'твори'")
        
        body = self._parse_statement_or_block()
        self._consume(TokenType.POKONCHI, "Ожидалось 'покончи'")
        
        return WhileLoop(condition, body, token.line, token.column)
    
    def _parse_for_loop(self) -> ForLoop:
        token = self._peek()
        
        var_token = self._consume(TokenType.IDENTIFIER, "Ожидалось имя переменной")
        self._consume(TokenType.ASSIGN, "Ожидалось ':='")
        
        start = self._parse_expression()
        self._consume(TokenType.DO, "Ожидалось 'до'")
        
        end = self._parse_expression()
        
        step = None
        if self._match(TokenType.SHAG):
            step = self._parse_expression()
        
        self._consume(TokenType.TVORI, "Ожидалось 'твори'")
        
        body = self._parse_statement_or_block()
        self._consume(TokenType.POKONCHI, "Ожидалось 'покончи'")
        
        return ForLoop(
            var_token.value, start, end, step, body,
            token.line, token.column
        )
    
    def _parse_return(self) -> ReturnStatement:
        token = self._peek()
        value = None
        
        if not self._check(TokenType.SEMICOLON):
            value = self._parse_expression()
        
        self._consume(TokenType.SEMICOLON, "Ожидалась ';' после возврата")
        
        return ReturnStatement(value, token.line, token.column)
    
    def _parse_print(self) -> PrintStatement:
        token = self._peek()
        arguments = []
        
        if not self._check(TokenType.SEMICOLON):
            arguments = self._parse_argument_list()
        
        self._consume(TokenType.SEMICOLON, "Ожидалась ';' после вывода")
        
        return PrintStatement(arguments, token.line, token.column)
    
    def _parse_input(self) -> InputStatement:
        token = self._peek()
        prompt = None
        
        if self._match(TokenType.LPAREN):
            if not self._check(TokenType.RPAREN):
                prompt = self._parse_expression()
            self._consume(TokenType.RPAREN, "Ожидалась ')'")
        
        self._consume(TokenType.SEMICOLON, "Ожидалась ';' после ввода")
        
        return InputStatement(prompt, token.line, token.column)
    
    def _parse_block(self) -> Block:
        token = self._peek()
        statements = []
        
        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)
        
        self._consume(TokenType.RBRACE, "Ожидалась '}'")
        
        return Block(statements, token.line, token.column)
    
    def _parse_statement_or_block(self) -> ASTNode:
        if self._match(TokenType.LBRACE):
            return self._parse_block()
        else:
            return self._parse_statement()
    
    def _parse_argument_list(self) -> List[ASTNode]:
        arguments = []
        
        while not self._check(TokenType.SEMICOLON) and not self._is_at_end():
            arguments.append(self._parse_expression())
            
            if not self._match(TokenType.COMMA):
                break
        
        return arguments
    
    def _parse_expression(self) -> ASTNode:
        return self._parse_logical_or()
    
    def _parse_logical_or(self) -> ASTNode:
        expr = self._parse_logical_and()
        
        while self._match(TokenType.ILI, TokenType.OR):
            operator = self._peek().value if self._peek() else "или"
            right = self._parse_logical_and()
            expr = BinaryOperation(operator, expr, right, expr.line, expr.column)
        
        return expr
    
    def _parse_logical_and(self) -> ASTNode:
        expr = self._parse_comparison()
        
        while self._match(TokenType.I, TokenType.AND):
            operator = self._peek().value if self._peek() else "и"
            right = self._parse_comparison()
            expr = BinaryOperation(operator, expr, right, expr.line, expr.column)
        
        return expr
    
    def _parse_comparison(self) -> ASTNode:
        expr = self._parse_addition()
        
        while self._match(TokenType.RAVNO, TokenType.EQ,
                         TokenType.NERAVNO, TokenType.NEQ,
                         TokenType.BOLEE, TokenType.GT,
                         TokenType.MENEE, TokenType.LT):
            token = self._peek()
            operator = token.value if token else "=="
            right = self._parse_addition()
            expr = BinaryOperation(operator, expr, right, expr.line, expr.column)
        
        return expr
    
    def _parse_addition(self) -> ASTNode:
        expr = self._parse_multiplication()
        
        while self._match(TokenType.PLUS, TokenType.MINUS):
            token = self._peek()
            operator = token.value if token else "+"
            right = self._parse_multiplication()
            expr = BinaryOperation(operator, expr, right, expr.line, expr.column)
        
        return expr
    
    def _parse_multiplication(self) -> ASTNode:
        expr = self._parse_unary()
        
        while self._match(TokenType.STAR, TokenType.SLASH):
            token = self._peek()
            operator = token.value if token else "*"
            right = self._parse_unary()
            expr = BinaryOperation(operator, expr, right, expr.line, expr.column)
        
        return expr
    
    def _parse_unary(self) -> ASTNode:
        token = self._peek()
        
        if self._match(TokenType.MINUS, TokenType.NE, TokenType.NOT):
            operator = token.value if token else "-"
            operand = self._parse_unary()
            return UnaryOperation(operator, operand, token.line, token.column)
        
        return self._parse_primary()
    
    def _parse_primary(self) -> ASTNode:
        token = self._peek()
        
        # Числа
        if self._match(TokenType.INTEGER):
            return IntegerLiteral(int(token.value), token.line, token.column)
        
        if self._match(TokenType.FLOAT):
            return FloatLiteral(float(token.value), token.line, token.column)
        
        # Строки
        if self._match(TokenType.STRING):
            return StringLiteral(token.value, token.line, token.column)
        
        # Булевы значения
        if self._match(TokenType.ISTINA):
            return BooleanLiteral(True, token.line, token.column)
        
        if self._match(TokenType.LOZH):
            return BooleanLiteral(False, token.line, token.column)
        
        # Скобки
        if self._match(TokenType.LPAREN):
            expr = self._parse_expression()
            self._consume(TokenType.RPAREN, "Ожидалась ')'")
            return expr
        
        # Идентификатор (переменная или вызов функции)
        if self._check(TokenType.IDENTIFIER):
            name_token = self._consume(TokenType.IDENTIFIER, "")
            
            # Проверяем вызов функции
            if self._match(TokenType.LPAREN):
                arguments = []
                
                if not self._check(TokenType.RPAREN):
                    arguments = self._parse_expression_list()
                
                self._consume(TokenType.RPAREN, "Ожидалась ')' после аргументов")
                return FunctionCall(name_token.value, arguments, name_token.line, name_token.column)
            
            # Обычная переменная
            return Variable(name_token.value, name_token.line, name_token.column)
        
        raise ParseError(f"Ожидалось выражение, получен '{token.value}'", token)
    
    def _parse_expression_list(self) -> List[ASTNode]:
        expressions = []
        
        while not self._check(TokenType.RPAREN) and not self._is_at_end():
            expressions.append(self._parse_expression())
            
            if not self._match(TokenType.COMMA):
                break
        
        return expressions

def print_ast(node: ASTNode, indent: int = 0, prefix: str = ""):
    indent_str = "  " * indent
    
    if isinstance(node, Program):
        print(f"{indent_str} Программа")
        for stmt in node.statements:
            print_ast(stmt, indent + 1)
    
    elif isinstance(node, IncludeStatement):
        print(f"{indent_str} Включить '{node.filename}'")
    
    elif isinstance(node, VariableDeclaration):
        init_str = f" = ..." if node.initializer else ""
        print(f"{indent_str} Переменная: {node.name}: {node.var_type.type_name}{init_str}")
        if node.initializer:
            print_ast(node.initializer, indent + 1, "↳ ")
    
    elif isinstance(node, Assignment):
        print(f"{indent_str}  Присваивание: {node.name} :=")
        print_ast(node.value, indent + 1)
    
    elif isinstance(node, IfStatement):
        print(f"{indent_str} Если:")
        print(f"{indent_str}  Условие:")
        print_ast(node.condition, indent + 2)
        print(f"{indent_str}  Тогда:")
        print_ast(node.then_branch, indent + 2)
        
        for i, (cond, body) in enumerate(node.elif_branches):
            print(f"{indent_str}  ИлиЖе {i + 1}:")
            print_ast(cond, indent + 3)
            print_ast(body, indent + 3)
        
        if node.else_branch:
            print(f"{indent_str}  Иначе:")
            print_ast(node.else_branch, indent + 2)
    
    elif isinstance(node, WhileLoop):
        print(f"{indent_str} Цикл Доколе:")
        print(f"{indent_str}  Условие:")
        print_ast(node.condition, indent + 2)
        print(f"{indent_str}  Твори:")
        print_ast(node.body, indent + 2)
    
    elif isinstance(node, ForLoop):
        step_str = f" шаг {node.step.value}" if hasattr(node.step, 'value') else ""
        print(f"{indent_str} Цикл Для: {node.variable} от ... до ...{step_str}")
        print_ast(node.start, indent + 1, "↳ начало: ")
        print_ast(node.end, indent + 1, "↳ конец: ")
        if node.step:
            print_ast(node.step, indent + 1, "↳ шаг: ")
        print_ast(node.body, indent + 1, "↳ тело: ")
    
    elif isinstance(node, ReturnStatement):
        print(f"{indent_str}↩️  Возврат")
        if node.value:
            print_ast(node.value, indent + 1)
    
    elif isinstance(node, PrintStatement):
        print(f"{indent_str}  Глаголи")
        for arg in node.arguments:
            print_ast(arg, indent + 1)
    
    elif isinstance(node, Block):
        print(f"{indent_str} Блок:")
        for stmt in node.statements:
            print_ast(stmt, indent + 1)
    
    elif isinstance(node, FunctionDeclaration):
        ret_str = f": {node.return_type.type_name}" if node.return_type else ""
        print(f"{indent_str} Служба: {node.name}{ret_str}")
        if node.parameters:
            print(f"{indent_str}  Параметры:")
            for param in node.parameters:
                print(f"{indent_str}    - {param.name}: {param.param_type.type_name}")
        print(f"{indent_str}  Тело:")
        print_ast(node.body, indent + 2)
    
    elif isinstance(node, FunctionCall):
        print(f"{indent_str} Вызов: {node.name}()")
        for i, arg in enumerate(node.arguments):
            print_ast(arg, indent + 1, f"↳ арг{i+1}: ")
    
    elif isinstance(node, BinaryOperation):
        print(f"{indent_str} {prefix}{node.operator}")
        print_ast(node.left, indent + 1, "↳ лев: ")
        print_ast(node.right, indent + 1, "↳ прав: ")
    
    elif isinstance(node, UnaryOperation):
        print(f"{indent_str} {prefix}{node.operator}")
        print_ast(node.operand, indent + 1)
    
    elif isinstance(node, IntegerLiteral):
        print(f"{indent_str} {prefix}{node.value}")
    
    elif isinstance(node, FloatLiteral):
        print(f"{indent_str} {prefix}{node.value}")
    
    elif isinstance(node, StringLiteral):
        print(f"{indent_str} {prefix}\"{node.value}\"")
    
    elif isinstance(node, BooleanLiteral):
        print(f"{indent_str}✓ {prefix}{'истина' if node.value else 'ложь'}")
    
    elif isinstance(node, Variable):
        print(f"{indent_str} {prefix}{node.name}")
    
    else:
        print(f"{indent_str} {prefix}{type(node).__name__}")

if __name__ == "__main__":
    test_code = """
    глаголи "Во имя Отца, и Сына, и Святаго Духа!"
    """
    
    print("=" * 80)
    print("ЛЕКСИЧЕСКИЙ АНАЛИЗ")
    print("=" * 80)
    
    lexer = BlagoglagolLexer(test_code)
    tokens = lexer.tokenize()
    
    print("\n" + "=" * 80)
    print("СИНТАКСИЧЕСКИЙ АНАЛИЗ (AST)")
    print("=" * 80)
    
    parser = BlagoglagolParser(tokens)
    
    try:
        ast = parser.parse()
        print_ast(ast)
        print("\nПарсинг успешно завершён!")
        
    except ParseError as e:
        print(f"\n {e}")
    except Exception as e:
        print(f"\n Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()