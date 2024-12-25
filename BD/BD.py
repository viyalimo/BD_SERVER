import mysql.connector
from mysql.connector import Error
import hashlib  # Для хэширования паролей
from Crypt.Crypt_controls import Crypt_controls


class BD_connector:
    def __init__(self):
        self._connection, self._cursor = self.__connect_to_mysql()
        self.crp = Crypt_controls()

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
                    key = self.crp.generate_key()
                    if self.get_user_token(username):
                        return "Пользователь уже авторизован"
                    elif self.get_shop_state() == False and self.get_user_data(username) != 'admin':
                        return "Сайт временно недоступен!"
                    else:
                        self.update_user_token(username, key)
                        return ("key", key)
                else:
                    return "Неверный логин или пароль!"
            else:
                return "Неверный логин или пароль!"

        except Error as e:
            print("Ошибка проверки пользователя:", e)
            return False

    def register_user(self, username, password, phone_number):
        try:
            # Проверяем, существует ли уже такой пользователь
            query = """SELECT user_name FROM users WHERE user_name = %s"""
            self._cursor.execute(query, (username,))
            result = self._cursor.fetchone()

            if result:
                return "Пользователь с таким именем уже существует"
            if self.get_shop_state() == False and self.get_user_data(username) != 'admin':
                return "Сайт временно недоступен!"

            # Хэшируем пароль
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            # Добавляем нового пользователя в базу данных
            insert_query = """INSERT INTO users (user_name, password, phone_number) VALUES (%s, %s, %s)"""
            self._cursor.execute(insert_query, (username, hashed_password, phone_number))
            self._connection.commit()
            key = self.crp.generate_key()
            self.update_user_token(username, key)
            return ("key", key)

        except Error as e:
            print("Ошибка регистрации пользователя:", e)
            return False

    def close(self):
        self._cursor.close()
        self._connection.close()
        print("Соединение закрыто")

    # Функции для работы с таблицей products

    def add_product(self, product_name, category, manufacturer_id, price, total_purchases, color, photo_base64,
                    warehouse):
        try:
            query = """
            INSERT INTO products (product_name, category, manufacturer_id, price, total_purchases, color, photo_base64, warehouse)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            self._cursor.execute(query, (
            product_name, category, manufacturer_id, price, total_purchases, color, photo_base64, warehouse))
            self._connection.commit()
        except Error as e:
            print("Ошибка добавления продукта:", e)

    def delete_product(self, product_id):
        try:
            query = """DELETE FROM products WHERE id = %s"""
            self._cursor.execute(query, (product_id,))
            self._connection.commit()
        except Error as e:
            print("Ошибка удаления продукта:", e)

    def get_product_id(self, id_product: int):
        try:
            query = """SELECT 
                p.id, 
                p.product_name, 
                p.category, 
                m.manufacturer_name, 
                p.price, 
                p.total_purchases, 
                p.color, 
                p.photo_base64, 
                p.warehouse
            FROM products p
            JOIN manufacturers m ON p.manufacturer_id = m.id
            WHERE p.id = %s"""
            self._cursor.execute(query, (id_product,))
            result = self._cursor.fetchone()  # fetchone для получения одной строки
            return result
        except Error as e:
            print("Ошибка получения продукта по ID:", e)
            return None

    def get_all_products(self):
        try:
            query = """
            SELECT 
                p.id, 
                p.product_name, 
                p.category, 
                m.manufacturer_name, 
                p.price, 
                p.total_purchases, 
                p.color, 
                p.photo_base64, 
                p.warehouse
            FROM 
                products p
            JOIN 
                manufacturers m ON p.manufacturer_id = m.id
            """
            self._cursor.execute(query)
            result = self._cursor.fetchall()
            return result
        except Error as e:
            print("Ошибка получения продуктов:", e)
            return None

        # Функция для получения товаров по категории

    def get_products_by_category(self, category):
        try:
            query = """SELECT 
                p.id, 
                p.product_name, 
                p.category, 
                m.manufacturer_name, 
                p.price, 
                p.total_purchases, 
                p.color, 
                p.photo_base64, 
                p.warehouse
            FROM products p
            JOIN manufacturers m ON p.manufacturer_id = m.id
            WHERE p.category = %s"""
            self._cursor.execute(query, (category,))
            result = self._cursor.fetchall()
            return result
        except Error as e:
            print("Ошибка получения продуктов по категории:", e)
            return None

        # Функция для получения товаров, отсортированных по количеству покупок

    def get_products_by_total_purchases_desc(self):
        try:
            query = """SELECT 
                p.id, 
                p.product_name, 
                p.category, 
                m.manufacturer_name, 
                p.price, 
                p.total_purchases, 
                p.color, 
                p.photo_base64, 
                p.warehouse
            FROM products p
            JOIN manufacturers m ON p.manufacturer_id = m.id
            WHERE p.total_purchases > 0
            ORDER BY p.total_purchases DESC"""
            self._cursor.execute(query)
            result = self._cursor.fetchall()
            return result
        except Error as e:
            print("Ошибка получения товаров по количеству покупок:", e)
            return None

        # Функция для получения товаров по производителю

    def get_products_by_manufacturer(self, manufacturer_name):
        try:
            query = """
            SELECT 
                p.id, 
                p.product_name, 
                p.category, 
                m.manufacturer_name, 
                p.price, 
                p.total_purchases, 
                p.color, 
                p.photo_base64, 
                p.warehouse
            FROM 
                products p
            JOIN 
                manufacturers m ON p.manufacturer_id = m.id
            WHERE 
                m.manufacturer_name = %s
            """
            self._cursor.execute(query, (manufacturer_name,))
            result = self._cursor.fetchall()
            return result
        except Error as e:
            print("Ошибка получения продуктов по производителю:", e)
            return None

    def add_manufacturer(self, manufacturer_name, image_path=None):
        try:
            # Конвертируем изображение в Base64, если путь указан
            if image_path:
                logo_base64 = image_to_base64(image_path)
                if not logo_base64:
                    print("Ошибка конвертации изображения. Производитель не добавлен.")
                    return "Ошибка конвертации изображения"
            else:
                logo_base64 = None

            # Запрос на добавление данных
            query = """
            INSERT INTO manufacturers (manufacturer_name, logo_base64)
            VALUES (%s, %s)
            """
            self._cursor.execute(query, (manufacturer_name, logo_base64))
            self._connection.commit()
            return "Производитель успешно добавлен"
        except Error as e:
            print("Ошибка добавления производителя:", e)
            return None

    def get_all_manufacturers(self):
        try:
            query = """
            SELECT id, manufacturer_name, logo_base64, purchased_items_count
            FROM manufacturers
            """
            self._cursor.execute(query)
            result = self._cursor.fetchall()
            return result
        except Error as e:
            print("Ошибка получения производителей:", e)
            return None

    def get_manufacturer_by_id(self, manufacturer_id):
        try:
            query = """
            SELECT id, manufacturer_name, logo_base64, purchased_items_count
            FROM manufacturers
            WHERE id = %s
            """
            self._cursor.execute(query, (manufacturer_id,))
            result = self._cursor.fetchone()  # Используем fetchone, так как ожидаем одну запись
            if result:
                return result
            else:
                return f"Производитель с ID {manufacturer_id} не найден"
        except Error as e:
            print("Ошибка получения производителя по ID:", e)
            return None

    def update_user_token(self, username: str, token: str):
        try:
            query = "UPDATE users SET token = %s WHERE user_name = %s"
            self._cursor.execute(query, (token, username))
            self._connection.commit()
        except Error as e:
            print(f"Ошибка при обновлении токена для пользователя {username}: {e}")

    def get_user_by_id(self, user_id: int):
        try:
            query = "SELECT * FROM users WHERE user_id = %s"
            self._cursor.execute(query, (user_id,))
            result = self._cursor.fetchone()
            if result:
                user_info = {
                    "user_role": result[4],
                    "token": result[6]
                }
                return user_info
            else:
                print(f"Пользователь с ID {user_id} не найден")
                return None
        except Error as e:
            print(f"Ошибка получения пользователя с ID {user_id}: {e}")
            return None

    def get_user_token(self, username: str):
        try:
            query = "SELECT token FROM users WHERE user_name = %s"
            self._cursor.execute(query, (username,))
            result = self._cursor.fetchone()
            if result and result[0]:
                return result[0]
            else:
                print(f"Токен для пользователя {username} не найден или пуст")
                return None
        except Error as e:
            print(f"Ошибка получения токена для пользователя {username}: {e}")
            return None

    def get_user_data(self, username: str):
        try:
            query = "SELECT * FROM users WHERE user_name = %s"
            self._cursor.execute(query, (username,))
            result = self._cursor.fetchone()
            if result:
                user_info = result[4]
                return user_info
            else:
                print(f"Пользователь с именем {username} не найден")
                return None
        except Error as e:
            print(f"Ошибка получения пользователя с именем {username}: {e}")
            return None

    def get_user_by_name(self, username: str):
        try:
            query = "SELECT * FROM users WHERE user_name = %s"
            self._cursor.execute(query, (username,))
            result = self._cursor.fetchone()
            if result:
                user_info = f"{result[0]},{result[1]},{result[3]},{result[4]},{result[5]}"
                user_info = self.crp.encrypt_message(result[6], user_info)
                return user_info
            else:
                print(f"Пользователь с именем {username} не найден")
                return None
        except Error as e:
            print(f"Ошибка получения пользователя с именем {username}: {e}")
            return None

    def update_photo(self, user_id: int, photo_base64: str):
        try:
            query = "UPDATE users SET photo = %s WHERE user_id = %s"
            self._cursor.execute(query, (photo_base64, user_id))
            self._connection.commit()
            return True
        except Error as e:
            print(f"Ошибка обновления фотографии пользователя: {e}")
            return False

    def update_password(self, user_id: int, new_password: str):
        try:
            # Хэшируем пароль
            hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
            query = "UPDATE users SET password = %s WHERE user_id = %s"
            self._cursor.execute(query, (hashed_password, user_id))
            self._connection.commit()
            return True
        except Error as e:
            print(f"Ошибка обновления пароля пользователя: {e}")
            return False

    def update_phone_number(self, user_id: int, new_phone_number: str):
        try:
            query = "UPDATE users SET phone_number = %s WHERE user_id = %s"
            self._cursor.execute(query, (new_phone_number, user_id))
            self._connection.commit()
            return True
        except Error as e:
            print(f"Ошибка обновления номера телефона пользователя: {e}")
            return False

    def delete_account(self, user_id: int):
        try:
            # Удаляем все данные пользователя из таблицы users
            query = "DELETE FROM users WHERE user_id = %s"
            self._cursor.execute(query, (user_id,))
            self._connection.commit()
            return True
        except Error as e:
            print(f"Ошибка при удалении аккаунта пользователя: {e}")
            return False

    def logout_user(self, user_id: int):
        try:
            # Обнуляем токен пользователя
            query = "UPDATE users SET token = %s WHERE user_id = %s"
            self._cursor.execute(query, (None, user_id))
            self._connection.commit()
            return True
        except Error as e:
            print(f"Ошибка при выходе пользователя: {e}")
            return False

    def search_products(self, search_term=None, category=None, min_price=None, max_price=None, manufacturer=None,
                        color=None, sort_by=None):
        query = """
        SELECT p.id, p.product_name, p.category, p.price, p.total_purchases, p.color, p.photo_base64, p.warehouse, 
               m.manufacturer_name
        FROM products p
        JOIN manufacturers m ON p.manufacturer_id = m.id
        WHERE 1=1
        """

        params = []

        # Условия для поиска по названию товара
        if search_term:
            query += " AND p.product_name LIKE %s"
            params.append(f"%{search_term}%")

        # Условия для поиска по категории
        if category:
            query += " AND p.category LIKE %s"
            params.append(f"%{category}%")

        # Условия для фильтрации по цене
        if min_price and max_price:
            query += " AND p.price BETWEEN %s AND %s"
            params.extend([float(min_price), float(max_price)])

        # Условия для поиска по производителю
        if manufacturer:
            query += " AND m.manufacturer_name LIKE %s"
            params.append(f"%{manufacturer}%")

        # Условия для поиска по цвету
        if color:
            query += " AND p.color LIKE %s"
            params.append(f"%{color}%")

        # Условия для фильтрации по наличию товара на складе
        query += " AND p.warehouse > 0"

        # Сортировка
        if sort_by == 'price':
            query += " ORDER BY p.price"
        elif sort_by == 'popularity':
            query += " ORDER BY p.total_purchases DESC"
        elif sort_by == 'new':
            query += " ORDER BY p.id DESC"

        # Выполнение запроса
        self._cursor.execute(query, tuple(params))
        results = self._cursor.fetchall()
        return results

    def get_shop_state(self):
        query = "SELECT state FROM `state_shop` WHERE id=1"
        self._cursor.execute(query)
        results = self._cursor.fetchall()
        state = True if results[0][0] == 1 else False
        return state

    def manage_state_shop(self, user_id: int):
        role_user = self.get_user_by_id(user_id)["user_role"]
        if role_user == "admin":
            if self.get_user_by_id(user_id):
                if self.get_shop_state():
                    query = "UPDATE `state_shop` SET state = 0 WHERE id=1"
                    self._cursor.execute(query)
                    return False
                else:
                    query = "UPDATE `state_shop` SET state = 1 WHERE id=1"
                    self._cursor.execute(query)
                    return True
        else:
            return "Нет прав доступа!"



import base64


def image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            # Чтение файла в байты
            image_bytes = image_file.read()

            # Преобразование в base64
            encoded_image = base64.b64encode(image_bytes).decode('utf-8')
            return encoded_image
    except Exception as e:
        print(f"Ошибка при конвертации изображения: {e}")
        return None

def base64_to_image(base64_data, output_path):
    try:
        # Декодируем строку base64 в байты
        image_data = base64.b64decode(base64_data)

        # Записываем байты в файл с расширением .jpg
        with open(output_path, "wb") as image_file:
            image_file.write(image_data)

        print(f"Изображение успешно сохранено в {output_path}")
    except Exception as e:
        print(f"Ошибка при сохранении изображения: {e}")

#
# if __name__ == '__main__':
#     BD = BD_connector()
#     print(BD.manage_state_shop(15))

# if __name__ == '__main__':
#     BD = BD_connector()
#     for i in BD.search_products(color="чёрный"):
#         print(i)
# if __name__ == '__main__':
#     BD = BD_connector()
#     print(BD.get_user_token("Alice"))
#     if BD.get_user_token("Alice"):
#         print("AHAHHAHHAHAHHAH")
#     else:
#         print("DDDDDDDDDDDDDDDDDDDDDD")


"""Добавление продукта"""
# if __name__ == "__main__":
#     connector = BD_connector()
#     # Указываем путь к изображению продукта
#     image_path = r"C:\Users\user1387\PycharmProjects\FastAPIProject\images\YRS-24B.jpg"
#     # Конвертируем изображение в строку Base64
#     photo_base64 = image_to_base64(image_path)
#     # Данные для добавления товара
#     product_name = "YRS-24B"
#     category = "Духовые"
#     manufacturer_id = 1  # ID производителя из таблицы `manufacturers`
#     price = 990.00
#     total_purchases = 1
#     color = "белый"
#     warehouse = 100
#     # Вызов метода для добавления товара
#     connector.add_product(
#         product_name=product_name,
#         category=category,
#         manufacturer_id=manufacturer_id,
#         price=price,
#         total_purchases=total_purchases,
#         color=color,
#         photo_base64=photo_base64,  # Передаём изображение в формате Base64
#         warehouse=warehouse
#     )

"""Добавление производителя"""
# if __name__ == "__main__":
#     connector = BD_connector()
#
#     # Указываем путь к изображению
#     image_path = r"C:\Users\user1387\PycharmProjects\FastAPIProject\images\MARSHALL.jpg"
#
#     # Добавляем производителя с изображением
#     connector.add_manufacturer("MARSHALL", image_path)



