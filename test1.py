import unittest
from prettytable import PrettyTable
from calc import calculate  # Импортируем функцию calculate из файла calc.py
import ast
import operator as op

# Поддерживаемые операторы
operators = {
    ast.Add: "Plus",
    ast.Sub: "Minus",
    ast.Mult: "Mult",
    ast.Div: "Div",
    ast.USub: "Neg",
}

def expression_to_tree(node):
    """
    Преобразует AST в строковое представление дерева.
    """
    if isinstance(node, ast.Constant):  # Число
        return str(node.value)
    elif isinstance(node, ast.BinOp):  # Бинарная операция
        left = expression_to_tree(node.left)
        right = expression_to_tree(node.right)
        op_name = operators[type(node.op)]
        return f"{op_name}({left}, {right})"
    elif isinstance(node, ast.UnaryOp):  # Унарная операция
        operand = expression_to_tree(node.operand)
        op_name = operators[type(node.op)]
        return f"{op_name}({operand})"
    else:
        raise TypeError("Неизвестная операция")

def run_tests():
    """
    Запускает тесты и выводит результаты в виде таблицы.
    """
    # Создаем таблицу для вывода результатов
    table = PrettyTable()
    table.field_names = [
        "Тест", 
        "Введенное выражение", 
        "Ожидаемый результат", 
        "Полученный результат", 
        "Дерево выражений", 
        "Статус"
    ]

    # Определяем тестовые случаи
    test_cases = [
        # Корректные выражения
        ("test_single_number", "42", 42, None, None),
        ("test_single_number", "3.14", 3.14, None, None),
        ("test_arithmetic_operations", "2 + 3", 5, None, None),
        ("test_arithmetic_operations", "2 - 3", -1, None, None),
        ("test_arithmetic_operations", "2 * 3", 6, None, None),
        ("test_arithmetic_operations", "6 / 3", 2.0, None, None),
        ("test_multi_digit_numbers", "10 + 20", 30, None, None),
        ("test_multi_digit_numbers", "100 - 50", 50, None, None),
        ("test_multi_digit_numbers", "123 * 2", 246, None, None),
        ("test_multi_digit_numbers", "1000 / 10", 100.0, None, None),
        ("test_two_operations", "2 + 3 * 4", 14, None, None),
        ("test_two_operations", "10 - 4 / 2", 8.0, None, None),
        ("test_two_operations", "2 * 3 + 4", 10, None, None),
        ("test_two_operations", "10 / 2 - 1", 4.0, None, None),
        ("test_expected_results", "2 + 2", 4, None, None),
        ("test_expected_results", "10 / 2", 5.0, None, None),
        ("test_expected_results", "3 * 4", 12, None, None),
        ("test_expected_results", "10 - 5", 5, None, None),

        # Некорректные выражения
        ("test_invalid_expressions", "2 /", None, None, None),
        ("test_invalid_expressions", "1 + 4j", None, None, None),
        ("test_invalid_expressions", "(1 + 1)", None, None, None),

        # Невозможные операции
        ("test_impossible_operations", "1 / 0", None, None, None),

        # Арифметическое переполнение
        ("test_arithmetic_overflow", "1e300 * 1e300", None, None, None),
        ("test_arithmetic_overflow", "1e300 / 1e-300", None, None, None),
    ]

    # Запускаем тесты
    for test_name, expression, expected, _, _ in test_cases:
        try:
            # Вычисляем результат
            result = calculate(expression)
            # Преобразуем выражение в дерево
            tree = expression_to_tree(ast.parse(expression, mode='eval').body)
            # Проверяем, совпадает ли результат с ожидаемым
            status = "✅ Успех" if result == expected else "❌ Ошибка"
        except Exception as e:
            result = str(e)
            tree = "Ошибка"
            status = "❌ Ошибка" if expected is None else "⚠ Пропущен"

        # Добавляем строку в таблицу
        table.add_row([test_name, expression, expected, result, tree, status])

    # Выводим таблицу
    print(table)

if __name__ == "__main__":
    run_tests()