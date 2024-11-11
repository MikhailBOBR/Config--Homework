import zipfile
import posixpath
import io
import os
import argparse

def ls(zip_archive, current_directory):
    entries = set()
    for info in zip_archive.infolist():
        filename = info.filename.rstrip('/')
        if current_directory:
            if not filename.startswith(current_directory + '/'):
                continue
            path = filename[len(current_directory):].lstrip('/')
        else:
            path = filename
        entry = path.split('/')[0]
        entries.add(entry)
    for entry in sorted(entries):
        print(entry)

def cd(zip_archive, current_directory, path):
    new_path = posixpath.normpath(posixpath.join('/', current_directory, path)).lstrip('/')
    is_directory = False
    for info in zip_archive.infolist():
        filename = info.filename.rstrip('/')
        if (filename == new_path or filename.startswith(new_path + '/')) and info.filename.endswith('/'):
            is_directory = True
            break
    if is_directory:
        return new_path
    else:
        print(f"cd: {path}: Нет такого файла или каталога")
        return current_directory

def rm(zip_path, zip_archive, current_directory, path):
    target_path = posixpath.normpath(posixpath.join('/', current_directory, path)).lstrip('/')
    found = False
    for info in zip_archive.infolist():
        filename = info.filename.rstrip('/')
        if filename == target_path or filename.startswith(target_path + '/'):
            found = True
            break

    if not found:
        print(f"rm: {path}: Нет такого файла или каталога")
        return zip_archive

    new_zip_bytes = io.BytesIO()
    with zipfile.ZipFile(new_zip_bytes, 'w') as new_zip:
        for item in zip_archive.infolist():
            item_filename = item.filename.rstrip('/')
            if not (item_filename == target_path or item_filename.startswith(target_path + '/')):
                new_zip.writestr(item, zip_archive.read(item.filename))
    zip_archive.close()
    with open(zip_path, 'wb') as f:
        f.write(new_zip_bytes.getvalue())
    return zipfile.ZipFile(zip_path, 'a')

def rev(zip_archive, current_directory, filename):
    file_path = posixpath.normpath(posixpath.join('/', current_directory, filename)).lstrip('/')
    try:
        content = zip_archive.read(file_path).decode('utf-8')
        print(content[::-1])
    except KeyError:
        print(f"rev: {filename}: Нет такого файла")
    except UnicodeDecodeError:
        print(f"rev: {filename}: Не удалось прочитать содержимое файла")

def exit_shell(zip_archive):
    zip_archive.close()
    exit()

def main():
    parser = argparse.ArgumentParser(description="Virtual File System Shell")
    parser.add_argument("name", help="Set computer name for prompt display")
    parser.add_argument("path", help="Set path to the virtual file system archive")
    args = parser.parse_args()

    computer_name = args.name
    zip_path = args.path

    if not os.path.exists(zip_path):
        print(f"Ошибка: файл {zip_path} не найден.")
        return

    zip_archive = zipfile.ZipFile(zip_path, 'a')
    current_directory = ''

    while True:
        prompt_directory = '/' + current_directory if current_directory else '/'
        prompt = f"{computer_name}:{prompt_directory}$ "
        command_input = input(prompt).strip()
        command_parts = command_input.split()
        if not command_parts:
            continue
        command, *args = command_parts


        if command == 'exit':
            exit_shell(zip_archive)
        elif command == 'ls':
            ls(zip_archive, current_directory)
        elif command == 'cd':
            current_directory = cd(zip_archive, current_directory, args[0]) if args else ''
        elif command == 'rm':
            if args:
                zip_archive = rm(zip_path, zip_archive, current_directory, args[0])
            else:
                print("rm: Недостаточно аргументов")
        elif command == 'rev':
            if args:
                rev(zip_archive, current_directory, args[0])
            else:
                print("rev: Недостаточно аргументов")
        else:
            print(f"{command}: Команда не найдена")

if __name__ == '__main__':
    main()

#python shell_emulator.py MyComputer vfs_root.zip
