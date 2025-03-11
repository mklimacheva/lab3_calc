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

def evaluate(node):
    """
    Рекурсивно вычисляет значение выражения, представленного в виде AST.
    """
    if isinstance(node, ast.Constant):  # Число
        return node.value
    elif isinstance(node, ast.BinOp):  # Бинарная операция
        left = evaluate(node.left)
        right = evaluate(node.right)
        return operators[type(node.op)](left, right)
    elif isinstance(node, ast.UnaryOp):  # Унарная операция
        operand = evaluate(node.operand)
        return operators[type(node.op)](operand)
    else:
        raise TypeError("Неверное выражение")

def parse(expression):
    """
    Преобразует выражение в дерево AST.
    """
    try:
        # Удаляем лишние пробелы, оставляя по одному пробелу между элементами
        expression = " ".join(expression.split())
        
        # Проверяем, есть ли в выражении скобки
        if "(" in expression or ")" in expression:
            raise SyntaxError("Выражение содержит скобки, которые не поддерживаются.")
        
        # Проверяем, есть ли в выражении буквы (кроме экспоненциальной записи)
        if any(c.isalpha() and c not in 'eE' for c in expression):
            raise ValueError("Неверное выражение")
        
        # Проверяем, есть ли в выражении степень
        if "**" in expression:
            raise ValueError("Степень не поддерживается")
        
        # Парсим выражение в AST
        tree = ast.parse(expression, mode='eval')
        
        return tree.body
    except SyntaxError as e:
        if "invalid syntax" in str(e):
            raise ValueError("Неполное выражение")
        else:
            raise ValueError(f"Некорректное выражение: {e}")
    except (TypeError, KeyError) as e:
        raise ValueError(f"Некорректное выражение: {e}")

def calculate(expression):
    """
    Вычисляет значение математического выражения.
    Возвращает результат вычисления или выбрасывает исключение в случае ошибки.
    """
    try:
        # Если выражение является строкой, парсим его в AST
        if isinstance(expression, str):
            tree = parse(expression)
        else:
            # Если выражение уже является деревом AST, используем его
            tree = expression
        
        # Вычисляем выражение
        result = evaluate(tree)
        
        # Проверка на арифметическое переполнение
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