# import_learners.py
import pandas as pd
import sqlite3

# Load Excel
df = pd.read_excel("DGCS Database 2025.xlsx")

# Clean column names
df.columns = [col.strip() for col in df.columns]

# Combine full name
df['Full Name'] = df['Last Name'].str.strip() + ", " + df['First Name'].str.strip() + " " + df['Middle Name'].fillna('').str.strip()

# Prepare learner data
learners = []
for _, row in df.iterrows():
    learners.append((
        str(row['LRN']).strip(),
        row['Full Name'],
        str(row['GRADE']).strip(),
        str(row['Section']).strip(),
        str(row['Sex']).strip(),
        str(row['Birth Date']),
        str(row['Age']),
        str(row['Religion']),
        str(row['Barangay']),
        str(row['Municipality']),
        str(row['Province']),
        str(row["Father's Name"]),
        str(row["Mother's Name"]),
        str(row.get("Guardian", "")),
        str(row["CCT Beneficiary"]),
        str(row.get("Average Grade", "")),
        str(row.get("Action Taken", "")),
        "",  # current_grade
        "",  # current_section
        "active",  # status
        "continuing",  # tag
        0,  # is_enrolled
        0,  # is_sped
        ""  # sped_type
    ))

# Insert into DB
conn = sqlite3.connect("learners.db")
c = conn.cursor()

for learner in learners:
    c.execute('''
        INSERT INTO learners (
            lrn, full_name, prev_grade, prev_section,
            sex, birth_date, age, religion, barangay,
            municipality, province, father_name, mother_name,
            guardian, cct_beneficiary, average_grade, action_taken,
            current_grade, current_section, status, tag,
            is_enrolled, is_sped, sped_type
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', learner)

conn.commit()
conn.close()

print(f"✅ Imported {len(learners)} learners.")
