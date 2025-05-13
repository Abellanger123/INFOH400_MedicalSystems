import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from dbgestion import DB
class Patient:
    def __init__(self, idpatient, db):
        self.idpatient = idpatient
        self.db = db
        self.build_window()

    def build_window(self):
        #creating the window itself
        self.window = tk.Tk()
        self.window.title("Your data")
        self.window.geometry("300x200")

        #creating the entry for temperature
        tk.Label(self.window, text="Temperature (°C) :").pack()
        self.tempEntry = tk.Entry(self.window, width=30)
        self.tempEntry.pack()

        #creating the entry for tension
        tk.Label(self.window,text="Blood pressure : ").pack()
        self.bpEntry = tk.Entry(self.window, width=30)
        self.bpEntry.pack()

        btn_submit = tk.Button(self.window, text="Submit", command=self.submit_data)
        btn_submit.pack(pady=10)

        self.window.mainloop()

    
    def submit_data(self):
        try:
            temp = float(self.tempEntry.get())
            bp = self.bpEntry.get()

            self.db.insert_patient_data(self.idpatient, temp, bp)
            messagebox.showinfo("Succès", "Les données ont été enregistrées avec succès.")

        except ValueError: 
            messagebox.showerror("Erreur", "Not valid temperature")



if __name__== "__main__":
    db = DB("projet.db")
    idpatient = 1
    patient= Patient(idpatient, db)

    db.show_table('person')
    print('----------------------')
    db.show_table('patient')
    print('----------------------')
    db.show_table('doctor')
    print('----------------------')
    db.show_table('patient_data')
    print('----------------------')
    db.show_table('doctor_patient')