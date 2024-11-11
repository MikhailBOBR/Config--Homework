import json
import sys
from io import StringIO

# Импортируем основную функцию main из файла config_language.py
from config_language import main

def run_test(json_input, expected_output):
    # Перенаправляем stdout для захвата выходных данных
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    
    # Записываем JSON входные данные во временный файл
    with open("temp_config.json", "w") as f:
        json.dump(json_input, f)
    
    # Запускаем основную функцию с временным файлом как аргумент
    sys.argv = ["config_language.py", "temp_config.json"]
    main()
    
    # Получаем результат из stdout и очищаем его от лишних символов для сравнения
    output = sys.stdout.getvalue().strip().replace("\n", "").replace(" ", "")
    expected_output = expected_output.strip().replace("\n", "").replace(" ", "")
    
    sys.stdout = old_stdout  # Восстанавливаем stdout

    # Проверка результата
    if output == expected_output:
        print("Тест пройден")
    else:
        print("Тест не пройден")
        print("Ожидаемый результат:\n", expected_output)
        print("Фактический результат:\n", output)

# Описание каждого теста с входными данными и ожидаемым результатом

def test_simple_expression():
    json_input = {
        "Demo": 42,
        "ComputedProperty": "${+ Demo 1}"
    }
    expected_output = """
#(
#([[Demo]], 42),
#([[ComputedProperty]], 43)
)
""".strip()
    print("Тест 1: Простое выражение")
    run_test(json_input, expected_output)

def test_arithmetic_operations():
    json_input = {
        "Base": 50,
        "Increment": 5,
        "ResultSum": "${+ Base Increment}",
        "ResultDifference": "${- Base Increment}",
        "ResultProduct": "${* Base Increment}",
        "ResultQuotient": "${/ Base Increment}"
    }
    expected_output = """
#(
#([[Base]], 50),
#([[Increment]], 5),
#([[ResultSum]], 55),
#([[ResultDifference]], 45),
#([[ResultProduct]], 250),
#([[ResultQuotient]], 10.0)
)
""".strip()
    print("Тест 2: Арифметические операции")
    run_test(json_input, expected_output)

def test_string_operations_and_ord():
    json_input = {
        "Greeting": "Hello",
        "Target": "World",
        "Message": "${concat [[Greeting]] [[ ]] [[Target]]}",
        "FirstLetterCode": "${ord [[A]]}"
    }
    expected_output = """
#(
#([[Greeting]], [[Hello]]),
#([[Target]], [[World]]),
#([[Message]], [[Hello World]]),
#([[FirstLetterCode]], 65)
)
""".strip()
    print("Тест 3: Операции со строками и ord")
    run_test(json_input, expected_output)

def test_nested_arrays():
    json_input = {
        "Values": [1, 2, 3],
        "BaseValue": 10,
        "ComputedArray": ["${+ BaseValue 5}", "${* BaseValue 2}", "${concat [[Hello]] [[ ]] [[World]]}", "${ord [[B]]}"]
    }
    expected_output = """
#(
#([[Values]], #( 1, 2, 3 )),
#([[BaseValue]], 10),
#([[ComputedArray]], #( 15, 20, [[Hello World]], 66 ))
)
""".strip()
    print("Тест 4: Вложенные массивы")
    run_test(json_input, expected_output)

def test_warehouse_management():
    json_input = {
        "WarehouseCapacity": 5000,
        "CurrentStock": 3000,
        "IncomingStock": 500,
        "OutgoingStock": 200,
        "UpdatedStock": "${+ CurrentStock IncomingStock}",
        "RemainingCapacity": "${- WarehouseCapacity UpdatedStock}",
        "GreetingMessage": "${concat [[Welcome to the warehouse with ID]] [[ ]] [[1234]]}",
        "CodeForA": "${ord [[A]]}"
    }
    expected_output = """
#(
#([[WarehouseCapacity]], 5000),
#([[CurrentStock]], 3000),
#([[IncomingStock]], 500),
#([[OutgoingStock]], 200),
#([[UpdatedStock]], 3500),
#([[RemainingCapacity]], 1500),
#([[GreetingMessage]], [[Welcome to the warehouse with ID 1234]]),
#([[CodeForA]], 65)
)
""".strip()
    print("Тест 5: Управление складом")
    run_test(json_input, expected_output)

def test_game_character_config():
    json_input = {
        "BaseHealth": 100,
        "HealthBoost": 20,
        "TotalHealth": "${+ BaseHealth HealthBoost}",
        "AttackPower": 50,
        "Defense": 30,
        "DamageReduction": "${- AttackPower Defense}",
        "CharacterName": "Hero",
        "WelcomeMessage": "${concat [[Welcome, ]] [[CharacterName]] [[, to the arena]]}"
    }
    expected_output = """
#(
#([[BaseHealth]], 100),
#([[HealthBoost]], 20),
#([[TotalHealth]], 120),
#([[AttackPower]], 50),
#([[Defense]], 30),
#([[DamageReduction]], 20),
#([[CharacterName]], [[Hero]]),
#([[WelcomeMessage]], [[Welcome, Hero, to the arena]])
)
""".strip()
    print("Тест 6: Конфигурация персонажа игры")
    run_test(json_input, expected_output)

def test_nested_array_config():
    json_input = {
        "NestedArray": [1, 2, ["${+ 1 1}", "${concat [[Hello]] [[ ]] [[World]]}"], 3]
    }
    expected_output = """
#(
#([[NestedArray]], #( 1, 2, #( 2, [[Hello World]] ), 3 ))
)
""".strip()
    print("Тест 7: Вложенные массивы с выражениями")
    run_test(json_input, expected_output)

def test_deeply_nested_arrays():
    json_input = {
        "DeepNestedArray": [
            1,
            ["${+ 1 1}", 2, ["${* 2 2}", "${concat [[Deep]] [[ ]] [[Nest]]}"]],
            3
        ]
    }
    expected_output = """
#(
#([[DeepNestedArray]], #( 1, #( 2, 2, #( 4, [[Deep Nest]] ) ), 3 ))
)
""".strip()
    print("Тест 8: Глубоко вложенные массивы с выражениями")
    run_test(json_input, expected_output)

# Запуск всех тестов
if __name__ == "__main__":
    test_simple_expression()
    test_arithmetic_operations()
    test_string_operations_and_ord()
    test_nested_arrays()
    test_warehouse_management()
    test_game_character_config()
    test_nested_array_config()  # Тест для вложенных массивов
    test_deeply_nested_arrays()  # Тест для глубокой вложенности
