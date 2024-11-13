import tkinter as tk
from tkinter import ttk
from ui.appointment_ui import AppointmentBookingWindow
from ui.medical_record_ui import MedicalRecordWindowView
from repositories import AppointmentRepository, PatientRepository

class PatientUI(tk.Toplevel):
    def __init__(self, user_id: int, patient_repository: PatientRepository, appointment_repository: AppointmentRepository, fetch_doctors_func):
        super().__init__()

        self.patient_repository = patient_repository
        self.appointment_repository = appointment_repository
        self.fetch_doctors = fetch_doctors_func
        patient_info = self.patient_repository.get_patient_by_user_id(user_id)
        
        self.name = patient_info['name']
        self.patient_id = patient_info['patient_id']

        self.title("Меню пациента")

        # Обозначение пациента
        self.label = ttk.Label(self, text=f"Здравствуйте, {self.name}")
        self.label.pack(pady=10)

        # Кнопки для просмотра своей карточки
        self.btn_manage_patients = ttk.Button(self, text="Ваша медицинская карта", command=self.view_medical_record)
        self.btn_manage_patients.pack(pady=5)

        # Кнопка для записи к врачу
        self.btn_view_requests = ttk.Button(self, text="Записаться к врачу", command=self.make_appointment)
        self.btn_view_requests.pack(pady=5)

        # Кнопка выхода
        self.btn_exit = ttk.Button(self, text="Выйти", command=self.destroy)
        self.btn_exit.pack(pady=20)

    def view_medical_record(self):
        """
        Передает вызов окну с просмотром мед карты
        """
        MedicalRecordWindowView(self.patient_id, self.patient_repository)
    
    def make_appointment(self):
        """
        Передает вызов окну с записью к врачу
        """
        AppointmentBookingWindow(self.patient_id, self.appointment_repository, fetch_doctors=self.fetch_doctors)
