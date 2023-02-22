from flask import Flask, render_template, request, g
import sqlite3

app = Flask(__name__)


def get_db() -> sqlite3.Connection:
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect("database.db")
        db.row_factory = sqlite3.Row
        cur = db.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS students(id INTEGER PRIMARY KEY AUTOINCREMENT, first_name NOT NULL, last_name NOT NULL, class STRING)")
        cur.execute("CREATE TABLE IF NOT EXISTS apousies(id INTEGER NOT NULL, hour INTEGER NOT NULL, day INTEGER NOT NULL, month INTEGER NOT NULL, year INTEGER NOT NULL)")
        cur.close()
        db.commit()
    return db


@app.teardown_appcontext
def close_connection(exception) -> None:
    db = getattr(g, '_database', None)
    if db is not None:
        db.commit()
        db.close()


@app.route("/")
def index() -> str:
    return render_template("index.html", x="potato")


@app.route("/convert", methods=['GET', 'POST'])
def convert() -> str:
    result = ((float(request.form['fahrenheit']) - 32)
              * 5) / 9 if request.method == 'POST' else None
    return render_template("convert.html", result=result)


@app.route("/students", methods=['GET', 'POST'])
@app.route("/students/<int:sid>", methods=['GET', 'POST', 'PATCH', 'DELETE'])
def students(sid: int = None) -> str:
    db = get_db()
    cur = db.cursor()
    if request.method == 'GET' and not sid:
        students = cur.execute("SELECT * FROM students").fetchall()

        def fixup(v):
            v["apousies"] = len(
                cur.execute("SELECT * FROM apousies WHERE id = ?", (v["id"],)).fetchall())
            return v
        students = [fixup(dict(v)) for v in students]
        cur.close()
        return render_template("students.html", students=students)
    elif request.method == 'GET':
        student = dict(cur.execute(
            "SELECT * FROM students WHERE id = ?", (sid,)).fetchone())
        apousies = cur.execute(
            "SELECT * FROM apousies WHERE id = ?", (sid,)).fetchall()
        student["apousies"] = apousies
        cur.close()
        return render_template("view_student.html", student=student)
    elif request.method == 'POST':
        data = request.get_json()
        apousia = data.get("apousia")
        if not apousia:
            cur.execute("INSERT INTO students (first_name, last_name, class) VALUES (?, ?, ?)",
                        (data["first_name"], data["last_name"], data.get("class", None)))
        else:
            cur.execute("INSERT INTO apousies (id, hour, day, month, year) VALUES (?, ?, ?, ?, ?)",
                        (sid, apousia["hour"], apousia["day"], apousia["month"], apousia["year"]))
    elif request.method == 'PATCH':
        data = request.get_json()
        apousia = data.get("apousia")
        if not apousia:
            cur.execute("UPDATE students SET first_name = ?, last_name = ?, class = ? WHERE id = ?",
                        (data["first_name"], data["last_name"], data.get("class", None), sid))
        else:
            cur.execute("UPDATE apousies SET hour = ?, day = ?, month = ?, year = ? WHERE id = ? AND hour = ? AND day = ? AND month = ? AND year = ?",
                        (data["hour"], data["day"], data["month"], data["year"], sid, apousia["hour"], apousia["day"], apousia["month"], apousia["year"]))
    elif request.method == 'DELETE':
        data = request.get_json(silent=True)
        if not data:
            cur.execute("DELETE FROM students WHERE id = ?", (sid,))
        else:
            cur.execute("DELETE FROM apousies WHERE id = ? AND hour = ? AND day = ? AND month = ? AND year = ?",
                        (sid, data["hour"], data["day"], data["month"], data["year"]))
    cur.close()
    db.commit()
    return ''
