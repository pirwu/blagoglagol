import math
import sys
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from enum import Enum

from parser import (
    ASTNode, Program, IncludeStatement, VariableDeclaration,
    Assignment, IfStatement, WhileLoop, ForLoop, ReturnStatement,
    PrintStatement, InputStatement, Block, FunctionDeclaration,
    FunctionCall, BinaryOperation, UnaryOperation, IntegerLiteral,
    FloatLiteral, StringLiteral, BooleanLiteral, Variable,
    TypeNode, Parameter
)

class RuntimeType(Enum):
    INTEGER = "число"
    FLOAT = "дробь"
    STRING = "слово"
    BOOLEAN = "истина"
    VOID = "ничто"
    FUNCTION = "служба"


@dataclass
class RuntimeValue:
    type: RuntimeType
    value: Any
    
    def __str__(self):
        if self.type == RuntimeType.STRING:
            return self.value
        elif self.type == RuntimeType.BOOLEAN:
            return "истина" if self.value else "ложь"
        else:
            return str(self.value)
    
    def to_python(self) -> Any:
        return self.value
    
    def is_truthy(self) -> bool:
        if self.type == RuntimeType.BOOLEAN:
            return self.value
        elif self.type == RuntimeType.INTEGER:
            return self.value != 0
        elif self.type == RuntimeType.FLOAT:
            return self.value != 0.0
        elif self.type == RuntimeType.STRING:
            return len(self.value) > 0
        return bool(self.value)


@dataclass
class FunctionValue:
    declaration: FunctionDeclaration
    closure: 'Environment'
    
    def __str__(self):
        return f"<служба {self.declaration.name}>"

class Environment:
    def __init__(self, parent: Optional['Environment'] = None):
        self.parent = parent
        self.variables: Dict[str, RuntimeValue] = {}
        self.functions: Dict[str, FunctionValue] = {}
    
    def define(self, name: str, value: RuntimeValue):
        self.variables[name] = value
    
    def define_function(self, name: str, func: FunctionValue):
        self.functions[name] = func
    
    def assign(self, name: str, value: RuntimeValue):
        if name in self.variables:
            self.variables[name] = value
        elif self.parent:
            self.parent.assign(name, value)
        else:
            raise RuntimeError(f"Переменная '{name}' не объявлена")
    
    def get(self, name: str) -> RuntimeValue:
        if name in self.variables:
            return self.variables[name]
        elif self.parent:
            return self.parent.get(name)
        else:
            raise RuntimeError(f"Переменная '{name}' не объявлена")
    
    def get_function(self, name: str) -> FunctionValue:
        if name in self.functions:
            return self.functions[name]
        elif self.parent:
            return self.parent.get_function(name)
        else:
            raise RuntimeError(f"Служба '{name}' не объявлена")
    
    def has_function(self, name: str) -> bool:
        if name in self.functions:
            return True
        elif self.parent:
            return self.parent.has_function(name)
        return False

class InterpreterError(Exception):
    def __init__(self, message: str, node: Optional[ASTNode] = None):
        self.message = message
        self.node = node
        location = f" (строка {node.line}, позиция {node.column})" if node else ""
        super().__init__(f"Ошибка выполнения{location}: {message}")


class ReturnException(Exception):
    def __init__(self, value: RuntimeValue):
        self.value = value


