import tkinter as tk
from tkinter import ttk, messagebox
from repositories import DoctorRepository, AppointmentRepository, PatientRepository
from ui.medical_record_ui import MedicalRecordWindowEdit

class DoctorUI(tk.Toplevel):
    def __init__(self, user_id, doctor_repository: DoctorRepository, appointment_repository: AppointmentRepository, patient_repository: PatientRepository):
        super().__init__()

        self.title("Список записей")

        self.doctor_repository = doctor_repository
        self.appointment_repository = appointment_repository
        self.patient_repository = patient_repository

        self.doctor = doctor_repository.get_doctor_by_user_id(user_id=user_id)

        self.label = ttk.Label(self, text=f"Здравствуйте, {self.doctor['name']}")
        self.label.pack(pady=10)

        # Создаем виджет Treeview
        self.tree = ttk.Treeview(self, columns=("ID", "Name", "Date"), show="headings")
        self.tree.heading("ID", text='ID')
        self.tree.heading("Name", text="Имя")
        self.tree.heading("Date", text="Дата")
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.edit_button = ttk.Button(self, text="Открыть запись", command=self.edit_record)
        self.edit_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.load_records_to_tree_view()

    def load_records_to_tree_view(self):
        """Загружает список записей к этому доктору в Treeview."""
        for row in self.tree.get_children():
            self.tree.delete(row)  # Очистка списка перед загрузкой новых данных

        appointments = self.appointment_repository.get_appointments_by_doctor_id(self.doctor['doctor_id'])

        for appointment in appointments:
            self.tree.insert("", tk.END, values=(appointment['patient_id'], appointment['name'], str(appointment['appointment_time'])))

    def edit_record(self):
        """Открыает окно мед карты выбранного пациента"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Ошибка", "Выберите доктора для редактирования.")
            return

        patient_id = self.tree.item(selected_item[0])["values"][0]

        MedicalRecordWindowEdit(patient_id, self.patient_repository)