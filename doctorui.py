import tkinter as tk
from tkinter import messagebox
from dbgestion import DB

class Doctor: 
    def __init__(self, iddoctor, db):
        self.iddoctor = iddoctor
        self.db = db
        self.build_window()
    
    def build_window(self):
        self.window = tk.Tk()
        self.window.title('Doctor View')
        self.window.geometry("300x200")

        #creating a place where we will print the patient of the doctor
        self.list = tk.Listbox(self.window)
        self.list.pack(fill=tk.BOTH, expand= True)
        #link to an event we we select one patient
        self.list.bind('<<ListboxSelect>>', self.patient_select)
        self.load_patients()

        #creating space for temperature visualisation
        tk.Label(self.window, text="Temperature of the patient:").pack()
        self.temp_text = tk.Text(self.window, height=6)
        self.temp_text.pack(fill=tk.BOTH, expand= True)

        #creating space for blood pressure visualisation
        tk.Label(self.window, text="Blood pressure of the patient:").pack()
        self.bp_text = tk.Text(self.window, height=6)
        self.bp_text.pack(fill= tk.BOTH, expand = True)


        self.window.mainloop()

    def load_patients(self):
        #we want to have a list of the patients of the doctor
        patients = self.db.get_patients_doctor(self.iddoctor)
        self.patients = patients  # garde pour lien idpatient <-> index
        for patient in patients:
            self.list.insert(tk.END, f"{patient['name']} {patient['lastname']} (ID: {patient['idpatient']})")  
        
    def patient_select(self, event):
        select = self.list.curselection()
        if not select:
            return
        index = select[0]
        #we will see in the list which is the patient to have his id
        patient = self.patients[index]
        idpatient = patient['idpatient']

        data = self.db.get_patient_data(idpatient)

        self.temp_text.delete('1.0', tk.END)
        self.bp_text.delete('1.0', tk.END)

        if not data:
            self.temp_text.insert(tk.END, "No temperature found for this patient.")
            self.bp_text.insert(tk.END, "No blood pressure found for this patient.")
            return
        else:
            for row in data:
                self.temp_text.insert(tk.END, f"{row['datetime']} — {row['temperature']}°C\n")
                self.bp_text.insert(tk.END, f"{row['datetime']} — {row['tension']}\n")
    

if __name__=='__main__': 
    db = DB('projet.db')

    iddoctor = 2

    doctor = Doctor(iddoctor, db)

    db.show_table('person')
    print('----------------------')
    db.show_table('patient')
    print('----------------------')
    db.show_table('doctor')
    print('----------------------')
    db.show_table('patient_data')
    print('----------------------')
    db.show_table('doctor_patient')