class BlagoglagolInterpreter:
    
    def __init__(self):
        self.global_env = Environment()
        self.current_env = self.global_env
        self.imported_files: set = set()
        
        # Регистрируем встроенные функции
        self._register_builtins()
    
    def interpret(self, program: Program):
        try:
            for statement in program.statements:
                self._execute(statement)
        except ReturnException:
            pass
        except InterpreterError as e:
            print(f" {e}", file=sys.stderr)
            sys.exit(1)
    
    def _execute(self, node: ASTNode) -> Optional[RuntimeValue]:
        if isinstance(node, IncludeStatement):
            return self._execute_include(node)
        elif isinstance(node, VariableDeclaration):
            return self._execute_variable_declaration(node)
        
        elif isinstance(node, FunctionDeclaration):
            return self._execute_function_declaration(node)
        elif isinstance(node, Assignment):
            return self._execute_assignment(node)
        
        elif isinstance(node, IfStatement):
            return self._execute_if(node)
        
        elif isinstance(node, WhileLoop):
            return self._execute_while(node)
        
        elif isinstance(node, ForLoop):
            return self._execute_for(node)
        
        elif isinstance(node, ReturnStatement):
            return self._execute_return(node)
        
        elif isinstance(node, PrintStatement):
            return self._execute_print(node)
        
        elif isinstance(node, InputStatement):
            return self._execute_input(node)
        
        elif isinstance(node, Block):
            return self._execute_block(node)
        elif isinstance(node, FunctionCall):
            return self._execute_function_call(node)
        
        elif isinstance(node, BinaryOperation):
            return self._evaluate_binary(node)
        
        elif isinstance(node, UnaryOperation):
            return self._evaluate_unary(node)
        
        elif isinstance(node, IntegerLiteral):
            return RuntimeValue(RuntimeType.INTEGER, node.value)
        
        elif isinstance(node, FloatLiteral):
            return RuntimeValue(RuntimeType.FLOAT, node.value)
        
        elif isinstance(node, StringLiteral):
            return RuntimeValue(RuntimeType.STRING, node.value)
        
        elif isinstance(node, BooleanLiteral):
            return RuntimeValue(RuntimeType.BOOLEAN, node.value)
        
        elif isinstance(node, Variable):
            return self._evaluate_variable(node)
        
        else:
            raise InterpreterError(f"Неизвестный тип узла: {type(node)}", node)
    
    def _execute_include(self, node: IncludeStatement) -> None:
        filename = node.filename
        
        if filename in self.imported_files:
            return
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                source = f.read()
            
            from lexer import BlagoglagolLexer
            from parser import BlagoglagolParser
            
            lexer = BlagoglagolLexer(source)
            tokens = lexer.tokenize()
            parser = BlagoglagolParser(tokens)
            library_ast = parser.parse()
            
            for stmt in library_ast.statements:
                self._execute(stmt)
            
            self.imported_files.add(filename)
            
        except FileNotFoundError:
            raise InterpreterError(f"Книга '{filename}' не найдена", node)
        except Exception as e:
            raise InterpreterError(f"Ошибка чтения книги '{filename}': {e}", node)
    
    def _execute_variable_declaration(self, node: VariableDeclaration) -> None:
        value = RuntimeValue(RuntimeType.VOID, None)
        
        if node.initializer:
            value = self._evaluate(node.initializer)
        
        expected_type = self._type_from_string(node.var_type.type_name)
        if value.type != RuntimeType.VOID and value.type != expected_type:
            value = self._convert_type(value, expected_type, node)
        
        self.current_env.define(node.name, value)
    
    def _execute_function_declaration(self, node: FunctionDeclaration) -> None:
        func_value = FunctionValue(node, self.current_env)
        self.current_env.define_function(node.name, func_value)
    
    def _execute_assignment(self, node: Assignment) -> None:
        value = self._evaluate(node.value)
        self.current_env.assign(node.name, value)
    
    def _execute_if(self, node: IfStatement) -> None:
        condition = self._evaluate(node.condition)
        
        if condition.is_truthy():
            self._execute(node.then_branch)
        else:
            executed = False
            for elif_cond, elif_body in node.elif_branches:
                if self._evaluate(elif_cond).is_truthy():
                    self._execute(elif_body)
                    executed = True
                    break
            
            if not executed and node.else_branch:
                self._execute(node.else_branch)
    
    def _execute_while(self, node: WhileLoop) -> None:
        while self._evaluate(node.condition).is_truthy():
            try:
                self._execute(node.body)
            except BreakException:
                break
            except ContinueException:
                continue
    
    def _execute_for(self, node: ForLoop) -> None:
        start = self._evaluate(node.start)
        end = self._evaluate(node.end)
        step = RuntimeValue(RuntimeType.INTEGER, 1)
        
        if node.step:
            step = self._evaluate(node.step)
        
        if start.type not in [RuntimeType.INTEGER, RuntimeType.FLOAT]:
            raise InterpreterError("Начало цикла должно быть числом", node)
        
        if end.type not in [RuntimeType.INTEGER, RuntimeType.FLOAT]:
            raise InterpreterError("Конец цикла должен быть числом", node)
        
        current = start
        self.current_env.define(node.variable, current)
        
        while True:
            if step.value > 0 and current.value > end.value:
                break
            if step.value < 0 and current.value < end.value:
                break
            
            try:
                self._execute(node.body)
            except BreakException:
                break
            except ContinueException:
                pass
            
            if current.type == RuntimeType.INTEGER:
                current = RuntimeValue(RuntimeType.INTEGER, current.value + step.value)
            else:
                current = RuntimeValue(RuntimeType.FLOAT, current.value + step.value)
            
            self.current_env.assign(node.variable, current)
    
    def _execute_return(self, node: ReturnStatement) -> None:
        value = RuntimeValue(RuntimeType.VOID, None)
        if node.value:
            value = self._evaluate(node.value)
        
        raise ReturnException(value)
    
    def _execute_print(self, node: PrintStatement) -> None:
        parts = []
        for arg in node.arguments:
            value = self._evaluate(arg)
            parts.append(str(value))
        
        print(" ".join(parts))
    
    def _execute_input(self, node: InputStatement) -> RuntimeValue:
        if node.prompt:
            prompt_value = self._evaluate(node.prompt)
            print(str(prompt_value), end="")
        
        user_input = sys.stdin.readline().strip()
        return RuntimeValue(RuntimeType.STRING, user_input)
    
    def _execute_block(self, node: Block) -> None:
        previous_env = self.current_env
        self.current_env = Environment(previous_env)
        
        try:
            for statement in node.statements:
                self._execute(statement)
        finally:
            self.current_env = previous_env
    
    def _execute_function_call(self, node: FunctionCall) -> RuntimeValue:
        if node.name in self.builtins:
            args = [self._evaluate(arg) for arg in node.arguments]
            return self.builtins[node.name](args, node)
        
        func_value = self.current_env.get_function(node.name)
        func_decl = func_value.declaration
        
        if len(node.arguments) != len(func_decl.parameters):
            raise InterpreterError(
                f"Служба '{node.name}' ожидает {len(func_decl.parameters)} "
                f"параметров, получено {len(node.arguments)}",
                node
            )
        
        args = [self._evaluate(arg) for arg in node.arguments]
        
        previous_env = self.current_env
        self.current_env = Environment(func_value.closure)
        
        for param, arg in zip(func_decl.parameters, args):
            expected_type = self._type_from_string(param.param_type.type_name)
            if arg.type != expected_type:
                arg = self._convert_type(arg, expected_type, node)
            
            self.current_env.define(param.name, arg)
        
        try:
            self._execute(func_decl.body)
            return RuntimeValue(RuntimeType.VOID, None)
        except ReturnException as ret:
            return ret.value
        finally:
            self.current_env = previous_env
    
    def _evaluate(self, node: ASTNode) -> RuntimeValue:
        return self._execute(node)
    
    def _evaluate_binary(self, node: BinaryOperation) -> RuntimeValue:
        left = self._evaluate(node.left)
        right = self._evaluate(node.right)
        
        operator = node.operator
       
        if operator in ['+', 'сложи']:
            return self._add(left, right, node)
        elif operator in ['-', 'отними']:
            return self._subtract(left, right, node)
        elif operator in ['*', 'умножь']:
            return self._multiply(left, right, node)
        elif operator in ['/', 'раздели']:
            return self._divide(left, right, node)
        
        elif operator in ['==', 'равно']:
            return self._equals(left, right)
        elif operator in ['!=', 'неравно']:
            return self._not_equals(left, right)
        elif operator in ['>', 'более']:
            return self._greater_than(left, right, node)
        elif operator in ['<', 'менее']:
            return self._less_than(left, right, node)
        
        elif operator in ['&&', 'и']:
            return self._logical_and(left, right)
        elif operator in ['||', 'или']:
            return self._logical_or(left, right)
        
        else:
            raise InterpreterError(f"Неизвестный оператор: {operator}", node)
    
    def _evaluate_unary(self, node: UnaryOperation) -> RuntimeValue:
        operand = self._evaluate(node.operand)
        operator = node.operator
        
        if operator in ['-', 'минус']:
            if operand.type == RuntimeType.INTEGER:
                return RuntimeValue(RuntimeType.INTEGER, -operand.value)
            elif operand.type == RuntimeType.FLOAT:
                return RuntimeValue(RuntimeType.FLOAT, -operand.value)
            else:
                raise InterpreterError(f"Нельзя применить '-' к типу {operand.type.value}", node)
        
        elif operator in ['!', 'не']:
            return RuntimeValue(RuntimeType.BOOLEAN, not operand.is_truthy())
        
        else:
            raise InterpreterError(f"Неизвестный унарный оператор: {operator}", node)
    
    def _evaluate_variable(self, node: Variable) -> RuntimeValue:
        return self.current_env.get(node.name)
    
    def _add(self, left: RuntimeValue, right: RuntimeValue, node: ASTNode) -> RuntimeValue:
        if left.type == RuntimeType.STRING or right.type == RuntimeType.STRING:
            # Конкатенация строк
            return RuntimeValue(RuntimeType.STRING, str(left) + str(right))
        
        elif left.type == RuntimeType.INTEGER and right.type == RuntimeType.INTEGER:
            return RuntimeValue(RuntimeType.INTEGER, left.value + right.value)
        
        elif left.type in [RuntimeType.INTEGER, RuntimeType.FLOAT] and \
             right.type in [RuntimeType.INTEGER, RuntimeType.FLOAT]:
            return RuntimeValue(RuntimeType.FLOAT, float(left.value) + float(right.value))
        
        else:
            raise InterpreterError(f"Нельзя сложить {left.type.value} и {right.type.value}", node)
    
    def _subtract(self, left: RuntimeValue, right: RuntimeValue, node: ASTNode) -> RuntimeValue:
        if left.type == RuntimeType.INTEGER and right.type == RuntimeType.INTEGER:
            return RuntimeValue(RuntimeType.INTEGER, left.value - right.value)
        
        elif left.type in [RuntimeType.INTEGER, RuntimeType.FLOAT] and \
             right.type in [RuntimeType.INTEGER, RuntimeType.FLOAT]:
            return RuntimeValue(RuntimeType.FLOAT, float(left.value) - float(right.value))
        
        else:
            raise InterpreterError(f"Нельзя вычесть {right.type.value} из {left.type.value}", node)
    
    def _multiply(self, left: RuntimeValue, right: RuntimeValue, node: ASTNode) -> RuntimeValue:
        if left.type == RuntimeType.INTEGER and right.type == RuntimeType.INTEGER:
            return RuntimeValue(RuntimeType.INTEGER, left.value * right.value)
        
        elif left.type in [RuntimeType.INTEGER, RuntimeType.FLOAT] and \
             right.type in [RuntimeType.INTEGER, RuntimeType.FLOAT]:
            return RuntimeValue(RuntimeType.FLOAT, float(left.value) * float(right.value))
        
        elif left.type == RuntimeType.STRING and right.type == RuntimeType.INTEGER:
            return RuntimeValue(RuntimeType.STRING, left.value * right.value)
        
        elif left.type == RuntimeType.INTEGER and right.type == RuntimeType.STRING:
            return RuntimeValue(RuntimeType.STRING, right.value * left.value)
        
        else:
            raise InterpreterError(f"Нельзя умножить {left.type.value} и {right.type.value}", node)
    
    def _divide(self, left: RuntimeValue, right: RuntimeValue, node: ASTNode) -> RuntimeValue:
        if right.value == 0:
            raise InterpreterError("Деление на ноль - грех!", node)
        
        if left.type in [RuntimeType.INTEGER, RuntimeType.FLOAT] and \
           right.type in [RuntimeType.INTEGER, RuntimeType.FLOAT]:
            return RuntimeValue(RuntimeType.FLOAT, float(left.value) / float(right.value))
        
        else:
            raise InterpreterError(f"Нельзя разделить {left.type.value} на {right.type.value}", node)
    
    def _equals(self, left: RuntimeValue, right: RuntimeValue) -> RuntimeValue:
        return RuntimeValue(RuntimeType.BOOLEAN, left.value == right.value)
    
    def _not_equals(self, left: RuntimeValue, right: RuntimeValue) -> RuntimeValue:
        return RuntimeValue(RuntimeType.BOOLEAN, left.value != right.value)
    
    def _greater_than(self, left: RuntimeValue, right: RuntimeValue, node: ASTNode) -> RuntimeValue:
        if left.type in [RuntimeType.INTEGER, RuntimeType.FLOAT] and \
           right.type in [RuntimeType.INTEGER, RuntimeType.FLOAT]:
            return RuntimeValue(RuntimeType.BOOLEAN, left.value > right.value)
        
        elif left.type == RuntimeType.STRING and right.type == RuntimeType.STRING:
            return RuntimeValue(RuntimeType.BOOLEAN, left.value > right.value)
        
        else:
            raise InterpreterError(f"Нельзя сравнить {left.type.value} и {right.type.value}", node)
    
    def _less_than(self, left: RuntimeValue, right: RuntimeValue, node: ASTNode) -> RuntimeValue:
        if left.type in [RuntimeType.INTEGER, RuntimeType.FLOAT] and \
           right.type in [RuntimeType.INTEGER, RuntimeType.FLOAT]:
            return RuntimeValue(RuntimeType.BOOLEAN, left.value < right.value)
        
        elif left.type == RuntimeType.STRING and right.type == RuntimeType.STRING:
            return RuntimeValue(RuntimeType.BOOLEAN, left.value < right.value)
        
        else:
            raise InterpreterError(f"Нельзя сравнить {left.type.value} и {right.type.value}", node)
    
    def _logical_and(self, left: RuntimeValue, right: RuntimeValue) -> RuntimeValue:
        return RuntimeValue(RuntimeType.BOOLEAN, left.is_truthy() and right.is_truthy())
    
    def _logical_or(self, left: RuntimeValue, right: RuntimeValue) -> RuntimeValue:
        return RuntimeValue(RuntimeType.BOOLEAN, left.is_truthy() or right.is_truthy())
    
    def _type_from_string(self, type_name: str) -> RuntimeType:
        mapping = {
            "число": RuntimeType.INTEGER,
            "дробь": RuntimeType.FLOAT,
            "слово": RuntimeType.STRING,
            "ничто": RuntimeType.VOID,
        }
        return mapping.get(type_name, RuntimeType.VOID)
    
    def _convert_type(self, value: RuntimeValue, target_type: RuntimeType, 
                     node: ASTNode) -> RuntimeValue:
        try:
            if target_type == RuntimeType.INTEGER:
                return RuntimeValue(RuntimeType.INTEGER, int(value.value))
            elif target_type == RuntimeType.FLOAT:
                return RuntimeValue(RuntimeType.FLOAT, float(value.value))
            elif target_type == RuntimeType.STRING:
                return RuntimeValue(RuntimeType.STRING, str(value.value))
            else:
                return value
        except (ValueError, TypeError):
            raise InterpreterError(
                f"Нельзя преобразовать {value.type.value} в {target_type.value}",
                node
            )
    
    def _register_builtins(self):
        self.builtins = {
            "синус": self._builtin_sin,
            "косинус": self._builtin_cos,
            "корень": self._builtin_sqrt,
            "степень": self._builtin_pow,
            "модуль": self._builtin_abs,
            
            "слово_длина": self._builtin_length,
            "слово_верх": self._builtin_upper,
            "слово_низ": self._builtin_lower,
            
            "в_число": self._builtin_to_int,
            "в_дробь": self._builtin_to_float,
            "в_слово": self._builtin_to_string,
        }
    
    def _builtin_sin(self, args: List[RuntimeValue], node: ASTNode) -> RuntimeValue:
        if len(args) != 1:
            raise InterpreterError("синус ожидает 1 параметр", node)
        val = float(args[0].value)
        return RuntimeValue(RuntimeType.FLOAT, math.sin(val))
    
    def _builtin_cos(self, args: List[RuntimeValue], node: ASTNode) -> RuntimeValue:
        if len(args) != 1:
            raise InterpreterError("косинус ожидает 1 параметр", node)
        val = float(args[0].value)
        return RuntimeValue(RuntimeType.FLOAT, math.cos(val))
    
    def _builtin_sqrt(self, args: List[RuntimeValue], node: ASTNode) -> RuntimeValue:
        if len(args) != 1:
            raise InterpreterError("корень ожидает 1 параметр", node)
        val = float(args[0].value)
        if val < 0:
            raise InterpreterError("Корень из отрицательного числа - грех!", node)
        return RuntimeValue(RuntimeType.FLOAT, math.sqrt(val))
    
    def _builtin_pow(self, args: List[RuntimeValue], node: ASTNode) -> RuntimeValue:
        if len(args) != 2:
            raise InterpreterError("степень ожидает 2 параметра", node)
        base = float(args[0].value)
        exp = float(args[1].value)
        return RuntimeValue(RuntimeType.FLOAT, math.pow(base, exp))
    
    def _builtin_abs(self, args: List[RuntimeValue], node: ASTNode) -> RuntimeValue:
        if len(args) != 1:
            raise InterpreterError("модуль ожидает 1 параметр", node)
        val = args[0].value
        if args[0].type == RuntimeType.INTEGER:
            return RuntimeValue(RuntimeType.INTEGER, abs(val))
        else:
            return RuntimeValue(RuntimeType.FLOAT, abs(float(val)))
    
    def _builtin_length(self, args: List[RuntimeValue], node: ASTNode) -> RuntimeValue:
        if len(args) != 1:
            raise InterpreterError("слово_длина ожидает 1 параметр", node)
        return RuntimeValue(RuntimeType.INTEGER, len(str(args[0].value)))
    
    def _builtin_upper(self, args: List[RuntimeValue], node: ASTNode) -> RuntimeValue:
        if len(args) != 1:
            raise InterpreterError("слово_верх ожидает 1 параметр", node)
        return RuntimeValue(RuntimeType.STRING, str(args[0].value).upper())
    
    def _builtin_lower(self, args: List[RuntimeValue], node: ASTNode) -> RuntimeValue:
        if len(args) != 1:
            raise InterpreterError("слово_низ ожидает 1 параметр", node)
        return RuntimeValue(RuntimeType.STRING, str(args[0].value).lower())
    
    def _builtin_to_int(self, args: List[RuntimeValue], node: ASTNode) -> RuntimeValue:
        if len(args) != 1:
            raise InterpreterError("в_число ожидает 1 параметр", node)
        try:
            return RuntimeValue(RuntimeType.INTEGER, int(args[0].value))
        except:
            raise InterpreterError("Нельзя преобразовать в число", node)
    
    def _builtin_to_float(self, args: List[RuntimeValue], node: ASTNode) -> RuntimeValue:
        if len(args) != 1:
            raise InterpreterError("в_дробь ожидает 1 параметр", node)
        try:
            return RuntimeValue(RuntimeType.FLOAT, float(args[0].value))
        except:
            raise InterpreterError("Нельзя преобразовать в дробь", node)
    
    def _builtin_to_string(self, args: List[RuntimeValue], node: ASTNode) -> RuntimeValue:
        if len(args) != 1:
            raise InterpreterError("в_слово ожидает 1 параметр", node)
        return RuntimeValue(RuntimeType.STRING, str(args[0].value))

