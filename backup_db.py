import os
import datetime
import subprocess
import time
import configparser

# Функция для чтения конфигурации
def read_config():
    """Читает параметры подключения к базе данных и время последнего бэкапа из `server_config.ini`"""
    base_dir = os.path.dirname(os.path.abspath(__file__))  # Определяем текущую папку
    filename = os.path.join(base_dir, "server_config.ini")  # Путь к конфигу

    if not os.path.exists(filename):
        raise FileNotFoundError(f"Файл конфигурации не найден: {filename}")

    config = configparser.ConfigParser()
    config.read(filename)

    try:
        db_settings = {
            "host": config["database"]["host"].strip(),
            "database": config["database"]["database"].strip(),
            "user": config["database"]["user"].strip(),
            "password": config["database"]["password"].strip(),
        }
        backup_settings = {
            "last_backup_time": config["backup"].get("last_backup_time", "1970-01-01 00:00:00").strip()
        }
        return db_settings, backup_settings, filename, config
    except KeyError as e:
        raise KeyError(f"Ошибка в конфигурационном файле: отсутствует ключ {e}")

# Загружаем конфиг
db_config, backup_config, config_file, config_parser = read_config()

# Параметры подключения
DB_USER = db_config["user"]
DB_PASSWORD = db_config["password"]
DB_NAME = db_config["database"]
BACKUP_DIR = os.path.join(os.path.dirname(__file__), "BD_DUMP")

# Полный путь к mysqldump (при необходимости можешь вынести в конфиг)
MYSQLDUMP_PATH = "C:\\wamp64\\bin\\mysql\\mysql8.3.0\\bin\\mysqldump.exe"

def get_last_backup_time():
    """Получаем время последнего бэкапа из конфигурационного файла"""
    try:
        return datetime.datetime.strptime(backup_config["last_backup_time"], "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return datetime.datetime(1970, 1, 1)  # Если формат времени неправильный

def set_last_backup_time():
    """Записываем текущее время в `server_config.ini`"""
    config_parser.set("backup", "last_backup_time", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    with open(config_file, "w") as configfile:
        config_parser.write(configfile)

def create_backup():
    """Создаём резервную копию базы данных."""
    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_file = os.path.join(BACKUP_DIR, f"{DB_NAME}_backup_{current_time}.sql")

    try:
        print("Создаётся резервная копия базы данных...")
        with open(backup_file, "w") as output_file:
            subprocess.run(
                [MYSQLDUMP_PATH, "-u", DB_USER, f"-p{DB_PASSWORD}", DB_NAME],
                stdout=output_file,
                check=True
            )
        print(f"Резервная копия успешно создана: {backup_file}")
        set_last_backup_time()  # Записываем новое время последнего бэкапа
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при создании резервной копии: {e}")

def delete_old_backups():
    """Удаление старых бэкапов старше 3 дней."""
    three_days_ago = time.time() - (3 * 24 * 60 * 60)
    for file in os.listdir(BACKUP_DIR):
        file_path = os.path.join(BACKUP_DIR, file)
        if os.path.isfile(file_path) and file.endswith(".sql"):
            if os.path.getmtime(file_path) < three_days_ago:
                os.remove(file_path)
                print(f"Удалена старая копия: {file_path}")

def main():
    """Основная функция: проверка времени и создание бэкапа."""
    last_backup = get_last_backup_time()
    now = datetime.datetime.now()

    # Проверка: прошло ли 24 часа с последнего бэкапа
    if (now - last_backup).total_seconds() > 86400:
        create_backup()
        delete_old_backups()
    else:
        print("Резервное копирование не требуется. Прошло менее 24 часов.")

if __name__ == "__main__":
    main()
