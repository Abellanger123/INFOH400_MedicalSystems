import tkinter as tk
from tkinter import messagebox
from dbgestion import DB
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import datetime, timedelta
import matplotlib.dates as mdates



class Doctor:
    def __init__(self, iddoctor, db):
        self.iddoctor = iddoctor
        self.db = DB(db)
        self.build_window()
    
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

        

        self.window.mainloop()

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

        if not data:
            self.temp_text.insert(tk.END, "No temperature data available for this patient.")
            self.bp_text.insert(tk.END, "No blood pressure data available for this patient.")
            self.plot_button.config(state=tk.DISABLED)
            self.selected_patient_data = None
        else:
            for row in data:
                self.temp_text.insert(tk.END, f"{row['datetime']} — {row['temperature']}°C\n")
                self.bp_text.insert(tk.END, f"{row['datetime']} — {row['tension']}\n")
            self.plot_button.config(state=tk.NORMAL)
            self.selected_patient_data = data

        self.selected_patient_name = f"{patient['name']} {patient['lastname']}"

        #Ajout : Affichage des prescriptions
        prescriptions = self.db.get_patient_prescriptions(idpatient)
        self.prescription_text.delete('1.0', tk.END)  
        if not prescriptions:
            self.prescription_text.insert(tk.END, "No prescription for this patient.")
        else:
            for p in prescriptions:
                statut = "Taken" if p['prise'] else "Not taken"
                self.prescription_text.insert(tk.END, f"{p['medicament']} — {p['frequence']} — {statut}\n")

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

        # Parse data
        dates = [datetime.strptime(entry["datetime"], "%Y-%m-%d %H:%M:%S") for entry in data]
        temperatures = [entry["temperature"] for entry in data]
        systolic = [int(entry["tension"].split("/")[0]) for entry in data]
        diastolic = [int(entry["tension"].split("/")[1]) for entry in data]

        # Create plot
        plt.figure(figsize=(10, 6))

        # Plot temperature
        plt.subplot(2, 1, 1)
        plt.plot(dates, temperatures, marker='o', color='red')
        plt.title(f"Temperature evolution - {patient_name}")
        plt.xlabel("Date")
        plt.ylabel("Temperature (°C)")
        plt.grid(True)

        # Format x-axis
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%d-%m"))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator())

        # Plot blood pressure
        plt.subplot(2, 1, 2)
        plt.plot(dates, systolic, marker='o', label='Systolic')
        plt.plot(dates, diastolic, marker='o', label='Diastolic')
        plt.title(f"Blood pressure evolution - {patient_name}")
        plt.xlabel("Date")
        plt.ylabel("Pressure (mmHg)")
        plt.legend()
        plt.grid(True)

        # Format x-axis
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%d-%m"))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator())

        # Improve layout
        plt.tight_layout()
        plt.show()

    def add_prescription(self):
        select = self.list.curselection()
        if not select:
            messagebox.showwarning("Warning", "Please select a patient.")
            return

        index = select[0]
        patient = self.patients[index]
        idpatient = patient['idperson']

        # Fenêtre pour saisir une prescription
        presc_window = tk.Toplevel(self.window)
        presc_window.title("Add a prescription")
        presc_window.geometry("300x200")

        tk.Label(presc_window, text="Medication :").pack(pady=5)
        med_entry = tk.Entry(presc_window)
        med_entry.pack(pady=5)

        tk.Label(presc_window, text="Frequency:").pack(pady=5)
        freq_entry = tk.Entry(presc_window)
        freq_entry.pack(pady=5)

        def save_prescription():
            med = med_entry.get().strip()
            freq = freq_entry.get().strip()

            if not med or not freq:
                messagebox.showerror("Error", "All fields must be filled.")
                return

            self.db.add_prescription(idpatient, med, freq)
            messagebox.showinfo("Succes", "Prescription added")
            presc_window.destroy()

        tk.Button(presc_window, text="Submit", command=save_prescription).pack(pady=10)



# Entry point of the app
if __name__ == '__main__':
    db = DB('projet.db')

