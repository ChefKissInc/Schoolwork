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
        cur.close()
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


@app.route("/python_upgrade_instructions")
def python_upgrade_instructions() -> str:
    return render_template("python_upgrade_instructions.html")


@app.route("/convert", methods=['GET', 'POST'])
def convert() -> str:
    result = ((float(request.form['fahrenheit']) - 32)
              * 5) / 9 if request.method == 'POST' else None
    return render_template("convert.html", result=result)


@app.route("/<int:wow>")
def hack_free_works(wow) -> str:
    return f"Hack NASA free works 2022: {wow + 5}"


@app.route("/studentManagement", methods=['GET', 'POST', 'PATCH', 'DELETE'])
def student_mgmt() -> str:
    cur = get_db().cursor()
    if request.method == 'POST':
        data = request.get_json()
        cur.execute("INSERT INTO students (first_name, last_name, class) VALUES (?, ?, ?)",
                    (data["first_name"], data["last_name"], data.get("class", None)))
    elif request.method == 'PATCH':
        data = request.get_json()
        cur.execute("UPDATE students SET first_name = ?, last_name = ?, class = ? WHERE id = ?",
                    (data["first_name"], data["last_name"], data.get("class", None), data["id"]))
    elif request.method == 'DELETE':
        data = request.get_json()
        cur.execute("DELETE FROM students WHERE id = ?", (data["id"],))
    else:
        students = cur.execute("SELECT * FROM students").fetchall()
        cur.close()
        return render_template("student_mgmt.html", students=students)
    cur.close()
    return ''
