from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
import requests
import time

# Serve static files from ./static
app = Flask(__name__, static_folder="static", static_url_path="")

# -----------------------------
# Database connection
# -----------------------------
def db_connection():
    return sqlite3.connect("database.db")

# -----------------------------
# Create table (run once)
# -----------------------------
conn = db_connection()
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS sensor_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip TEXT,
    timestamp TEXT,
    level REAL,
    temperature REAL,
    angle REAL,
    alarmLevel INTEGER,
    alarmFire INTEGER,
    alarmFall INTEGER,
    alarmBattery INTEGER,
    frameCounter INTEGER
)
""")
conn.commit()
conn.close()

# -----------------------------
# RECEIVE DATA FROM DINGTEK / TCP SERVER
# -----------------------------
@app.route("/dingtek", methods=["POST"])
def receive_data():
    # Accept JSON or form-encoded payloads and be flexible with the IP key
    data = None
    try:
        data = request.get_json(silent=True)
    except Exception:
        data = None

    if not data or not isinstance(data, dict):
        if request.form:
            data = request.form.to_dict()
        else:
            raw = request.data.decode('utf-8', errors='ignore')
            if raw:
                try:
                    import json
                    data = json.loads(raw)
                except Exception:
                    data = {}
            else:
                data = {}

    if not data:
        return jsonify({"error": "No payload received"}), 400

    # Accept several possible keys for the device IP
    ip = data.get("device_ip") or data.get("ip") or data.get("IP") or data.get("deviceIp")

    if not ip:
        return jsonify({"error": "device_ip (or ip) missing"}), 400

    conn = db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO sensor_data
        (ip, timestamp, level, temperature, angle,
         alarmLevel, alarmFire, alarmFall, alarmBattery, frameCounter)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        ip,
        data.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        data.get("level"),
        data.get("temperature"),
        data.get("angle"),
        data.get("alarmLevel", 0),
        data.get("alarmFire", 0),
        data.get("alarmFall", 0),
        data.get("alarmBattery", 0),
        data.get("frameCounter", 0)
    ))

    conn.commit()
    conn.close()

    print(f"✅ Data received from {ip}")
    print("Payload:", data)

    return jsonify({"status": "received"})

# -----------------------------
# DASHBOARD API (READ DATA)
# -----------------------------
@app.route("/api/data")
def get_data():
    ip = request.args.get("ip")
    if not ip:
        return jsonify([])

    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT timestamp, level, temperature, angle,
               alarmLevel, alarmFire, alarmFall, alarmBattery, frameCounter
        FROM sensor_data
        WHERE ip=?
        ORDER BY id DESC
        LIMIT 50
    """, (ip,))
    rows = cursor.fetchall()
    conn.close()

    result = []
    for r in rows:
        result.append({
            "timestamp": r[0],
            "level": r[1],
            "temperature": r[2],
            "angle": r[3],
            "alarmLevel": r[4],
            "alarmFire": r[5],
            "alarmFall": r[6],
            "alarmBattery": r[7],
            "frameCounter": r[8]
        })

    return jsonify(result)


@app.route("/api/ips")
def get_ips():
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT ip FROM sensor_data WHERE ip IS NOT NULL AND ip != '' ORDER BY ip")
    rows = cursor.fetchall()
    conn.close()

    ips = [r[0] for r in rows]
    return jsonify(ips)

# -----------------------------
# SERVE DASHBOARD
# -----------------------------
@app.route("/")
def dashboard():
    return app.send_static_file("index.html")

@app.route("/favicon.ico")
def favicon():
    return "", 204

# -----------------------------
# CLOUD API INTEGRATION
# -----------------------------
CLOUD_API = "https://cloud.dingtek.com/api/devices/<device_id>/data"
HEADERS = {"Authorization":"Bearer YOUR_TOKEN"}

def fetch_and_store():
    r = requests.get(CLOUD_API, headers=HEADERS)
    data = r.json()
    # parse device payload and insert into database.db (same schema)

# -----------------------------
# START SERVER
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

{
  "device_ip": "199.36.158.10",
  "level": 1.23,
  "temperature": 25.0,
  "angle": 3.5,
  "alarmLevel": 0,
  "alarmFire": 0,
  "alarmFall": 0,
  "alarmBattery": 0,
  "frameCounter": 123
}
