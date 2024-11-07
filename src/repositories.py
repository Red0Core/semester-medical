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

class PatientRepository:
    def __init__(self, db_name='healthcare.db'):
        self.db_name = db_name

    @handle_db_errors()
    def get_all_patients(self):
        with DatabaseConnection(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT patient_id, name FROM patients")
            return cursor.fetchall()

    @handle_db_errors()
    def get_patient_record(self, patient_id):
        with DatabaseConnection(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT record FROM medical_records WHERE patient_id = ?", (patient_id,))
            return cursor.fetchone()
        
    @handle_db_errors()
    def get_patient(self, patient_id):
        with DatabaseConnection(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT patient_id, name FROM patients WHERE patient_id = ?", (patient_id,))
            return cursor.fetchone()
        
    @handle_db_errors()
    def update_patient(self, patient_id, name):
        with DatabaseConnection(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE patients SET name = ? WHERE patient_id = ?", (name, patient_id))

    @handle_db_errors()
    def delete_patient(self, patient_id):
        with DatabaseConnection(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM patients WHERE patient_id = ?", (patient_id,))
    
    @handle_db_errors()
    def add_patient(self, username, password, name):
        """Добавляет нового пациента в базу данных."""
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            # 1. Создаем пользователя

            cursor.execute("""
                INSERT INTO users (username, password, role) VALUES (?, ?, ?)
            """, (username, password, 'patient'))
            
            # Получаем сгенерированный user_id
            user_id = cursor.lastrowid
            
            # 2. Добавляем пациента с user_id в таблицу patients
            cursor.execute("""
                INSERT INTO patients (user_id, name) VALUES (?, ?)
            """, (user_id, name))

    @handle_db_errors()
    def update_medical_record(self, patient_id, record):
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO medical_records (patient_id, record)
                VALUES (?, ?)
                ON CONFLICT(patient_id) DO UPDATE SET record = excluded.record
            """, (patient_id, record))
            