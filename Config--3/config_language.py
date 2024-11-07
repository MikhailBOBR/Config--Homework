import json
import re
import sys

class ConfigLanguageConverter:
    def __init__(self, json_file_path="config.json"):
        self.constants = {}
        self.json_file_path = json_file_path

    def parse_json(self):
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            sys.stderr.write(f"JSON parsing error: {e}\n")
            sys.exit(1)
        except FileNotFoundError:
            sys.stderr.write(f"File not found: {self.json_file_path}\n")
            sys.exit(1)

    def convert_value(self, value):
        if isinstance(value, int) or isinstance(value, float):
            return str(value)
        elif isinstance(value, str):
            return f"[[{value}]]"
        elif isinstance(value, list):
            return "#(" + ", ".join(self.convert_value(v) for v in value) + ")"
        elif isinstance(value, dict):
            # Обработка словарей как массива пар ключ-значение
            return "#(" + ", ".join(f"#([[{k}]], {self.convert_value(v)})" for k, v in value.items()) + ")"
        else:
            raise ValueError("Unsupported value type")

    def define_constant(self, name, value):
        if not re.match(r'[_A-Z][_a-zA-Z0-9]*', name):
            sys.stderr.write(f"Invalid constant name: {name}\n")
            sys.exit(1)
        self.constants[name] = value
        return f"(def {name} {self.convert_value(value)})"

    def evaluate_expression(self, expr):
        if isinstance(expr, list) and expr[0] in ["+", "-", "*", "/"]:
            operator = expr[0]
            if len(expr) != 3:
                sys.stderr.write("Invalid expression format\n")
                sys.exit(1)
            operand1 = self.constants.get(expr[1], expr[1])
            operand2 = self.constants.get(expr[2], expr[2])
            if operator == "+":
                return operand1 + operand2
            elif operator == "-":
                return operand1 - operand2
            elif operator == "*":
                return operand1 * operand2
            elif operator == "/":
                return operand1 / operand2
        else:
            sys.stderr.write("Unsupported expression or invalid syntax\n")
            sys.exit(1)

    def convert_json_to_config(self, data):
        config_lines = []
        for key, value in data.items():
            if re.match(r'^[_A-Z][_a-zA-Z0-9]*$', key):  # Если ключ соответствует синтаксису константы
                config_lines.append(self.define_constant(key, value))
            else:  # Если ключ не соответствует, обрабатываем его как переменную
                config_lines.append(f"{key} = {self.convert_value(value)}")
        return "\n".join(config_lines)

    def process(self):
        json_data = self.parse_json()
        config_output = self.convert_json_to_config(json_data)
        print(config_output)

if __name__ == "__main__":
    converter = ConfigLanguageConverter()
    converter.process()
