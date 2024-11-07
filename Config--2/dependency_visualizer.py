import json
import toml
import requests
import subprocess
from graphviz import Digraph
import re


def load_config(config_path):
    with open(config_path, 'r') as f:
        return toml.load(f)


def load_dependencies(package_file):
    with open(package_file, 'r') as f:
        data = json.load(f)
    dependencies = data.get("dependencies", {})
    dependencies.update(data.get("devDependencies", {}))
    return dependencies


def normalize_version(version):
    # Извлекаем версию в формате x.x.x, игнорируя символы ~ или ^
    match = re.search(r"(\d+\.\d+\.\d+)", version)
    if match:
        return match.group(0)
    return "latest"


def fetch_dependencies(pkg, version="latest", repository_url="https://registry.npmjs.org"):
    url = f"{repository_url}/{pkg}/{version}"
    response = requests.get(url)
    
    if response.status_code == 200:
        try:
            package_data = response.json()
            return package_data.get("dependencies", {})
        except json.JSONDecodeError:
            print(f"Failed to parse response for {pkg}@{version}")
            return {}
    else:
        print(f"Failed to fetch {pkg}@{version}")
        return {}


def collect_dependencies(dependencies, repository_url, max_depth, all_dependencies=None, visited=None, depth=1):
    if all_dependencies is None:
        all_dependencies = {}
    if visited is None:
        visited = set()

    if depth > max_depth:
        return all_dependencies

    for pkg, version in dependencies.items():
        if pkg in visited:
            continue
        visited.add(pkg)

        normalized_version = normalize_version(version)
        
        # Добавление зависимостей пакета
        if pkg not in all_dependencies:
            all_dependencies[pkg] = []

        deps = fetch_dependencies(pkg, normalized_version, repository_url)
        all_dependencies[pkg].extend(deps.keys())
        
        # Рекурсивно собираем зависимости с учетом глубины
        collect_dependencies(deps, repository_url, max_depth, all_dependencies, visited, depth + 1)

    return all_dependencies


def generate_graphviz_graph(dependencies):
    graph = Digraph(comment="Dependency Graph")
    for pkg, deps in dependencies.items():
        for dep in deps:
            graph.edge(pkg, dep)
    return graph


def save_graph(graph, output_path, graphviz_path):
    graph_file = output_path.replace(".png", ".dot")
    graph.save(graph_file)
    try:
        subprocess.run([graphviz_path, "-Tpng", graph_file, "-o", output_path], check=True)
        print("Graph successfully saved to", output_path)
    except subprocess.CalledProcessError as e:
        print("Error generating graph:", e)


def main():
    config = load_config("config.toml")
    graphviz_path = config["settings"]["graphviz_path"]
    package_name = config["settings"]["package_name"]
    output_path = config["settings"]["output_path"]
    max_depth = config["settings"]["max_depth"]
    repository_url = config["settings"]["repository_url"]

    print(f"Generating dependency graph for package '{package_name}' from repository '{repository_url}' with max depth {max_depth}")

    dependencies = load_dependencies("package_dependecies.json")
    all_dependencies = collect_dependencies(dependencies, repository_url, max_depth)
    graph = generate_graphviz_graph(all_dependencies)
    save_graph(graph, output_path, graphviz_path)


if __name__ == "__main__":
    main()
