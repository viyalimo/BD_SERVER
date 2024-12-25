from cryptography.fernet import Fernet
import json

class Crypt_controls:
    # Генерация ключа шифрования
    def generate_key(self):
        key = Fernet.generate_key()
        return key

    # Функция для шифрования текста
    def encrypt_message(self, key, message):
        try:
            fernet = Fernet(key)
            encrypted_message = fernet.encrypt(message.encode())
            return encrypted_message
        except Exception as e:
            print(f"Ошибка при шифровании: {e}")
            return None

    # Функция для расшифровки текста
    def decrypt_message(self, key: str, encrypted_message):
        try:
            fernet = Fernet(key)
            decrypted_message = fernet.decrypt(encrypted_message).decode()
            return decrypted_message
        except Exception as e:
            print(f"Ошибка при расшифровке: {e}")
            return None

    def encrypt_dict(self, key, data_dict):
        try:
            # Преобразуем словарь в строку JSON
            json_message = json.dumps(data_dict)
            # Шифруем JSON строку
            return self.encrypt_message(key, json_message)
        except Exception as e:
            print(f"Ошибка: {e}")
            return None

    def decrypt_dict(self, key, encrypted_dict):
        try:
            # Расшифровываем сообщение
            decrypted_message = self.decrypt_message(key, encrypted_dict)
            # Преобразуем строку JSON обратно в словарь
            return json.loads(decrypted_message)
        except Exception as e:
            print(f"Ошибка: {e}")
            return None