import sqlite3
from database import DatabaseConnection, handle_db_errors
from user import User, Role
from sqlite3 import IntegrityError

class UserRepository:
    def __init__(self, db_name='healthcare.db'):
        self.db_name = db_name

    @handle_db_errors()
    def authenticate(self, username, password):
        """
        Возвращает роль пользователя.

        :param username: Логин
        :param password: Пароль
        :return role: Роль
        """
        with DatabaseConnection(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT role FROM users WHERE username = ? AND password = ?', (username, password))
            result = cursor.fetchone()
            return result['role'] if result else None

    @handle_db_errors()
    def add_user(self, user: User):
        """
        Может выполнять только Админ
        :param user: Новый пользователь: логин, хэш пароля и роль
        """
        with DatabaseConnection(self.db_name) as conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO users (username, password, role) VALUES (?, ?, ?)
                """, (user.username, user.password, user.role.value))
            except IntegrityError:
                print(f"Пользователь {user.username} уже существует.")
                raise
    
    @handle_db_errors()
    def find_by_username(self, username):
        """
        Ищет пользователя по логину

        :param username: логин пользователя
        :return User: None, если нет
        """
        with DatabaseConnection(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT * FROM users WHERE username = ?
            """, (username,))
            row = cursor.fetchone()
            if row:
                return User(row['username'], row['password'], Role(row['role']))
            return None

    @handle_db_errors()
    def get_all_users(self) -> list[dict]:
        """
        Возвращает всех пользователей
        """
        with DatabaseConnection(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            return cursor.fetchall()
    