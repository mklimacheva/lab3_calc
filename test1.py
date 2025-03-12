import unittest
from prettytable import PrettyTable
from calc import calculate
from calc import parse
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
   #Преобразуем дерево AST в строковое представление.
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
        table = PrettyTable()
        table.field_names = [
            "Введенное выражение", 
            "Дерево выражений"
        ]
        test_cases = [
            ("42", 42),
            ("3.14", 3.14),
            ("2 + 3", 5),
            ("5 * 6", 30),
            ("50 / 0.5", 100.0),
            ("500 - 800", -300.0),
            ("2 + 3 * 4", 14),
            ("10 - 4 / 2", 8.0),
            ("0.25 / 0.001 + 0.081 * 25", 252.025),
            ("a", ValueError),
            ("2 /", ValueError),
            ("5**4", ValueError),
            ("(1 + 1)", SyntaxError),
            ("1e300 / 1e-300", OverflowError),
        ]
        for expression, expected in test_cases:
            try:
                # Парсим выражение в AST
                tree = parse(expression)
                result = ast_to_str(tree)
            except Exception as e:
                result = e
            table.add_row([expression, result])
        print("\nТесты для парсера:")
        print(table)

class TestCalculator(unittest.TestCase):
    def test_calculations(self):
        calculator_table = PrettyTable()
        calculator_table.field_names = [
            "Дерево выражений", 
            "Ожидаемый результат", 
            "Полученный результат", 
            "Статус"
        ]
        test_cases = [
            ("Add(2,2)", 4, None),
            ("Mult(3,4)", 12, None),
            ("Div(10,2)", 5.0, None),
            ("Sub(10, 5)", 5, None),
            ("Div(2, 0)", None, ZeroDivisionError),
            ("Div(1, Sub(2, 2))", None, ZeroDivisionError), 
            ("Add(1, 4j)", None, ValueError),
            ("Div(1e300, 1e-300)", None, OverflowError),
        ]

        for tree_str, expected, expected_exception in test_cases:
            try:
                # Преобразуем строку с деревом выражений в AST
                tree = parse_tree_string(tree_str)
                result = calculate(tree)
                if expected_exception is not None:
                    status = "Тест не пройден"
                else:
                    status = "Тест пройден" if result == expected else "Тест не пройден"
            except Exception as e:
                result = str(e)
                if expected_exception is not None and isinstance(e, expected_exception):
                    status = "Тест пройден"
                else:
                    status = "Ошибка"
            calculator_table.add_row([tree_str, expected, result, status])
        print("\nТесты для вычислителя:")
        print(calculator_table)

if __name__ == "__main__":
    unittest.main()