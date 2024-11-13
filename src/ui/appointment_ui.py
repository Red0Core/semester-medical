import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry  # Нужно установить tkcalendar для выбора даты
from repositories import AppointmentRepository  # Предполагается, что есть PatientRepository с нужными методами

from datetime import datetime, timedelta

def generate_time_slots(start_time="10:00", end_time="18:00", interval_minutes=10, booked_slots_in_date: list | None=None, date=datetime.today()):
    if booked_slots_in_date is None:
        booked_slots_in_date = []
        
    time_slots = []
    current_time = datetime.strptime(start_time, "%H:%M")
    end_time = datetime.strptime(end_time, "%H:%M")

    if booked_slots_in_date:
        date = booked_slots_in_date[0].date()
    
    while current_time <= end_time:
        # Сравниваем только время, игнорируя дату
        slot = current_time.strftime("%H:%M")
        slot_datetime = datetime.combine(date, current_time.time())  # Получаем объект datetime с текущей датой
        
        # Проверяем, занято ли время
        if not any(slot_datetime.time() == booked_slot.time() for booked_slot in booked_slots_in_date):
            time_slots.append(slot)
        
        current_time += timedelta(minutes=interval_minutes)
    
    print(f"Слоты временные: {time_slots}")
    return time_slots

class AppointmentBookingWindow(tk.Toplevel):
    def __init__(self, patient_id,
                 appointment_repository: AppointmentRepository,
                 fetch_doctors):
        super().__init__()
        self.patient_id = patient_id
        self.appointment_repository = appointment_repository
        self.get_all_doctors = fetch_doctors
        self.title("Запись к врачу")

        # Выбор врача
        self.doctors = self.get_all_doctors()
        self.doctor_combobox = ttk.Combobox(self, values=[f"{doc['name']} - {doc['speciality']}" for doc in self.doctors])
        self.doctor_combobox.set("Выберите врача")
        self.doctor_combobox.pack(pady=10, fill=tk.X)
        self.doctor_combobox.bind("<<ComboboxSelected>>", self.update_time_slots)

        # Выбор даты
        self.date_label = ttk.Label(self, text="Выберите дату:")
        self.date_label.pack(pady=5)
        self.date_entry = DateEntry(self, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.date_entry.pack(pady=5)
        self.date_entry.bind("<<DateEntrySelected>>", self.update_time_slots)

        # Выбор времени
        self.time_label = ttk.Label(self, text="Выберите время:")
        self.time_label.pack(pady=5)
        self.time_combobox = ttk.Combobox(self)
        self.time_combobox.set("Сначала выберите врача и дату")
        self.time_combobox.pack(pady=5)

        # Кнопка для записи на прием
        self.book_button = ttk.Button(self, text="Записаться", command=self.book_appointment)
        self.book_button.pack(pady=10)

    def update_time_slots(self, event=None):
        # Проверка, что выбран врач и дата
        selected_doctor_name = [x.strip() for x in self.doctor_combobox.get().split('-')][0] # Выделяет имя с комбобокса
        selected_date = self.date_entry.get_date()
        
        if selected_doctor_name == "Выберите врача":
            return

        # Получаем ID выбранного врача
        selected_doctor = next((doc for doc in self.doctors if doc['name'] == selected_doctor_name), None)
        if selected_doctor:
            doctor_id = selected_doctor["doctor_id"]
            
            # Получаем занятые слоты для выбранного врача и даты
            booked_slots = self.appointment_repository.get_booked_slots_in_one_day(doctor_id, selected_date)
            print(f"Слоты занятые: {booked_slots}")
            # Генерируем свободные временные слоты с учетом уже забронированных
            available_time_slots = generate_time_slots(booked_slots_in_date=booked_slots)
            self.time_combobox.config(values=available_time_slots)
            self.time_combobox.set("Выберите время")

    def book_appointment(self):
        selected_doctor_name = [x.strip() for x in self.doctor_combobox.get().split('-')][0] # Выделяет имя с комбобокса
        selected_date = self.date_entry.get_date()

        if selected_date < datetime.today().date():
            messagebox.showerror(message="Нельзя записаться на старую дату!")
            return
        
        selected_time = self.time_combobox.get()

        # Проверка, что врач и время выбраны
        if selected_doctor_name == "Выберите врача" or selected_time == "Выберите время":
            messagebox.showwarning(message="Пожалуйста, выберите врача и время.")
            return
        
        selected_time = [int(x) for x in self.time_combobox.get().split(":")]

        # Получаем ID выбранного врача
        selected_doctor = next((doc for doc in self.doctors if doc['name'] == selected_doctor_name), None)
        if selected_doctor:
            doctor_id = selected_doctor["doctor_id"]
            appointment_time = datetime(year=selected_date.year, month=selected_date.month, day=selected_date.day,
                                         hour=selected_time[0], minute=selected_time[1])
            try:
                self.appointment_repository.add_appointment(self.patient_id, doctor_id, appointment_time)
                messagebox.showinfo(message="Запись успешно добавлена")
            except Exception as e:
                messagebox.showerror(message=f"Ошибка: {str(e)}")

        self.update_time_slots()
        