import tkinter as tk
from tkinter import messagebox
from db_management import DatabaseManager

class PatientApp:
    def __init__(self, root):
        self.db = DatabaseManager()
        self.root = root
        self.root.title("Patient Login")
        self.root.geometry("300x200")

        # Login Frame
        self.login_frame = tk.Frame(root)
        self.login_frame.pack(pady=20)

        tk.Label(self.login_frame, text="First Name:").grid(row=0, column=0)
        self.first_name_entry = tk.Entry(self.login_frame)
        self.first_name_entry.grid(row=0, column=1)

        tk.Label(self.login_frame, text="Last Name:").grid(row=1, column=0)
        self.last_name_entry = tk.Entry(self.login_frame)
        self.last_name_entry.grid(row=1, column=1)

        self.login_button = tk.Button(self.login_frame, text="Login", command=self.login)
        self.login_button.grid(row=2, columnspan=2, pady=10)

    def login(self):
        first_name = self.first_name_entry.get()
        last_name = self.last_name_entry.get()

        user = self.db.cursor.execute(
            "SELECT ID FROM Users WHERE FirstName = ? AND LastName = ? AND Role = 'Patient'", 
            (first_name, last_name)
        ).fetchone()

        if user:
            self.user_id = user[0]
            self.open_patient_dashboard()
        else:
            messagebox.showerror("Error", "Patient not found or incorrect credentials.")

    def open_patient_dashboard(self):
        self.login_frame.destroy()
        self.root.title("Add Vital Signs")

        # Dashboard Frame
        self.dashboard_frame = tk.Frame(self.root)
        self.dashboard_frame.pack(pady=20)

        tk.Label(self.dashboard_frame, text="Date (YYYY-MM-DD):").grid(row=0, column=0)
        self.date_entry = tk.Entry(self.dashboard_frame)
        self.date_entry.grid(row=0, column=1)

        tk.Label(self.dashboard_frame, text="Blood Pressure:").grid(row=1, column=0)
        self.bp_entry = tk.Entry(self.dashboard_frame)
        self.bp_entry.grid(row=1, column=1)

        tk.Label(self.dashboard_frame, text="Temperature:").grid(row=2, column=0)
        self.temp_entry = tk.Entry(self.dashboard_frame)
        self.temp_entry.grid(row=2, column=1)

        tk.Label(self.dashboard_frame, text="Heart Rate:").grid(row=3, column=0)
        self.hr_entry = tk.Entry(self.dashboard_frame)
        self.hr_entry.grid(row=3, column=1)

        tk.Label(self.dashboard_frame, text="Blood Glucose:").grid(row=4, column=0)
        self.bg_entry = tk.Entry(self.dashboard_frame)
        self.bg_entry.grid(row=4, column=1)

        self.submit_button = tk.Button(self.dashboard_frame, text="Submit", command=self.add_vital_signs)
        self.submit_button.grid(row=5, columnspan=2, pady=10)

    def add_vital_signs(self):
        date = self.date_entry.get()
        blood_pressure = self.bp_entry.get()
        temperature = self.temp_entry.get()
        heart_rate = self.hr_entry.get()
        blood_glucose = self.bg_entry.get()

        try:
            # Add vital signs for the logged-in patient
            self.db.add_vital_signs(self.user_id, date, blood_pressure, float(temperature), int(heart_rate), float(blood_glucose))
            messagebox.showinfo("Success", "Vital signs added successfully.")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid data.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = PatientApp(root)
    root.mainloop()
