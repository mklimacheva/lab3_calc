from prettytable import PrettyTable
from calc import calculate  # Импортируем функции из calc.py
import ast

def parse_tree_string(tree_str):
    """
    Преобразует строку с деревом выражений (например, "Add(2, 2)") в AST.
    Поддерживает вложенные выражения, такие как "Div(1, Sub(2, 2))".
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
            args_str = tree_str[4:-1]  # Убираем "Sub(" и ")"
        elif tree_str.startswith("Mult"):
            op = ast.Mult()
            args_str = tree_str[5:-1]  # Убираем "Mult(" и ")"
        elif tree_str.startswith("Div"):
            op = ast.Div()
            args_str = tree_str[4:-1]  # Убираем "Div(" и ")"
        else:
            # Если строка не начинается с операции, это может быть число
            try:
                # Пробуем преобразовать строку в число
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
    """
    Разделяет строку аргументов на левый и правый аргументы.
    Учитывает вложенные выражения.
    """
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
    """
    Разбирает аргумент: либо число, либо вложенное выражение.
    """
    if arg_str.replace(".", "", 1).replace("e", "", 1).replace("E", "", 1).isdigit():  # Проверяем, является ли аргумент числом
        return ast.Constant(value=float(arg_str))
    else:
        # Если это не число, то это вложенное выражение
        return parse_tree_string(arg_str)

def ast_to_str(node):
    """
    Преобразует дерево AST в строковое представление.
    """
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
        raise ValueError(f"Unsupported node type: {type(node)}")

def run_parser_tests():
    """
    Запускает тесты и выводит результаты в виде таблицы.
    """
    # Создаем таблицу для вывода результатов
    table = PrettyTable()
    table.field_names = [
        "Введенное выражение", 
        "Дерево выражений"
    ]

    # Определяем тестовые случаи
    test_cases = [
        # Корректные выражения
        ("42", 42, None, None),
        ("3.14", 3.14, None, None),
        ("2 + 3", 5, None, None),
        ("5 * 6", 30, None, None),
        ("50 / 0.5", 100.0, None, None),
        ("500 - 800", -300.0, None, None),
        ("2 + 3 * 4", 14, None, None),
        ("10 - 4 / 2", 8.0, None, None),
        ("0.25 / 0.001 + 0.081 * 25", 252.025, None, None),

        # Некорректные выражения
        ("a", None, None, None),
        ("2 /", None, None, None),
        ("5**4", None, None, None),
        ("(1 + 1)", None, None, None),
        ("1e300 / 1e-300", None, None, None),
    ]

    # Запускаем тесты
    for expression, expected, _, _ in test_cases:
        try:
            # Проверяем, есть ли в выражении скобки
            if "(" in expression or ")" in expression:
                raise SyntaxError("Выражение содержит скобки, которые не поддерживаются.")
        
            # Проверяем, есть ли в выражении степень
            if "**" in expression:
                raise ValueError("Степень не поддерживается")
        
            # Удаляем лишние пробелы, оставляя по одному пробелу между элементами
            expression = " ".join(expression.split())
        
            # Парсим выражение в AST
            tree = ast.parse(expression, mode='eval')
            result = ast_to_str(tree)
        
            
        except SyntaxError as e:
            if "invalid syntax" in str(e):
                result = "Неполное выражение"
            else:
                result = f"Некорректное выражение: {e}"
        except (TypeError, KeyError, ValueError) as e:
            result = f"Некорректное выражение: {e}"
        except Exception as e:
            result = f"Неизвестная ошибка: {e}"

        # Добавляем строку в таблицу
        table.add_row([expression, result])

    # Выводим таблицу
    print("\nТесты для парсера:")
    print(table)
    

def run_calculator_tests():
    """
    Запускает тесты для вычислителя и выводит результаты в виде таблицы.
    """
    # Создаем таблицу для вывода результатов
    calculator_table = PrettyTable()
    calculator_table.field_names = [
        "Дерево выражений", 
        "Ожидаемый результат", 
        "Полученный результат", 
        "Статус"
    ]

    # Определяем тестовые случаи для вычислителя
    calculator_test_cases = [
        # Корректные выражения
        ("Add(2,2)", 4, None),
        ("Mult(3,4)", 12, None),
        ("Div(10,2)", 5.0, None),
        ("Sub(10, 5)", 5, None),

        # Невозможные арифметические операции
        ("Div(2, 0)", None, "Ошибка: деление на ноль"),
        ("Div(1, Sub(2, 2))", None, "Ошибка: деление на ноль"),  
        ("Add(1, 4j)", None, "Ошибка: неверное выражение"),
        ("Div(1e300, 1e-300)", None, "Ошибка: арифметическое переполнение"),
    ]

    # Запускаем тесты для вычислителя
    for tree_str, expected, _ in calculator_test_cases:
        try:
            # Преобразуем строку с деревом выражений в AST
            tree = parse_tree_string(tree_str)
            # Вычисляем результат
# Вычисляем выражение
            result = calculate(tree)
            # Проверяем, совпадает ли результат с ожидаемым
            status = "Тест пройден" if result == expected else "Тест не пройден"
        except Exception as e:
            result = str(e)
            status = "Ошибка"

        # Добавляем строку в таблицу
        calculator_table.add_row([tree_str, expected, result, status])

    # Выводим таблицу
    print("\nТесты для вычислителя:")
    print(calculator_table)

if __name__ == "__main__":
    run_parser_tests()
    run_calculator_tests()