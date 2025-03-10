from prettytable import PrettyTable
import sys
import ast
import operator as op
import argparse

# Парсер аргументов командной строки
parser = argparse.ArgumentParser()
parser.add_argument("-t", "--test", action="store_true", help="Запустить тесты")

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
        
        return result
    except (SyntaxError, TypeError, KeyError) as e:
        print(f"Ошибка: Некорректное выражение. {e}")
        return None
    except ZeroDivisionError:
        print("Ошибка: Деление на ноль.")
        return None

def run_tests():
    """
    Запускает тесты для проверки всех путей выполнения.
    """
    test_cases = [
        # Корректные выражения
        ("1 + 1", 2),
        ("2 * 3 + 4", 10),
        ("10 / 2 - 1", 4.0),
        ("-5 + 10", 5),
        ("1 + 1 / 4", 1.25),
        
        # Ошибки синтаксиса
        ("(1 + 1)", None),  # Некорректный синтаксис (скобки)
        ("a", None),        # Некорректный синтаксис (неизвестный символ)
        ("1 + ", None),     # Незавершенное выражение
        ("2 ** 3", None),   # Возведение в степень (неподдерживаемая операция)
        
        # Деление на ноль
        ("1 / 0", None),    # Деление на ноль
        
        # Неподдерживаемые операции
        ("1 % 2", None),    # Неподдерживаемый оператор %
    ]

    # Создаем таблицу
    table = PrettyTable()
    table.field_names = ["Выражение", "Ожидаемый результат", "Полученный", "Вывод"]

    print("Запуск тестов...")
    for i, (expression, expected) in enumerate(test_cases, 1):
        result = calculate(expression)
        stroka = "Тест пройден" if result == expected else "Тест не пройден"
        table.add_row([expression, expected, result, stroka])
    
    print(table)
    print("Тесты завершены.")

if __name__ == "__main__":
    args = parser.parse_args()
    if args.test:
        run_tests()
    else:
        if len(sys.argv) != 2:
            print("Использование: python calculator.py <выражение>")
            sys.exit(1)
        
        # Передаем выражение целиком (все, что после имени скрипта)
        expression = sys.argv[1]
        result = calculate(expression)
        if result is not None:
            print(f"Результат: {result}")