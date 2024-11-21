import datetime
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
        Ищет user_id по логину

        :param username: логин пользователя
        :return int: user_id или None, если нет
        """
        with DatabaseConnection(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT user_id FROM users WHERE username = ?
            """, (username,))
            row = cursor.fetchone()
            return row['user_id']

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
            res = cursor.fetchone()
            # Если еще не создана запись, то создается пустая
            if res is None:
                cursor.execute("""
                INSERT INTO medical_records (patient_id, record)
                VALUES (?, ?)
                ON CONFLICT(patient_id) DO UPDATE SET record = excluded.record
                """, (patient_id, ""))
                return {'record': ''}

            return res

        
    @handle_db_errors()
    def get_patient(self, patient_id):
        with DatabaseConnection(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT patient_id, name FROM patients WHERE patient_id = ?", (patient_id,))
            return cursor.fetchone()
        
    @handle_db_errors()
    def update_patient(self, patient_id, name, username=None, password=None):
        with DatabaseConnection(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE patients SET name = ? WHERE patient_id = ?", (name, patient_id))

            # Получение user_id пациента
            cursor.execute("SELECT user_id FROM patients WHERE patient_id = ?", (patient_id,))
            user_id = cursor.fetchone()
            if user_id and username and password:
                user_id = user_id['user_id']  # Извлечение user_id из результата запроса
                
                # Обновление имени пользователя и пароля, если они предоставлены
                if username is not None:
                    cursor.execute("UPDATE users SET username = ? WHERE user_id = ?", (username, user_id))
                if password is not None:
                    cursor.execute("UPDATE users SET password = ? WHERE user_id = ?", (password, user_id))
        
    @handle_db_errors()
    def get_patient_login_data(self, patient_id):
        with DatabaseConnection(self.db_name) as conn:
            cursor = conn.cursor()
            
            # Получение user_id пациента
            cursor.execute("SELECT user_id FROM patients WHERE patient_id = ?", (patient_id,))
            user_id = cursor.fetchone()

            # Получаем входные данные
            cursor.execute("SELECT username, password FROM users WHERE user_id = ?", (user_id['user_id'],))
            return cursor.fetchone()
    
    @handle_db_errors()
    def get_patient_by_user_id(self, user_id):
        """
        Возвращает информацию о пациенте по его user_id.

        :param user_id: Идентификатор пользователя (int), по которому осуществляется поиск пациента.
        :return: Словарь с информацией о пациенте, содержащий 'patient_id' и 'name', 
                или None, если пациент не найден.
        :rtype: Optional[dict]
        """
        with DatabaseConnection(self.db_name) as conn:
            cursor = conn.cursor()

            # Получаем имя и айди пациента по его user_id
            cursor.execute("SELECT patient_id, name FROM patients WHERE user_id = ?", (user_id,))
            return cursor.fetchone()

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
            """, (username, password, Role.PATIENT.value))
            
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
    def get_all_doctors(self) -> list[dict]:
        """
        Возвращает словарь с doctor_id его именем и специальностью
        """
        with DatabaseConnection(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT doctor_id, name, speciality FROM doctors")
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
            """, (username, password, Role.DOCTOR.value))
            
            # Получаем сгенерированный user_id
            user_id = cursor.lastrowid
            
            # 2. Добавляем доктора с user_id в таблицу doctors
            cursor.execute("""
                INSERT INTO doctors (user_id, name, speciality) VALUES (?, ?, ?)
            """, (user_id, name, speciality))
    
    @handle_db_errors()
    def get_doctor_login_data(self, doctor_id):
        with DatabaseConnection(self.db_name) as conn:
            cursor = conn.cursor()
            
            # Получение user_id пациента
            cursor.execute("SELECT user_id FROM doctors WHERE doctor_id = ?", (doctor_id,))
            user_id = cursor.fetchone()

            # Получаем входные данные
            cursor.execute("SELECT username, password FROM users WHERE user_id = ?", (user_id['user_id'],))
            return cursor.fetchone()
        
    @handle_db_errors()
    def update_doctor(self, doctor_id, name, speciality, username=None, password=None):
        with DatabaseConnection(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE doctors SET name = ?, speciality = ? WHERE doctor_id = ?", (name, speciality, doctor_id))
            # Получение user_id пациента
            cursor.execute("SELECT user_id FROM doctors WHERE doctor_id = ?", (doctor_id,))
            user_id = cursor.fetchone()
            if user_id and username and password:
                user_id = user_id['user_id']  # Извлечение user_id из результата запроса
                
                # Обновление имени пользователя и пароля, если они предоставлены
                if username is not None:
                    cursor.execute("UPDATE users SET username = ? WHERE user_id = ?", (username, user_id))
                if password is not None:
                    cursor.execute("UPDATE users SET password = ? WHERE user_id = ?", (password, user_id))
    
    @handle_db_errors()
    def get_doctor_by_user_id(self, user_id):
        """
        Возвращает информацию о докторе по его user_id.

        :param user_id: Идентификатор пользователя (int), по которому осуществляется поиск доктора.
        :return: Словарь с информацией о докторе, содержащий 'doctor_id' и 'name', 
                или None, если докторпациент не найден.
        :rtype: Optional[dict]
        """
        with DatabaseConnection(self.db_name) as conn:
            cursor = conn.cursor()

            # Получаем имя и айди пациента по его user_id
            cursor.execute("SELECT doctor_id, name, speciality FROM doctors WHERE user_id = ?", (user_id,))
            return cursor.fetchone()

class AppointmentRepository:
    def __init__(self, db_name = "healthcare.db"):
        self.db_name = db_name

    @handle_db_errors()
    def add_appointment(self, patient_id, doctor_id, appointment_time):
        with DatabaseConnection(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO appointments (doctor_id, patient_id, appointment_time)
                VALUES (?, ?, ?)
            """, (doctor_id, patient_id, appointment_time))

    @handle_db_errors()
    def get_booked_slots_in_one_day(self, doctor_id, date: datetime.datetime):
        """
        Этот метод запрашивает занятые временные интервалы для определенного врача на определенную дату

        :param doctor_id: Айди доктора
        :param date: Дата, на которую надо найти занятые слоты
        :return: Возвращает все занятые слоты в формате datetime
        :rtype: datetime.datetime
        """
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT appointment_time FROM appointments
                WHERE doctor_id = ? AND DATE(appointment_time) = ?
            """, (doctor_id, date.isoformat()))
            booked_slots = [datetime.datetime.fromisoformat(row['appointment_time']) for row in cursor.fetchall()]  # Получаем только время HH:MM
            return booked_slots
    
    @handle_db_errors()
    def get_appointments_by_doctor_id(self, doctor_id):
        """
        Этот метод запрашивает все записи для конкретного доктора

        :param doctor_id: Айди доктора
        :return: Записи в формате словаря с ключами 'patient_id', 'name', 'appointment_time', где name это имя пациента
        :rtype: dict
        """
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT patient_id, appointment_time FROM appointments WHERE doctor_id = ?
            """, (doctor_id,))

            appointments = []
            for row in cursor.fetchall():
                cursor.execute("""
                    SELECT name FROM patients WHERE patient_id = ?
                """, (row['patient_id'],))
                patient_name = cursor.fetchone()['name']
                appointments.append(dict(patient_id=row['patient_id'],
                                         name=patient_name,
                                         appointment_time=row['appointment_time']))
                
            return appointments
