import sqlite3

conn = sqlite3.connect("learners.db")
c = conn.cursor()

# Delete existing table
c.execute("DROP TABLE IF EXISTS learners")

conn.commit()
conn.close()

print("✅ Old learners table dropped. You can now re-import with the full structure.")
