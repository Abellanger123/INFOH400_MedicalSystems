import tkinter as tk
from tkinter import ttk, messagebox
from dbgestion import DB



class Account(tk.Toplevel):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.build()
        self.db = DB(db)


    def build(self):
        self.title('New Account')
        self.geometry('700x600')


        #name of the person
        tk.Label(self, text='Enter your name:').pack(pady=(20,5))
        self.name = tk.Entry(self,width=30)
        self.name.pack(pady=5)

        #last_name 
        tk.Label(self, text='Enter your lastname:').pack(pady=(20,5))
        self.lastname= tk.Entry(self, width=30)
        self.lastname.pack(pady=5)

        #dateofbirth
        tk.Label(self, text='Enter your dateofbirth:').pack(pady=(20,5))
        self.dateofbirth= tk.Entry(self, width=30)
        self.dateofbirth.pack(pady=5)

        #email
        tk.Label(self, text='Enter your email:').pack(pady=(20,5))
        self.email= tk.Entry(self, width=30)
        self.email.pack(pady=5)

        #password
        tk.Label(self, text='Enter a password:').pack(pady=(20,5))
        self.password= tk.Entry(self, width=30)
        self.password.pack(pady=5)

        #Doctor or patient
        tk.Label(self, text="Are you a patient or a doctor:").pack(pady=(20, 5))
        self.role= tk.StringVar()
        self.role_com= ttk.Combobox(self, textvariable=self.role)
        self.role_com['values'] = ("patient", "doctor")
        self.role_com['state'] = 'readonly'  # pour empêcher l'utilisateur de taper autre chose
        self.role_com.bind("<<ComboboxSelected>>", self.on_role_selected)
        self.role_com.pack(pady=5)
        
        self.doctor_frame = tk.Frame(self)
        self.doctor_frame.pack(pady=(10, 5))


        #button create account 
        tk.Button(self, text='Create your account', command=self.submit).pack(pady=20)


    def submit(self):
        name = self.name.get()
        lastname = self.lastname.get()
        dateofbirth = self.dateofbirth.get()
        email = self.email.get()
        password = self.password.get()
        role = self.role.get()


        #insert into the database
        idp = self.db.insert_person(name,dateofbirth,lastname,email,password,role)

        #link the patient and the doctor
        if role == 'patient':
            selected_doctor = self.doctor_var.get()
            if selected_doctor:
                idd = self.doctor_map[selected_doctor]
                self.db.link_doctor_to_patient(idd, idp)
        
        messagebox.showinfo('Succes! Your account is ready.')
        self.destroy()



    def on_role_selected(self, event=None):
        for widget in self.doctor_frame.winfo_children():
            widget.destroy()
        
        if self.role.get() == 'patient':
            tk.Label(self.doctor_frame, text="Who is your doctor:").pack()

            doctors = self.db.alldoctor()
            if not doctors:
                tk.Label(self.doctor_frame, text='Your doctor needs to be already registered.').pack()
                return
            
            self.doctor_map = {f"{name} {lastname}": idperson for idperson, name, lastname in doctors}
            doctor_names = list(self.doctor_map.keys())  

            self.doctor_var = tk.StringVar()
            self.doctor_combobox = ttk.Combobox(self.doctor_frame, textvariable=self.doctor_var, values=doctor_names, state='readonly')
            self.doctor_combobox.pack()









        












