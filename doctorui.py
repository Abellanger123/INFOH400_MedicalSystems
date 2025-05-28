import tkinter as tk
from tkinter import messagebox
from dbgestion import DB
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import datetime, timedelta
import matplotlib.dates as mdates
from tkcalendar import DateEntry



class Doctor:
    def __init__(self, iddoctor, db):
        self.iddoctor = iddoctor
        self.db = DB(db)
        self.build_window()       
        self.check_initial_alerts()    
        self.window.mainloop()         
    
    def build_window(self):
        self.window = tk.Tk()
        self.window.title('Doctor View')
        self.window.geometry("500x550")

        # Patient list on the left
        self.list = tk.Listbox(self.window)
        self.list.pack(fill=tk.BOTH, expand=True)
        self.list.bind('<<ListboxSelect>>', self.patient_select)
        self.load_patients()

        # Display for temperature records
        tk.Label(self.window, text="Temperature of the patient:").pack()
        self.temp_text = tk.Text(self.window, height=6)
        self.temp_text.pack(fill=tk.BOTH, expand=True)

        # Display for blood pressure records
        tk.Label(self.window, text="Blood pressure of the patient:").pack()
        self.bp_text = tk.Text(self.window, height=6)
        self.bp_text.pack(fill=tk.BOTH, expand=True)

        # Heart rate display
        tk.Label(self.window, text="Heart rate of the patient:").pack()
        self.hr_text = tk.Text(self.window, height=4)
        self.hr_text.pack(fill=tk.BOTH, expand=True)

        # Glucose level display
        tk.Label(self.window, text="Glucose level of the patient:").pack()
        self.glucose_text = tk.Text(self.window, height=4)
        self.glucose_text.pack(fill=tk.BOTH, expand=True)

        # Button to show plots
        self.plot_button = tk.Button(self.window, text="View Graphs", command=self.show_graphs)
        self.plot_button.pack(pady=10)
        self.plot_button.config(state=tk.DISABLED)  # Initially disabled

        # Attributes to store selected data
        self.selected_patient_data = None
        self.selected_patient_name = ""

        
        # Bouton pour ajouter une prescription
        self.prescription_button = tk.Button(self.window, text="Add Prescription", command=self.add_prescription)
        self.prescription_button.pack(pady=5)
        self.prescription_button.config(state=tk.DISABLED)  # Disabled until the patient is choosen

        # Zone pour afficher les prescriptions du patient sélectionné
        tk.Label(self.window, text="Prescriptions:").pack()
        self.prescription_text = tk.Text(self.window, height=6)
        self.prescription_text.pack(fill=tk.BOTH, expand=True)


    def load_patients(self):
        # Load the doctor's patients from the database
        patients = self.db.get_patients_doctor(self.iddoctor)
        self.patients = patients
        for patient in patients:
            self.list.insert(tk.END, f"{patient['name']} {patient['lastname']} (ID: {patient['idperson']})")

    def patient_select(self, event):
        select = self.list.curselection()
        if not select:
            return
        self.prescription_button.config(state=tk.NORMAL)

        index = select[0]
        patient = self.patients[index]
        idpatient = patient['idperson']

        # Fetch medical data
        data = self.db.get_patient_data(idpatient)

        self.temp_text.delete('1.0', tk.END)
        self.bp_text.delete('1.0', tk.END)
        self.hr_text.delete('1.0', tk.END)
        self.glucose_text.delete('1.0', tk.END)
        self.prescription_text.delete('1.0', tk.END)

        if not data:
            self.temp_text.insert(tk.END, "No temperature data available for this patient.")
            self.bp_text.insert(tk.END, "No blood pressure data available for this patient.")
            self.hr_text.insert(tk.END, "No heart rate data available for this patient.")
            self.glucose_text.insert(tk.END, "No glucose data available for this patient.")
            self.plot_button.config(state=tk.DISABLED)
            self.selected_patient_data = None
        else:
            for row in data:
                self.temp_text.insert(tk.END, f"{row['datetime']} — {row['temperature']}°C\n")
                self.bp_text.insert(tk.END, f"{row['datetime']} — {row['tension']}\n")
                self.hr_text.insert(tk.END, f"{row['datetime']} — {row.get('heartrate', 'N/A')} bpm\n")
                self.glucose_text.insert(tk.END, f"{row['datetime']} — {row.get('glucose', 'N/A')} mg/dL\n")
            self.plot_button.config(state=tk.NORMAL)
            self.selected_patient_data = data

        self.selected_patient_name = f"{patient['name']} {patient['lastname']}"

        # --- Prescriptions résumé ---
        prescriptions = self.db.get_patient_prescriptions(idpatient)
        if not prescriptions:
            self.prescription_text.insert(tk.END, "No prescription for this patient.\n")
        else:
            for p in prescriptions:
                self.prescription_text.insert(
                    tk.END,
                    f"{p['medicament']} — from {p['start_date']} to {p['end_date']}\n"
                )

        # --- Détail journalier des prises ---
        schedules = self.db.get_prescription_schedule_for_patient(idpatient)
        if schedules:
            self.prescription_text.insert(tk.END, "\nDetailed schedule:\n")
            for med, date, hour, taken in schedules:
                status = "✅ Taken" if taken else "❌ Not taken"
                self.prescription_text.insert(
                    tk.END,
                    f"{date} at {hour} — {med} — {status}\n"
                )
        else:
            self.prescription_text.insert(tk.END, "\nNo scheduled doses found.")



    def show_graphs(self):
        # Trigger plotting if data is selected
        if not self.selected_patient_data:
            messagebox.showwarning("Warning", "No data available to display graphs.")
            return
        self.plot_patient_data(self.selected_patient_data, self.selected_patient_name)



    def plot_patient_data(self, data, patient_name="Patient"):
        if not data:
            print("No data to display.")
            return

        dates = [datetime.strptime(entry["datetime"], "%Y-%m-%d %H:%M:%S") for entry in data]
        temperatures = [entry["temperature"] for entry in data]
        systolic = [int(entry["tension"].split("/")[0]) for entry in data]
        diastolic = [int(entry["tension"].split("/")[1]) for entry in data]

        heartrates = [entry.get("heartrate") for entry in data]
        glucose = [entry.get("glucose") for entry in data]

        plt.figure(figsize=(12, 10))

        # Température
        plt.subplot(4, 1, 1)
        plt.plot(dates, temperatures, marker='o', color='red')
        plt.title(f"Temperature Evolution - {patient_name}")
        plt.ylabel("Temperature (°C)")
        plt.grid(True)
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%d-%m"))

        # Pression artérielle
        plt.subplot(4, 1, 2)
        plt.plot(dates, systolic, marker='o', label='Systolic')
        plt.plot(dates, diastolic, marker='o', label='Diastolic')
        plt.title("Blood Pressure Evolution")
        plt.ylabel("Pressure (mmHg)")
        plt.legend()
        plt.grid(True)
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%d-%m"))

        # Fréquence cardiaque
        if any(h is not None for h in heartrates):
            plt.subplot(4, 1, 3)
            plt.plot(dates, heartrates, marker='o', color='blue')
            plt.title("Heart Rate Evolution")
            plt.ylabel("BPM")
            plt.grid(True)
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%d-%m"))

        # Glycémie
        if any(g is not None for g in glucose):
            plt.subplot(4, 1, 4)
            plt.plot(dates, glucose, marker='o', color='green')
            plt.title("Glucose Level Evolution")
            plt.xlabel("Date")
            plt.ylabel("mg/dL")
            plt.grid(True)
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%d-%m"))

        plt.tight_layout()
        plt.show()


    from tkcalendar import DateEntry

    def add_prescription(self):
        select = self.list.curselection()
        if not select:
            messagebox.showwarning("Warning", "Please select a patient.")
            return

        index = select[0]
        patient = self.patients[index]
        idpatient = patient['idperson']

        # Popup window
        presc_window = tk.Toplevel(self.window)
        presc_window.title("Add a prescription")
        presc_window.geometry("350x400")

        # Medication name
        tk.Label(presc_window, text="Medication:").pack(pady=5)
        med_entry = tk.Entry(presc_window)
        med_entry.pack(pady=5)

        # Start date
        tk.Label(presc_window, text="Start date:").pack()
        start_date = DateEntry(presc_window, date_pattern='yyyy-mm-dd')
        start_date.pack(pady=5)

        # End date
        tk.Label(presc_window, text="End date:").pack()
        end_date = DateEntry(presc_window, date_pattern='yyyy-mm-dd')
        end_date.pack(pady=5)

        # Time entries
        tk.Label(presc_window, text="Hours (max 4):").pack(pady=5)

        hour_entries = []
        for i in range(4):
            entry = tk.Entry(presc_window, width=10)
            entry.insert(0, "")  # leave empty by default
            entry.pack()
            hour_entries.append(entry)

        def save_prescription():
            med = med_entry.get().strip()
            sd = start_date.get_date().strftime('%Y-%m-%d')
            ed = end_date.get_date().strftime('%Y-%m-%d')
            hours = [e.get().strip() for e in hour_entries if e.get().strip()]

            if not med or not hours:
                messagebox.showerror("Error", "Please fill medication and at least one hour.")
                return

            self.db.add_prescription_with_hours(idpatient, med, sd, ed, hours)
            messagebox.showinfo("Success", "Prescription added successfully.")
            presc_window.destroy()

        tk.Button(presc_window, text="Submit", command=save_prescription).pack(pady=10)

    def check_initial_alerts(self):
        alerts = self.db.get_alerts_for_doctor(self.iddoctor)

        if alerts:
            from tkinter import messagebox

            for dt, msg, name, lastname in alerts:
                message = f"{dt} — {name} {lastname}\n{msg}"
                messagebox.showwarning("⚠️ Patient Alert", message)

            # Supprimer les alertes une fois affichées
            self.db.delete_alerts_for_doctor(self.iddoctor)




# Entry point of the app
if __name__ == '__main__':
    db = DB('projet.db')

