import tkinter as tk
from tkinter import ttk
from ui.manage_patients_ui import PatientAdminUI
from ui.manage_doctors_ui import DoctorAdminUI

class AdminUI(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.title("Администратор - Управление")
        
        # Заголовок интерфейса
        self.label_title = ttk.Label(self, text="Панель администратора", font=("Arial", 16))
        self.label_title.pack(pady=10)

        # Кнопки для управления врачами
        self.btn_manage_doctors = ttk.Button(self, text="Управление врачами", command=self.manage_doctors)
        self.btn_manage_doctors.pack(pady=5)

        # Кнопки для управления пациентами
        self.btn_manage_patients = ttk.Button(self, text="Управление пациентами", command=self.manage_patients)
        self.btn_manage_patients.pack(pady=5)

        # Кнопка выхода
        self.btn_exit = ttk.Button(self, text="Выйти", command=self.destroy)
        self.btn_exit.pack(pady=20)

    def manage_doctors(self):
        # Вызов функции управления списком врачей
        DoctorAdminUI()

    def manage_patients(self):
        # Вызов функции управления списком пациентов
        PatientAdminUI()