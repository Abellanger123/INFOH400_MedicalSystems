import sqlite3 as sql
from datetime import datetime, timedelta


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
        from datetime import datetime as dt
        if datetime is None:
            datetime = dt.now().strftime('%Y-%m-%d %H:%M:%S')

        with self.con:  # starts and commits transaction safely
            cur = self.con.cursor()

            cur.execute("""
                INSERT INTO patient_data (idpatient, temperature, tension, datetime)
                VALUES (?, ?, ?, ?) RETURNING iddata;
            """, (idpatient, temperature, tension, datetime))
            iddata = cur.fetchone()[0]

            # Insert alerts using the same cursor and transaction
            self._insert_alerts_if_needed(cur, idpatient, temperature, tension, datetime)

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
    
    def alldoctor(self):
        cur = self.con.cursor()
        cur.execute("""
            SELECT idperson, name, lastname
            FROM person
            WHERE role = 'doctor';
        """)
        doctors = cur.fetchall()
        cur.close()
        return doctors 


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
            SELECT medicament, start_date, end_date
            FROM prescription
            WHERE idpatient = ?
        """, (idpatient,))
        rows = cursor.fetchall()
        cursor.close()
        return [{'medicament': r[0], 'start_date': r[1], 'end_date': r[2]} for r in rows]

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

    from datetime import datetime, timedelta

    def add_prescription_with_hours(self, idpatient, medicament, start_date, end_date, hours_list):
        cur = self.con.cursor()

        # Ajouter prescription
        cur.execute("""
            INSERT INTO prescription (idpatient, medicament, start_date, end_date)
            VALUES (?, ?, ?, ?)
        """, (idpatient, medicament, start_date, end_date))
        idprescription = cur.lastrowid

        # Ajouter les prises programmées
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        while start <= end:
            for hour in hours_list:
                cur.execute("""
                    INSERT INTO prescription_schedule (idprescription, date, hour)
                    VALUES (?, ?, ?)
                """, (idprescription, start.strftime("%Y-%m-%d"), hour))
            start += timedelta(days=1)
 
        self.con.commit()
        cur.close()

    def _insert_alerts_if_needed(self, cur, idpatient, temperature, tension, datetime):
        alerts = []

        if temperature > 38.5:
            alerts.append(f"High temperature: {temperature}°C")
        elif temperature < 35.0:
            alerts.append(f"Low temperature: {temperature}°C")

        try:
            systolic, diastolic = map(int, tension.split("/"))
            if systolic > 140:
                alerts.append(f"High systolic pressure: {systolic}")
            elif systolic < 90:
                alerts.append(f"Low systolic pressure: {systolic}")
            if diastolic > 90:
                alerts.append(f"High diastolic pressure: {diastolic}")
            elif diastolic < 60:
                alerts.append(f"Low diastolic pressure: {diastolic}")
        except:
            alerts.append("⚠️ Invalid blood pressure format.")

        for msg in alerts:
            cur.execute("""
                INSERT INTO alerts (idpatient, message, datetime)
                VALUES (?, ?, ?)
            """, (idpatient, msg, datetime))



    def get_alerts_for_doctor(self, iddoctor):
        cursor = self.con.cursor()
        cursor.execute("""
            SELECT a.datetime, a.message, p.name, p.lastname
            FROM alerts a
            JOIN person p ON a.idpatient = p.idperson
            JOIN doctor_patient dp ON dp.idpatient = p.idperson
            WHERE dp.iddoctor = ?
            ORDER BY a.datetime DESC
        """, (iddoctor,))
        rows = cursor.fetchall()
        cursor.close()
        return rows

