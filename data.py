from dbgestion import DB



db = DB('projet.db')
# === Insérer les docteurs ===
id_doc1 = db.insert_person("Alice", "1980-01-01", "Smith", "alice@example.com", "docpass1", "doctor")
id_doc2 = db.insert_person("John", "1975-06-15", "Doe", "john@example.com", "docpass2", "doctor")

# === Insérer les patients ===
id_pat1 = db.insert_person("Emma", "2000-02-20", "Brown", "emma@example.com", "patpass1", "patient")
id_pat2 = db.insert_person("Liam", "1995-10-10", "White", "liam@example.com", "patpass2", "patient")
id_pat3 = db.insert_person("Olivia", "1998-05-05", "Green", "olivia@example.com", "patpass3", "patient")

# === Lier docteurs et patients ===
db.link_doctor_to_patient(id_doc1, id_pat1)
db.link_doctor_to_patient(id_doc1, id_pat2)
db.link_doctor_to_patient(id_doc2, id_pat3)
db.link_doctor_to_patient(id_doc2, id_pat1)  # Un patient peut avoir plusieurs médecins