import sys
import ast
import operator as op
import argparse
import math

# Парсер аргументов командной строки
parser = argparse.ArgumentParser(
    prog="Калькулятор",
    description="Вычисление выражений",
    epilog="Использование: python calc.py '1+1'",
)

parser.add_argument("expression", nargs="?", help="Математическое выражение для вычисления.")

# Поддерживаемые операторы
operators = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.USub: op.neg,
}

def evaluate_expression(node):
    """
    Рекурсивно вычисляет значение выражения, представленного в виде AST.
    """
    if isinstance(node, ast.Constant):  # Число
        return node.value
    elif isinstance(node, ast.BinOp):  # Бинарная операция
        left = evaluate_expression(node.left)
        right = evaluate_expression(node.right)
        return operators[type(node.op)](left, right)
    elif isinstance(node, ast.UnaryOp):  # Унарная операция
        operand = evaluate_expression(node.operand)
        return operators[type(node.op)](operand)
    else:
        raise TypeError("Неизвестная операция")

def calculate(expression):
    """
    Вычисляет значение математического выражения.
    Возвращает результат вычисления или выбрасывает исключение в случае ошибки.
    """
    try:
        # Удаляем лишние пробелы, оставляя по одному пробелу между элементами
        expression = " ".join(expression.split())
        
        # Проверяем, есть ли в выражении скобки
        if "(" in expression or ")" in expression:
            raise SyntaxError("Выражение содержит скобки, которые не поддерживаются.")
        
        # Парсим выражение в AST
        tree = ast.parse(expression, mode='eval')
        
        # Вычисляем выражение
        result = evaluate_expression(tree.body)
        
        # Проверка на арифметическое переполнение
        if math.isinf(result) or math.isnan(result):
            raise OverflowError("Арифметическое переполнение.")
        
        return result
    except (SyntaxError, TypeError, KeyError) as e:
        raise ValueError(f"Некорректное выражение: {e}")
    except ZeroDivisionError:
        raise ZeroDivisionError("Деление на ноль.")

if __name__ == "__main__":
    args = parser.parse_args()  # Парсим аргументы командной строки
    if not args.expression:
        parser.print_help()
        sys.exit(1)
        
    # Передаем выражение целиком (все, что после имени скрипта)
    expression = args.expression
    try:
        result = calculate(expression)
        print(f"Результат: {result}")
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)