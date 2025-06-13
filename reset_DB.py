import sqlite3

DATABASE = 'learners.db'

def reset_database():
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()

        # Optional: clear learners but keep table
        c.execute("DELETE FROM learners")

        # Optional: reset auto-increment ID (for neatness)
        c.execute("DELETE FROM sqlite_sequence WHERE name='learners'")

        # Optional: clear learner history if it exists
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='learner_history'")
        if c.fetchone():
            c.execute("DELETE FROM learner_history")
            c.execute("DELETE FROM sqlite_sequence WHERE name='learner_history'")

        # Optional: keep sections intact, or uncomment next lines to wipe:
        # c.execute("DELETE FROM sections")
        # c.execute("DELETE FROM sqlite_sequence WHERE name='sections'")

        conn.commit()

    print("✅ Database reset complete. All learner records cleared.")

if __name__ == '__main__':
    reset_database()
