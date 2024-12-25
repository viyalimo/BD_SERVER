import os
from typing import Optional
from Crypt.Crypt_controls import Crypt_controls
import uvicorn
from fastapi import HTTPException
from fastapi.responses import FileResponse
from fastapi import FastAPI
from pydantic import BaseModel
from BD import DB  # Импортируем ваш класс DB
from decimal import Decimal
from Cart import cart_manager
from Admin import admin_muve
app = FastAPI()


# Модель для получения данных логина
class LoginData(BaseModel):
    username: str
    password: str


class RegisterData(BaseModel):
    username: str
    password: str
    phone_number: str


class GETPHOTO(BaseModel):
    id: int
    muve: list
    key: str

class CartManagement(BaseModel):
    user_id: int
    product_id: int
    order_id: int

class CommandEdit(BaseModel):
    user_id: int
    data: str

class get_info(BaseModel):
    user_id: int
    data: str

# Модель для запроса поиска (используем Pydantic)
class SearchQuery(BaseModel):
    search_term: Optional[str] = None
    category: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    manufacturer: Optional[str] = None
    color: Optional[str] = None
    sort_by: Optional[str] = None  # 'price', 'popularity', 'new'

class Shop_State(BaseModel):
    user_id: int



# Создаем экземпляр подключения к базе данных


# Указываем папку, где будут храниться изображения
IMAGE_FOLDER = "C:\\Users\\user1387\\PycharmProjects\\FastAPIProject\\Image"
IMAGE_DARK_FOLDER = r"C:\Users\user1387\PycharmProjects\FastAPIProject\Image\DARK_ICON"
IMAGE_LIGHT_FOLDER = r"C:\Users\user1387\PycharmProjects\FastAPIProject\Image\LIGHT_ICON"
IMAGE_MAIN_FOLDER = r"C:\Users\user1387\PycharmProjects\FastAPIProject\Image\MAIN"

# Проверка наличия папки (если её нет, создаём)
if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)


@app.get("/images/{image_name}")
async def get_image(image_name: str):
    image_path = os.path.join(IMAGE_FOLDER, image_name)

    # Проверяем, существует ли файл
    if os.path.exists(image_path):
        # Отправляем изображение в ответ
        return FileResponse(image_path)
    else:
        raise HTTPException(status_code=404, detail="Image not found")


@app.get("/images/{style}/{image_name}")
async def get_back_icon(style: str, image_name: str):
    if style == "DARK":
        image_path = os.path.join(IMAGE_DARK_FOLDER, image_name)
    elif style == "LIGHT":
        image_path = os.path.join(IMAGE_LIGHT_FOLDER, image_name)
    else:
        image_path = os.path.join(IMAGE_MAIN_FOLDER, image_name)
    # Проверяем, существует ли файл
    if os.path.exists(image_path):
        # Отправляем изображение в ответ
        return FileResponse(image_path)
    else:
        raise HTTPException(status_code=404, detail="Image not found")


# Эндпоинт для получения всех продуктов
@app.get("/products")
async def get_all_products():
    try:
        # Получаем все продукты
        products = DB.get_all_products()
        for i in range(len(products)):
            products[i] = tuple(float(value) if isinstance(value, Decimal) else value for value in products[i])
        if products:
            return {"products": products}
        else:
            raise HTTPException(status_code=404, detail="Продукты не найдены")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка при получении продуктов: {str(e)}")


@app.get("/manufacturers")
async def get_all_manufacturers():
    try:
        # Получаем всех производителей
        manufacturers = DB.get_all_manufacturers()

        # Преобразуем данные из базы (Decimal -> float, если есть)
        for i in range(len(manufacturers)):
            manufacturers[i] = tuple(
                float(value) if isinstance(value, Decimal) else value for value in manufacturers[i])

        # Проверяем, есть ли производители
        if manufacturers:
            return {"manufacturers": manufacturers}
        else:
            raise HTTPException(status_code=404, detail="Производители не найдены")

    except Exception as e:
        # Обработка ошибок
        raise HTTPException(status_code=400, detail=f"Ошибка при получении производителей: {str(e)}")


