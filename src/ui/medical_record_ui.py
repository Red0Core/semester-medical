import tkinter as tk
from tkinter import ttk, messagebox

from repositories import PatientRepository

class MedicalRecordWindowView(tk.Toplevel):
    def __init__(self, patient_id, patient_repository: PatientRepository) -> None:
        super().__init__()
        self.title = "Медицинская карта пациента"
        self.patient_id = patient_id
        self.repository = patient_repository

        self.label = ttk.Label(self, text="Медицинская карта пациента", font=("Arial", 14))
        self.label.pack(pady=10)

        # Многострочное поле для отображения медицинской карты
        self.record_text = tk.Text(self, wrap="word")
        self.record_text.insert(tk.END, self.repository.get_patient_record(self.patient_id)['record'])
        self.record_text.config(state=tk.DISABLED)  # только для чтения
        self.record_text.pack(pady=10)

        # Кнопка "Закрыть"
        self.close_button = ttk.Button(self, text="Закрыть", command=self.destroy)
        self.close_button.pack(pady=5)

class MedicalRecordWindowEdit(MedicalRecordWindowView):
    def __init__(self, patient_id, patient_repository: PatientRepository):
        super().__init__(patient_id, patient_repository)

        self.record_text.config(state=tk.NORMAL)

        # Кнопка "Сохранить"
        self.save_button = ttk.Button(self, text="Сохранить", command=self.save_record)
        self.save_button.pack(pady=5)
    
    def save_record(self):
        # Сохранить изменения в базе данных
        new_record = self.record_text.get("1.0", tk.END).strip()
        if new_record:
            self.repository.update_medical_record(self.patient_id, new_record)
            messagebox.showinfo("Сохранено", "Медицинская карта успешно обновлена!")
        else:
            messagebox.showwarning("Ошибка", "Запись не может быть пустой!")