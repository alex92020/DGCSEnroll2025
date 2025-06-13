from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import os

app = Flask(__name__)
DATABASE = 'learners.db'


def init_db():
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS learners (
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
        c.execute('''
            CREATE TABLE IF NOT EXISTS learner_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lrn TEXT,
                prev_school_id TEXT,
                prev_school_name TEXT,
                last_sy_attended TEXT
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS sections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                grade_level TEXT
            )
        ''')
        conn.commit()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/grade/<grade>')
def grade_view(grade):
    sort_by = request.args.get('sort_by', 'full_name')
    filter_section = request.args.get('section', None)
    order_by = 'prev_section, full_name' if sort_by == 'prev_section' else 'full_name'

    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        # Query logic
        if grade == 'sped':
            query = "SELECT * FROM learners WHERE is_sped = 1"
        elif grade == 'kinder':
            query = "SELECT * FROM learners WHERE current_grade = 'Kinder'"
        else:
            prev_grade_text = "%Kinder%" if grade == "1" else f"%{int(grade) - 1}%"
            query = "SELECT * FROM learners WHERE prev_grade LIKE ? AND is_sped = 0"

        params = [prev_grade_text] if 'prev_grade_text' in locals() else []
        if filter_section:
            query += " AND prev_section = ?"
            params.append(filter_section)
        query += f" ORDER BY {order_by}"

        c.execute(query, tuple(params))
        learners = c.fetchall()

        # Section list
        section_query = {
            'sped': "SELECT DISTINCT prev_section FROM learners WHERE is_sped = 1 AND prev_section IS NOT NULL AND prev_section != '' ORDER BY prev_section",
            'kinder': "SELECT DISTINCT prev_section FROM learners WHERE current_grade = 'Kinder' AND prev_section IS NOT NULL AND prev_section != '' ORDER BY prev_section"
        }.get(grade,
              "SELECT DISTINCT prev_section FROM learners WHERE prev_grade LIKE ? AND is_sped = 0 AND prev_section IS NOT NULL AND prev_section != '' ORDER BY prev_section")

        c.execute(section_query, (prev_grade_text,) if grade not in ['sped', 'kinder'] else ())
        sections = [row[0] for row in c.fetchall()]

    return render_template('grade.html', learners=learners, grade=grade, sections=sections,
                           selected_section=filter_section, sort_by=sort_by)


@app.route('/toggle_status/<int:learner_id>/<grade>')
def toggle_status(learner_id, grade):
    sort_by = request.args.get('sort_by', 'full_name')
    section = request.args.get('section', '')

    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute("SELECT status FROM learners WHERE id = ?", (learner_id,))
        current_status = c.fetchone()[0]

        if current_status == 'active':
            # If deactivating: reset current grade and enrollment
            c.execute("""
                UPDATE learners
                SET status = 'inactive',
                    current_grade = '',
                    current_section = '',
                    is_enrolled = 0
                WHERE id = ?
            """, (learner_id,))
        else:
            # If reactivating: just change status to active
            c.execute("UPDATE learners SET status = 'active' WHERE id = ?", (learner_id,))

        conn.commit()

    return redirect(url_for('grade_view', grade=grade, sort_by=sort_by, section=section))


@app.route('/enroll_active/<grade>')
def enroll_active(grade):
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()

        if grade == 'sped':
            c.execute("""
                UPDATE learners
                SET is_enrolled = 1,
                    current_grade = 'Sped'
                WHERE status = 'active' AND is_sped = 1
            """)
        else:
            prev_grade_text = 'Kinder' if grade == '1' else f"Grade {int(grade) - 1}"
            current_grade_text = f"Grade {grade}"

            c.execute("""
                UPDATE learners
                SET is_enrolled = 1,
                    current_grade = ?
                WHERE status = 'active' AND prev_grade = ? AND is_sped = 0
            """, (current_grade_text, prev_grade_text))

        conn.commit()

    return redirect(url_for('grade_view', grade=grade))

@app.route('/add_learner', methods=['GET', 'POST'])
def add_learner():
    if request.method == 'POST':
        lrn = request.form['lrn']
        tag = request.form['tag']
        prev_grade = request.form['prev_grade']

        if tag in ['continuing', 'repeater']:
            with sqlite3.connect(DATABASE) as conn:
                c = conn.cursor()
                c.execute("SELECT * FROM learners WHERE lrn = ? AND prev_grade = ? AND status = 'active'",
                          (lrn, prev_grade))
                if c.fetchone():
                    return "❌ Learner already active on this grade. Wait for chairman to mark them inactive first."

        data = (
            lrn,
            request.form['full_name'],
            prev_grade,
            request.form['prev_section'],
            request.form.get('sex', ''),
            request.form.get('birth_date', ''),
            request.form.get('age', ''),
            request.form.get('religion', ''),
            request.form['barangay'],
            request.form['municipality'],
            request.form['province'],
            request.form['father_name'],
            request.form['mother_name'],
            request.form.get('guardian', ''),
            request.form['cct_beneficiary'],
            request.form['average_grade'],
            request.form.get('action_taken', ''),
            "", "",  # current_grade, current_section
            request.form['status'],
            tag,
            0,
            int(request.form.get('is_sped', 0)),
            request.form.get('sped_type', '')
        )

        with sqlite3.connect(DATABASE) as conn:
            c = conn.cursor()
            c.execute('''
                INSERT INTO learners (
                    lrn, full_name, prev_grade, prev_section, sex, birth_date, age, religion,
                    barangay, municipality, province, father_name, mother_name, guardian,
                    cct_beneficiary, average_grade, action_taken, current_grade, current_section,
                    status, tag, is_enrolled, is_sped, sped_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', data)

            if tag == 'transfer_in':
                c.execute('''
                    INSERT INTO learner_history (lrn, prev_school_id, prev_school_name)
                    VALUES (?, ?, ?)
                ''', (lrn, request.form.get('prev_school_id', ''), request.form.get('prev_school_name', '')))
            elif tag == 'balik_aral':
                c.execute('''
                    INSERT INTO learner_history (lrn, last_sy_attended)
                    VALUES (?, ?)
                ''', (lrn, request.form.get('last_sy', '')))
            conn.commit()

        return redirect(url_for('add_success', name=request.form['full_name']))
    return render_template('add_learner.html')


@app.route('/add_success')
def add_success():
    name = request.args.get('name', 'Learner')
    return f"✅ Successfully added {name}. <br><a href='/'>Back to dashboard</a>"


@app.route('/lookup_lrn')
def lookup_lrn():
    lrn = request.args.get('lrn')
    grade = request.args.get('grade')

    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM learners WHERE lrn = ? AND prev_grade = ? AND status = 'inactive'", (lrn, grade))
        learner = c.fetchone()
        if learner is None:
            return jsonify({'error': 'Learner not found or still marked active.'})
        return jsonify({key: learner[key] for key in learner.keys()})


@app.route('/monitor')
def monitor():
    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        def fetch_grouped_data(query):
            c.execute(query)
            return c.fetchall()

        # Breakdown by tag
        tag_totals = {row['tag']: row['total'] for row in fetch_grouped_data("""
            SELECT tag, COUNT(*) as total FROM learners WHERE is_enrolled = 1 GROUP BY tag
        """)}

        # Per section
        section_data = {}
        for row in fetch_grouped_data("""
            SELECT current_grade, current_section, sex, COUNT(*) as total
            FROM learners WHERE is_enrolled = 1 GROUP BY current_grade, current_section, sex
        """):
            key = f"{row['current_grade']} - {row['current_section']}"
            section_data.setdefault(key, {'M': 0, 'F': 0, 'Total': 0})
            section_data[key][row['sex']] += row['total']
            section_data[key]['Total'] += row['total']

        # Per grade
        grade_data = {}
        for row in fetch_grouped_data("""
            SELECT current_grade, sex, COUNT(*) as total
            FROM learners WHERE is_enrolled = 1 GROUP BY current_grade, sex
        """):
            g = row['current_grade']
            grade_data.setdefault(g, {'M': 0, 'F': 0, 'Total': 0})
            grade_data[g][row['sex']] += row['total']
            grade_data[g]['Total'] += row['total']

        # School-wide
        school_totals = {'M': 0, 'F': 0, 'Total': 0}
        for row in fetch_grouped_data("""
            SELECT sex, COUNT(*) as total FROM learners WHERE is_enrolled = 1 GROUP BY sex
        """):
            school_totals[row['sex']] = row['total']
            school_totals['Total'] += row['total']

        # Inactive by prev grade
        inactive_counts = {row['prev_grade']: row['total'] for row in fetch_grouped_data("""
            SELECT prev_grade, COUNT(*) as total FROM learners WHERE status = 'inactive' GROUP BY prev_grade
        """)}

    return render_template("monitor.html",
                           tag_totals=tag_totals,
                           section_data=section_data,
                           grade_data=grade_data,
                           school_totals=school_totals,
                           inactive_counts=inactive_counts
                           )


if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))

