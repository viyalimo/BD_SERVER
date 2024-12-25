class CartManager:
    def __init__(self, db_connector):
        self.db_connector = db_connector  # Экземпляр BD_connector
        self.cursor = db_connector._cursor
        self.connection = db_connector._connection
        self.shop_state = self.db_connector.get_shop_state()

    # 1. Добавление одного товара в корзину
    def add_to_cart(self, user_id, product_id):
        role_user = self.db_connector.get_user_by_id(user_id)["user_role"]
        if role_user == "admin" or self.shop_state:
            try:
                # Проверка наличия товара на складе
                query_check_stock = "SELECT warehouse FROM products WHERE id = %s"
                self.cursor.execute(query_check_stock, (product_id,))
                result = self.cursor.fetchone()

                if not result:
                    print("Товар не найден.")
                    return False

                warehouse = result[0]

                if warehouse == 0:
                    print(f"Товар с ID {product_id} отсутствует на складе.")
                    return "Товар отсутствует на складе"

                # Получаем cart_id пользователя
                query_get_cart = "SELECT cart_id FROM cart WHERE user_id = %s"
                self.cursor.execute(query_get_cart, (user_id,))
                cart_result = self.cursor.fetchone()

                if not cart_result:
                    print(f"Корзина для пользователя {user_id} не найдена.")
                    return False

                cart_id = cart_result[0]

                # Добавляем товар по одной единице
                query_add = """
                    INSERT INTO cart_items (cart_id, product_id, quantity)
                    VALUES (%s, %s, 1)
                """
                self.cursor.execute(query_add, (cart_id, product_id))
                self.connection.commit()
                print(f"Товар {product_id} добавлен в корзину пользователя {user_id}.")
                return True
            except Exception as e:
                print("Ошибка добавления товара в корзину:", e)
                return False
        else:
            return None

    # 2. Удаление одного товара из корзины
    def remove_from_cart(self, user_id, product_id):
        role_user = self.db_connector.get_user_by_id(user_id)["user_role"]
        if role_user == "admin" or self.shop_state:
            try:
                # Получаем cart_id пользователя
                query_get_cart = "SELECT cart_id FROM cart WHERE user_id = %s"
                self.cursor.execute(query_get_cart, (user_id,))
                cart_result = self.cursor.fetchone()

                if not cart_result:
                    print(f"Корзина для пользователя {user_id} не найдена.")
                    return False

                cart_id = cart_result[0]

                # Удаляем один товар из корзины
                query_remove = """
                    DELETE FROM cart_items 
                    WHERE cart_id = %s AND product_id = %s 
                    LIMIT 1
                """
                self.cursor.execute(query_remove, (cart_id, product_id))
                self.connection.commit()
                print(f"Товар {product_id} удалён из корзины пользователя {user_id}.")
                return True
            except Exception as e:
                print("Ошибка удаления товара из корзины:", e)
                return False
        else: return None


    # 3. Получение содержимого корзины пользователя
    def get_cart_items(self, user_id):
        role_user = self.db_connector.get_user_by_id(user_id)["user_role"]
        if role_user == "admin" or self.shop_state:
            try:
                query = """
                    SELECT ci.product_id
                    FROM cart_items ci
                    JOIN cart c ON ci.cart_id = c.cart_id
                    WHERE c.user_id = %s
                """
                self.cursor.execute(query, (user_id,))
                items = self.cursor.fetchall()
                # Преобразуем результат в список ID товаров
                product_ids = [item[0] for item in items]
                return product_ids
            except Exception as e:
                print("Ошибка получения ID товаров из корзины:", e)
                return []
        else: return None

    # 4. Очистка корзины пользователя
    def clear_cart(self, user_id):
        role_user = self.db_connector.get_user_by_id(user_id)["user_role"]
        if role_user == "admin" or self.shop_state:
            try:
                # Получаем cart_id пользователя
                query_get_cart = "SELECT cart_id FROM cart WHERE user_id = %s"
                self.cursor.execute(query_get_cart, (user_id,))
                cart_result = self.cursor.fetchone()

                if not cart_result:
                    print(f"Корзина для пользователя {user_id} не найдена.")
                    return False

                cart_id = cart_result[0]

                # Удаляем все товары из корзины
                query_clear = "DELETE FROM cart_items WHERE cart_id = %s"
                self.cursor.execute(query_clear, (cart_id,))
                self.connection.commit()
                print(f"Корзина пользователя {user_id} успешно очищена.")
                return True
            except Exception as e:
                print("Ошибка очистки корзины:", e)
                return False
        else: return None

    # 5. Создание заказа для одного товара из корзины
    def create_order_for_single_item(self, user_id, product_id):
        role_user = self.db_connector.get_user_by_id(user_id)["user_role"]
        if role_user == "admin" or self.shop_state:
            try:
                # Получаем cart_id пользователя
                query_get_cart = "SELECT cart_id FROM cart WHERE user_id = %s"
                self.cursor.execute(query_get_cart, (user_id,))
                cart_result = self.cursor.fetchone()

                if not cart_result:
                    print(f"Корзина для пользователя {user_id} не найдена.")
                    return False

                cart_id = cart_result[0]

                # Получаем информацию о товаре из корзины
                query_get_item = """
                    SELECT p.price, ci.quantity, ci.cart_item_id
                    FROM cart_items ci
                    JOIN products p ON ci.product_id = p.id
                    WHERE ci.cart_id = %s AND ci.product_id = %s
                    LIMIT 1
                """
                self.cursor.execute(query_get_item, (cart_id, product_id))
                item = self.cursor.fetchone()

                if not item:
                    print("Товар не найден в корзине.")
                    return False

                price, quantity, cart_item_id = item
                total_price = price * quantity

                # Сначала обновляем поле is_paid
                query_update_paid = "UPDATE cart_items SET is_paid = 1 WHERE cart_item_id = %s"
                self.cursor.execute(query_update_paid, (cart_item_id,))
                print(f"Поле is_paid обновлено для товара с cart_item_id = {cart_item_id}")

                # Создаём заказ
                # query_insert_order = """
                #     INSERT INTO orders (product_id, user_id, quantity, total_price, status)
                #     VALUES (%s, %s, %s, %s, 'pending')
                # """
                # self.cursor.execute(query_insert_order, (product_id, user_id, quantity, total_price))

                # Удаляем товар из корзины
                query_delete_item = """
                    DELETE FROM cart_items 
                    WHERE cart_item_id = %s
                """
                self.cursor.execute(query_delete_item, (cart_item_id,))

                self.connection.commit()
                print(f"Заказ для товара {product_id} пользователя {user_id} успешно создан.")
                return True
            except Exception as e:
                print("Ошибка создания заказа для одного товара:", e)
                return False
        else: return None

    # 6. Создание заказа напрямую, минуя корзину
    def create_direct_order(self, user_id, product_id, quantity=1):
        role_user = self.db_connector.get_user_by_id(user_id)["user_role"]
        if role_user == "admin" or self.shop_state:
            try:
                # Проверяем количество на складе
                query_get_price = "SELECT price, warehouse FROM products WHERE id = %s"
                self.cursor.execute(query_get_price, (product_id,))
                result = self.cursor.fetchone()

                if not result:
                    print("Товар не найден.")
                    return False

                price, warehouse = result

                if warehouse < quantity:
                    print(f"Недостаточное количество товара на складе. Доступно: {warehouse}.")
                    return "Товара нет на складе"

                total_price = price * quantity

                # Создаём заказ
                query_insert_order = """
                    INSERT INTO orders (product_id, user_id, quantity, total_price, status)
                    VALUES (%s, %s, %s, %s, 'pending')
                """
                self.cursor.execute(query_insert_order, (product_id, user_id, quantity, total_price))

                # Уменьшаем количество на складе
                query_update_warehouse = "UPDATE products SET warehouse = warehouse - %s WHERE id = %s"
                self.cursor.execute(query_update_warehouse, (quantity, product_id))

                self.connection.commit()
                print(f"Заказ для товара {product_id} пользователя {user_id} успешно создан напрямую.")
                return True
            except Exception as e:
                print("Ошибка создания прямого заказа:", e)
                return False
        else: return None

    # 7. Отмена заказа
    def cancel_order(self, user_id, order_id):
        role_user = self.db_connector.get_user_by_id(user_id)["user_role"]
        if role_user == "admin" or self.shop_state:
            try:
                # Получаем информацию о заказе
                query_get_order = """
                    SELECT product_id, quantity, status 
                    FROM orders 
                    WHERE order_id = %s
                """
                self.cursor.execute(query_get_order, (order_id,))
                order = self.cursor.fetchone()

                if not order:
                    print(f"Заказ с ID {order_id} не найден.")
                    return False

                product_id, quantity, status = order

                # Проверяем статус заказа
                if status == 'canceled':
                    print(f"Заказ {order_id} уже отменён.")
                    return "Заказ уже отменён"

                # Обновляем статус заказа на 'canceled'
                query_update_status = """
                    UPDATE orders 
                    SET status = 'canceled' 
                    WHERE order_id = %s
                """
                self.cursor.execute(query_update_status, (order_id,))

                # Возвращаем количество товара на склад
                # query_update_stock = """
                #     UPDATE products
                #     SET warehouse = warehouse + 1
                #     WHERE id = %s
                # """
                # self.cursor.execute(query_update_stock, (product_id,))

                self.connection.commit()
                print(f"Заказ {order_id} успешно отменён. Товар возвращён на склад.")
                return True
            except Exception as e:
                print("Ошибка отмены заказа:", e)
                return False
        else: return None


    # 8. Получение информации о заказах пользователя
    def get_user_orders(self, user_id):
        role_user = self.db_connector.get_user_by_id(user_id)["user_role"]
        if role_user == "admin" or self.shop_state:
            try:
                # SQL-запрос для получения информации о заказах пользователя
                query = """
                    SELECT order_id, product_id, status, order_date, delivery_date
                    FROM orders
                    WHERE user_id = %s
                """
                self.cursor.execute(query, (user_id,))
                orders = self.cursor.fetchall()

                if not orders:
                    print(f"Заказы для пользователя {user_id} не найдены.")
                    return []

                # Преобразуем результат в список словарей для удобного отображения
                orders_info = [
                    {
                        "order_id": order[0],
                        "product_id": order[1],
                        "status": order[2],
                        "order_date": order[3],
                        "delivery_date": order[4]
                    }
                    for order in orders
                ]
                return orders_info
            except Exception as e:
                print("Ошибка получения информации о заказах пользователя:", e)
                return []
        else: return None


