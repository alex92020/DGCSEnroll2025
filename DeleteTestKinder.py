import sqlite3

DATABASE = 'learners.db'
test_lrns = ["100000000001", "100000000002", "100000000003"]

with sqlite3.connect(DATABASE) as conn:
    c = conn.cursor()
    for lrn in test_lrns:
        c.execute("DELETE FROM learners WHERE lrn = ?", (lrn,))
    conn.commit()

print("✅ Test Kinder learners removed.")
