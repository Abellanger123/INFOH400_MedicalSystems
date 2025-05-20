import sqlite3 as sql

#creating a connection to a database
con = sql.connect("projet.db")

#set a cursor for the database
cur = con.cursor()

#creating table in the database 
cur.execute("""
    CREATE TABLE IF NOT EXISTS person (
    idperson INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    lastname TEXT,
    dateofbirth TEXT,
    email TEXT UNIQUE,
    password TEXT,
    role TEXT CHECK(role IN ('doctor', 'patient'))

);""")


cur.execute("""

CREATE TABLE IF NOT EXISTS patient_data (
    iddata INTEGER PRIMARY KEY AUTOINCREMENT,
    idpatient INTEGER NOT NULL,
    temperature REAL,
    tension TEXT, 
    datetime DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (idpatient) REFERENCES patient(idpatient)
            );""")


cur.execute("""

CREATE TABLE IF NOT EXISTS doctor_patient (
    iddoctor INTEGER NOT NULL,
    idpatient INTEGER NOT NULL,
    PRIMARY KEY (iddoctor, idpatient),
    FOREIGN KEY (iddoctor) REFERENCES doctor(iddoctor),
    FOREIGN KEY (idpatient) REFERENCES patient(idpatient)
);
""")

cur.execute("""

CREATE TABLE IF NOT EXISTS prescription (
    idprescription INTEGER PRIMARY KEY AUTOINCREMENT,
    idpatient INTEGER,
    medicament TEXT,
    frequence TEXT,
    prise INTEGER DEFAULT 0, -- 0 = non pris, 1 = pris
    horodatage TEXT,
    FOREIGN KEY(idpatient) REFERENCES patient(idpatient)
);

""")

cur.execute("""


CREATE TABLE IF NOT EXISTS prescription_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prescription_id INTEGER,
    timestamp TEXT,
    FOREIGN KEY (prescription_id) REFERENCES prescriptions(id)
);


""")


con.commit()
cur.close()

cur2 = con.cursor()
cur2.execute("""
    UPDATE patient_data
    SET tension = ?
    WHERE iddata = ?;
""", ("120/67",4))
    
con.commit()
cur2.close()
