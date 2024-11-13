from pydoc import doc
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from repositories import AppointmentRepository, DoctorRepository, PatientRepository, UserRepository, Role
from ui.patient_ui import PatientUI
from ui.admin_ui import AdminUI
from ui.doctor_ui import DoctorUI

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Система медицинских записей")

        self.label = ttk.Label(self, text="Добро пожаловать в систему медицинских записей!")
        self.label.pack(pady=10)

        self.login_button = ttk.Button(self, text="Войти", command=self.open_login)
        self.login_button.pack(pady=5)

        self.exit_button = ttk.Button(self, text="Выйти", command=self.destroy)
        self.exit_button.pack(pady=5)

    def open_login(self):
        username = simpledialog.askstring("Вход", "Введите логин:")
        password = simpledialog.askstring("Вход", "Введите пароль:", show='*')

        if username and password:
            # Происходит аутентификация и выбор интерфейса в зависимости от роли
            user_repository = UserRepository("healthcare.db")
            doctor_repository = DoctorRepository("healthcare.db")
            patient_repository = PatientRepository("healthcare.db")
            appointment_repository = AppointmentRepository("healthcare.db")
            fetch_doctors = doctor_repository.get_all_doctors

            role = user_repository.authenticate(username, password)
            user_id = user_repository.find_by_username(username)
            if role == Role.ADMIN.value:
                messagebox.showinfo("Информация", "Успешно вошли с ролью администратора")
                AdminUI(doctor_repository=doctor_repository, patient_repository=patient_repository)
            elif role == Role.DOCTOR.value:
                messagebox.showinfo("Информация", "Успешно вошли с ролью доктора")
                DoctorUI(user_id=user_id,
                         doctor_repository=doctor_repository, 
                         patient_repository=patient_repository, 
                         appointment_repository=appointment_repository)
            elif role == Role.PATIENT.value:
                messagebox.showinfo("Информация", "Успешно вошли с ролью пациента")
                PatientUI(user_id=user_id,
                          patient_repository=patient_repository, appointment_repository=appointment_repository,
                          fetch_doctors_func=fetch_doctors)
            else:
                messagebox.showinfo("Информация", "Попытка входа выполнена.")     
                 
            print(f"Попытка входа: {username} с паролем: {password}")
        else:
            messagebox.showwarning("Предупреждение", "Логин и пароль не могут быть пустыми.")
            