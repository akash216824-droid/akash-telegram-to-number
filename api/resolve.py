from http.server import BaseHTTPRequestHandler
import urllib.parse
import urllib.request
import json
import re
import os

# ---------- CONFIGURATION ----------
REAL_API_URL = os.getenv("TG_API_URL", "https://dark-info.site/tg/api.php")
REAL_API_KEY = os.getenv("TG_API_KEY", "V8qL2mX7aP4zK9nR6tW3cJ1sH5")
DEVELOPER = "𐙚 𓆩𝘼𝙠𝙖𝙨𝗵 𝙊𝙨𝙞𝙣𝙩𓆪𓂃🧑💻🎀⃤"
API_KEY = "DEMO"


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        key = params.get("key", [None])[0]
        raw_num = params.get("query", [None])[0]

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        # ---------- Validate Path ----------
        if parsed.path != "/resolve":
            self.wfile.write(json.dumps({"error": "Invalid Key"}, indent=4).encode())
            return

        # ---------- Validate API Key ----------
        if key != API_KEY:
            self.wfile.write(json.dumps({"error": "Invalid Key"}, indent=4).encode())
            return

        # ---------- Validate Query ----------
        if not raw_num:
            self.wfile.write(json.dumps({"error": "Invalid Key"}, indent=4).encode())
            return

        # Clean – Telegram ID is numeric
        tg_id = re.sub(r"[^\d]", "", raw_num.strip())

        if not tg_id:
            self.wfile.write(json.dumps({"error": "No data found"}, indent=4).encode())
            return

        # ---------- Call Real API ----------
        try:
            real_url = f"{REAL_API_URL}?key={REAL_API_KEY}&num={tg_id}"
            req = urllib.request.Request(real_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                raw_text = resp.read().decode("utf-8", errors="ignore")
        except Exception as e:
            print("API error:", e)
            self.wfile.write(json.dumps({"error": "No data found"}, indent=4).encode())
            return

        # ---------- Parse Response ----------
        try:
            data = json.loads(raw_text)
        except json.JSONDecodeError:
            self.wfile.write(json.dumps({"error": "No data found"}, indent=4).encode())
            return

        result = self.parse_response(data, tg_id)
        self.wfile.write(json.dumps(result, indent=4, ensure_ascii=False).encode())

    # ---------- Parse Response ----------
    def parse_response(self, data, query):
        # Support multiple possible response structures
        if not isinstance(data, dict):
            return {"error": "No data found"}

        # Case 1: {"status": "success", "data": {...}}
        status = data.get("status", "error")
        inner = data.get("data", {})

        if status != "success" or not inner:
            # Case 2: flat response {"Telegram ID": ..., "Phone": ...}
            if "Phone" in data or "phone" in data:
                inner = data
                status = "success"
            else:
                return {"error": "No data found"}

        # Extract fields (multiple possible key names)
        phone = (
            inner.get("Owner≠Number")
            or inner.get("Owner\u2260Number")
            or inner.get("Phone")
            or inner.get("phone")
            or inner.get("number")
            or inner.get("Number")
        )

        tg_id = (
            inner.get("TG -ID")
            or inner.get("TG-ID")
            or inner.get("TG ID")
            or inner.get("Telegram ID")
            or inner.get("tg_id")
            or query
        )

        country_code = (
            inner.get("Country-Code")
            or inner.get("Country Code")
            or inner.get("country_code")
        )

        country = (
            inner.get("Country")
            or inner.get("country")
        )

        if not phone:
            return {"error": "No data found"}

        # ---------- Auto-detect Country from Country Code ----------
        country_map = {
            "+91": "India",
            "+880": "Bangladesh",
            "+92": "Pakistan",
            "+1": "United States",
            "+44": "United Kingdom",
            "+971": "United Arab Emirates",
            "+966": "Saudi Arabia",
            "+977": "Nepal",
            "+94": "Sri Lanka",
            "+60": "Malaysia",
        }

        if not country and country_code:
            cc_digits = re.sub(r"\D", "", country_code)
            for code, name in country_map.items():
                if cc_digits.startswith(re.sub(r"\D", "", code)):
                    country = name
                    break

        if not country:
            country = "Unknown"

        # ---------- Format Phone (WITHOUT + sign) ----------
        phone_str = re.sub(r"\D", "", str(phone).strip())

        # ---------- Response ----------
        return {
            "Telegram ID": str(tg_id),
            "Phone": phone_str,
            "Country": country,
            "Country Code": country_code or "N/A",
            "developer": DEVELOPER
        }

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
