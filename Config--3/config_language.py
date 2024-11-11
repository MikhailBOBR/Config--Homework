import argparse
import json
import sys
import re
import operator

# Регулярное выражение для проверки идентификаторов
IDENTIFIER_REGEX = re.compile(r'^[_A-Z][_a-zA-Z0-9]*$')

# Регулярное выражение для распознавания выражений
EXPR_REGEX = re.compile(r'^\$\{(.+)\}$')

# Регулярное выражение для токенизации выражений
EXPR_TOKEN_REGEX = re.compile(r'\[\[[^\]]*\]\]|\S+')

# Поддерживаемые операции
OPERATIONS = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv,
    'concat': lambda *args: ''.join(args),
    'ord': lambda x: ord(x) if isinstance(x, str) and len(x) == 1 else (
        sys.stderr.write("Ошибка: 'ord' требует одиночный символ.\n") or sys.exit(1)
    )
}

def parse_arguments():
    parser = argparse.ArgumentParser(description='Преобразователь JSON в учебный конфигурационный язык.')
    # Устанавливаем config.json как файл по умолчанию
    parser.add_argument('input_file', nargs='?', default='config.json', help='Путь к входному JSON файлу (по умолчанию: config.json).')
    return parser.parse_args()

def read_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        sys.stderr.write(f"Ошибка: Файл '{file_path}' не найден.\n")
        sys.exit(1)
    except json.JSONDecodeError as e:
        sys.stderr.write(f"Ошибка: Неверный JSON формат. {e}\n")
        sys.exit(1)

def validate_identifier(identifier):
    if not IDENTIFIER_REGEX.match(identifier):
        sys.stderr.write(f"Ошибка: Недопустимый идентификатор '{identifier}'.\n")
        sys.exit(1)

def escape_string(s):
    # Экранируем символы, если необходимо
    return s.replace(']]', ']]]]')  # Пример экранирования

def evaluate_expression(expr, constants):
    tokens = EXPR_TOKEN_REGEX.findall(expr)
    if not tokens:
        sys.stderr.write("Ошибка: Пустое выражение.\n")
        sys.exit(1)
    
    operator_token = tokens[0]
    operands = tokens[1:]
    
    if operator_token not in OPERATIONS:
        sys.stderr.write(f"Ошибка: Неизвестный оператор или функция '{operator_token}'.\n")
        sys.exit(1)
    
    # Подготовка операндов
    evaluated_operands = []
    for operand in operands:
        operand = operand.strip()
        # Проверка, является ли операнд идентификатором
        if IDENTIFIER_REGEX.match(operand):
            if operand not in constants:
                sys.stderr.write(f"Ошибка: Неопределенная константа '{operand}'.\n")
                sys.exit(1)
            evaluated_operands.append(constants[operand])
        else:
            # Попытка интерпретировать как число или строку
            try:
                if operand.startswith('[[') and operand.endswith(']]'):
                    # Строковый операнд
                    inner = operand[2:-2]
                    if inner in constants and isinstance(constants[inner], str):
                        evaluated_operands.append(constants[inner])
                    else:
                        evaluated_operands.append(inner)
                elif '.' in operand:
                    evaluated_operands.append(float(operand))
                else:
                    evaluated_operands.append(int(operand))
            except ValueError:
                sys.stderr.write(f"Ошибка: Недопустимый операнд '{operand}'. Ожидалась константа, число или строка в формате [[строка]].\n")
                sys.exit(1)
    
    # Проверка количества операндов
    if operator_token in ['+', '-', '*', '/']:
        if len(evaluated_operands) < 2:
            sys.stderr.write(f"Ошибка: Оператор '{operator_token}' требует как минимум два операнда.\n")
            sys.exit(1)
    elif operator_token == 'concat':
        if len(evaluated_operands) < 1:
            sys.stderr.write(f"Ошибка: Функция '{operator_token}' требует как минимум один аргумент.\n")
            sys.exit(1)
    elif operator_token == 'ord':
        if len(evaluated_operands) != 1:
            sys.stderr.write(f"Ошибка: Функция '{operator_token}' требует ровно один аргумент.\n")
            sys.exit(1)
    
    # Выполнение операции
    try:
        result = OPERATIONS[operator_token](*evaluated_operands)
        return result
    except Exception as e:
        sys.stderr.write(f"Ошибка при выполнении операции '{operator_token}': {e}\n")
        sys.exit(1)

def convert_value(value, constants):
    if isinstance(value, str):
        expr_match = EXPR_REGEX.match(value.strip())
        if expr_match:
            # Проверка на строку и заключение в [[...]]
            evaluated_value = evaluate_expression(expr_match.group(1).strip(), constants)
            if isinstance(evaluated_value, str):
                return f"[[{escape_string(evaluated_value)}]]"
            return str(evaluated_value)
        return f"[[{escape_string(value)}]]"
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, list):
        # Рекурсивно обрабатываем массивы для поддержки вложенности
        return f"#( {', '.join(str(convert_value(elem, constants)) for elem in value)} )"
    else:
        sys.stderr.write(f"Ошибка: Недопустимый тип значения '{value}'.\n")
        sys.exit(1)

def convert_json_to_config(json_data):
    if not isinstance(json_data, dict):
        sys.stderr.write("Ошибка: Входной JSON должен быть объектом.\n")
        sys.exit(1)
    
    constants = {}
    config_lines = ["#("]
    first = True
    for key, value in json_data.items():
        if not first:
            config_lines.append(",")
        else:
            first = False
        
        # Преобразуем значение с учетом вложенных массивов и выражений
        converted_value = convert_value(value, constants)
        
        # Проверка выражений и их вычисление
        if isinstance(value, str) and EXPR_REGEX.match(value.strip()):
            expr = EXPR_REGEX.match(value.strip()).group(1).strip()
            evaluated_value = evaluate_expression(expr, constants)
            constants[key] = evaluated_value
            config_lines.append(f"#([[{key}]], {converted_value})")
        else:
            constants[key] = value
            config_lines.append(f"#([[{key}]], {converted_value})")

    config_lines.append(")")
    return '\n'.join(config_lines)

def main():
    args = parse_arguments()
    json_data = read_json(args.input_file)
    config_output = convert_json_to_config(json_data)
    print(config_output)

if __name__ == "__main__":
    main()
