import json
import math
from pathlib import Path
from http.server import BaseHTTPRequestHandler

DATA_PATH = Path(__file__).resolve().parent.parent / "telemetry.json"
with DATA_PATH.open("r", encoding="utf-8") as f:
    RECORDS = json.load(f)

def percentile95(values):
    # Linear interpolation (same convention as NumPy's default percentile).
    xs = sorted(values)
    if not xs:
        return None
    pos = (len(xs) - 1) * 0.95
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return float(xs[lo])
    return float(xs[lo] + (xs[hi] - xs[lo]) * (pos - lo))

class handler(BaseHTTPRequestHandler):
    def _send(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._send(204, {})

    def do_GET(self):
        self._send(405, {"error": "Use POST with JSON body."})

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(length).decode("utf-8"))
            regions = body.get("regions", [])
            threshold = float(body.get("threshold_ms", 180))
            if not isinstance(regions, list) or not all(isinstance(r, str) for r in regions):
                self._send(400, {"error": "'regions' must be a list of strings."})
                return

            result = {}
            for region in regions:
                rows = [x for x in RECORDS if x.get("region") == region]
                if not rows:
                    result[region] = {
                        "avg_latency": None,
                        "p95_latency": None,
                        "avg_uptime": None,
                        "breaches": 0
                    }
                    continue
                latencies = [float(x["latency_ms"]) for x in rows]
                uptimes = [float(x["uptime_pct"]) for x in rows]
                result[region] = {
                    "avg_latency": sum(latencies) / len(latencies),
                    "p95_latency": percentile95(latencies),
                    "avg_uptime": sum(uptimes) / len(uptimes),
                    "breaches": sum(1 for value in latencies if value > threshold)
                }
            self._send(200, result)
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            self._send(400, {"error": "Invalid JSON or request values.", "detail": str(exc)})

    def log_message(self, format, *args):
        pass
