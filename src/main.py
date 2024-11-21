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

    print("Юзеры:")
    for i in user_repository.get_all_users():
        print(i)
        user_id = i['user_id']
        role = i['role']
        if role == Role.DOCTOR.value:
            print(f"--{doctor_repository.get_doctor_by_user_id(user_id)}\n")
        if role == Role.PATIENT.value:
            print(f"--{patient_repository.get_patient_by_user_id(user_id)}\n")

    print("Пациенты:")
    for i in patient_repository.get_all_patients():
        print(i)

    print("Врачи:")
    for i in doctor_repository.get_all_doctors():
        print(i)

    app = MainApp()
    app.mainloop()
