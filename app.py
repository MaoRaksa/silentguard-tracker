from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB = "tracker.db"

def init_db():
    conn = sqlite3.connect(DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            task TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.close()

@app.route("/", methods=["GET"])
def home():
    conn = sqlite3.connect(DB)
    logs = conn.execute("SELECT id, name, task, timestamp FROM logs ORDER BY id DESC").fetchall()
    stats = conn.execute("SELECT name, COUNT(*) FROM logs GROUP BY name ORDER BY COUNT(*) DESC").fetchall()
    conn.close()
    return render_template("index.html", logs=logs, stats=stats)

@app.route("/add", methods=["POST"])
def add_log():
    name = request.form["name"]
    task = request.form["task"]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    conn = sqlite3.connect(DB)
    conn.execute("INSERT INTO logs (name, task, timestamp) VALUES (?, ?, ?)", (name, task, timestamp))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/delete/<int:log_id>")
def delete_log(log_id):
    conn = sqlite3.connect(DB)
    conn.execute("DELETE FROM logs WHERE id = ?", (log_id,))
    conn.commit()
    conn.close()
    return redirect("/")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)