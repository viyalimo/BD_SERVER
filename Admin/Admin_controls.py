from BD import DB
from mysql.connector import Error
from Crypt.Crypt_controls import Crypt_controls

class Admin(Crypt_controls):
    def __init__(self):
        super().__init__()

    def command(self, admin_id: int, data: str):
        data = data.encode('utf-8')
        admin_info = DB.get_user_by_id(admin_id)
        if not admin_info or admin_info["user_role"] != "admin":
            return "Ошибка доступа!"
        else:
            message_data = self.decrypt_dict(admin_info["token"], data)
            print(message_data)
            if message_data["command"] == "edit_profile":
                result = self.edit_user(admin_id, message_data["data"])
                if isinstance(result, str):
                    return result
                elif isinstance(result, bytes):
                    return result.decode('utf-8')
            elif message_data["command"] == "get_user_info":
                result = self.get_all_users(admin_id).decode('utf-8')
                if isinstance(result, str):
                    return result
                elif isinstance(result, bytes):
                    return result.decode('utf-8')
            elif message_data["command"] == "edit_product":
                result = self.edit_product(admin_id, message_data["data"])
                if isinstance(result, str):
                    return result
                elif isinstance(result, bytes):
                    return result.decode('utf-8')
            elif message_data["command"] == "get_products_info":
                result = self.get_all_products(admin_id)
                if isinstance(result, str):
                    return result
                elif isinstance(result, bytes):
                    return result.decode('utf-8')
            elif message_data["command"] == "edit_order":
                result = self.edit_order(admin_id, message_data["data"])
                if isinstance(result, str):
                    return result
                elif isinstance(result, bytes):
                    return result.decode('utf-8')
            elif message_data["command"] == "get_orders_info":
                result = self.get_all_orders(admin_id)
                if isinstance(result, str):
                    return result
                elif isinstance(result, bytes):
                    return result.decode('utf-8')
            elif message_data["command"] == "edit_manufactures":
                result = self.edit_manufacturer(admin_id, message_data["data"])
                if isinstance(result, str):
                    return result
                elif isinstance(result, bytes):
                    return result.decode('utf-8')
            elif message_data["command"] == "get_manufacturer_info":
                result = self.get_all_manufacture(admin_id)
                if isinstance(result, str):
                    return result
                elif isinstance(result, bytes):
                    return result.decode('utf-8')
            elif message_data["command"] == "edit_cart":
                result = self.edit_cart_item(admin_id, message_data["data"])
                if isinstance(result, str):
                    return result
                elif isinstance(result, bytes):
                    return result.decode('utf-8')
            elif message_data["command"] == "add_product":
                return self.add_product(admin_id, message_data["data"])
            elif message_data["command"] == "delete_product":
                return self.delete_product(admin_id, message_data["data"])
            elif message_data["command"] == "delete_account":
                return self.delete_account(admin_id, message_data["data"])
            elif message_data["command"] == "block_account":
                return self.block_account(admin_id, message_data["data"])
            elif message_data["command"] == "add_manufacturer":
                return self.add_manufacturer(admin_id, message_data["data"])
            elif message_data["command"] == "delete_manufacturer":
                return self.delete_manufacturer(admin_id, message_data["data"])
            else:
                result = self.get_all_cart_items(admin_id)
                if isinstance(result, str):
                    return result
                elif isinstance(result, bytes):
                    return result.decode('utf-8')

    def edit_user(self, admin_id, data: dict):
        try:
            # Проверка роли администратора
            admin_info = DB.get_user_by_id(admin_id)
            if not admin_info or admin_info["user_role"] != "admin":
                response_message = "Ошибка доступа!"
                encrypted_response = self.encrypt_message(admin_info["token"].encode(), response_message)
                return encrypted_response
            else:
                access_key_admin = admin_info["token"]
                print(type(data), data)
                user_id = data["user_id"]
                print(type(user_id))
                update_data = data["update_data"]
                # Получение информации о пользователе для расшифровки
                user_info = DB.get_user_by_id(user_id)
                if not user_info:
                    response_message = "Пользователь не найден."
                    encrypted_response = self.encrypt_message(access_key_admin, response_message)
                    return encrypted_response

                token = user_info["token"]
                # print(type(token), token)
                # if not token and token != "null":
                #     response_message = "Ошибка: токен пользователя отсутствует!"
                #     encrypted_response = self.encrypt_message(access_key_admin, response_message)
                #     return encrypted_response

                # Формирование строки запроса для обновления
                fields = []
                values = []
                for key, value in update_data.items():
                    if key not in ["user_name", "password", "phone_number", "rule", "photo", "token"]:
                        response_message = f"Недопустимый параметр: {key}"
                        encrypted_response = self.encrypt_message(access_key_admin, response_message)
                        return encrypted_response
                    fields.append(f"{key} = %s")
                    values.append(value)

                # Проверка, есть ли поля для изменения
                if not fields:
                    response_message = "Нет данных для обновления!"
                    encrypted_response = self.encrypt_message(access_key_admin, response_message)
                    return encrypted_response


                # Выполнение запроса
                update_query = f"UPDATE users SET {', '.join(fields)} WHERE user_id = %s"
                values.append(user_id)
                DB._cursor.execute(update_query, tuple(values))
                DB._connection.commit()

                # Шифрование ответа
                response_message = "Данные пользователя успешно обновлены."
                encrypted_response = self.encrypt_message(access_key_admin, response_message)
                return encrypted_response

        except Error as e:
            return f"{e}"

    def get_all_users(self, admin_id: int):
        try:
            # Проверка роли администратора
            admin_info = DB.get_user_by_id(admin_id)
            if not admin_info or admin_info["user_role"] != "admin":
                response_message = "Ошибка доступа!"
                encrypted_response = self.encrypt_message(admin_info["token"].encode(), response_message)
                return encrypted_response

            # Запрос данных всех пользователей
            query = "SELECT * FROM users"
            DB._cursor.execute(query)
            users = DB._cursor.fetchall()

            # Формирование списка пользователей
            user_list = []
            for user in users:
                user_data = {
                    "user_id": user[0],
                    "user_name": user[1],
                    "password": user[2],
                    "phone_number": user[3],
                    "rule": user[4],
                    "photo": user[5],
                    "token": user[6]
                }
                user_list.append(user_data)
            # Шифрование данных ответа
            token_admin = admin_info["token"]
            encrypted_response = self.encrypt_dict(token_admin.encode(), user_list)
            return encrypted_response

        except Error as e:
            return f"Ошибка получения информации о клиентах: {e}"

    def edit_product(self, admin_id: int, data: dict):
        try:
            # Проверка роли администратора
            admin_info = DB.get_user_by_id(admin_id)
            if not admin_info or admin_info["user_role"] != "admin":
                response_message = "Ошибка доступа!"
                encrypted_response = self.encrypt_message(admin_info["token"].encode(), response_message)
                return encrypted_response

            # Расшифровка входных данных
            access_key_admin = admin_info["token"]
            product_id = data["product_id"]
            update_data = data["update_data"]
            # Формирование запроса для обновления
            fields = []
            values = []
            for key, value in update_data.items():
                if key not in ["product_name", "category", "manufacturer_id", "price", "total_purchases", "color",
                               "photo_base64", "warehouse"]:
                    response_message = f"Недопустимый параметр: {key}"
                    encrypted_response = self.encrypt_message(access_key_admin, response_message)
                    return encrypted_response
                fields.append(f"{key} = %s")
                values.append(value)

            # Проверка, есть ли данные для обновления
            if not fields:
                response_message = "Нет данных для обновления."
                encrypted_response = self.encrypt_message(access_key_admin, response_message)
                return encrypted_response

            # Выполнение запроса
            update_query = f"UPDATE products SET {', '.join(fields)} WHERE id = %s"
            values.append(product_id)
            DB._cursor.execute(update_query, tuple(values))
            DB._connection.commit()

            # Шифрование ответа
            response_message = "Данные о товаре успешно обновлены."
            encrypted_response = self.encrypt_message(access_key_admin.encode(), response_message)
            return encrypted_response

        except Error as e:
            return f"{e}"


    def get_all_products(self, admin_id: int):
        try:
            # Проверка роли администратора
            admin_info = DB.get_user_by_id(admin_id)
            if not admin_info or admin_info["user_role"] != "admin":
                response_message = "Ошибка доступа!"
                encrypted_response = self.encrypt_message(admin_info["token"].encode(), response_message)
                return encrypted_response

            # Запрос данных всех товаров
            query = "SELECT * FROM products"
            DB._cursor.execute(query)
            products = DB._cursor.fetchall()

            # Формирование списка товаров
            product_list = []
            for product in products:
                product_data = {
                    "id": product[0],
                    "product_name": product[1],
                    "category": product[2],
                    "manufacturer_id": product[3],
                    "price": float(product[4]),
                    "total_purchases": product[5],
                    "color": product[6],
                    "photo_base64": product[7],
                    "warehouse": product[8]
                }
                product_list.append(product_data)

            # Шифрование данных ответа
            token = admin_info["token"]
            encrypted_response = self.encrypt_dict(token.encode(), product_list)
            return encrypted_response

        except Error as e:
            return f"Ошибка получения информации о товарах: {e}"

    def edit_order(self, admin_id: int, data: dict):
        try:
            # Проверка роли администратора
            admin_info = DB.get_user_by_id(admin_id)
            if not admin_info or admin_info["user_role"] != "admin":
                response_message = "Ошибка доступа!"
                encrypted_response = self.encrypt_message(admin_info["token"].encode(), response_message)
                return encrypted_response

            # Формирование запроса для обновления
            admin_key_access = admin_info["token"]
            order_id = data["order_id"]
            update_data = data["update_data"]
            fields = []
            values = []
            for key, value in update_data.items():
                if key not in ["product_id", "user_id", "delivery_date", "quantity", "total_price", "status"]:
                    response_message = f"Недопустимый параметр: {key}"
                    encrypted_response = self.encrypt_message(admin_key_access, response_message)
                    return encrypted_response
                fields.append(f"{key} = %s")
                values.append(value)

            # Проверка, есть ли данные для обновления
            if not fields:
                response_message = "Нет данных для обновления."
                encrypted_response = self.encrypt_message(admin_key_access, response_message)
                return encrypted_response

            # Выполнение запроса
            update_query = f"UPDATE orders SET {', '.join(fields)} WHERE order_id = %s"
            values.append(order_id)
            DB._cursor.execute(update_query, tuple(values))
            DB._connection.commit()

            # Шифрование ответа
            response_message = "Данные о заказе успешно обновлены."
            encrypted_response = self.encrypt_message(admin_key_access.encode(), response_message)
            return encrypted_response

        except Error as e:
            return f"Ошибка редактирования заказа: {e}"

    def get_all_orders(self, admin_id: int):
        try:
            # Проверка роли администратора
            admin_info = DB.get_user_by_id(admin_id)
            if not admin_info or admin_info["user_role"] != "admin":
                response_message = "Ошибка доступа!"
                encrypted_response = self.encrypt_message(admin_info["token"].encode(), response_message)
                return encrypted_response

            # Запрос данных всех заказов
            query = "SELECT * FROM orders"
            DB._cursor.execute(query)
            orders = DB._cursor.fetchall()

            # Формирование списка заказов
            order_list = []
            for order in orders:
                order_data = {
                    "order_id": order[0],
                    "product_id": order[1],
                    "user_id": order[2],
                    "order_date": order[3].strftime("%Y-%m-%d %H:%M:%S") if order[3] else None,
                    "delivery_date": order[4].strftime("%Y-%m-%d") if order[4] else None,
                    "quantity": order[5],
                    "total_price": float(order[6]),
                    "status": order[7]
                }
                order_list.append(order_data)

            # Шифрование данных ответа
            token = admin_info["token"]
            encrypted_response = self.encrypt_dict(token.encode(), order_list)
            return encrypted_response

        except Error as e:
            return f"Ошибка получения информации о заказах: {e}"

    def edit_manufacturer(self, admin_id: int, data: dict):
        try:
            # Проверка роли администратора
            admin_info = DB.get_user_by_id(admin_id)
            if not admin_info or admin_info["user_role"] != "admin":
                response_message = "Ошибка доступа!"
                encrypted_response = self.encrypt_message(admin_info["token"].encode(), response_message)
                return encrypted_response

            # Формирование запроса для обновления
            admin_key_access = admin_info["token"]
            manufacturer_id = data["manufacturer_id"]
            update_data = data["update_data"]
            fields = []
            values = []
            for key, value in update_data.items():
                if key not in ["manufacturer_name", "logo_base64", "purchased_items_count"]:
                    response_message = f"Недопустимый параметр: {key}"
                    encrypted_response = self.encrypt_message(admin_key_access.encode(), response_message)
                    return encrypted_response
                fields.append(f"{key} = %s")
                values.append(value)

            # Проверка, есть ли данные для обновления
            if not fields:
                response_message = "Нет данных для обновления."
                encrypted_response = self.encrypt_message(admin_key_access.encode(), response_message)
                return encrypted_response

            # Выполнение запроса
            update_query = f"UPDATE manufacturers SET {', '.join(fields)} WHERE id = %s"
            values.append(manufacturer_id)
            DB._cursor.execute(update_query, tuple(values))
            DB._connection.commit()

            # Шифрование ответа
            response_message = "Данные о производителе успешно обновлены."
            encrypted_response = self.encrypt_message(admin_key_access.encode(), response_message)
            return encrypted_response

        except Error as e:
            return f"Ошибка редактирования производителя: {e}"

    def get_all_manufacture(self, admin_id: int):
        try:
            # Проверка роли администратора
            admin_info = DB.get_user_by_id(admin_id)
            if not admin_info or admin_info["user_role"] != "admin":
                response_message = "Ошибка доступа!"
                encrypted_response = self.encrypt_message(admin_info["token"].encode(), response_message)
                return encrypted_response


            # Запрос данных всех производителей
            query = "SELECT * FROM manufacturers"
            DB._cursor.execute(query)
            manufacturers = DB._cursor.fetchall()

            # Формирование списка производителей
            manufacturer_list = []
            for manufacturer in manufacturers:
                manufacturer_data = {
                    "id": manufacturer[0],
                    "manufacturer_name": manufacturer[1],
                    "logo_base64": manufacturer[2],
                    "purchased_items_count": manufacturer[3]
                }
                manufacturer_list.append(manufacturer_data)

            # Шифрование данных ответа
            token = admin_info["token"]
            encrypted_response = self.encrypt_dict(token.encode(), manufacturer_list)
            return encrypted_response

        except Error as e:
            return f"Ошибка получения информации о производителях: {e}"

    def edit_cart_item(self, admin_id: int, data: dict):
        try:
            # Проверка роли администратора
            admin_info = DB.get_user_by_id(admin_id)
            if not admin_info or admin_info["user_role"] != "admin":
                response_message = "Ошибка доступа!"
                encrypted_response = self.encrypt_message(admin_info["token"].encode(), response_message)
                return encrypted_response

            # Формирование запроса для обновления
            admin_key_access = admin_info["token"]
            cart_item_id = data["cart_item_id"]
            update_data = data["update_data"]
            fields = []
            values = []
            for key, value in update_data.items():
                if key not in ["cart_id", "product_id", "quantity", "is_paid"]:
                    response_message = f"Недопустимый параметр: {key}"
                    encrypted_response = self.encrypt_message(admin_key_access.encode(), response_message)
                    return encrypted_response
                fields.append(f"{key} = %s")
                values.append(value)

            # Проверка, есть ли данные для обновления
            if not fields:
                response_message = "Нет данных для обновления."
                encrypted_response = self.encrypt_message(admin_key_access.encode(), response_message)
                return encrypted_response


            # Выполнение запроса
            update_query = f"UPDATE cart_items SET {', '.join(fields)} WHERE cart_item_id = %s"
            values.append(cart_item_id)
            DB._cursor.execute(update_query, tuple(values))
            DB._connection.commit()

            # Шифрование ответа
            response_message = "Данные о товаре в корзине успешно обновлены."
            encrypted_response = self.encrypt_message(admin_key_access.encode(), response_message)
            return encrypted_response

        except Error as e:
            return f"Ошибка редактирования товара в корзине: {e}"

    def get_all_cart_items(self, admin_id: int):
        try:
            admin_info = DB.get_user_by_id(admin_id)
            if not admin_info or admin_info["user_role"] != "admin":
                responce_message = "Ошибка доступа!"
                token = admin_info["token"]
                encrypted_response = self.encrypt_dict(token.encode(), responce_message)

            # Запрос данных всех товаров в корзине
            query = "SELECT * FROM cart_items"
            DB._cursor.execute(query)
            cart_items = DB._cursor.fetchall()

            # Формирование списка товаров в корзине
            cart_item_list = []
            for cart_item in cart_items:
                cart_item_data = {
                    "cart_item_id": cart_item[0],
                    "cart_id": cart_item[1],
                    "product_id": cart_item[2],
                    "quantity": cart_item[3],
                    "is_paid": bool(cart_item[4])
                }
                cart_item_list.append(cart_item_data)

            # Шифрование данных ответа
            token = admin_info["token"]
            encrypted_response = self.encrypt_dict(token.encode(), cart_item_list)
            return encrypted_response

        except Error as e:
            return f"Ошибка получения информации о товарах в корзине: {e}"

    """Дополнительный функционал"""

    def add_product(self, admin_id: int, data: dict):
        try:
            admin_info = DB.get_user_by_id(admin_id)
            if not admin_info or admin_info["user_role"] != "admin":
                return self.encrypt_message(admin_info["token"].encode(), "Ошибка доступа!").decode()

            # Формирование запроса для добавления товара
            query = """
                INSERT INTO products (product_name, category, manufacturer_id, price, total_purchases, color, photo_base64, warehouse)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            data = data["update_data"]
            values = (
                data.get("product_name"),
                data.get("category"),
                data.get("manufacturer_id"),
                data.get("price"),
                data.get("total_purchases", 0),
                data.get("color"),
                data.get("photo_base64"),
                data.get("warehouse")
            )
            DB._cursor.execute(query, values)
            DB._connection.commit()
            return self.encrypt_message(admin_info["token"].encode(), "Товар успешно добавлен!").decode()
        except Error as e:
            admin_info = DB.get_user_by_id(admin_id)
            return self.encrypt_message(admin_info["token"].encode(), f"Ошибка добавления товара: {e}").decode()

    # Удаление товара
    def delete_product(self, admin_id: int, data:dict):
        try:
            admin_info = DB.get_user_by_id(admin_id)
            if not admin_info or admin_info["user_role"] != "admin":
                return self.encrypt_message(admin_info["token"].encode(), "Ошибка доступа!").decode()

            product_id = data["product_id"]
            # Удаление товара
            query = "DELETE FROM products WHERE id = %s"
            DB._cursor.execute(query, (product_id,))
            DB._connection.commit()
            return self.encrypt_message(admin_info["token"].encode(), "Товар успешно удален!").decode()
        except Error as e:
            admin_info = DB.get_user_by_id(admin_id)
            return self.encrypt_message(admin_info["token"].encode(), f"Ошибка удаления товара: {e}").decode()

    # Удаление аккаунта
    def delete_account(self, admin_id: int, data: dict):
        try:
            admin_info = DB.get_user_by_id(admin_id)
            if not admin_info or admin_info["user_role"] != "admin":
                return self.encrypt_message(admin_info["token"].encode(), "Ошибка доступа!").decode()

            user_id = data["user_id"]
            # Удаление аккаунта
            query = "DELETE FROM users WHERE user_id = %s"
            DB._cursor.execute(query, (user_id,))
            DB._connection.commit()
            return self.encrypt_message(admin_info["token"].encode(), "Аккаунт успешно удален!").decode()
        except Error as e:
            admin_info = DB.get_user_by_id(admin_id)
            return self.encrypt_message(admin_info["token"].encode(), f"Ошибка удаления аккаунта: {e}").decode()

    # Блокировка аккаунта (смена токена)
    def block_account(self, admin_id: int, data: dict):
        try:
            admin_info = DB.get_user_by_id(admin_id)
            if not admin_info or admin_info["user_role"] != "admin":
                return self.encrypt_message(admin_info["token"].encode(), "Ошибка доступа!").decode()

            # Генерация нового токена
            new_token = self.generate_key()
            user_id = data["user_id"]
            # Обновление токена пользователя
            query = "UPDATE users SET token = %s WHERE user_id = %s"
            DB._cursor.execute(query, (new_token, user_id))
            DB._connection.commit()
            return self.encrypt_message(admin_info["token"].encode(), "Пользователь заблокирован!").decode()
        except Error as e:
            admin_info = DB.get_user_by_id(admin_id)
            return self.encrypt_message(admin_info["token"].encode(), f"Ошибка блокировки пользователя: {e}").decode()

    # Добавление производителя
    def add_manufacturer(self, admin_id: int, data: dict):
        try:
            admin_info = DB.get_user_by_id(admin_id)
            if not admin_info or admin_info["user_role"] != "admin":
                return self.encrypt_message(admin_info["token"].encode(), "Ошибка доступа!").decode()

            # Формирование запроса для добавления производителя
            query = """
                INSERT INTO manufacturers (manufacturer_name, logo_base64, purchased_items_count)
                VALUES (%s, %s, %s)
            """
            data = data["add_data"]
            values = (
                data.get("manufacturer_name"),
                data.get("logo_base64"),
                data.get("purchased_items_count", 0)
            )
            DB._cursor.execute(query, values)
            DB._connection.commit()
            return self.encrypt_message(admin_info["token"].encode(), "Производитель успешно добавлен!").decode()
        except Error as e:
            admin_info = DB.get_user_by_id(admin_id)
            return self.encrypt_message(admin_info["token"].encode(), f"Ошибка добавления производителя: {e}").decode()

    # Удаление производителя
    def delete_manufacturer(self, admin_id: int, data: dict):
        try:
            admin_info = DB.get_user_by_id(admin_id)
            if not admin_info or admin_info["user_role"] != "admin":
                return self.encrypt_message(admin_info["token"].encode(), "Ошибка доступа!").decode()

            # Удаление производителя
            manufacturer_id = data["manufacturer_id"]
            query = "DELETE FROM manufacturers WHERE id = %s"
            DB._cursor.execute(query, (manufacturer_id,))
            DB._connection.commit()
            return self.encrypt_message(admin_info["token"].encode(), "Производитель успешно удален!").decode()
        except Error as e:
            admin_info = DB.get_user_by_id(admin_id)
            return self.encrypt_message(admin_info["token"].encode(), f"Ошибка удаления производителя: {e}").decode()