@app.get("/manufacturers/{id}")
async def get_manufacturer_by_id(id: int):
    try:
        # Получаем производителя по id из базы данных
        manufacturer = DB.get_manufacturer_by_id(id)

        # Проверяем, существует ли производитель
        if manufacturer:
            return {"manufacturer": manufacturer}
        else:
            raise HTTPException(status_code=404, detail=f"Производитель с ID {id} не найден")

    except Exception as e:
        # Обработка ошибок
        raise HTTPException(status_code=400, detail=f"Ошибка при получении производителя: {str(e)}")


@app.get("/products/total")
async def get_total_products():
    try:
        # Получаем все продукты
        products = DB.get_products_by_total_purchases_desc()
        for i in range(len(products)):
            products[i] = tuple(float(value) if isinstance(value, Decimal) else value for value in products[i])
        if products:
            return {"products": products}
        else:
            raise HTTPException(status_code=404, detail="Продукты не найдены")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка при получении продуктов: {str(e)}")


@app.get("/products/{id}")
async def get_products_id(id: int):  # Указываем тип id
    try:
        # Получаем данные о продукте по ID
        product = DB.get_product_id(id)
        if product:
            # Преобразуем Decimal в float (если есть)
            product = tuple(float(value) if isinstance(value, Decimal) else value for value in product)
            return {"id": product}
        else:
            # Если продукт не найден, выбрасываем 404
            raise HTTPException(status_code=404, detail=f"Продукт с id {id} не найден")
    except Exception as e:
        # Обработка любых других ошибок
        raise HTTPException(status_code=400, detail=f"Ошибка при получении продукта по id: {str(e)}")


# Эндпоинт для поиска товаров по категории
@app.get("/products/category/{category}")
async def get_products_by_category(category: str):
    try:
        # Получаем товары по категории
        products = DB.get_products_by_category(category)

        if not products:
            raise HTTPException(status_code=404, detail=f"Продукты в категории '{category}' не найдены")

        # Преобразуем Decimal в float, если нужно
        products = [
            tuple(float(value) if isinstance(value, Decimal) else value for value in product)
            for product in products
        ]

        return {"products": products}

    except HTTPException:
        # Повторно выбрасываем исключение HTTPException
        raise

    except Exception as e:
        # Ловим все другие ошибки
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")


@app.get("/products/manufacturer/{manufacturer}")
async def get_products_by_manufacturer(manufacturer: str):
    try:
        # Получаем товары по производителю
        products = DB.get_products_by_manufacturer(manufacturer)
        for i in range(len(products)):
            products[i] = tuple(float(value) if isinstance(value, Decimal) else value for value in products[i])
        if products:
            return {"products": products}
        else:
            raise HTTPException(status_code=404, detail=f"Продукты производителя {manufacturer} не найдены")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка при получении продуктов по производителю: {str(e)}")


@app.get("/profile/{name}/{key}")
async def get_profile_inf(name: str, key: str):
    try:

        if key == DB.get_user_token(name):
            inf = DB.get_user_by_name(name)
            return {"inf": inf}
        else:
            return "Что-то пошло не так, перезайдите в профиль!"

    except HTTPException:
        # Повторно выбрасываем исключение HTTPException
        raise

    except Exception as e:
        # Ловим все другие ошибки
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")


