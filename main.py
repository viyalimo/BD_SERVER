import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi import FastAPI
from pydantic import BaseModel
from BD import DB  # Импортируем ваш класс DB



app = FastAPI()



# Модель для получения данных логина
class LoginData(BaseModel):
    username: str
    password: str

class RegisterData(BaseModel):
    username: str
    password: str
    phone_number: str

# Создаем экземпляр подключения к базе данных


# Указываем папку, где будут храниться изображения
IMAGE_FOLDER = "C:\\Users\\user1387\\PycharmProjects\\FastAPIProject\\Image"
IMAGE_DARK_FOLDER = r"C:\Users\user1387\PycharmProjects\FastAPIProject\Image\DARK_ICON"
IMAGE_LIGHT_FOLDER = r"C:\Users\user1387\PycharmProjects\FastAPIProject\Image\LIGHT_ICON"

# Проверка наличия папки (если её нет, создаём)
if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)

# Эндпоинт для получения изображения
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
    else:
        image_path = os.path.join(IMAGE_LIGHT_FOLDER, image_name)
    # Проверяем, существует ли файл
    if os.path.exists(image_path):
        # Отправляем изображение в ответ
        return FileResponse(image_path)
    else:
        raise HTTPException(status_code=404, detail="Image not found")


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


# Ожидаем, что FastAPI автоматически закроет соединение с БД после завершения работы.
@app.on_event("shutdown")
def shutdown_db():
    DB.close()
