import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from repositories import UserRepository
from ui.admin_ui import AdminUI
from user import Role

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

            role = user_repository.authenticate(username, password)
            if role == Role.ADMIN.value:
                messagebox.showinfo("Информация", "Успешно вошли с ролью администратора")
                AdminUI()
            else:
                messagebox.showinfo("Информация", "Попытка входа выполнена.")     
                 
            print(f"Попытка входа: {username} с паролем: {password}")
        else:
            messagebox.showwarning("Предупреждение", "Логин и пароль не могут быть пустыми.")
            