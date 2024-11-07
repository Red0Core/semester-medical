import tkinter as tk
from tkinter import messagebox, ttk
from ui.manage_patients_ui import PatientAdminUI

class AdminUI(tk.Toplevel):
    def __init__(self, root):
        self.root = root
        self.root.title("Администратор - Управление")
        self.root.geometry("500x400")
        
        # Заголовок интерфейса
        self.label_title = ttk.Label(root, text="Панель администратора", font=("Arial", 16))
        self.label_title.pack(pady=10)

        # Кнопки для управления врачами
        self.btn_manage_doctors = ttk.Button(root, text="Управление врачами", command=self.manage_doctors)
        self.btn_manage_doctors.pack(pady=5)

        # Кнопки для управления пациентами
        self.btn_manage_patients = ttk.Button(root, text="Управление пациентами", command=self.manage_patients)
        self.btn_manage_patients.pack(pady=5)

        # Кнопка для просмотра заявок
        self.btn_view_requests = ttk.Button(root, text="Просмотр заявок пациентов", command=self.medical_records)
        self.btn_view_requests.pack(pady=5)

        # Кнопка выхода
        self.btn_exit = ttk.Button(root, text="Выйти", command=self.root.destroy)
        self.btn_exit.pack(pady=20)

    def manage_doctors(self):
        # Вызов функции управления списком врачей
        messagebox.showinfo("Управление врачами", "Открывается окно управления врачами (реализовать в дальнейшем)")

    def manage_patients(self):
        # Вызов функции управления списком пациентов
        manage_patients_window = tk.Toplevel(self.root)
        PatientAdminUI(manage_patients_window)

    def medical_records(self):
        # Просмотр медицинских карт
        messagebox.showinfo("Просмотр заявок", "Здесь будет список заявок пациентов (реализовать в дальнейшем)")