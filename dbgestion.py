import sqlite3 as sql

class DB:
    def __init__(self, dbfile):
        self.dbfile = dbfile      #self est ici pour référencer à l'objet lui-même ses attributs
        self.con = sql.connect(dbfile)

    def insert_person(self, Name, DateOfBirth, LastName, Email, Password, Role):
        #We create one cursor per action, this ensure that the fetch applied gives the result of the wanted action, not the latest
        cur = self.con.cursor() 
        #Add a new row to the person table                                                           
        cur.execute("""INSERT INTO person (name, lastname, dateofbirth, email, password, role)
                        VALUES (?,?,?,?,?,?) RETURNING idperson;""", (Name, LastName, DateOfBirth, Email,Password, Role))   #returning the Idperson because it is generated automatically
        #Retrieve the added person ID
        personid = cur.fetchone()[0]
        self.con.commit()
        cur.close()
        return personid
    
    def insert_doctor(self, Name, LastName, DateOfBirth, Email, Password, Role= 'doctor', idperson=None):
        cur = self.con.cursor() 
        #If the new doctor is not in our database, we first need to add him as a person
        if idperson == None:
            idperson = self.insert_person(Name,DateOfBirth,LastName, Email, Password, Role)    #crée le docteur dans la table personne 
        #We can then add the doctor and retrieve its ID
        cur.execute("""INSERT INTO doctor (idperson, d_name, d_lastname)
                    VALUES (?,?,?) RETURNING iddoctor;""", (idperson, Name, LastName))    #crée la personne dans la table docteur
        iddoctor = cur.fetchone()[0]
        #We update the person associated to the doctor in order to be able to find doctor from person
        cur.execute("""UPDATE person SET iddoctor = ? WHERE idperson = ?;""", (iddoctor, idperson))     #permet de relier ensemble les deux lignes et ainsi savoir que ce sont les mêmes
        self.con.commit()
        cur.close()
        return iddoctor
    
    def insert_patient(self, PhoneNumber, DateOfBirth, Name, LastName,Email, Password, Role='patient', idperson=None):
        cur = self.con.cursor() 
        #If the new patient is not in our database, we first need to add him as a person
        if idperson == None:
            idperson = self.insert_person(Name,DateOfBirth,LastName, Email, Password, Role)    #crée le patient dans la table personne 
        #We can then add the patient and retrieve its ID
        cur.execute("""INSERT INTO patient (idperson, phonenumber, p_dateofbirth, p_name, p_lastname)
                    VALUES (?,?,?,?,?) RETURNING idpatient;""", (idperson, PhoneNumber, DateOfBirth, Name, LastName))    #crée la personne dans la table patient
        idpatient = cur.fetchone()[0]
        #We update the person associated to the patient in order to be able to find patient from person
        cur.execute("""UPDATE person SET idpatient = ? WHERE idperson = ?;""", (idpatient, idperson))     #permet de relier ensemble les deux lignes et ainsi savoir que ce sont les mêmes
        cur.close()
        return idpatient
    
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
            SELECT p.idpatient, p.p_name, p.p_lastname
            FROM doctor_patient dp 
            JOIN patient p ON dp.idpatient = p.idpatient
            WHERE dp.iddoctor = ?
        """,(iddoctor,))
        rows = cur.fetchall()
        cur.close()
        return [dict(zip(['idpatient', 'name', 'lastname'], row)) for row in rows]
        
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
    
    def get_id_doctor(self, email):
        cur = self.con.cursor()
        cur.execute("""SELECT iddoctor FROM person WHERE email = ?;""", (email,))
        iddoctor = cur.fetchone()
        return iddoctor[0]   

    def get_id_patient(self, email):
        cur = self.con.cursor()
        cur.execute("""SELECT idpatient FROM person WHERE email = ?;""", (email,))
        idpatient = cur.fetchone()
        cur.close()
        return idpatient[0]
    
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


if __name__ == "__main__":
    # Création d'une instance de la base
    db = DB("projet.db")

    # 1. Ajouter un docteur
    iddoctor1 = db.insert_doctor(
        Name="John", LastName="Doe", DateOfBirth="1975-06-15",
        Email="j.doe@hospital.com", Password="secure123"
    )
    iddoctor2 = db.insert_doctor(
        Name='Louis',LastName= "Chirong", DateOfBirth="2013", 
        Email="Loulouchichi@hotmail.com", Password="loulouchichi"
    )

    # 2. Ajouter deux patients
    idpatient1 = db.insert_patient(
        PhoneNumber="0456112233", DateOfBirth="1990-01-01",
        Name="Alice", LastName="Durand", Email="alice@example.com",
        Password="alicepwd"
    )

    idpatient2 = db.insert_patient(
        PhoneNumber="0456445566", DateOfBirth="1988-04-21",
        Name="Bob", LastName="Martin", Email="bob@example.com",
        Password="bobpwd"
    )

    idpatient3 = db.insert_patient(PhoneNumber="0478521362", DateOfBirth="2001-04-07",
                                   Name='Juliette', LastName='Dedong', Email= "jdedong@gmail.com",
                                   Password="123456")
    
    idpatient4 = db.insert_patient(PhoneNumber="0478521362", DateOfBirth="2001-04-07",
                                   Name='Un', LastName='Deux', Email= "undeux@gmail.com",
                                   Password="123456")

    # 3. Lier le docteur aux deux patients
    db.link_doctor_to_patient(iddoctor1, idpatient1)
    db.link_doctor_to_patient(iddoctor1, idpatient2)
    db.link_doctor_to_patient(iddoctor2, idpatient3)
    db.link_doctor_to_patient(iddoctor2, idpatient4)

    # 4. Ajouter des données médicales pour un patient
    db.insert_patient_data(idpatient1, temperature=37.8, tension="125/85")
    db.insert_patient_data(idpatient1, temperature=38.2, tension="130/90")
    db.insert_patient_data(idpatient3, 37.8, '125/80')
    db.insert_patient_data(idpatient4, 37.5, '110/70')
    db.insert_patient_data(idpatient4, 37.5, '125/80')
    db.insert_patient_data(idpatient4, 40, '135/85')

    print("Docteur, patients et données ajoutés avec succès.")

    # 5. Print toutes les tables ainsi voir si ça fonctionne bien

    db.show_table('person')
    print('----------------------')
    db.show_table('patient')
    print('----------------------')
    db.show_table('doctor')
    print('----------------------')
    db.show_table('patient_data')
    print('----------------------')
    db.show_table('doctor_patient')

