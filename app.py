from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__, static_folder="static", static_url_path="")

# In-memory storage
sensor_data = {}

@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.route("/dingtek", methods=["POST"])
def receive_dingtek():
    try:
        # 1️⃣ Try form data first (most Dingtek devices)
        if request.form:
            raw_dict = request.form.to_dict()
        else:
            raw_text = request.get_data(as_text=True).strip()
            raw_dict = {}

            if raw_text:
                parts = raw_text.replace("&", ",").split(",")
                for p in parts:
                    if "=" in p:
                        k, v = p.split("=", 1)  # SAFE split
                        raw_dict[k.strip()] = v.strip()

        if not raw_dict:
            return jsonify({"error": "No valid data received"}), 400

        device_id = request.args.get("id", "DINGTEK-001")

        sensor_data[device_id] = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "level": raw_dict.get("level", raw_dict.get("lvl", "-")),
            "temperature": raw_dict.get("temp", raw_dict.get("temperature", "-")),
            "angle": raw_dict.get("angle", "-"),
            "battery": raw_dict.get("bat", raw_dict.get("battery", "-")),
            "fire": 0,
            "fall": 0,
            "frame": 1
        }

        return jsonify({"status": "received"}), 200

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"error": "server error"}), 500


@app.route("/api/ips")
def get_ips():
    return jsonify(list(sensor_data.keys()))


@app.route("/api/data")
def get_data():
    ip = request.args.get("ip")
    if ip in sensor_data:
        return jsonify(sensor_data[ip])
    return jsonify({})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

