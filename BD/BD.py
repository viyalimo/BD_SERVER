import mysql.connector
from mysql.connector import Error
import hashlib  # Для хэширования паролей

class BD_connector:
    def __init__(self):
        self._connection, self._cursor = self.__connect_to_mysql()

    def __connect_to_mysql(self):
        try:
            # Параметры подключения
            connection = mysql.connector.connect(
                host='localhost',  # Адрес сервера базы данных
                database='mmi',  # Имя базы данных
                user='root',  # Имя пользователя
                password='root'  # Пароль пользователя
            )

            if connection.is_connected():
                print("Успешное подключение к базе данных")

                # Получаем информацию о сервере
                db_info = connection.get_server_info()
                print("Версия MySQL:", db_info)

                # Возвращаем соединение и курсор
                return connection, connection.cursor()

        except Error as e:
            print("Ошибка подключения к MySQL:", e)
            return None, None

    def execute_query(self, query, params=None):
        try:
            self._cursor.execute(query, params)
            self._connection.commit()
            print("Запрос успешно выполнен")
        except Error as e:
            print("Ошибка выполнения запроса:", e)

    def verify_user(self, username, password):
        try:
            # Хэшируем введенный пароль для сравнения с базой данных
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            # Выполняем запрос
            query = "SELECT password FROM users WHERE user_name = %s"
            self._cursor.execute(query, (username,))
            result = self._cursor.fetchone()

            # Проверяем результат
            if result:
                stored_password = result[0]
                if hashed_password == stored_password:
                    return "Аутентификация успешна"
                else:
                   return "Неверный логин или пароль!"
            else:
                return "Неверный логин или пароль!"


        except Error as e:
            print("Ошибка проверки пользователя:", e)
            return False

    def register_user(self, username, password, phone_number):
        # try:
        # Проверяем, существует ли уже такой пользователь
        query = "SELECT user_name FROM users WHERE user_name = %s"
        self._cursor.execute(query, (username,))
        result = self._cursor.fetchone()

        if result:
            return "Пользователь с таким именем уже существует"

        # Хэшируем пароль
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Добавляем нового пользователя в базу данных
        insert_query = "INSERT INTO users (user_name, password, phone_number) VALUES (%s, %s, %s)"
        self._cursor.execute(insert_query, (username, hashed_password, phone_number))
        self._connection.commit()
        return "Пользователь успешно зарегистрирован"

        # except Error as e:
        #     print("Ошибка регистрации пользователя:", e)
        #     return False

    def close(self):
        self._cursor.close()
        self._connection.close()
        print("Соединение закрыто")



