import sqlite3

conn = sqlite3.connect("learners.db")
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS learner_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lrn TEXT,
    prev_school_id TEXT,
    prev_school_name TEXT,
    last_sy_attended TEXT
)
''')

conn.commit()
conn.close()
print("✅ learner_history table created.")
