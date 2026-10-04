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

        status = data.get("status", "error")
        inner = data.get("data", {})

        if status != "success" or not inner:
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

        # ---------- Full Country Codes Map ----------
        country_map = {
            "+1": "United States/Canada",
            "+7": "Russia",
            "+20": "Egypt",
            "+27": "South Africa",
            "+30": "Greece",
            "+31": "Netherlands",
            "+32": "Belgium",
            "+33": "France",
            "+34": "Spain",
            "+36": "Hungary",
            "+39": "Italy",
            "+40": "Romania",
            "+41": "Switzerland",
            "+43": "Austria",
            "+44": "United Kingdom",
            "+45": "Denmark",
            "+46": "Sweden",
            "+47": "Norway",
            "+48": "Poland",
            "+49": "Germany",
            "+51": "Peru",
            "+52": "Mexico",
            "+53": "Cuba",
            "+54": "Argentina",
            "+55": "Brazil",
            "+56": "Chile",
            "+57": "Colombia",
            "+58": "Venezuela",
            "+60": "Malaysia",
            "+61": "Australia",
            "+62": "Indonesia",
            "+63": "Philippines",
            "+64": "New Zealand",
            "+65": "Singapore",
            "+66": "Thailand",
            "+81": "Japan",
            "+82": "South Korea",
            "+84": "Vietnam",
            "+86": "China",
            "+90": "Turkey",
            "+91": "India",
            "+92": "Pakistan",
            "+93": "Afghanistan",
            "+94": "Sri Lanka",
            "+95": "Myanmar",
            "+98": "Iran",
            "+212": "Morocco",
            "+213": "Algeria",
            "+216": "Tunisia",
            "+218": "Libya",
            "+220": "Gambia",
            "+221": "Senegal",
            "+222": "Mauritania",
            "+223": "Mali",
            "+224": "Guinea",
            "+225": "Ivory Coast",
            "+226": "Burkina Faso",
            "+227": "Niger",
            "+228": "Togo",
            "+229": "Benin",
            "+230": "Mauritius",
            "+231": "Liberia",
            "+232": "Sierra Leone",
            "+233": "Ghana",
            "+234": "Nigeria",
            "+235": "Chad",
            "+236": "Central African Republic",
            "+237": "Cameroon",
            "+238": "Cape Verde",
            "+239": "Sao Tome and Principe",
            "+240": "Equatorial Guinea",
            "+241": "Gabon",
            "+242": "Republic of the Congo",
            "+243": "DR Congo",
            "+244": "Angola",
            "+245": "Guinea-Bissau",
            "+246": "British Indian Ocean Territory",
            "+248": "Seychelles",
            "+249": "Sudan",
            "+250": "Rwanda",
            "+251": "Ethiopia",
            "+252": "Somalia",
            "+253": "Djibouti",
            "+254": "Kenya",
            "+255": "Tanzania",
            "+256": "Uganda",
            "+257": "Burundi",
            "+258": "Mozambique",
            "+260": "Zambia",
            "+261": "Madagascar",
            "+262": "Reunion",
            "+263": "Zimbabwe",
            "+264": "Namibia",
            "+265": "Malawi",
            "+266": "Lesotho",
            "+267": "Botswana",
            "+268": "Eswatini",
            "+269": "Comoros",
            "+290": "Saint Helena",
            "+291": "Eritrea",
            "+297": "Aruba",
            "+298": "Faroe Islands",
            "+299": "Greenland",
            "+350": "Gibraltar",
            "+351": "Portugal",
            "+352": "Luxembourg",
            "+353": "Ireland",
            "+354": "Iceland",
            "+355": "Albania",
            "+356": "Malta",
            "+357": "Cyprus",
            "+358": "Finland",
            "+359": "Bulgaria",
            "+370": "Lithuania",
            "+371": "Latvia",
            "+372": "Estonia",
            "+373": "Moldova",
            "+374": "Armenia",
            "+375": "Belarus",
            "+376": "Andorra",
            "+377": "Monaco",
            "+378": "San Marino",
            "+379": "Vatican City",
            "+380": "Ukraine",
            "+381": "Serbia",
            "+382": "Montenegro",
            "+383": "Kosovo",
            "+385": "Croatia",
            "+386": "Slovenia",
            "+387": "Bosnia and Herzegovina",
            "+389": "North Macedonia",
            "+420": "Czech Republic",
            "+421": "Slovakia",
            "+423": "Liechtenstein",
            "+500": "Falkland Islands",
            "+501": "Belize",
            "+502": "Guatemala",
            "+503": "El Salvador",
            "+504": "Honduras",
            "+505": "Nicaragua",
            "+506": "Costa Rica",
            "+507": "Panama",
            "+508": "Saint Pierre and Miquelon",
            "+509": "Haiti",
            "+590": "Guadeloupe",
            "+591": "Bolivia",
            "+592": "Guyana",
            "+593": "Ecuador",
            "+594": "French Guiana",
            "+595": "Paraguay",
            "+596": "Martinique",
            "+597": "Suriname",
            "+598": "Uruguay",
            "+599": "Netherlands Antilles",
            "+670": "East Timor",
            "+672": "Norfolk Island",
            "+673": "Brunei",
            "+674": "Nauru",
            "+675": "Papua New Guinea",
            "+676": "Tonga",
            "+677": "Solomon Islands",
            "+678": "Vanuatu",
            "+679": "Fiji",
            "+680": "Palau",
            "+681": "Wallis and Futuna",
            "+682": "Cook Islands",
            "+683": "Niue",
            "+685": "Samoa",
            "+686": "Kiribati",
            "+687": "New Caledonia",
            "+688": "Tuvalu",
            "+689": "French Polynesia",
            "+690": "Tokelau",
            "+691": "Micronesia",
            "+692": "Marshall Islands",
            "+850": "North Korea",
            "+852": "Hong Kong",
            "+853": "Macau",
            "+855": "Cambodia",
            "+856": "Laos",
            "+880": "Bangladesh",
            "+886": "Taiwan",
            "+960": "Maldives",
            "+961": "Lebanon",
            "+962": "Jordan",
            "+963": "Syria",
            "+964": "Iraq",
            "+965": "Kuwait",
            "+966": "Saudi Arabia",
            "+967": "Yemen",
            "+968": "Oman",
            "+970": "Palestine",
            "+971": "United Arab Emirates",
            "+972": "Israel",
            "+973": "Bahrain",
            "+974": "Qatar",
            "+975": "Bhutan",
            "+976": "Mongolia",
            "+977": "Nepal",
            "+992": "Tajikistan",
            "+993": "Turkmenistan",
            "+994": "Azerbaijan",
            "+995": "Georgia",
            "+996": "Kyrgyzstan",
            "+998": "Uzbekistan",
        }

        # ---------- Auto-detect Country from Country Code ----------
        if not country and country_code:
            cc_digits = re.sub(r"\D", "", country_code)
            # Sort by code length (longest first) to match correctly
            sorted_codes = sorted(
                country_map.items(),
                key=lambda x: -len(re.sub(r"\D", "", x[0]))
            )
            for code, name in sorted_codes:
                code_digits = re.sub(r"\D", "", code)
                if cc_digits.startswith(code_digits):
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
