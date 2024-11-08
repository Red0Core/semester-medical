from database import DatabaseConnection, handle_db_errors
from sqlite3 import IntegrityError
from enum import Enum

class Role(Enum):
    ADMIN = "admin"
    PATIENT = "patient"
    DOCTOR = "doctor"

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
    def add_user(self, username, password, role: Role):
        """
        Может выполнять только Админ
        :param user: Новый пользователь: логин, хэш пароля и роль
        """
        with DatabaseConnection(self.db_name) as conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO users (username, password, role) VALUES (?, ?, ?)
                """, (username, password, role.value))
            except IntegrityError:
                print(f"Пользователь {username} уже существует.")
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
            return row

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
            cursor.execute("SELECT user_id FROM patients WHERE patient_id = ?", (patient_id,))
            result = cursor.fetchone()
            
            if result is not None:  # Проверяем, что patient_id существует
                print(result)
                # Удаляем пользователя по user_id, это также удалит пациента благодаря каскадному удалению
                cursor.execute("DELETE FROM users WHERE user_id = ?", (result['user_id'],))
            else:
                print(f"Пациент с ID {patient_id} не найден.")
    
    @handle_db_errors()
    def add_patient(self, username, password, name):
        """Добавляет нового пациента в базу данных."""
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            # 1. Создаем пользователя

            cursor.execute("""
                INSERT INTO users (username, password, role) VALUES (?, ?, ?)
            """, (username, password, Role.PATIENT))
            
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

class DoctorRepository:
    def __init__(self, db_name='healthcare.db'):
        self.db_name = db_name
    
    @handle_db_errors()
    def get_all_doctors(self):
        with DatabaseConnection(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT doctor_id, name, specialty FROM doctors")
            return cursor.fetchall()
        
    @handle_db_errors()
    def get_doctor(self, doctor_id):
        with DatabaseConnection(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT doctor_id, name, specialty FROM doctors WHERE doctor_id = ?", (doctor_id,))
            return cursor.fetchone()
        
    @handle_db_errors()
    def delete_doctor(self, doctor_id):
        with DatabaseConnection(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM doctors WHERE doctor_id = ?", (doctor_id,))
            result = cursor.fetchone()
            
            if result is not None:  # Проверяем, что doctor_id существует
                print(result)
                # Удаляем пользователя по user_id, это также удалит доктора благодаря каскадному удалению
                cursor.execute("DELETE FROM users WHERE user_id = ?", (result['user_id'],))
            else:
                print(f"Доктор {doctor_id} не найден.")
    
    @handle_db_errors()
    def add_doctor(self, username, password, name, speciality):
        """Добавляет нового доктора в базу данных."""
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            # 1. Создаем пользователя

            cursor.execute("""
                INSERT INTO users (username, password, role) VALUES (?, ?, ?)
            """, (username, password, Role.DOCTOR))
            
            # Получаем сгенерированный user_id
            user_id = cursor.lastrowid
            
            # 2. Добавляем доктора с user_id в таблицу doctors
            cursor.execute("""
                INSERT INTO doctors (user_id, name, speciality) VALUES (?, ?, ?)
            """, (user_id, name, speciality))
