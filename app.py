from flask import Flask, render_template, request, jsonify, Response
import psycopg2
import os
import csv
import io
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            task TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/data")
def data():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, name, task, timestamp FROM logs ORDER BY id DESC")
    logs = cur.fetchall()
    cur.execute("SELECT name, COUNT(*) FROM logs GROUP BY name ORDER BY COUNT(*) DESC")
    stats = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify({
        "logs": [{"id": r[0], "name": r[1], "task": r[2], "timestamp": r[3]} for r in logs],
        "stats": [{"name": r[0], "count": r[1]} for r in stats]
    })

@app.route("/add", methods=["POST"])
def add_log():
    name = request.form["name"]
    task = request.form["task"]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO logs (name, task, timestamp) VALUES (%s, %s, %s)", (name, task, timestamp))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"status": "ok"})

@app.route("/delete/<int:log_id>", methods=["POST"])
def delete_log(log_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM logs WHERE id = %s", (log_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"status": "ok"})

@app.route("/export")
def export_csv():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT name, task, timestamp FROM logs ORDER BY id DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Name", "Task", "Time"])
    writer.writerows(rows)

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=silentguard_log.csv"}
    )

init_db()

if __name__ == "__main__":
    app.run(debug=True)