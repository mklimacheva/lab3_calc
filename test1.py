import unittest
from prettytable import PrettyTable
from calc import calculate, parse, evaluate
import ast
import math

def parse_tree_string(tree_str):
    try:
        # Удаляем пробелы
        tree_str = tree_str.replace(" ", "")

        # Определяем операцию и аргументы
        if tree_str.startswith("Add"):
            op = ast.Add()
            args_str = tree_str[4:-1]  # Убираем "Add(" и ")"
        elif tree_str.startswith("Sub"):
            op = ast.Sub()
            args_str = tree_str[4:-1]  
        elif tree_str.startswith("Mult"):
            op = ast.Mult()
            args_str = tree_str[5:-1]  
        elif tree_str.startswith("Div"):
            op = ast.Div()
            args_str = tree_str[4:-1]  
        elif tree_str.startswith("Pow"):  
            op = ast.Pow()
            args_str = tree_str[4:-1]  
        elif tree_str.startswith(('sqrt', 'sin', 'cos', 'tg', 'ctg', 'ln', 'exp')):
            # Обработка вызовов функций
            func_name = tree_str.split('(')[0]
            args_str = tree_str[len(func_name)+1:-1]
            arg = parse_argument(args_str)
            return ast.Call(
                func=ast.Name(id=func_name, ctx=ast.Load()),
                args=[arg],
                keywords=[]
            )
        else:
            # Если строка не начинается с операции
            try:
                value = float(tree_str)
                return ast.Constant(value=value)
            except ValueError:
                if tree_str in ['pi', 'e']:
                    return ast.Name(id=tree_str, ctx=ast.Load())
                raise ValueError(f"Неизвестная операция: {tree_str}")

        # Разделяем аргументы
        left_str, right_str = split_arguments(args_str)

        # Рекурсивно разбираем левый и правый аргументы
        left = parse_argument(left_str)
        right = parse_argument(right_str)

        # Создаем узел AST
        return ast.BinOp(left=left, op=op, right=right)
    except Exception as e:
        raise ValueError(e)

def split_arguments(args_str):
    # Разделяем аргументы
    balance = 0  # Счетчик для отслеживания вложенности
    for i, char in enumerate(args_str):
        if char == "(":
            balance += 1
        elif char == ")":
            balance -= 1
        elif char == "," and balance == 0:
            # Нашли разделитель аргументов
            return args_str[:i], args_str[i+1:]
    # Если не нашли разделитель, значит аргумент один
    return args_str, ""

def parse_argument(arg_str):
    # Проверяем, является ли аргумент числом
    if arg_str.replace(".", "", 1).replace("e", "", 1).isdigit():  
        return ast.Constant(value=float(arg_str))
    elif arg_str in ['pi', 'e']:
        return ast.Name(id=arg_str, ctx=ast.Load())
    else:
        return parse_tree_string(arg_str)

def ast_to_str(node):
    # Преобразуем дерево AST в строковое представление.
    if isinstance(node, ast.Expression):
        return ast_to_str(node.body)
    elif isinstance(node, ast.BinOp):
        left = ast_to_str(node.left)
        right = ast_to_str(node.right)
        op = type(node.op).__name__
        return f"{op}({left}, {right})"
    elif isinstance(node, ast.Constant):
        return str(node.value)
    elif isinstance(node, ast.UnaryOp):
        operand = ast_to_str(node.operand)
        op = type(node.op).__name__
        return f"{op}({operand})"
    elif isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Call):
        args = ", ".join(ast_to_str(arg) for arg in node.args)
        return f"{node.func.id}({args})"
    else:
        raise ValueError(f"Неподдерживаемый тип узла: {type(node)}")

class TestParser(unittest.TestCase):
    def test_expressions(self):
        test_cases = [
            ("42", "42"),
            ("3.14", "3.14"),
            ("2 + 3", "Add(2, 3)"),
            ("5 * 6", "Mult(5, 6)"),
            ("50 / 0.5", "Div(50, 0.5)"),
            ("500 - 800", "Sub(500, 800)"),
            ("2 + 3 * 4", "Add(2, Mult(3, 4))"),
            ("10 - 4 / 2", "Sub(10, Div(4, 2))"),
            ("0.25 / 0.001 + 0.081 * 25", "Add(Div(0.25, 0.001), Mult(0.081, 25))"),
            ("5^4", "Pow(5, 4)"),
            ("(1 + 1)", "Add(1, 1)"),
            ("1e+03", "1000.0"),
            ("pi", "pi"),
            ("e", "e"),
            ("sqrt(4)", "sqrt(4)"),  
            ("sin(pi/2)", "sin(Div(pi, 2))"),  
            ("ln(e^2)", "ln(Pow(e, 2))"),  
        ]

        for expression, expected in test_cases:
            with self.subTest(expression=expression):
                tree = parse(expression)
                result = ast_to_str(tree)
                self.assertEqual(result, expected)

class TestCalculator(unittest.TestCase):
    def test_calculations(self):
        test_cases = [
            ("Add(2,2)", 4),
            ("Mult(3,4)", 12),
            ("Div(10,2)", 5.0),
            ("Sub(10, 5)", 5),
            ("Pow(5, 4)", 625),
            ("Div(1e+03, 500)", 2),
            ("pi", math.pi),
            ("e", math.e),
            ("sqrt(4)", 2),  
            ("sin(Div(pi, 2))", 1),  
            ("ln(Pow(e, 2))", 2),  
        ]

        for tree_str, expected in test_cases:
            with self.subTest(tree_str=tree_str):
                tree = parse_tree_string(tree_str)
                result = calculate(tree)
                self.assertAlmostEqual(result, expected, places=6)

class TestIntegration(unittest.TestCase):
    def test_integration(self):
        test_cases = [
            ("1 + 1", 2),
            ("2 * 3", 6),
            ("10 / 2", 5.0),
            ("5 - 3", 2),
            ("2 ^ 3", 8),
            ("2 + (3 * 4)", 14),
            ("3.375e+09^(1/3)", 1500),
            ("sqrt(ln(e))", 1),
            ("sin(pi/2)", 1),
            ("cos(0)", 1),
            ("tg(0)", 0),
            ("exp(ln(2))", 2),
            ("ln(exp(2))", 2),
            ("ln(e^2)", 2),
            ("sqrt(2^2 * 2 + 1)", 3),  
        ]

        for expression, expected in test_cases:
            with self.subTest(expression=expression):
                result = calculate(expression)
                self.assertAlmostEqual(result, expected, places=6)

class TestAngleUnits(unittest.TestCase):
    def test_angle_units(self):
        test_cases = [
            ("sin(90)", 1, 'degree'),
            ("sin(pi/2)", 1, 'radian'),
            ("cos(0)", 1, 'degree'),
            ("cos(0)", 1, 'radian'),
            ("tg(45)", 1, 'degree'),
            ("ctg(45)", 1, 'degree'),
        ]

        for expression, expected, unit in test_cases:
            with self.subTest(expression=expression, unit=unit):
                result = calculate(expression, angle_unit=unit)
                self.assertAlmostEqual(result, expected, places=6)

if __name__ == "__main__":
    unittest.main()