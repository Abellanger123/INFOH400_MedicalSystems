import sqlite3

# Database Setup - Creating Tables
def create_tables():
    conn = sqlite3.connect('vital_signs_monitoring.db')
    cursor = conn.cursor()

    # Drop the existing Users table (if needed)
    cursor.execute('''DROP TABLE IF EXISTS Users''')
    cursor.execute('''DROP TABLE IF EXISTS VitalSigns''')
    cursor.execute('''DROP TABLE IF EXISTS DoctorPatientLink''')

    # Create Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        FirstName TEXT NOT NULL,
        LastName TEXT NOT NULL,
        Role TEXT NOT NULL CHECK (Role IN ('Patient', 'Doctor'))
    )
    ''')

    # Create VitalSigns table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS VitalSigns (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        PatientID INTEGER NOT NULL,
        Date TEXT NOT NULL,
        BloodPressure TEXT,
        Temperature REAL,
        HeartRate INTEGER,
        BloodGlucose REAL,
        FOREIGN KEY (PatientID) REFERENCES Users(ID)
    )
    ''')

    # Create DoctorPatientLink table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS DoctorPatientLink (
        DoctorID INTEGER NOT NULL,
        PatientID INTEGER NOT NULL,
        PRIMARY KEY (DoctorID, PatientID),
        FOREIGN KEY (DoctorID) REFERENCES Users(ID),
        FOREIGN KEY (PatientID) REFERENCES Users(ID)
    )
    ''')

    conn.commit()
    conn.close()
    print('Database and tables created successfully.')

if __name__ == "__main__":
    create_tables()
