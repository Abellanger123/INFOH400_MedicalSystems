import tkinter as tk
from tkinter import messagebox
from dbgestion import DB
from datetime import datetime
from tkcalendar import DateEntry


class Patient:
    def __init__(self, idpatient, db):
        self.idpatient = idpatient
        self.db = DB(db)
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

        tk.Label(self.window, text="Select date to view:").pack()

        self.date_entry = DateEntry(self.window, width=30, background='darkblue',
                                    foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.date_entry.set_date(datetime.now())  # Default to today
        self.date_entry.pack()

        tk.Button(self.window, text="Show Prescriptions", command=self.refresh_prescriptions).pack(pady=5)

        self.refresh_prescriptions()
        self.window.mainloop()

    def submit_data(self):
        try:
            temp = float(self.tempEntry.get())
            bp = self.bpEntry.get()
            self.db.insert_patient_data(self.idpatient, temp, bp)
            messagebox.showinfo("Success", "Data has been saved.")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid temperature.")


    def display_prescriptions_by_date(self, date):
        cur = self.db.con.cursor()
        cur.execute("""
            SELECT ps.idschedule, p.medicament, ps.hour, ps.taken
            FROM prescription_schedule ps
            JOIN prescription p ON ps.idprescription = p.idprescription
            WHERE p.idpatient = ? AND ps.date = ?
            ORDER BY ps.hour
        """, (self.idpatient, date))
        rows = cur.fetchall()
        cur.close()

        for idschedule, medicament, hour, taken in rows:
            frame = tk.Frame(self.prescription_frame)
            frame.pack(anchor='w', padx=10, pady=2, fill='x')

            label = tk.Label(frame, text=f"{medicament} — {hour}")
            label.pack(side='left')

            var = tk.IntVar(value=taken)
            checkbox = tk.Checkbutton(frame, text="Taken", variable=var,
                                    command=lambda i=idschedule, v=var: self.mark_taken_schedule(i, v))
            checkbox.pack(side='right')


    def mark_taken_schedule(self, idschedule, var):
        if var.get() == 1:
            cur = self.db.con.cursor()
            cur.execute("UPDATE prescription_schedule SET taken = 1 WHERE idschedule = ?", (idschedule,))
            self.db.con.commit()
            cur.close()
            messagebox.showinfo("Merci", "Prise enregistrée.")

    def refresh_prescriptions(self):
        for widget in self.prescription_frame.winfo_children():
            widget.destroy()

        date = self.date_entry.get().strip()
        self.display_prescriptions_by_date(date)





if __name__ == "__main__":
    db = DB("projet.db")
 