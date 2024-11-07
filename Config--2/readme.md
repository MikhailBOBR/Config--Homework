# Визуализатор зависимостей Python

## Общее описание
Этот проект представляет визуализатор зависимостей, который извлекает зависимости из файла `package_dependencies.json`, получает подзависимости пакетов из указанного репозитория и визуализирует их в виде графа, используя Graphviz. Это полезно для анализа и понимания структуры зависимостей проекта.

## Структура файлов
Проект состоит из следующих файлов:

- `visualize_dependencies.py`: Основной файл с реализацией визуализатора зависимостей.
- `package_dependencies.json`: Файл, содержащий зависимости проекта.
- `config.toml`: Конфигурационный файл, в котором указываются параметры визуализации (например, путь к Graphviz и выходному изображению).

## Функциональность
Визуализатор зависимостей поддерживает следующие функции:

- Загрузка конфигурации из `config.toml`.
- Извлечение зависимостей из `package_dependencies.json`.
- Получение подзависимостей пакетов из репозитория.
- Генерация графа зависимостей в формате Graphviz.
- Сохранение графа в виде изображения.

## Описание функций
- **load_config(config_path)**: Загружает конфигурацию из файла `config.toml`.
- **load_dependencies(package_file)**: Загружает зависимости из `package_dependencies.json`.
- **normalize_version(version)**: Нормализует версию пакета, игнорируя символы `~` или `^`.
- **fetch_dependencies(pkg, version, repository_url)**: Получает зависимости пакета из указанного репозитория.
- **collect_dependencies(dependencies, repository_url, max_depth)**: Рекурсивно собирает все зависимости до указанной глубины.
- **generate_graphviz_graph(dependencies)**: Создает граф зависимостей в формате Graphviz.
- **save_graph(graph, output_path, graphviz_path)**: Сохраняет граф в виде изображения.

## Запуск визуализатора
```bash
python visualize_dependencies.py
```
Пример конфигурационного файла config.toml
```toml
[settings]
graphviz_path = "/usr/local/bin/dot"
package_name = "your-package-name"
output_path = "output/dependency_graph.png"
max_depth = 3
repository_url = "https://registry.npmjs.org"
```

### Результаты тестирования
![Скриншот результата](photo/Снимок%20экрана%202024-11-07%20123651.png)