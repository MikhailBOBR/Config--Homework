import json
from config_language import ConfigLanguageConverter

# JSON с примерами для тестирования
json_data = {
    "_Const1": 100,
    "_Const2": "Example string",
    "Array1": [1, 2, 3, 4],
    "Expression1": { "$": ["+", "_Const1", 50] },
    "NestedArray": [["nested1", 10], ["nested2", 20]]
}

# Создаем экземпляр конвертера
converter = ConfigLanguageConverter()

# Тесты
print("=== Тест: Объявление числовой константы ===")
result = converter.define_constant("_Const1", 100)
print("Ожидаемый результат: (def _Const1 100)")
print("Фактический результат:", result)
print()

print("=== Тест: Объявление строковой константы ===")
result = converter.define_constant("_Const2", "Example string")
print("Ожидаемый результат: (def _Const2 [[Example string]])")
print("Фактический результат:", result)
print()

print("=== Тест: Массив ===")
result = converter.convert_value([1, 2, 3, 4])
print("Ожидаемый результат: #(1, 2, 3, 4)")
print("Фактический результат:", result)
print()

print("=== Тест: Вложенный массив ===")
result = converter.convert_value([["nested1", 10], ["nested2", 20]])
print("Ожидаемый результат: #(#([[nested1]], 10), #([[nested2]], 20))")
print("Фактический результат:", result)
print()

print("=== Тест: Вычисление выражения ===")
converter.constants["_Const1"] = 100  # Определяем константу, которая понадобится для выражения
result = converter.evaluate_expression(["+", "_Const1", 50])
print("Ожидаемый результат: 150")
print("Фактический результат:", result)
print()

print("=== Тест: Полное преобразование JSON в конфигурацию ===")
result = converter.convert_json_to_config(json_data)
expected_output = """(def _Const1 100)
(def _Const2 [[Example string]])
Array1 = #(1, 2, 3, 4)
(def Expression1 150)
NestedArray = #(#([[nested1]], 10), #([[nested2]], 20))"""
print("Ожидаемый результат:\n", expected_output)
print("Фактический результат:\n", result)
print()

# Дополнительные примеры конфигураций из разных областей
print("=== Пример 1: Конфигурация веб-сервера ===")
web_server_config = {
    "_host": "localhost",
    "_port": 8080,
    "_maxConnections": 100,
    "_ssl": True,
    "routes": [
        { "path": "/home", "handler": "homeHandler" },
        { "path": "/about", "handler": "aboutHandler" }
    ]
}
print("Конфигурация веб-сервера JSON:", json.dumps(web_server_config, indent=2))
print("Конфигурация веб-сервера в учебном конфигурационном языке:")
print(converter.convert_json_to_config(web_server_config))
print()

print("=== Пример 2: Конфигурация библиотеки ===")
library_config = {
    "books": [
        { "title": "The Catcher in the Rye", "author": "J.D. Salinger", "year": 1951 },
        { "title": "To Kill a Mockingbird", "author": "Harper Lee", "year": 1960 }
    ],
    "location": "Main Street 123",
    "openHours": {
        "monday": "9am - 6pm",
        "tuesday": "9am - 6pm",
        "wednesday": "9am - 6pm"
    }
}
print("Конфигурация библиотеки JSON:", json.dumps(library_config, indent=2))
print("Конфигурация библиотеки в учебном конфигурационном языке:")
print(converter.convert_json_to_config(library_config))
print()
