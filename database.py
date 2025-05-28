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
    heartrate INTEGER,
    glucose REAL,
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
# Prescription générale
cur.execute("""
CREATE TABLE IF NOT EXISTS prescription (
    idprescription INTEGER PRIMARY KEY AUTOINCREMENT,
    idpatient INTEGER NOT NULL,
    medicament TEXT NOT NULL,
    start_date TEXT NOT NULL,  -- Format YYYY-MM-DD
    end_date TEXT NOT NULL,
    FOREIGN KEY(idpatient) REFERENCES person(idperson)
);
""")

# Chaque prise programmée
cur.execute("""
CREATE TABLE IF NOT EXISTS prescription_schedule (
    idschedule INTEGER PRIMARY KEY AUTOINCREMENT,
    idprescription INTEGER NOT NULL,
    date TEXT NOT NULL,       -- Date exacte : YYYY-MM-DD
    hour TEXT NOT NULL,       -- Heure prévue : HH:MM
    taken INTEGER DEFAULT 0,  -- 0 = pas encore pris, 1 = pris
    FOREIGN KEY(idprescription) REFERENCES prescription(idprescription)
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS alerts (
    idalert INTEGER PRIMARY KEY AUTOINCREMENT,
    idpatient INTEGER,
    message TEXT,
    datetime TEXT,
    FOREIGN KEY (idpatient) REFERENCES person(idperson)
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
