import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
from repositories import UserRepository
from ui.admin_ui import AdminUI
from user import Role

class MainApp:
    def __init__(self, root):
        self.root = root
        root.title("Система медицинских записей")

        self.label = tk.Label(root, text="Добро пожаловать в систему медицинских записей!")
        self.label.pack(pady=10)

        self.login_button = tk.Button(root, text="Войти", command=self.open_login)
        self.login_button.pack(pady=5)

        self.exit_button = tk.Button(root, text="Выйти", command=root.destroy)
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
                admin_window = tk.Toplevel(self.root)
                AdminUI(admin_window)
            else:
                messagebox.showinfo("Информация", "Попытка входа выполнена.")     
                 
            print(f"Попытка входа: {username} с паролем: {password}")
        else:
            messagebox.showwarning("Предупреждение", "Логин и пароль не могут быть пустыми.")

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()