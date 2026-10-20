import http.server
import socketserver
import sqlite3
import json
import os
import datetime
import webbrowser

PORT = 8000
DB_FILE = "cardioguard_v4.db"

# Initialize SQLite Database (Built-in to Python, zero pip install needed)
conn = sqlite3.connect(DB_FILE)
conn.execute("""
    CREATE TABLE IF NOT EXISTS telemetry_logs (
        id TEXT,
        timestamp TEXT,
        event_type TEXT,
        payload TEXT
    )
""")
conn.execute("""
    CREATE TABLE IF NOT EXISTS model_state (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        sqi_trees INTEGER,
        st_trees INTEGER,
        windows_trained INTEGER,
        base_ii REAL,
        base_v2 REAL,
        base_v5 REAL,
        updated_at TEXT
    )
""")
conn.commit()

class CardioGuardHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Allow CORS from any local file or browser tab
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        if self.path == "/api/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ONLINE", "db": DB_FILE}).encode("utf-8"))
            return
        return super().do_GET()

    def do_POST(self):
        if self.path == "/api/telemetry":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length).decode("utf-8")) if length > 0 else {}
            entry = body.get("entry", {})
            st = body.get("state", {})

            with sqlite3.connect(DB_FILE) as db:
                if entry:
                    db.execute(
                        "INSERT INTO telemetry_logs VALUES (?, ?, ?, ?)",
                        (entry.get("id", ""), datetime.datetime.utcnow().isoformat(), entry.get("type", ""), json.dumps(entry.get("payload", {})))
                    )
                if st:
                    db.execute("""
                        INSERT OR REPLACE INTO model_state (id, sqi_trees, st_trees, windows_trained, base_ii, base_v2, base_v5, updated_at)
                        VALUES (1, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        st.get("sqiTrees", 60), st.get("stTrees", 80), st.get("windowsTrained", 60000),
                        st.get("baseII", 0.0), st.get("baseV2", 0.0), st.get("baseV5", 0.0),
                        datetime.datetime.utcnow().isoformat()
                    ))
                db.commit()

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"saved": True}).encode("utf-8"))
            return

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)) or ".")
    print(f"CARDIO_GUARD v4.0 SQLite Backend running at http://127.0.0.1:{PORT}")
    webbrowser.open(f"http://127.0.0.1:{PORT}/index.html")
    with socketserver.TCPServer(("127.0.0.1", PORT), CardioGuardHandler) as httpd:
        httpd.serve_forever()
