import tkinter as tk
from tkinter import messagebox
from dbgestion import DB

class Patient:
    def __init__(self, idpatient, db):
        self.idpatient = idpatient
        self.db = db
        self.build_window()

    def build_window(self):
        # Create main window
        self.window = tk.Tk()
        self.window.title("Your Medical Data")
        self.window.geometry("400x400")

        # --- Vital Signs Input ---
        tk.Label(self.window, text="Temperature (°C):").pack()
        self.tempEntry = tk.Entry(self.window, width=30)
        self.tempEntry.pack()

        tk.Label(self.window, text="Blood Pressure (e.g., 120/80):").pack()
        self.bpEntry = tk.Entry(self.window, width=30)
        self.bpEntry.pack()

        btn_submit = tk.Button(self.window, text="Submit Data", command=self.submit_data)
        btn_submit.pack(pady=10)

        # --- Separator ---
        tk.Label(self.window, text="--- Your Prescriptions ---", font=('Arial', 12, 'bold')).pack(pady=5)

        self.prescription_frame = tk.Frame(self.window)
        self.prescription_frame.pack(pady=5)

        self.display_prescriptions()

        self.window.mainloop()

    def submit_data(self):
        try:
            temp = float(self.tempEntry.get())
            bp = self.bpEntry.get()
            self.db.insert_patient_data(self.idpatient, temp, bp)
            messagebox.showinfo("Success", "Data has been saved.")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid temperature.")

    def display_prescriptions(self):
        prescriptions = self.db.get_prescriptions(self.idpatient)
        for idprescription, medication, frequency, taken in prescriptions:
            frame = tk.Frame(self.prescription_frame)
            frame.pack(anchor='w', padx=10, pady=2, fill='x')

            # Prescription text
            label = tk.Label(frame, text=f"{medication} - {frequency}")
            label.pack(side='left')

            # "Taken" checkbox
            var = tk.IntVar(value=taken)
            checkbox = tk.Checkbutton(frame, text="Taken", variable=var, command=lambda i=idprescription, v=var: self.mark_taken(i, v))

            # Prevent unchecking if already taken
            # if taken:
            #     checkbox.config(state=tk.DISABLED)

            checkbox.pack(side='right')

    def mark_taken(self, idprescription, var):
        if var.get() == 1:
            self.db.mark_as_taken(idprescription)
            messagebox.showinfo("Thank you", "Marked as taken.")


if __name__ == "__main__":
    db = DB("projet.db")
    # idpatient = 4  # Adjust patient ID if necessary
    # patient = Patient(idpatient, db)

    # # Debug: display tables content in console
    # db.show_table('person')
    # print('----------------------')
    # db.show_table('patient')
    # print('----------------------')
    # db.show_table('doctor')
    # print('----------------------')
    # db.show_table('patient_data')
    # print('----------------------')
    # db.show_table('doctor_patient')
