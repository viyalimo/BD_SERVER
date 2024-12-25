import os
import datetime
import subprocess
import time

# Параметры подключения
DB_USER = "root"
DB_PASSWORD = "root"
DB_NAME = "mmi"
BACKUP_DIR = r"C:\Users\user1387\PycharmProjects\FastAPIProject\BD_DUMP"

# Полный путь к mysqldump
MYSQLDUMP_PATH = "C:\\wamp64\\bin\\mysql\\mysql8.3.0\\bin\\mysqldump.exe"

# Файл для хранения времени последнего бэкапа
LAST_BACKUP_FILE = os.path.join(BACKUP_DIR, "last_backup.txt")

def get_last_backup_time():
    """Получаем время последнего бэкапа из файла."""
    if os.path.exists(LAST_BACKUP_FILE):
        with open(LAST_BACKUP_FILE, "r") as file:
            last_time = file.read().strip()
            return datetime.datetime.strptime(last_time, "%Y-%m-%d %H:%M:%S")
    return None

def set_last_backup_time():
    """Записываем текущее время в файл последнего бэкапа."""
    with open(LAST_BACKUP_FILE, "w") as file:
        file.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

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
        set_last_backup_time()  # Записываем время успешного выполнения
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
    if not last_backup or (now - last_backup).total_seconds() > 86400:
        create_backup()
        delete_old_backups()
    else:
        print("Резервное копирование не требуется. Прошло менее 24 часов.")

if __name__ == "__main__":
    main()