class BreakException(Exception):
    pass


class ContinueException(Exception):
    pass


class BlagoglagolRunner:
    
    def __init__(self):
        self.interpreter = BlagoglagolInterpreter()
    
    def run_file(self, filename: str):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                source = f.read()
            self.run(source, filename)
        except FileNotFoundError:
            print(f" Файл '{filename}' не найден", file=sys.stderr)
            sys.exit(1)
    
    def run(self, source: str, filename: str = "<строка>"):
        from lexer import BlagoglagolLexer, LexerError
        from parser import BlagoglagolParser, ParseError
        
        lexer = BlagoglagolLexer(source)
        try:
            tokens = lexer.tokenize()
        except LexerError as e:
            print(f" {e}", file=sys.stderr)
            sys.exit(1)
        
        parser = BlagoglagolParser(tokens)
        try:
            ast = parser.parse()
        except ParseError as e:
            print(f" {e}", file=sys.stderr)
            sys.exit(1)
        try:
            self.interpreter.interpret(ast)
        except Exception as e:
            print(f" Ошибка выполнения: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    test_code = """
    глаголи "Во имя Отца, и Сына, и Святаго Духа!"
    """
    
    runner = BlagoglagolRunner()
    print("=" * 80)
    print("ВЫПОЛНЕНИЕ ПРОГРАММЫ НА БЛАГОГЛАГОЛЕ")
    print("=" * 80)
    runner.run(test_code)