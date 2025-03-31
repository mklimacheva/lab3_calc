import sys
import ast
import operator as op
import argparse
import math
import re

# Парсер аргументов командной строки
parser = argparse.ArgumentParser(
    prog="Калькулятор",
    description="""Вычисление математических выражений с поддержкой:
    - Базовых операций: +, -, *, /, ^ 
    - Тригонометрических функций: sin, cos, tg, ctg
    - Других математических функций: sqrt (квадратный корень), ln (натуральный логарифм), exp (экспонента)
    - Констант: pi, e 
    - Поддержка градусов и радиан для тригонометрических функций""",
    epilog="Примеры использования:\n"
           "  python3 calc.py '2^3 + cos(0)'",
    formatter_class=argparse.RawDescriptionHelpFormatter
)
parser.add_argument("expression", nargs="?", help="Математическое выражение для вычисления.")
parser.add_argument("--angle-unit", choices=["degree", "radian"], default="radian",
                   help="Единицы измерения углов для тригонометрических функций (по умолчанию: radian)")

operators = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.USub: op.neg,
    ast.Pow: op.pow,
}

functions = {
    'sqrt': math.sqrt,
    'sin': math.sin,
    'cos': math.cos,
    'tg': math.tan,
    'ctg': lambda x: 1/math.tan(x),
    'ln': math.log,
    'exp': math.exp,
}

constants = {
    'pi': math.pi,
    'e': math.e,
}

def parse(expression):
    # Преобразуем выражение в дерево AST
    try:
        # Удаляем лишние пробелы
        expression = " ".join(expression.split())
        
        # Проверяем на наличие недопустимых символов
        allowed_chars = set('+-*/^() .0123456789eE')
        allowed_pattern = re.compile(r'^[+\-*/^() .\d\s]*|[a-z]+\(|pi|e')
        
        # Разрешаем буквы только в названиях функций и констант
        for token in re.findall(r'[a-zA-Z]+', expression):
            if token not in functions and token not in constants and not token.startswith(('sqrt', 'sin', 'cos', 'tg', 'ctg', 'ln', 'exp')):
                raise ValueError(f"Выражение содержит неверные символы: {token}")
        
        # Заменяем ^ на ** для корректного парсинга
        expression = expression.replace('^', '**')
        
        # Парсим выражение в AST
        tree = ast.parse(expression, mode='eval')
        return tree.body
    except SyntaxError as e:
        if "invalid syntax" in str(e):
            raise ValueError("Некорректное выражение: Неполное выражение")
        else:
            raise ValueError(f"Некорректное выражение: {e}")
    except (TypeError, KeyError, ValueError) as e:
        raise ValueError(f"Некорректное выражение: {e}")

def evaluate(node, angle_unit='radian'):
    # Рекурсивно вычисляем значение выражения, представленного в виде AST
    if isinstance(node, ast.Constant):
        return node.value
    elif isinstance(node, ast.BinOp):
        left = evaluate(node.left, angle_unit)
        right = evaluate(node.right, angle_unit)
        return operators[type(node.op)](left, right)
    elif isinstance(node, ast.UnaryOp):
        operand = evaluate(node.operand, angle_unit)
        return operators[type(node.op)](operand)
    elif isinstance(node, ast.Name):
        if node.id in constants:
            return constants[node.id]
        raise ValueError(f"Неизвестная константа: {node.id}")
    elif isinstance(node, ast.Call):
        func_name = node.func.id
        if func_name not in functions:
            raise ValueError(f"Неизвестная функция: {func_name}")
        
        args = [evaluate(arg, angle_unit) for arg in node.args]
        if len(args) != 1:
            raise ValueError(f"Функция {func_name} принимает ровно 1 аргумент")
        
        value = args[0]
        if func_name in ['sin', 'cos', 'tg', 'ctg'] and angle_unit == 'degree':
            value = math.radians(value)
        
        try:
            return functions[func_name](value)
        except ValueError as e:
            raise ValueError(f"Ошибка в функции {func_name}: {e}")
    else:
        raise TypeError(f"Неверное выражение: неподдерживаемый узел AST {type(node)}")

def calculate(expression, angle_unit='radian'):
    try:
        # Если выражение является строкой, парсим его в AST
        if isinstance(expression, str):
            tree = parse(expression)
        else:
            tree = expression
        result = evaluate(tree, angle_unit)
        if math.isinf(result) or math.isnan(result):
            raise OverflowError("Арифметическое переполнение.")
        return result
    except (SyntaxError, TypeError, KeyError) as e:
        raise ValueError(f"Некорректное выражение: {e}")
    except ZeroDivisionError:
        raise ZeroDivisionError("Деление на ноль.")
    except OverflowError:
        raise OverflowError("Арифметическое переполнение.")

if __name__ == "__main__":
    args = parser.parse_args()
    if not args.expression:
        parser.print_help()
        sys.exit(1)
    expression = args.expression
    try:
        result = calculate(expression, args.angle_unit)
        print(f"Результат: {result}")
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)