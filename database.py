import sqlite3 as sql

#creating a connection to a database
con = sql.connect("projet.db")

#set a cursor for the database
cur = con.cursor()

#creating table in the database 
cur.execute("""
    CREATE TABLE person (
    idperson INTEGER PRIMARY KEY AUTOINCREMENT,
    iddoctor INTEGER,
    idpatient INTEGER,
    name TEXT NOT NULL,
    lastname TEXT NOT NULL,
    dateofbirth DATE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL, -- à chiffrer côté app !
    role TEXT CHECK(role IN ('patient', 'doctor')) NOT NULL
);""")


cur.execute("""
-- Creating the doctor table
CREATE TABLE doctor (
    iddoctor INTEGER PRIMARY KEY AUTOINCREMENT,
    idperson INTEGER NOT NULL,
    d_name TEXT NOT NULL,
    d_lastname TEXT NOT NULL,
    FOREIGN KEY (idperson) REFERENCES person(idperson)
);""")         

cur.execute("""
-- Creating the patient table
CREATE TABLE patient (
    idpatient INTEGER PRIMARY KEY AUTOINCREMENT,
    idperson INTEGER NOT NULL,
    phonenumber INTEGER NOT NULL,
    p_dateofbirth DATE NOT NULL,
    p_name TEXT NOT NULL,
    p_lastname TEXT NOT NULL,
    FOREIGN KEY (idperson) REFERENCES person(idperson)
);""")

cur.execute("""

CREATE TABLE patient_data (
    iddata INTEGER PRIMARY KEY AUTOINCREMENT,
    idpatient INTEGER NOT NULL,
    temperature REAL,
    tension TEXT, 
    datetime DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (idpatient) REFERENCES patient(idpatient)
            );""")


cur.execute("""

CREATE TABLE doctor_patient (
    iddoctor INTEGER NOT NULL,
    idpatient INTEGER NOT NULL,
    PRIMARY KEY (iddoctor, idpatient),
    FOREIGN KEY (iddoctor) REFERENCES doctor(iddoctor),
    FOREIGN KEY (idpatient) REFERENCES patient(idpatient)
);
""")

