import sys
import ast
import operator as op
import argparse
import math

# Парсер аргументов командной строки
parser = argparse.ArgumentParser(
    prog="Калькулятор",
    description="Вычисление выражений",
    epilog="Использование: python3 calc.py '1+1'",
)
parser.add_argument("expression", nargs="?", help="Математическое выражение для вычисления.")

operators = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.USub: op.neg,
}

def parse(expression):
    #Преобразуем выражение в дерево AST
    try:
        # Удаляем лишние пробелы
        expression = " ".join(expression.split())
        if "(" in expression or ")" in expression:
            raise ValueError("Выражение содержит скобки, которые не поддерживаются.")
        if any(c.isalpha() and c not in 'eE' for c in expression):
            raise ValueError("Выражение содержит неверные символы")
        if "**" in expression:
            raise ValueError("Степень не поддерживается")
        tree = ast.parse(expression, mode='eval')
        return tree.body
    except SyntaxError as e:
        if "invalid syntax" in str(e):
            raise ValueError("Некорректное выражение: Неполное выражение")
        else:
            raise ValueError(f"Некорректное выражение: {e}")
    except (TypeError, KeyError, ValueError) as e:
        raise ValueError(f"Некорректное выражение: {e}")

def evaluate(node):
    #Рекурсивно вычисляем значение выражения, представленного в виде AST
    if isinstance(node, ast.Constant):  
        return node.value
    elif isinstance(node, ast.BinOp):  
        left = evaluate(node.left)
        right = evaluate(node.right)
        return operators[type(node.op)](left, right)
    elif isinstance(node, ast.UnaryOp):  
        operand = evaluate(node.operand)
        return operators[type(node.op)](operand)
    else:
        raise TypeError("Неверное выражение")

def calculate(expression):
    try:
        # Если выражение является строкой, парсим его в AST
        if isinstance(expression, str):
            tree = parse(expression)
        else:
            tree = expression
        result = evaluate(tree)
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
        result = calculate(expression)
        print(f"Результат: {result}")
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)