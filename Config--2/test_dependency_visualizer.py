import json
import os  # Добавляем импорт os
from unittest.mock import patch, MagicMock
from dependency_visualizer import (
    load_dependencies,
    normalize_version,
    fetch_dependencies,
    collect_dependencies,
    generate_graphviz_graph,
    save_graph,
    load_config
)


def test_load_dependencies():
    with open("test_package_dependencies.json", "w") as f:
        json.dump({"dependencies": {"express": "4.17.1"}}, f)
    
    dependencies = load_dependencies("test_package_dependencies.json")
    assert dependencies == {"express": "4.17.1"}, "Ошибка в load_dependencies"


def test_normalize_version():
    assert normalize_version("~1.2.3") == "1.2.3", "Ошибка в normalize_version с ~1.2.3"
    assert normalize_version("^1.2.3") == "1.2.3", "Ошибка в normalize_version с ^1.2.3"
    assert normalize_version("1.2.3") == "1.2.3", "Ошибка в normalize_version с 1.2.3"
    assert normalize_version("latest") == "latest", "Ошибка в normalize_version с latest"


@patch("requests.get")
def test_fetch_dependencies(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"dependencies": {"lodash": "4.17.20"}}
    mock_get.return_value = mock_response

    response = fetch_dependencies("express", "4.17.1")
    assert "lodash" in response, "Ошибка в fetch_dependencies: ожидаемая зависимость 'lodash' отсутствует"
    assert response["lodash"] == "4.17.20", "Ошибка в fetch_dependencies: неверная версия для 'lodash'"


@patch("dependency_visualizer.fetch_dependencies")
def test_collect_dependencies(mock_fetch_dependencies):
    mock_fetch_dependencies.side_effect = lambda pkg, ver, url: {"lodash": "4.17.20"} if pkg == "express" else {}

    dependencies = {"express": "4.17.1"}
    all_dependencies = collect_dependencies(dependencies, "https://registry.npmjs.org", max_depth=2)
    
    assert "express" in all_dependencies, "Ошибка в collect_dependencies: 'express' не найдена"
    assert "lodash" in all_dependencies["express"], "Ошибка в collect_dependencies: 'lodash' не найдена в 'express'"


def test_generate_graphviz_graph():
    dependencies = {"express": ["lodash"], "lodash": []}
    graph = generate_graphviz_graph(dependencies)
    assert "express -> lodash" in graph.source, "Ошибка в generate_graphviz_graph: 'express -> lodash' отсутствует"


def test_save_graph():
    from graphviz import Digraph
    graph = Digraph(comment="Test Graph")
    graph.node("A")
    graph.node("B")
    graph.edge("A", "B")
    
    save_graph(graph, "test_output.png", "C:\\Program Files\\Graphviz\\bin\\dot.exe")
    assert os.path.exists("test_output.png"), "Ошибка в save_graph: файл не был создан"
    os.remove("test_output.png")


def test_load_config():
    with open("test_config.toml", "w") as f:
        f.write("""
[settings]
graphviz_path = "dot"
package_name = "express"
output_path = "output.png"
max_depth = 2
repository_url = "https://registry.npmjs.org"
        """)
    
    config = load_config("test_config.toml")
    assert config["settings"]["package_name"] == "express", "Ошибка в load_config: неверное имя пакета"
    assert config["settings"]["max_depth"] == 2, "Ошибка в load_config: неверная глубина анализа"
    os.remove("test_config.toml")


# Запуск всех тестов
if __name__ == "__main__":
    test_load_dependencies()
    print("test_load_dependencies пройден")
    
    test_normalize_version()
    print("test_normalize_version пройден")
    
    test_fetch_dependencies()
    print("test_fetch_dependencies пройден")
    
    test_collect_dependencies()
    print("test_collect_dependencies пройден")
    
    test_generate_graphviz_graph()
    print("test_generate_graphviz_graph пройден")
    
    test_save_graph()
    print("test_save_graph пройден")
    
    test_load_config()
    print("test_load_config пройден")
