import zipfile
import io
from shell_emulator import ls, cd, rm, rev

# Создаем виртуальный zip-файл в памяти
def create_test_zip():
    zip_bytes = io.BytesIO()
    with zipfile.ZipFile(zip_bytes, 'w') as zip_archive:
        zip_archive.writestr('file1.txt', 'Hello, world!')
        zip_archive.writestr('dir1/', '')
        zip_archive.writestr('dir1/file2.txt', 'Python testing')
    zip_bytes.seek(0)
    return zipfile.ZipFile(zip_bytes, 'a')

# Тесты для ls
def test_ls():
    global successful_tests, total_tests
    zip_archive = create_test_zip()
    current_directory = ''

    # Проверка содержимого корневого каталога
    print("Тест ls - корневой каталог")
    ls(zip_archive, current_directory)  # Ожидаем увидеть 'dir1' и 'file1.txt'

    # Проверка содержимого подкаталога
    current_directory = 'dir1'
    print("\nТест ls - подкаталог dir1")
    ls(zip_archive, current_directory)  # Ожидаем увидеть 'file2.txt'

    zip_archive.close()

# Тесты для cd
def test_cd():
    global successful_tests, total_tests
    zip_archive = create_test_zip()
    current_directory = ''

    # Переход в подкаталог dir1
    total_tests += 1
    new_directory = cd(zip_archive, current_directory, 'dir1')
    assert new_directory == 'dir1', "Ошибка: переход в подкаталог dir1 не выполнен корректно"
    print("Тест cd - переход в подкаталог dir1 прошел успешно")

    # Переход в несуществующий каталог
    new_directory = cd(zip_archive, current_directory, 'nonexistent')
    assert new_directory == current_directory, "Ошибка: переход в несуществующий каталог должен возвращать текущий каталог"
    print("Тест cd - переход в несуществующий каталог прошел успешно")

    zip_archive.close()

# Тесты для rm
def test_rm():
    global successful_tests, total_tests
    zip_archive = create_test_zip()
    current_directory = ''

    # Удаление файла file1.txt
    rm('filesystem.zip', zip_archive, current_directory, 'file1.txt')
    try:
        zip_archive.getinfo('file1.txt')
        print("Ошибка: файл file1.txt должен был быть удален")
    except KeyError:
        print("Тест rm - удаление файла file1.txt прошло успешно")

    # Попытка удаления несуществующего файла
    original_file_count = len(zip_archive.infolist())
    rm('filesystem.zip', zip_archive, current_directory, 'nonexistent.txt')
    assert len(zip_archive.infolist()) == original_file_count, "Ошибка: количество файлов изменилось при попытке удаления несуществующего файла"
    print("Тест rm - попытка удаления несуществующего файла прошла успешно")

    zip_archive.close()

# Тесты для rev
def test_rev():
    global successful_tests, total_tests
    zip_archive = create_test_zip()
    current_directory = ''

    # Реверсирование содержимого файла file1.txt
    print("Тест rev - реверсирование файла file1.txt")
    rev(zip_archive, current_directory, 'file1.txt')  # Ожидаем увидеть "!dlrow ,olleH"

    # Попытка реверсирования несуществующего файла
    print("\nТест rev - реверсирование несуществующего файла nonexistent.txt")
    rev(zip_archive, current_directory, 'nonexistent.txt')  # Ожидаем сообщение об ошибке

    zip_archive.close()

# Функция для запуска всех тестов
def run_tests():
    print("Запуск тестов для ls")
    test_ls()

    print("\nЗапуск тестов для cd")
    test_cd()

    print("\nЗапуск тестов для rm")
    test_rm()

    print("\nЗапуск тестов для rev")
    test_rev()

    # Вывод итогового сообщения
    print(f"\nВсе тесты завершены успешно!")

# Запускаем все тесты
run_tests()
