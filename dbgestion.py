import sqlite3 as sql

class DB:
    def __init__(self, dbfile):
        self.dbfile = dbfile      #self est ici pour référencer à l'objet lui-même ses attributs
        self.con = sql.connect(dbfile)

    def insert_person(self, Name, DateOfBirth, LastName, Email, Password, Role):
        cur = self.con.cursor() 
        cur.execute("""INSERT INTO person (name, lastname, dateofbirth, email, password, role)
                    VALUES (?, ?, ?, ?, ?, ?) RETURNING idperson;""",
                    (Name, LastName, DateOfBirth, Email, Password, Role))
        idperson = cur.fetchone()[0]
        self.con.commit()
        cur.close()
        return idperson
    
    def insert_patient_data(self, idpatient, temperature, tension, datetime=None):
        cur = self.con.cursor()
        
        # Si aucune date/heure n'est précisée, on utilise l'heure actuelle
        if datetime is None:
            from datetime import datetime as dt
            datetime = dt.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Insertion dans la table patient_data
        cur.execute("""
            INSERT INTO patient_data (idpatient, temperature, tension, datetime)
            VALUES (?, ?, ?, ?) RETURNING iddata;
        """, (idpatient, temperature, tension, datetime))
        
        iddata = cur.fetchone()[0]
        self.con.commit()
        cur.close()
        return iddata
    
    def link_doctor_to_patient(self, iddoctor, idpatient):
        cur = self.con.cursor()

        # Vérifie si la relation existe déjà pour éviter les doublons
        cur.execute("""
            SELECT 1 FROM doctor_patient WHERE iddoctor = ? AND idpatient = ?
        """, (iddoctor, idpatient))
        exists = cur.fetchone()

        if not exists:
            # Ajoute la relation
            cur.execute("""
                INSERT INTO doctor_patient (iddoctor, idpatient)
                VALUES (?, ?)
            """, (iddoctor, idpatient))
            self.con.commit()
        
        cur.close()

    def get_patients_doctor(self, iddoctor):
        cur = self.con.cursor()
        cur.execute("""
            SELECT p.idperson, p.name, p.lastname
            FROM doctor_patient dp 
            JOIN person p ON dp.idpatient = p.idperson
            WHERE dp.iddoctor = ?
        """,(iddoctor,))
        rows = cur.fetchall()
        cur.close()
        return [dict(zip(['idperson', 'name', 'lastname'], row)) for row in rows]
        
    def get_patient_data(self,idpatient):
        cur = self.con.cursor()
        cur.execute("""
            SELECT temperature, tension, datetime
            FROM patient_data
            WHERE idpatient = ?
            ORDER BY datetime DESC
        """, (idpatient,))
        rows = cur.fetchall()
        cur.close()
        return  [dict(zip(['temperature', 'tension', 'datetime'], row)) for row in rows]


    def __del__(self):
        #In the case where the object would destroyed, we want our connection to end smmothly, with commit and close.
        self.con.commit()
        self.con.close()
    
    def show_table(self, table_name):
        cur = self.con.cursor()
        cur.execute(f"SELECT * FROM {table_name};")
        rows = cur.fetchall()
        cur.close()
        for row in rows:
            print(row)

    def add_prescription(self, idpatient, medicament, frequence):
        cursor = self.con.cursor()
        print("add_prescription called")
        cursor.execute("""
            INSERT INTO prescription (idpatient, medicament, frequence, prise, horodatage)
            VALUES (?, ?, ?, 0, datetime('now'))
        """, (idpatient, medicament, frequence))
        self.con.commit()

    def get_prescriptions(self, idpatient):
        cursor = self.con.cursor()
        cursor.execute("""
            SELECT idprescription, medicament, frequence, prise
            FROM prescription
            WHERE idpatient = ?
        """, (idpatient,))
        return cursor.fetchall()

    def mark_as_taken(self, idprescription):
        cursor = self.con.cursor()
        cursor.execute("""
            UPDATE prescription
            SET prise = 1
            WHERE idprescription = ?
        """, (idprescription,))
        self.con.commit()

    def get_patient_prescriptions(self, idpatient):
        cursor = self.con.cursor()
        cursor.execute("""
            SELECT medicament, frequence, prise
            FROM prescription
            WHERE idpatient = ?
        """, (idpatient,))
        rows = cursor.fetchall()
        return [{'medicament': r[0], 'frequence': r[1], 'prise': r[2]} for r in rows]
    
    def get_id_person_by_email(self, email):
        cur = self.con.cursor()
        cur.execute("""SELECT idperson FROM person WHERE email = ?;""", (email,))
        result = cur.fetchone()
        cur.close()
        return result[0] 

    
    def authentification(self, email, password):
        cur = self.con.cursor()
        cur.execute("""SELECT role, password FROM person WHERE email = ?;""", (email,))
        res = cur.fetchall()
        if len(res)==0:                 #nobody found with this email 
            return 0
        elif res[0][1] == password:
            return res[0][0]               #return = role
        else: 
            return 1                    #there is no correspondance between the password and the email