@app.post("/editprofile")
async def edit_profile(data: GETPHOTO):
    try:
        if data.key == DB.get_user_by_id(int(data.id))["token"]:
            if data.muve[0] == "name":

                return DB.update_name(int(data.id), data.muve[1])
            elif data.muve[0] == "password":
                return DB.update_password(int(data.id), data.muve[1])
            elif data.muve[0] == "phone":
                return DB.update_phone_number(int(data.id), data.muve[1])
            elif data.muve[0] == "photo":
                return DB.update_photo(int(data.id), data.muve[1])
            elif data.muve[0] == "delete":
                return DB.delete_account(int(data.id))
            elif data.muve[0] == "logout":
                return DB.logout_user(int(data.id))
            else:
                return "Ошибка"
        else:
            return "Что-то пошло не так, перезайдите в профиль!"

    except HTTPException:
        # Повторно выбрасываем исключение HTTPException
        raise

    except Exception as e:
        # Ловим все другие ошибки
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.post("/login")
async def login(data: LoginData):
    # Проверка логина и пароля в базе данных
    return DB.verify_user(data.username, data.password)


@app.post("/register")
async def register(data: RegisterData):
    # Проверка, существует ли уже пользователь
    return DB.register_user(data.username, data.password, data.phone_number)


# Маршрут для поиска товаров
@app.post("/search")
async def search_products(query: SearchQuery):
    # Получаем результаты поиска из BD_connector
    results = DB.search_products(
        search_term=query.search_term,
        category=query.category,
        min_price=query.min_price,
        max_price=query.max_price,
        manufacturer=query.manufacturer,
        color=query.color,
        sort_by=query.sort_by
    )

    # Если результатов нет, возвращаем пустой список
    if not results:
        return []

    return results

@app.post("/add_cart")
async def add_in_cart(query: CartManagement):
    results = cart_manager.add_to_cart(
        user_id=query.user_id,
        product_id=query.product_id,
    )
    return results

@app.post("/remove_from_cart")
async def remove_from_cart(query: CartManagement):
    results = cart_manager.remove_from_cart(
        user_id=query.user_id,
        product_id=query.product_id,
    )

    return results

@app.post("/get_cart")
async def get_cart_items(query: CartManagement):
    results = cart_manager.get_cart_items(
        user_id=query.user_id,
    )
    return results

@app.post("/clear_cart")
async def clear_cart(query: CartManagement):
    results = cart_manager.clear_cart(
        user_id=query.user_id,
    )
    return results

@app.post("/create_order")
async def create_order(query: CartManagement):
    results = cart_manager.create_order_for_single_item(
        user_id=query.user_id,
        product_id=query.product_id,
    )
    return results

@app.post("/create_direct_order")
async def create_direct_order(query: CartManagement):
    results = cart_manager.create_direct_order(
        user_id=query.user_id,
        product_id=query.product_id,
    )
    return results

@app.post("/cancel_order")
async def cancel_order(query: CartManagement):
    results = cart_manager.cancel_order(
        order_id=query.order_id,
        user_id=query.user_id,
    )
    return results

@app.post("/get_all_orders")
async def get_all_orders(query: CartManagement):
    results = cart_manager.get_user_orders(
        user_id=query.user_id,
    )
    return results


"Аддминские команды"
@app.post("/edit")
async def admin_command(query: CommandEdit):
    results = admin_muve.command(
        admin_id=query.user_id,
        data=query.data,
    )
    return results

"""Конец"""
@app.post("/set_state_shop")
async def set_shop_state(query: Shop_State):
    results = DB.manage_state_shop(
        user_id=query.user_id,
    )
    return results

@app.get("/get_state_shop")
async def get_state_shop():
    return DB.get_shop_state()




# Ожидаем, что FastAPI автоматически закроет соединение с БД после завершения работы.
@app.on_event("shutdown")
def shutdown_db():
    DB.close()

def main():
    crypt = Crypt_controls()
    uvicorn.run(app,
                # host=str(socket.gethostbyname(socket.gethostname())),
                host="localhost",
                port=30000)

if __name__ == "__main__":
    import subprocess
    script_path = r"C:\Users\user1387\PycharmProjects\FastAPIProject\backup_db.py"
    try:
        print("Запуск скрипта для создания резервной копии...")
        subprocess.run(["python", script_path], check=True)
        print("Скрипт успешно выполнен.")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при выполнении скрипта: {e}")
    main()

