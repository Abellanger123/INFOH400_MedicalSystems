import tkinter as tk
from tkinter import messagebox
from dbgestion import DB
import re 
from patientui import Patient
from doctorui import Doctor
from account import Account


class Login: 
    def __init__(self, dbfile):
        self.dbfile = dbfile
        self.db = DB(dbfile)
        self.build()



    def build(self):
        #create the window
        self.window = tk.Tk()
        self.window.title('Login page')
        self.window.geometry('600x400')

        #Label login
        tk.Label(self.window, text='Enter your email and your password').pack(pady=(30,20))

        #email text
        tk.Label(self.window, text='Email:').pack(pady=10)
        self.email = tk.Entry(self.window, width=30)
        self.email.pack()

        #password text
        tk.Label(self.window, text='Password:').pack(pady=10)
        self.password = tk.Entry(self.window, width=30)
        self.password.pack()

        #Login button
        tk.Button(self.window, text='Submit', command=self.log).pack(pady=10)

        #New account button
        tk.Button(self.window, text='New Account', command=self.new_account).pack(pady=10)
        
        self.window.mainloop()


    def log(self):
        email = self.email.get()
        password = self.password.get()
        if not self.is_valid_email(email):   #verify if the e-mail is valid
            messagebox.showerror("Invalid Email", "The email you entered is not valid, please retry after correction.")
        
        else: 
            auth = self.db.authentification(email, password)
            if auth == 0:
                messagebox.showerror("Invalid Email", "The email you entered is not associated with an account.")
            elif auth == 1:
                messagebox.showerror("Invalid Password", "The password you entered is not correct")
            else:
                id = self.db.get_id_person_by_email(email)
                if auth == 'patient':
                    self.is_patient(id, self.dbfile)
                else : 
                    self.is_doctor(id, self.dbfile)


    def is_patient(self, idpatient, db):
        if self.window:
            self.window.destroy()
        patient = Patient(idpatient, db)
    
    def is_doctor(self, iddoctor, db):
        if self.window:
            self.window.destroy()
        doctor = Doctor(iddoctor, db)



    def is_valid_email(self, email):
        #Email pattern = some characters + @ + some character + . + some characters.
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        #Check if the email matches the pattern
        if re.match(email_pattern,email):
            return True
        else:
            return False
        

    def new_account(self):
        Account(self.window, self.dbfile)



def main():
   
    log = Login('projet.db')

if __name__ == "__main__":
    main()

