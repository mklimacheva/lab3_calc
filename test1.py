import unittest
from prettytable import PrettyTable
from calc import calculate, parse, evaluate
import ast

def parse_tree_string(tree_str):
    #Преобразуем строку с деревом выражений Add(2, 2) в AST.
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
        else:
            # Если строка не начинается с операции
            try:
                value = float(tree_str)
                return ast.Constant(value=value)
            except ValueError:
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
    raise ValueError(f"Не удалось разделить аргументы: {args_str}")

def parse_argument(arg_str):
    # Проверяем, является ли аргумент числом
    if arg_str.replace(".", "", 1).replace("e", "", 1).isdigit():  
        return ast.Constant(value=float(arg_str))
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
        ]

        for expression, expected in test_cases:
            with self.subTest(expression=expression):
                tree = parse(expression)
                result = ast_to_str(tree)
                self.assertEqual(result, expected)

        # Тесты на ошибки
        with self.assertRaises(ValueError):
            parse("a")
        with self.assertRaises(ValueError):
            parse("2 /")

class TestCalculator(unittest.TestCase):
    def test_calculations(self):
        test_cases = [
            ("Add(2,2)", 4),
            ("Mult(3,4)", 12),
            ("Div(10,2)", 5.0),
            ("Sub(10, 5)", 5),
            ("Pow(5, 4)", 625),  
            ("Div(1e+03, 500)", 2),
        ]

        for tree_str, expected in test_cases:
            with self.subTest(tree_str=tree_str):
                tree = parse_tree_string(tree_str)
                result = calculate(tree)
                self.assertEqual(result, expected)

        # Тесты на ошибки
        with self.assertRaises(ZeroDivisionError):
            calculate(parse_tree_string("Div(2, 0)"))
        with self.assertRaises(ZeroDivisionError):
            calculate(parse_tree_string("Div(1, Sub(2, 2))"))
        with self.assertRaises(ValueError):
            calculate(parse_tree_string("Add(1, 4j)"))
        with self.assertRaises(OverflowError):
            calculate(parse_tree_string("Div(1e300, 1e-300)"))

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
        ]

        for expression, expected in test_cases:
            with self.subTest(expression=expression):
                result = calculate(expression)
                self.assertAlmostEqual(result, expected, places=6)

        # Тесты на ошибки
        with self.assertRaises(ZeroDivisionError):
            calculate("1 / 0")
        with self.assertRaises(ValueError):
            calculate("a + 1")
        with self.assertRaises(OverflowError):
            calculate("1e300 / 1e-300")

if __name__ == "__main__":
    unittest.main()