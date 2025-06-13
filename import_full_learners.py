import pandas as pd
import sqlite3

# Load Excel
df = pd.read_excel("DGCS Database 2025.xlsx")
df.columns = [col.strip() for col in df.columns]

# Combine name fields
df['Full Name'] = df['Last Name'].str.strip() + ", " + df['First Name'].str.strip() + " " + df['Middle Name'].fillna('').str.strip()

# Prepare learner tuples
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
        str(row.get("Guardian", "")).strip(),
        str(row["CCT Beneficiary"]),
        str(row["Average Grade"]),
        str(row["Action Taken"]),
        "",  # current_grade
        "",  # current_section
        "active",
        "continuing",
        0,
        0,
        ""
    ))

# Connect to DB
conn = sqlite3.connect("learners.db")
c = conn.cursor()

# 1. Add UNIQUE index on lrn + prev_grade
c.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_lrn_prevgrade ON learners(lrn, prev_grade)")

# 2. Remove existing duplicates (keep first occurrence only)
c.execute('''
    DELETE FROM learners
    WHERE rowid NOT IN (
        SELECT MIN(rowid)
        FROM learners
        GROUP BY lrn, prev_grade
    )
''')

# 3. Re-populate using INSERT OR IGNORE to prevent new duplicates
for learner in learners:
    c.execute('''
        INSERT OR IGNORE INTO learners (
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

print(f"✅ Cleaned duplicates and imported {len(learners)} learners.")
