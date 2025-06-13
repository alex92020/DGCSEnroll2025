# reset_init.py
import sqlite3
import os

DATABASE = 'learners.db'

def reset_and_reinitialize_db():
    if os.path.exists(DATABASE):
        os.remove(DATABASE)  # Delete existing database

    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()

        # Learners table
        c.execute('''
            CREATE TABLE learners (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lrn TEXT,
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

        # Learner history (for transfer_in and balik_aral)
        c.execute('''
            CREATE TABLE learner_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lrn TEXT,
                prev_school_id TEXT,
                prev_school_name TEXT,
                last_sy_attended TEXT
            )
        ''')

        # Sections table
        c.execute('''
            CREATE TABLE sections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                grade_level TEXT
            )
        ''')

        conn.commit()
        print("✅ learners.db wiped and reinitialized successfully.")

if __name__ == '__main__':
    reset_and_reinitialize_db()
