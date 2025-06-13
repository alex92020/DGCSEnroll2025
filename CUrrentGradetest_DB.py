import sqlite3

conn = sqlite3.connect("learners.db")
c = conn.cursor()

# For testing: mark some Grade 1 to Grade 6 learners as enrolled
for i in range(1, 7):
    prev = "Kinder" if i == 1 else f"Grade {i - 1}"
    curr = f"Grade {i}"
    c.execute("""
        UPDATE learners
        SET is_enrolled = 1, current_grade = ?
        WHERE status = 'active' AND prev_grade = ?
    """, (curr, prev))

conn.commit()
conn.close()
print("✅ Some learners marked as enrolled for Grades 1-6.")
