from database import create_tables
from repositories import *
from ui.main_ui import MainApp

if __name__ == "__main__":
    create_tables("healthcare.db")

    user_repository = UserRepository("healthcare.db")
    patient_repository = PatientRepository("healthcare.db")
    doctor_repository = DoctorRepository("healthcare.db")

    # Добавим тестовых пользователей
    if not user_repository.find_by_username("admin"):
        user_repository.add_user("admin", "admin_password", Role.ADMIN)

    if not user_repository.find_by_username("doctor"):
        doctor_repository.add_doctor("doctor", "doctor_password", "доктор 228", "крутая специальность")

    if not user_repository.find_by_username("patient"):
        patient_repository.add_patient("patient", "patient_password", "Бебр228")

    for i in user_repository.get_all_users():
        print(i)    

    app = MainApp()
    app.mainloop()
