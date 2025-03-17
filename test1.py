import unittest
from prettytable import PrettyTable
from calc import calculate, parse, evaluate
import ast

def parse_tree_string(tree_str):
    """
    Преобразуем строку с деревом выражений Add(2, 2) в AST.
    """
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
        table = PrettyTable()
        table.field_names = [
            "Введенное выражение", 
            "Ожидаемый результат", 
            "Полученный результат", 
            "Статус"
        ]
        test_cases = [
            ("42", "42", None),
            ("3.14", "3.14", None),
            ("2 + 3", "Add(2, 3)", None),
            ("5 * 6", "Mult(5, 6)", None),
            ("50 / 0.5", "Div(50, 0.5)", None),
            ("500 - 800", "Sub(500, 800)", None),
            ("2 + 3 * 4", "Add(2, Mult(3, 4))", None),
            ("10 - 4 / 2", "Sub(10, Div(4, 2))", None),
            ("0.25 / 0.001 + 0.081 * 25", "Add(Div(0.25, 0.001), Mult(0.081, 25))", None),
            ("a", None, ValueError),
            ("2 /", None,  ValueError),
            ("5**4", "Pow(5, 4)", None),
            ("(1 + 1)", "Add(1, 1)", None),
            ("1e+03", "1000.0", None),

        ]

        for tree_str, expected, expected_exception in test_cases:
            try:
                # Парсим выражение в AST
                tree = parse(tree_str)  
                result = ast_to_str(tree)
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
            table.add_row([tree_str, expected, result, status])
        
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
            ("Pow(5, 4)", 625, None),
            ("Div(1e+03, 500)", 2, None),
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

class TestIntegration(unittest.TestCase):
    def test_integration(self):
        integration_table = PrettyTable()
        integration_table.field_names = [
            "Введенное выражение", 
            "Ожидаемый результат", 
            "Полученный результат", 
            "Статус"
        ]
        test_cases = [
            ("1 + 1", 2, None),
            ("2 * 3", 6, None),
            ("10 / 2", 5.0, None),
            ("5 - 3", 2, None),
            ("2 ** 3", 8, None),
            ("2 + (3 * 4)", 14, None),
	    ("3.375e+09**(1/3)", 1500, None),
	    ("1 / 0", None, ZeroDivisionError),
            ("a + 1", None, ValueError),
            ("1e300 / 1e-300", None, OverflowError),
        ]

        for expression, expected, expected_exception in test_cases:
            try:
                # Парсим выражение и вычисляем результат
                result = calculate(expression)
                if expected_exception is not None:
                    status = "Тест не пройден"
                else:
                    status = "Тест пройден" if (abs(result - expected) < 1e-06) else "Тест не пройден"
            except Exception as e:
                result = str(e)
                if expected_exception is not None and isinstance(e, expected_exception):
                    status = "Тест пройден"
                else:
                    status = "Ошибка"
            integration_table.add_row([expression, expected, result, status])
        
        print("\nИнтеграционные тесты (parse + evaluate):")
        print(integration_table)

if __name__ == "__main__":
    # Создаем TestSuite и добавляем тесты в нужном порядке
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Добавляем тесты для парсера
    suite.addTest(loader.loadTestsFromTestCase(TestParser))

    # Добавляем тесты для вычислителя
    suite.addTest(loader.loadTestsFromTestCase(TestCalculator))

    # Добавляем интеграционные тесты
    suite.addTest(loader.loadTestsFromTestCase(TestIntegration))

    # Запускаем тесты
    runner = unittest.TextTestRunner()
    runner.run(suite)