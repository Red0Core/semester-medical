from sqlite3 import Connection
import tkinter as tk
from database import DatabaseConnection, create_tables
from repositories import UserRepository
from user import User, Role
from ui.main_ui import MainApp

if __name__ == "__main__":
    create_tables("healthcare.db")

    user_repository = UserRepository("healthcare.db")

    # Добавим тестовых пользователей
    if not user_repository.find_by_username("admin"):
        admin_user = User("admin", "admin_password", Role.ADMIN)
        user_repository.add_user(admin_user)

    if not user_repository.find_by_username("doctor"):
        doctor_user = User("doctor", "doctor_password", Role.DOCTOR)
        user_repository.add_user(doctor_user)

    if not user_repository.find_by_username("patient"):
        patient_user = User("patient", "patient_password", Role.PATIENT)
        user_repository.add_user(patient_user)

    for i in user_repository.get_all_users():
        print(i)    

    app = MainApp()
    app.mainloop()
