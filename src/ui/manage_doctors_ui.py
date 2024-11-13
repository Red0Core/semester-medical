import tkinter as tk
from tkinter import ttk, messagebox
from repositories import DoctorRepository

class DoctorAdminUI(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.title("Список врачей")

        self.doctor_repository = DoctorRepository("healthcare.db")

        # Создаем виджет Treeview
        self.tree = ttk.Treeview(self, columns=("ID", "Name", "Speciality"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Имя")
        self.tree.heading("Speciality", text="Специальность")
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Добавляем кнопки для управления
        self.edit_button = ttk.Button(self, text="Редактировать", command=self.edit_doctor)
        self.delete_button = ttk.Button(self, text="Удалить", command=self.delete_doctor)
        self.add_button = ttk.Button(self, text="Добавить", command=self.add_doctor)

        self.edit_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.delete_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.add_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Загрузка данных
        self.load_doctors_to_tree_view()

    def load_doctors_to_tree_view(self):
        """Загружает список докторов в Treeview."""
        for row in self.tree.get_children():
            self.tree.delete(row)  # Очистка списка перед загрузкой новых данных

        doctors = self.doctor_repository.get_all_doctors()

        for doctor in doctors:
            self.tree.insert("", tk.END, values=(doctor['doctor_id'], doctor['name'], doctor['speciality']))

    def edit_doctor(self):
        """Открывает окно для редактирования информации о враче."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Ошибка", "Выберите доктора для редактирования.")
            return

        doctor_id = self.tree.item(selected_item[0])["values"][0]
        doctor_name = self.tree.item(selected_item[0])["values"][1]
        doctor_speciality = self.tree.item(selected_item[0])["values"][2]

        patient_login_data = self.doctor_repository.get_doctor_login_data(doctor_id)

        # Открываем новое окно для редактирования
        EditDoctorWindow(self, self.doctor_repository, self.load_doctors_to_tree_view,
                         doctor_id, doctor_name, doctor_speciality,
                         patient_login_data['username'], patient_login_data['password'])
        self.load_doctors_to_tree_view()

    def delete_doctor(self):
        """Удаляет выбранного врача и обновляет список."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Ошибка", "Выберите врача для удаления.")
            return

        doctor_id = self.tree.item(selected_item[0])["values"][0]
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить доктора?"):
            self.doctor_repository.delete_doctor(doctor_id)
            self.load_doctors_to_tree_view()  # Обновляем список после удаления
            print("Список докторов:")
            for i in self.doctor_repository.get_all_doctors():
                print(i)
            print()
    
    def add_doctor(self):
        """Добавляет нового доктора и обновляет список"""

        # Открываем новое окно для редактирования
        EditDoctorWindow(self, self.doctor_repository, self.load_doctors_to_tree_view)

class EditDoctorWindow(tk.Toplevel):
    def __init__(self, master, doctor_repository: DoctorRepository, callback_refresh,
                 doctor_id=None, doctor_name="",  doctor_speciality="",
                 username="", password=""):
        super().__init__(master)
        self.title("Добавить врача" if doctor_id is None else "Редактировать врача")
        self.doctor_id = doctor_id
        self.repository = doctor_repository
        self.callback_refresh = callback_refresh

        # Поле для имени доктора
        ttk.Label(self, text="Имя доктора:").grid(row=0, column=0, padx=5, pady=5)
        self.name_entry = ttk.Entry(self)
        self.name_entry.insert(0, doctor_name)  # Заполняем, если редактируем иначе пустой будет
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        # Поле для специальности доктора
        ttk.Label(self, text="Специальность доктора:").grid(row=1, column=0, padx=5, pady=5)
        self.speciality_entry = ttk.Entry(self)
        self.speciality_entry.insert(0, doctor_speciality)  # Заполняем, если редактируем иначе пустой будет
        self.speciality_entry.grid(row=1, column=1, padx=5, pady=5)

        # Поля для username и password
        ttk.Label(self, text="Имя пользователя:").grid(row=2, column=0, padx=5, pady=5)
        self.username_entry = ttk.Entry(self)
        self.username_entry.insert(0, username) # Заполняем, если редактируем
        self.username_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(self, text="Пароль:").grid(row=3, column=0, padx=5, pady=5)
        self.password_entry = ttk.Entry(self, show="*")
        self.password_entry.insert(0, password) # Заполняем, если редактируем
        self.password_entry.grid(row=3, column=1, padx=5, pady=5)

        # Кнопка для сохранения врача
        ttk.Button(self, text="Сохранить", command=self.save_doctor_data).grid(row=4, column=0, columnspan=2, pady=10)

    def save_doctor_data(self):
        """Сохраняет или обновляет данные врача в базе данных."""
        name = self.name_entry.get().strip()
        speciality = self.speciality_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        # Проверяем обязательные поля
        if not name or not speciality or \
            (self.doctor_id is None and (not username or not password)):
            messagebox.showwarning("Ошибка", "Все поля должны быть заполнены.")
            return

        try:

            if self.doctor_id is None:
                # Добавялем нового доктора
                self.repository.add_doctor(username, password, name, speciality)
            else:
                # Обновляем данные существующего доктора
                self.repository.update_doctor(self.doctor_id, name, speciality, username, password)
            
            self.callback_refresh()
            messagebox.showinfo("Успех", "Данные врача успешно сохранены.")
            self.destroy()  # Закрываем окно
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные врача: {e}")
