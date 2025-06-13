import sqlite3

DATABASE = "learners.db"

sample_learners = [
    ("100000000001", "ALONZO, MARIA LUNA", "Kinder", "KINDER-A", "", "", "active", "continuing", 0, 0, ""),
    ("100000000002", "RAMIREZ, JUAN MIGUEL", "Kinder", "KINDER-B", "", "", "active", "continuing", 0, 0, ""),
    ("100000000003", "TORRES, LARA MAE", "Kinder", "KINDER-A", "", "", "active", "continuing", 0, 0, ""),
]

conn = sqlite3.connect(DATABASE)
c = conn.cursor()

for learner in sample_learners:
    c.execute('''
        INSERT INTO learners (
            lrn, full_name, prev_grade, prev_section,
            current_grade, current_section, status, tag,
            is_enrolled, is_sped, sped_type
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', learner)

conn.commit()
conn.close()

print(f"✅ Inserted {len(sample_learners)} Kinder learners.")
