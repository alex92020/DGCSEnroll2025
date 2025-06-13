import pandas as pd
import sqlite3

# Load Excel
df = pd.read_excel("DGCS Database 2025.xlsx")
df.columns = [col.strip() for col in df.columns]

# Combine full name
df['Full Name'] = df['Last Name'].str.strip() + ", " + df['First Name'].str.strip() + " " + df['Middle Name'].fillna('').str.strip()

# Connect to database
conn = sqlite3.connect("learners.db")
c = conn.cursor()

# Create table if it doesn't exist
c.execute('''
CREATE TABLE IF NOT EXISTS learners (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lrn TEXT UNIQUE,
    full_name TEXT,
    prev_grade TEXT,
    prev_section TEXT,
    sex TEXT,
    birth_date TEXT,
    age TEXT,
    religion TEXT,
    barangay TEXT,
    municipality TEXT,
    province TEXT,
    father_name TEXT,
    mother_name TEXT,
    guardian TEXT,
    cct_beneficiary TEXT,
    average_grade TEXT,
    action_taken TEXT,
    current_grade TEXT,
    current_section TEXT,
    status TEXT DEFAULT 'active',
    tag TEXT DEFAULT 'continuing',
    is_enrolled INTEGER DEFAULT 0,
    is_sped INTEGER DEFAULT 0,
    sped_type TEXT
)
''')

updated = 0
inserted = 0

for _, row in df.iterrows():
    lrn = str(row['LRN']).strip()
    full_name = row['Full Name']
    prev_grade = str(row['GRADE']).strip()
    prev_section = str(row['Section']).strip()
    sex = str(row['Sex']).strip()
    birth_date = str(row['Birth Date'])
    age = str(row['Age'])
    religion = str(row['Religion'])
    barangay = str(row['Barangay'])
    municipality = str(row['Municipality'])
    province = str(row['Province'])
    father_name = str(row["Father's Name"])
    mother_name = str(row["Mother's Name"])
    guardian = str(row["Guardian"]) if pd.notna(row["Guardian"]) else ""
    cct = str(row["CCT Beneficiary"])
    avg_grade = str(row["Average Grade"])
    action_taken = str(row["Action Taken"])

    # Check if LRN exists
    c.execute("SELECT id FROM learners WHERE lrn = ?", (lrn,))
    existing = c.fetchone()

    if existing:
        # Update
        c.execute('''
            UPDATE learners SET
                full_name=?, prev_grade=?, prev_section=?, sex=?, birth_date=?, age=?,
                religion=?, barangay=?, municipality=?, province=?, father_name=?,
                mother_name=?, guardian=?, cct_beneficiary=?, average_grade=?, action_taken=?
            WHERE lrn=?
        ''', (
            full_name, prev_grade, prev_section, sex, birth_date, age,
            religion, barangay, municipality, province, father_name,
            mother_name, guardian, cct, avg_grade, action_taken,
            lrn
        ))
        updated += 1
    else:
        # Insert
        c.execute('''
            INSERT INTO learners (
                lrn, full_name, prev_grade, prev_section,
                sex, birth_date, age, religion, barangay,
                municipality, province, father_name, mother_name,
                guardian, cct_beneficiary, average_grade, action_taken,
                current_grade, current_section, status, tag,
                is_enrolled, is_sped, sped_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            lrn, full_name, prev_grade, prev_section, sex, birth_date, age,
            religion, barangay, municipality, province, father_name, mother_name,
            guardian, cct, avg_grade, action_taken,
            "", "", "active", "continuing", 0, 0, ""
        ))
        inserted += 1

conn.commit()
conn.close()

print(f"✅ {updated} learners updated, {inserted} learners inserted.")
