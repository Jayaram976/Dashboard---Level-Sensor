import socket
import requests

TCP_IP = "0.0.0.0"
TCP_PORT = 10560

DASHBOARD_URL = "https://dashboard-level-sensor.onrender.com/dingtek"

print("TCP Server started on port", TCP_PORT)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((TCP_IP, TCP_PORT))
sock.listen(1)

while True:
    conn, addr = sock.accept()
    print("Connected from", addr)

    data = conn.recv(4096)
    if not data:
        conn.close()
        continue

    hex_payload = data.hex()
    print("HEX:", hex_payload)

    # TEMPORARY (for proof only)
    payload = {
        "device_id": "BIN-001",
        "raw": hex_payload
    }

    try:
        r = requests.post(DASHBOARD_URL, json=payload, timeout=5)
        print("Dashboard Response:", r.status_code)
    except Exception as e:
        print("Dashboard Error:", e)

    conn.close()
