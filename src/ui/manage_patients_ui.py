from re import U
import tkinter as tk
from tkinter import ttk, messagebox
from repositories import PatientRepository
from ui.medical_record_ui import *

class PatientAdminUI(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.title("Список пациентов")

        self.patient_repository = PatientRepository("healthcare.db")

        # Создаем виджет Treeview
        self.tree = ttk.Treeview(self, columns=("ID", "Name"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Имя")
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Добавляем кнопки для управления
        self.view_button = ttk.Button(self, text="Просмотр", command=self.view_patient)
        self.edit_button = ttk.Button(self, text="Редактировать", command=self.edit_patient)
        self.delete_button = ttk.Button(self, text="Удалить", command=self.delete_patient)
        self.add_button = ttk.Button(self, text="Добавить", command=self.add_patient)
        self.edit_medical_button = ttk.Button(self, text="Изменить карту", command=self.edit_medical_card)

        self.view_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.edit_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.delete_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.add_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.edit_medical_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Загрузка данных
        self.load_patients_to_tree_view()

    def load_patients_to_tree_view(self):
        """Загружает список пациентов в Treeview."""
        for row in self.tree.get_children():
            self.tree.delete(row)  # Очистка списка перед загрузкой новых данных

        patients = self.patient_repository.get_all_patients()

        for patient in patients:
            self.tree.insert("", tk.END, values=(patient['patient_id'], patient['name']))

    def view_patient(self):
        """Показывает медицинскую карту выбранного пациента."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Ошибка", "Выберите пациента для просмотра.")
            return

        patient_id = self.tree.item(selected_item[0])["values"][0]
        record = self.patient_repository.get_patient_record(patient_id)

        if not record:
            messagebox.showinfo("Медицинская карта", "Медицинская карта отсутствует.")
        else:
            MedicalRecordWindow(patient_id, self.patient_repository)
    
    def edit_medical_card(self):
        """Изменяет медицинскую карту выбранного пациента"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Ошибка", "Выберите пациента для просмотра.")
            return

        patient_id = self.tree.item(selected_item[0])["values"][0]
        record = self.patient_repository.get_patient_record(patient_id)
        # Если нет медицинской карты, то мы пустую сделаем
        if not record:
            self.patient_repository.update_medical_record(patient_id, "")

        MedicalRecordWindowEdit(patient_id, self.patient_repository)

    def edit_patient(self):
        """Открывает окно для редактирования информации о пациенте."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Ошибка", "Выберите пациента для редактирования.")
            return

        patient_id = self.tree.item(selected_item[0])["values"][0]
        patient_name = self.tree.item(selected_item[0])["values"][1]

        patient_login_data = self.patient_repository.get_patient_login_data(patient_id)

        # Открываем новое окно для редактирования
        PatientWindow(self, self.load_patients_to_tree_view, self.patient_repository, patient_id, patient_name,
                      patient_login_data['username'], patient_login_data['password'])

    def delete_patient(self):
        """Удаляет выбранного пациента и обновляет список."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Ошибка", "Выберите пациента для удаления.")
            return

        patient_id = self.tree.item(selected_item[0])["values"][0]
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить пациента?"):
            self.patient_repository.delete_patient(patient_id)
            self.load_patients_to_tree_view()  # Обновляем список после удаления
            print("Список пациентов:")
            for i in self.patient_repository.get_all_patients():
                print(i)
            print()
    
    def add_patient(self):
        """Добавляет нового пациента и обновляет список"""

        # Открываем новое окно для редактирования
        PatientWindow(self, self.load_patients_to_tree_view, self.patient_repository)

class PatientWindow(tk.Toplevel):
    def __init__(self, master, refresh_callback, patient_repository: PatientRepository,
                  patient_id=None, patient_name="", username="", password="", medical_record=""):
        super().__init__(master)
        self.title("Добавить пациента" if patient_id is None else "Редактировать пациента")
        self.refresh_callback = refresh_callback
        self.patient_id = patient_id
        self.repository = patient_repository

        # Поле для имени пациента
        ttk.Label(self, text="Имя пациента:").grid(row=0, column=0, padx=5, pady=5)
        self.name_entry = ttk.Entry(self)
        self.name_entry.insert(0, patient_name)  # Заполняем, если редактируем иначе пустой будет
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        # Поля для username и password
        ttk.Label(self, text="Имя пользователя:").grid(row=1, column=0, padx=5, pady=5)
        self.username_entry = ttk.Entry(self)
        self.username_entry.insert(0, username) # Заполняем, если редактируем
        self.username_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self, text="Пароль:").grid(row=2, column=0, padx=5, pady=5)
        self.password_entry = ttk.Entry(self, show="*")
        self.password_entry.insert(0, password) # Заполняем, если редактируем
        self.password_entry.grid(row=2, column=1, padx=5, pady=5)

        # Кнопка для сохранения пациента
        ttk.Button(self, text="Сохранить", command=self.save_patient_data).grid(row=3, column=0, columnspan=2, pady=10)

    def save_patient_data(self):
        """Сохраняет или обновляет данные пациента в базе данных."""
        name = self.name_entry.get().strip()

        # Проверяем обязательные поля
        if not name or (self.patient_id is None and (not self.username_entry.get().strip() or not self.password_entry.get().strip())):
            messagebox.showwarning("Ошибка", "Все поля должны быть заполнены.")
            return

        try:
            username = self.username_entry.get().strip()
            password = self.password_entry.get().strip()

            if self.patient_id is None:
                # Добавялем нового пациента
                self.repository.add_patient(username, password, name)
            else:
                # Обновляем данные существующего пациента
                self.repository.update_patient(self.patient_id, name, username, password)
                
            messagebox.showinfo("Успех", "Данные пациента успешно сохранены.")
            self.refresh_callback()  # Обновляем список пациентов в главном окне
            self.destroy()  # Закрываем окно
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные пациента: {e}")
