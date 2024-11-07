from hashlib import sha256
from enum import Enum

class Role(Enum):
    ADMIN = "admin"
    PATIENT = "patient"
    DOCTOR = "doctor"

class User:
    def __init__(self, username, password, role: Role):
        """
        :param login: Логин пользователя
        :param password: Пароль пользователя
        :param role: Роль пользователя
        """
        self.username = username
        self.password = password
        self.role = role
    
    @staticmethod
    def hash_password(password):
        return sha256(password.encode()).hexdigest()

    def login(self, username, password):
        """Проверяет учетные данные для входа."""
        return self.username == username and self.password == password
    
    def logout(self):
        """Метод для выхода."""
        print(f"Пользователь {self.username} вышел из системы.")
    

