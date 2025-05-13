import sqlite3

class DatabaseManager:
    def __init__(self, db_name='vital_signs_monitoring.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def add_user(self, first_name, last_name, role):
        try:
            self.cursor.execute("INSERT INTO Users (FirstName, LastName, Role) VALUES (?, ?, ?)", (first_name, last_name, role))
            self.conn.commit()
            print(f"User '{first_name} {last_name}' added successfully as a {role}.")
        except sqlite3.Error as e:
            print(f"Error adding user: {e}")

    def add_vital_signs(self, user_id, date, blood_pressure, temperature, heart_rate, blood_glucose):
        try:
            # Verify if the user is a Patient
            self.cursor.execute("SELECT Role FROM Users WHERE ID = ?", (user_id,))
            role = self.cursor.fetchone()

            if role and role[0] == "Patient":
                self.cursor.execute(
                    "INSERT INTO VitalSigns (PatientID, Date, BloodPressure, Temperature, HeartRate, BloodGlucose) VALUES (?, ?, ?, ?, ?, ?)",
                    (user_id, date, blood_pressure, temperature, heart_rate, blood_glucose)
                )
                self.conn.commit()
                print("Vital signs added successfully.")
            else:
                print("Only patients can add vital signs.")
        except sqlite3.Error as e:
            print(f"Error adding vital signs: {e}")

    def link_doctor_patient(self, doctor_id, patient_id):
        try:
            self.cursor.execute("INSERT INTO DoctorPatientLink (DoctorID, PatientID) VALUES (?, ?)", (doctor_id, patient_id))
            self.conn.commit()
            print("Doctor linked to patient successfully.")
        except sqlite3.Error as e:
            print(f"Error linking doctor to patient: {e}")

    def get_patients_of_doctor(self, doctor_id):
        try:
            self.cursor.execute(
                "SELECT Users.ID, Users.FirstName, Users.LastName FROM DoctorPatientLink "
                "INNER JOIN Users ON DoctorPatientLink.PatientID = Users.ID "
                "WHERE DoctorPatientLink.DoctorID = ?",
                (doctor_id,)
            )
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching patients: {e}")
            return []

    def get_vital_signs(self, patient_id):
        try:
            self.cursor.execute(
                "SELECT Date, BloodPressure, Temperature, HeartRate, BloodGlucose FROM VitalSigns WHERE PatientID = ?",
                (patient_id,)
            )
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching vital signs: {e}")
            return []

    def close(self):
        self.conn.close()

if __name__ == "__main__":
    db = DatabaseManager()
    db.add_user("Paul", "Young", "Patient")
    db.close()
