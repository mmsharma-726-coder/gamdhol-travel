import collections
import collections.abc
if not hasattr(collections, 'abc'):
    collections.abc = collections.abc

import datetime
import os
import sqlite3
import razorpay
import requests
import streamlit as st
import swisseph as swe
from fpdf import FPDF
from geopy.geocoders import Nominatim

# 1. Page Configuration
st.set_page_config(
    page_title="Lal Kitab Kundli Grah Upay and Couple Milan",
    page_icon="🔮",
    layout="wide",
)

# Custom Styling
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Poppins', sans-serif;
        }

        .stButton>button { 
            width: 100%; 
            border-radius: 8px; 
            font-weight: 600; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            transition: all 0.3s ease;
        }
        
        .stButton>button:hover {
            opacity: 0.9;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(118, 75, 162, 0.3);
        }

        .block-container { 
            padding-top: 1.5rem; 
        }

        .title-red { color: #d32f2f; font-weight: 700; }
        .title-purple { color: #7b1fa2; font-weight: 700; }
        .title-orange { color: #e65100; font-weight: 700; }
        .title-green { color: #2e7d32; font-weight: 700; }
        .title-pink { color: #ec407a; font-weight: 700; }

        .pos-heading {
            color: #2e7d32;
            font-weight: 700;
            border-left: 4px solid #2e7d32;
            padding-left: 8px;
            margin-top: 10px;
        }

        .neg-heading {
            color: #c62828;
            font-weight: 700;
            border-left: 4px solid #c62828;
            padding-left: 8px;
            margin-top: 10px;
        }

        .upay-heading {
            color: #ef6c00;
            font-weight: 700;
            border-left: 4px solid #ef6c00;
            padding-left: 8px;
            margin-top: 10px;
        }
    </style>
""",
    unsafe_allow_html=True,
)

# App Title Function for styled text
def render_app_title():
    st.markdown(
        """
        <h1 style='text-align: left; font-size: 2.2rem;'>
            🔮 <span class='title-red'>Lal Kitab</span> 
            <span class='title-purple'>Kundli</span> 
            <span class='title-orange'>Grah</span> 
            <span class='title-green'>Upay</span> and 
            <span class='title-pink'>💖 Couple Milan</span>
        </h1>
        """,
        unsafe_allow_html=True
    )

# 2. Database Setup & Migration
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            phone TEXT PRIMARY KEY,
            has_paid_report INTEGER DEFAULT 0,
            questions_left INTEGER DEFAULT 0,
            free_report_token INTEGER DEFAULT 0,
            report_link_id TEXT,
            chat_link_id TEXT,
            gender TEXT,
            dob TEXT,
            tob TEXT,
            city TEXT,
            state TEXT,
            country TEXT
        )
    ''')
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if "has_paid_report" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN has_paid_report INTEGER DEFAULT 0")
    if "questions_left" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN questions_left INTEGER DEFAULT 0")
    if "free_report_token" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN free_report_token INTEGER DEFAULT 0")
    if "report_link_id" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN report_link_id TEXT")
    if "chat_link_id" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN chat_link_id TEXT")
    if "gender" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN gender TEXT")
    if "dob" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN dob TEXT")
    if "tob" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN tob TEXT")
    if "city" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN city TEXT")
    if "state" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN state TEXT")
    if "country" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN country TEXT")
    
    conn.commit()
    conn.close()

init_db()

# 3. Session State Initialization
if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False
if "active_user_phone" not in st.session_state:
    st.session_state.active_user_phone = ""
if "match_generated" not in st.session_state:
    st.session_state.match_generated = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "master_report" not in st.session_state:
    st.session_state.master_report = ""
if "planet_details" not in st.session_state:
    st.session_state.planet_details = None
if "questions_left" not in st.session_state:
    st.session_state.questions_left = 0
if "match_report" not in st.session_state:
    st.session_state.match_report = ""


# ==========================================
# 4. REAL APPLICATION LOGIN SCREEN (TOP LEVEL)
# ==========================================
if not st.session_state.is_logged_in:
    render_app_title()
    st.markdown("### 🔐 Secure User Login / Account Verification")
    st.info("Kripya app ko access karne ke liye apna mobile number darj karein.")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            entered_phone = st.text_input("Mobile Number (10 Digits):", placeholder="e.g. 9876543210")
            submit_login = st.form_submit_button("🚀 Login / Continue to App", type="primary")
            
            if submit_login:
                clean_phone = entered_phone.strip()
                if len(clean_phone) >= 10:
                    st.session_state.active_user_phone = clean_phone
                    
                    conn = sqlite3.connect('users.db')
                    cursor = conn.cursor()
                    cursor.execute('''
                        SELECT has_paid_report, questions_left, free_report_token, report_link_id, chat_link_id, gender, dob, tob, city, state, country 
                        FROM users WHERE phone = ?
                    ''', (clean_phone,))
                    record = cursor.fetchone()
                    
                    if record:
                        st.session_state.questions_left = record[1] or 0
                        if record[6] and record[7] and record[8]:
                            st.session_state.saved_gender = record[5]
                            st.session_state.saved_dob = datetime.datetime.strptime(record[6], "%Y-%m-%d").date()
                            st.session_state.saved_tob = datetime.datetime.strptime(record[7], "%H:%M:%S").time()
                            st.session_state.saved_city = record[8]
                            st.session_state.saved_state = record[9] or ""
                            st.session_state.saved_country = record[10] or "India"
                            
                            from contextlib import suppress
                            with suppress(Exception):
                                lagna, d1, d9, d10, details, moon_nak, dasha, transit, err = calculate_advanced_kundli(
                                    st.session_state.saved_dob, st.session_state.saved_tob, 
                                    st.session_state.saved_city, st.session_state.saved_state, st.session_state.saved_country
                                )
                                if not err:
                                    st.session_state.lagna = lagna
                                    st.session_state.planet_details = details
                                    st.session_state.dasha = dasha
                                    st.session_state.transit = transit
                    else:
                        cursor.execute('INSERT OR IGNORE INTO users (phone, has_paid_report, questions_left, free_report_token) VALUES (?, 0, 0, 0)', (clean_phone,))
                        conn.commit()
                        st.session_state.questions_left = 0
                    conn.close()
                    
                    st.session_state.is_logged_in = True
                    st.success("✅ Login Successful! App load ho raha hai...")
                    st.rerun()
                else:
                    st.error("Kripya ek valid mobile number darj karein.")
    
    st.stop()


# ==========================================
# 5. MAIN APP (AFTER SUCCESSFUL LOGIN)
# ==========================================

active_phone = st.session_state.active_user_phone

if active_phone:
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT has_paid_report, free_report_token, report_link_id, chat_link_id, questions_left, gender, dob, tob, city, state, country FROM users WHERE phone = ?', (active_phone,))
    db_row = cursor.fetchone()
    conn.close()
    
    if db_row:
        st.session_state.has_paid_report = bool(db_row[0])
        current_free_token = db_row[1]
        st.session_state.report_link_id = db_row[2] or ""
        current_chat_link = db_row[3] or ""
        
        if "questions_left" not in st.session_state or st.session_state.questions_left == 0:
            st.session_state.questions_left = db_row[4]

        if db_row[6] and db_row[7] and db_row[8]:
            st.session_state.saved_gender = db_row[5]
            st.session_state.saved_dob = datetime.datetime.strptime(db_row[6], "%Y-%m-%d").date()
            st.session_state.saved_tob = datetime.datetime.strptime(db_row[7], "%H:%M:%S").time()
            st.session_state.saved_city = db_row[8]
            st.session_state.saved_state = db_row[9] or ""
            st.session_state.saved_country = db_row[10] or "India"

            if "planet_details" not in st.session_state or st.session_state.planet_details is None:
                from contextlib import suppress
                with suppress(Exception):
                    lagna, d1, d9, d10, details, moon_nak, dasha, transit, err = calculate_advanced_kundli(
                        st.session_state.saved_dob, st.session_state.saved_tob, 
                        st.session_state.saved_city, st.session_state.saved_state, st.session_state.saved_country
                    )
                    if not err:
                        st.session_state.lagna = lagna
                        st.session_state.planet_details = details
                        st.session_state.dasha = dasha
                        st.session_state.transit = transit

        # Auto-verify payment link if active
        if current_chat_link:
            try:
                rzp_key_id = st.secrets["razorpay"]["key_id"]
                rzp_key_secret = st.secrets["razorpay"]["key_secret"]
                client = razorpay.Client(auth=(rzp_key_id, rzp_key_secret))
                link_info = client.payment_link.fetch(current_chat_link)
                
                if link_info.get("status") == "paid":
                    amt = link_info.get("amount", 0)
                    exact_q = 0
                    if amt == 500:  # ₹5 for 1 question
                        exact_q = 1
                    elif amt == 2100: # ₹21 for 6 questions
                        exact_q = 6
                    elif amt == 4100: # ₹41 for 12 questions
                        exact_q = 12
                        current_free_token = 1

                    if exact_q > 0:
                        new_total_questions = st.session_state.questions_left + exact_q
                        st.session_state.questions_left = new_total_questions
                        
                        conn = sqlite3.connect('users.db')
                        cursor = conn.cursor()
                        cursor.execute('''
                            UPDATE users 
                            SET questions_left = ?, free_report_token = ?, chat_link_id = NULL 
                            WHERE phone = ?
                        ''', (new_total_questions, current_free_token, active_phone))
                        conn.commit()
                        conn.close()
                        
                        st.success(f"🎉 Payment Successful! Aapke account mein {exact_q} sawal jod diye gaye hain.")
                        st.rerun()
            except Exception as e:
                pass

st.sidebar.subheader("📱 Account Profile")
st.sidebar.markdown(f"**Phone:** `{active_phone}`")
st.sidebar.markdown(f"**Questions Left:** `{st.session_state.questions_left}`")

if hasattr(st.session_state, 'saved_dob') and st.session_state.saved_dob:
    st.sidebar.markdown("---")
    st.sidebar.subheader("📜 Active Kundli Details")
    st.sidebar.info(
        f"**DOB:** {st.session_state.saved_dob}\n\n"
        f"**Time:** {getattr(st.session_state, 'saved_tob', 'N/A')}\n\n"
        f"**Place:** {getattr(st.session_state, 'saved_city', 'N/A')}"
    )

if st.sidebar.button("🚪 Logout / Switch Account"):
    st.session_state.is_logged_in = False
    st.session_state.active_user_phone = ""
    st.session_state.match_generated = False
    st.session_state.chat_history = []
    st.session_state.master_report = ""
    st.session_state.planet_details = None
    st.session_state.questions_left = 0
    st.session_state.match_report = ""
    
    for key in ['saved_gender', 'saved_dob', 'saved_tob', 'saved_city', 'saved_state', 'saved_country', 'lagna', 'dasha', 'transit']:
        if key in st.session_state:
            del st.session_state[key]
            
    st.rerun()

st.sidebar.markdown("---")
app_mode = st.sidebar.radio(
    "Mode Chunein:",
    ["👤 Individual Kundli (Single)", "💖 Couple Milan"],
)

render_app_title()


def get_coordinates(city_name, state_name="", country_name="India"):
    try:
        clean_city = " ".join(city_name.split()).strip()
        clean_state = " ".join(state_name.split()).strip()
        clean_country = " ".join(country_name.split()).strip()
        parts = [clean_city]
        if clean_state and clean_state.lower() != clean_city.lower() and clean_state.lower() != "delhi":
            parts.append(clean_state)
        if clean_country:
            parts.append(clean_country)
        full_location = ", ".join(parts)
        geolocator = Nominatim(user_agent="lal_kitab_ai_app_support@gmail.com")
        location = geolocator.geocode(full_location, timeout=10)
        if location:
            return location.latitude, location.longitude
        if clean_city.lower() in ["delhi", "new delhi"]:
            return 28.6139, 77.2090
    except Exception:
        pass
    return 28.6139, 77.2090


def dec_to_dms(deg_val):
    d = int(deg_val)
    m_float = (deg_val - d) * 60
    m = int(m_float)
    s = int((m_float - m) * 60)
    return f"{d}° {m}' {s}\""


DASHA_LORDS = [
    ("Ketu", 7), ("Venus", 20), ("Sun", 6), ("Moon", 10),
    ("Mars", 7), ("Rahu", 18), ("Jupiter", 16), ("Saturn", 19), ("Mercury", 17)
]
NAKSHATRA_SPAN = 13 + (20 / 60)


def calculate_vimshottari_dasha(moon_deg):
    nakshatra_index = int(moon_deg / NAKSHATRA_SPAN)
    degrees_into_nakshatra = moon_deg % NAKSHATRA_SPAN
    lord_index = nakshatra_index % 9
    starting_lord, total_years = DASHA_LORDS[lord_index]
    fraction_elapsed = degrees_into_nakshatra / NAKSHATRA_SPAN
    balance_years = total_years * (1 - fraction_elapsed)
    return {
        "nakshatra_number": nakshatra_index + 1,
        "starting_lord": starting_lord,
        "balance_years_at_birth": round(balance_years, 2),
    }


def get_current_planetary_transits():
    today = datetime.date.today()
    jd = swe.julday(today.year, today.month, today.day, 12.0)
    planets = {"Jupiter": swe.JUPITER, "Saturn": swe.SATURN, "Rahu": swe.MEAN_NODE}
    zodiac_signs = [
        "Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
        "Tula", "Vrishchika", "Dhanu", "Makara", "Kumbha", "Meena"
    ]
    transits = {}
    for name, p_id in planets.items():
        res, flag = swe.calc_ut(jd, p_id)
        longitude = res[0]
        sign_index = int(longitude / 30)
        transits[name] = {"sign": zodiac_signs[sign_index], "degree": round(longitude % 30, 2)}
    return transits


def create_pdf_report(report_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, txt="Lal Kitab Advanced AI Kundli Report", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", size=11)
    for line in report_text.split("\n"):
        clean_line = line.encode("latin-1", "ignore").decode("latin-1") if line else ""
        pdf.multi_cell(0, 8, txt=clean_line)
    return pdf.output(dest="S").encode("latin-1")


def calculate_advanced_kundli(dob, tob_time, city_name, state_name, country_name):
    lat, lon = get_coordinates(city_name, state_name, country_name)
    dt = datetime.datetime(dob.year, dob.month, dob.day, tob_time.hour, tob_time.minute)
    dt_utc = dt - datetime.timedelta(hours=5, minutes=30)
    julian_day = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute / 60.0)
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)

    try:
        cusps, ascmc = swe.houses(julian_day, lat, lon, b"P")
        ayanamsa = swe.get_ayanamsa_ut(julian_day)
    except Exception as e:
        return None, None, None, None, None, None, None, None, f"Ephemeris Error: {str(e)}"

    tropical_asc = ascmc[0]
    sidereal_asc = (tropical_asc - ayanamsa) % 360
    lagna_rashi = int(sidereal_asc / 30) + 1

    rashi_names = [
        "Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
        "Tula", "Vrishchika", "Dhanu", "Makara", "Kumbha", "Meena"
    ]
    lagna_rashi_name = rashi_names[lagna_rashi - 1]

    planets = {
        "Surya": swe.SUN, "Chandra": swe.MOON, "Mangal": swe.MARS,
        "Budh": swe.MERCURY, "Guru": swe.JUPITER, "Shukra": swe.VENUS,
        "Shani": swe.SATURN, "Rahu": swe.MEAN_NODE
    }

    d1_results, d9_results, d10_results, planet_details = {}, {}, {}, {}
    moon_nakshatra, moon_deg_val = "", 0.0

    for p_name, p_code in planets.items():
        calc_res = swe.calc_ut(julian_day, p_code, swe.FLG_SIDEREAL)
        p_degree = calc_res[0][0]
        sign_deg = p_degree % 30
        exact_deg_str = dec_to_dms(sign_deg)
        p_rashi_idx = int(p_degree / 30)
        p_rashi_name = rashi_names[p_rashi_idx]
        planet_rashi = p_rashi_idx + 1

        house_num = ((planet_rashi - lagna_rashi) % 12) + 1
        d1_results[p_name] = house_num
        d9_results[p_name] = int((p_degree * 9) % 360 / 30) + 1
        d10_results[p_name] = int((p_degree * 10) % 360 / 30) + 1

        nak_index = int(p_degree / (13 + 20 / 60)) % 27
        nak_names = [
            "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Ashlesha",
            "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
            "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
        ]
        nak_name = nak_names[nak_index]

        if p_name == "Chandra":
            moon_nakshatra = nak_name
            moon_deg_val = p_degree

        planet_details[p_name] = {
            "house": house_num, "rashi": p_rashi_name, "degree": exact_deg_str,
            "d9": rashi_names[d9_results[p_name] - 1], "d10": rashi_names[d10_results[p_name] - 1], "nakshatra": nak_name
        }

    rahu_h = d1_results["Rahu"]
    ketu_h = ((rahu_h + 6 - 1) % 12) + 1
    d1_results["Ketu"] = ketu_h
    planet_details["Ketu"] = {
        "house": ketu_h, "rashi": rashi_names[(rashi_names.index(planet_details["Rahu"]["rashi"]) + 6) % 12],
        "degree": planet_details["Rahu"]["degree"], "d9": "", "d10": "", "nakshatra": "Opposite Rahu"
    }

    return lagna_rashi_name, d1_results, d9_results, d10_results, planet_details, moon_nakshatra, calculate_vimshottari_dasha(moon_deg_val), get_current_planetary_transits(), None


def get_clean_response(user_query, history_context="", dasha=None, transit=None, planet_details=None):
    try:
        clean_key = st.secrets["gemini"]["api_key"].strip()
    except Exception:
        return None, "Gemini API key missing in Streamlit secrets!"

    current_date_str = datetime.date.today().strftime("%d %B %Y")
    current_year = datetime.date.today().year

    saved_birth_str = ""
    if hasattr(st.session_state, 'saved_dob') and st.session_state.saved_dob:
        saved_birth_str = (
            f"CURRENT ACTIVE KUNDLI DETAILS (Isi ke anusaar accurate jawab dein):\n"
            f"- Gender: {getattr(st.session_state, 'saved_gender', 'N/A')}\n"
            f"- Date of Birth: {st.session_state.saved_dob}\n"
            f"- Time of Birth: {getattr(st.session_state, 'saved_tob', 'N/A')}\n"
            f"- Birth Place: {getattr(st.session_state, 'saved_city', 'N/A')}, {getattr(st.session_state, 'saved_state', 'N/A')}, {getattr(st.session_state, 'saved_country', 'N/A')}\n\n"
        )

    pl_context_str = ""
    if planet_details:
        pl_context_str = "EXACT PLANETARY PLACEMENTS IN CURRENT KUNDLI:\n"
        for p_name, p_info in planet_details.items():
            pl_context_str += f"- {p_name}: House {p_info['house']} (Rashi: {p_info['rashi']}, Degree: {p_info['degree']})\n"

    full_prompt = (
        "System: Aap ek expert Lal Kitab aur Vedic Astrologer AI Assistant hain.\n"
        f"CRITICAL DATE INSTRUCTION: Aaj ki vartaman date **{current_date_str}** (Year: **{current_year}**) hai. Sabhi bhavishyavaniyan ishi year ke anusaar karein.\n\n"
        "ADVANCED TIMING & FUTURE PREDICTION REQUIREMENT:\n"
        "Jab bhi user future event (jaise videsh yatra, naukri badalna, vivah, dhan labh, aadi) ke baare mein puche, toh:\n"
        "1. Pehle kundli ki grah sthiti (Planetary placements) aur Dasha data analyze karein ki kya grah uss event ko support karte hain ya nahi.\n"
        "2. Agar support karte hain, toh Vimshottari Dasha aur Vartaman Gochar (Transits) ko calculate karke exact time, mahina ya saal batayein jab wo grah active honge aur uss event ke hone ke sabse zyada chances banenge.\n"
        "3. Agar grah support nahi karte, toh spasht roop se batayein ki kyon sambhavna kam hai aur uske kya Lal Kitab upay hain.\n\n"
        "FORMATTING & HEADING COLOR REQUIREMENT:\n"
        "- Positive points ke liye heading ko HTML `<div class='pos-heading'>...</div>` ke andar rakhein.\n"
        "- Negative points/dosha ke liye heading ko HTML `<div class='neg-heading'>...</div>` ke andar rakhein.\n"
        "- Upay/Remedies ke liye heading ko HTML `<div class='upay-heading'>...</div>` ke andar rakhein.\n\n"
        "Kripya poora jawab shuddh aur saral **Hindi (Devanagari lipi)** mein dein.\n"
        f"{saved_birth_str}"
        f"{pl_context_str}\n"
        f"VIMSHOTTARI DASHA DATA: {dasha}\n"
        f"CURRENT PLANETARY TRANSITS: {transit}\n\n"
        f"RECENT CONVERSATION HISTORY:\n{history_context}\n\n"
        f"USER QUERY: {user_query}"
    )

    payload = {
        "contents": [{"parts": [{"text": full_prompt}]}],
        "generationConfig": {"maxOutputTokens": 4000, "temperature": 0.4},
    }
    headers = {"Content-Type": "application/json"}
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={clean_key}"

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        res_data = response.json()
        if response.status_code == 200:
            if "candidates" in res_data and res_data["candidates"]:
                content = res_data["candidates"][0].get("content", {})
                parts = content.get("parts", [])
                if parts:
                    return "".join([p.get("text", "") for p in parts]).strip(), None
        return None, f"API Error: {res_data}"
    except Exception as e:
        return None, str(e)


# ==========================================
# INPUT FORM & REPORT GENERATION
# ==========================================
if app_mode == "👤 Individual Kundli (Single)":
    st.subheader("📝 Individual Janam Details Darj Karein")
    
    default_dob = getattr(st.session_state, 'saved_dob', datetime.date(1992, 4, 24))
    default_city = getattr(st.session_state, 'saved_city', 'Delhi')
    default_state = getattr(st.session_state, 'saved_state', 'Delhi')
    default_country = getattr(st.session_state, 'saved_country', 'India')
    default_gender = getattr(st.session_state, 'saved_gender', 'Male (Purush)')
    
    gender_idx = 0 if "Male" in default_gender else 1
    gender_option = st.radio("Jatak ka Gender chunein:", ["Male (Purush)", "Female (Stree)"], index=gender_idx, horizontal=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        ind_dob = st.date_input("Date of Birth", value=default_dob, key="ind_dob")
    with col2:
        st.markdown("**Time of Birth (12-Hour Style)**")
        
        default_tob = getattr(st.session_state, 'saved_tob', datetime.time(9, 30))
        h_24 = default_tob.hour
        ampm_val = "PM" if h_24 >= 12 else "AM"
        h_12 = h_24 % 12
        if h_12 == 0: 
            h_12 = 12
        
        hour_list = list(range(1, 13))
        h_index = hour_list.index(h_12) if h_12 in hour_list else 8
        ampm_index = 0 if ampm_val == "AM" else 1

        t_col1, t_col2, t_col3 = st.columns(3)
        with t_col1:
            sel_hour = st.selectbox("Hour", hour_list, index=h_index, key="sel_hour")
        with t_col2:
            sel_min = st.selectbox("Minute", list(range(0, 60)), index=default_tob.minute, key="sel_min")
        with t_col3:
            sel_ampm = st.selectbox("AM/PM", ["AM", "PM"], index=ampm_index, key="sel_ampm")

        final_h_24 = sel_hour % 12
        if sel_ampm == "PM":
            final_h_24 += 12
        ind_tob = datetime.time(final_h_24, sel_min)

    with col3:
        ind_city = st.text_input("City / District", value=default_city, key="ind_city")

    col4, col5 = st.columns(2)
    with col4:
        ind_state = st.text_input("State", value=default_state, key="ind_state")
    with col5:
        ind_country = st.text_input("Country", value=default_country, key="ind_country")

    st.markdown("---")

    if st.button("💾 Save Details & Calculate Kundli", type="primary"):
        with st.spinner("Details save aur Kundli calculate ki ja rahi hai..."):
            lagna, d1, d9, d10, details, moon_nak, dasha, transit, err = calculate_advanced_kundli(ind_dob, ind_tob, ind_city, ind_state, ind_country)
            if err:
                st.error(err)
            else:
                st.session_state.saved_gender = gender_option
                st.session_state.saved_dob = ind_dob
                st.session_state.saved_tob = ind_tob
                st.session_state.saved_city = ind_city
                st.session_state.saved_state = ind_state
                st.session_state.saved_country = ind_country

                conn = sqlite3.connect('users.db')
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users SET gender = ?, dob = ?, tob = ?, city = ?, state = ?, country = ? WHERE phone = ?
                ''', (gender_option, str(ind_dob), str(ind_tob), ind_city, ind_state, ind_country, active_phone))
                conn.commit()
                conn.close()

                st.session_state.match_generated = True
                st.session_state.mode = "single"
                st.session_state.lagna = lagna
                st.session_state.planet_details = details
                st.session_state.dasha = dasha
                st.session_state.transit = transit
                
                initial_query = f"Naye jatak (DOB: {ind_dob}, Time: {sel_hour}:{sel_min:02d} {sel_ampm}, Place: {ind_city}) ke liye ek complete Lal Kitab analysis provide karein."
                ans, api_err = get_clean_response(initial_query, dasha=dasha, transit=transit, planet_details=details)
                if ans:
                    st.session_state.master_report = ans
                    st.session_state.chat_history = [{"role": "assistant", "content": ans}]
                    st.success("✨ Jatak ki details aur Kundli successfully update ho chuki hain!")
                    st.rerun()
                else:
                    st.error(f"Gemini API Error: {api_err}")

else:
    # ==========================================
    # COUPLE MILAN MODE (WITH PERCENTAGE VERDICT)
    # ==========================================
    st.subheader("💖 Couple Milan & Gun Milan Details")
    st.info("Var (Boy) aur Vadhu (Girl) dono ki janam details darj karein.")

    hour_list = list(range(1, 13))
    minute_list = list(range(0, 60))

    m_col1, m_col2 = st.columns(2)
    
    with m_col1:
        st.markdown("### 🤵 Boy (Var) Details")
        boy_dob = st.date_input("Boy Date of Birth", value=datetime.date(1990, 1, 15), key="boy_dob")
        
        st.markdown("**Boy Time of Birth (12-Hour Style)**")
        bt_col1, bt_col2, bt_col3 = st.columns(3)
        with bt_col1:
            boy_hour = st.selectbox("Hour", hour_list, index=9, key="boy_hour")
        with bt_col2:
            boy_min = st.selectbox("Minute", minute_list, index=0, key="boy_min")
        with bt_col3:
            boy_ampm = st.selectbox("AM/PM", ["AM", "PM"], index=0, key="boy_ampm")

        final_boy_h24 = boy_hour % 12
        if boy_ampm == "PM":
            final_boy_h24 += 12
        boy_tob = datetime.time(final_boy_h24, boy_min)

        boy_city = st.text_input("Boy Birth City", value="Delhi", key="boy_city")
        boy_state = st.text_input("Boy Birth State", value="Delhi", key="boy_state")
        boy_country = st.text_input("Boy Birth Country", value="India", key="boy_country")

    with m_col2:
        st.markdown("### 👰 Girl (Vadhu) Details")
        girl_dob = st.date_input("Girl Date of Birth", value=datetime.date(1992, 6, 20), key="girl_dob")
        
        st.markdown("**Girl Time of Birth (12-Hour Style)**")
        gt_col1, gt_col2, gt_col3 = st.columns(3)
        with gt_col1:
            girl_hour = st.selectbox("Hour", hour_list, index=1, key="girl_hour")
        with gt_col2:
            girl_min = st.selectbox("Minute", minute_list, index=30, key="girl_min")
        with gt_col3:
            girl_ampm = st.selectbox("AM/PM", ["AM", "PM"], index=1, key="girl_ampm")

        final_girl_h24 = girl_hour % 12
        if girl_ampm == "PM":
            final_girl_h24 += 12
        girl_tob = datetime.time(final_girl_h24, girl_min)

        girl_city = st.text_input("Girl Birth City", value="Delhi", key="girl_city")
        girl_state = st.text_input("Girl Birth State", value="Delhi", key="girl_state")
        girl_country = st.text_input("Girl Birth Country", value="India", key="girl_country")

    st.markdown("---")

    if st.button("💍 Match Kundlis & Generate Report", type="primary"):
        with st.spinner("Dono Kundliyon ka milan aur Lal Kitab analysis kiya ja raha hai..."):
            boy_lagna, b_d1, b_d9, b_d10, boy_details, b_moon_nak, b_dasha, b_transit, b_err = calculate_advanced_kundli(boy_dob, boy_tob, boy_city, boy_state, boy_country)
            girl_lagna, g_d1, g_d9, g_d10, girl_details, g_moon_nak, g_dasha, g_transit, g_err = calculate_advanced_kundli(girl_dob, girl_tob, girl_city, girl_state, girl_country)

            if b_err or g_err:
                st.error(f"Kundli Calculation Error: {b_err or g_err}")
            else:
                match_query = (
                    f"Kripya Var (DOB: {boy_dob}, Time: {boy_hour}:{boy_min:02d} {boy_ampm}, Place: {boy_city}, Lagna: {boy_lagna}) aur "
                    f"Vadhu (DOB: {girl_dob}, Time: {girl_hour}:{girl_min:02d} {girl_ampm}, Place: {girl_city}, Lagna: {girl_lagna}) ke beech "
                    f"Lal Kitab aur Vedic astrology ke anusaar Gun Milan, Manglik dosh, grah sthiti aur vaivahik jivan ka vistar se vishleshan karein. "
                    f"REPORT KE ANTIM HISSSE MEIN EK DEFINITIVE PERCENTAGE SCORE (Jaise: Vivah ke liye Anumati / Gun Milan Score: XX% Positive) "
                    f"aur aakhri spashth verdict zaroor dein ki yeh rishta kitna safal rahega."
                )
                
                ans, api_err = get_clean_response(match_query, planet_details=boy_details)
                if ans:
                    st.session_state.match_report = ans
                    st.success("🎉 Couple Milan Report Safalpurvak Taiyar Ho Chuki Hai!")
                else:
                    st.error(f"API Error: {api_err}")

    if st.session_state.get("match_report"):
        st.markdown("---")
        st.subheader("📜 Couple Milan Report")
        st.markdown(st.session_state.match_report, unsafe_allow_html=True)
        
        match_pdf_bytes = create_pdf_report(st.session_state.match_report)
        st.download_button("📥 Download Couple Milan Report as PDF", data=match_pdf_bytes, file_name="Couple_Milan_Report.pdf", mime="application/pdf")


# ==========================================
# REPORT DISPLAY & CHAT SECTION (FOR INDIVIDUAL MODE)
# MANDATORY STEP: REPORT GENERATION BEFORE QUESTION ASK
# ==========================================
if app_mode == "👤 Individual Kundli (Single)":
    # Agar Master Report generate ho chuki hai
    if st.session_state.master_report:
        st.markdown("---")
        st.success("🎉 Aapki Lal Kitab Master Report taiyar hai!")
        pdf_bytes = create_pdf_report(st.session_state.master_report)
        st.download_button("📥 Download Report as PDF", data=pdf_bytes, file_name="Kundli_Report.pdf", mime="application/pdf")

        st.markdown("---")
        st.subheader("💬 Interactive Astrological Q&A Chat")

        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"], unsafe_allow_html=True)

        if st.session_state.questions_left > 0:
            st.markdown(f"*Aapke paas abhi **{st.session_state.questions_left}** sawal bacha hai.*")
            
            st.markdown("💡 **Jaldi poochne ke liye quick options chunein:**")
            quick_cols = st.columns(3)
            
            q_options = [
                "Dhan-Labh aur Aamdani ke Lal Kitab Upay",
                "Career ya Naukri mein badha ke karan",
                "Vivah aur Vaivahik Jivan ki sthiti",
                "Swasthya aur Bimari ke sateek upay",
                "Mangal ya Shani dosh ke nivaran",
                "Vartaman Gochar ka prabhav"
            ]
            
            triggered_quick_query = ""
            for idx, q_text in enumerate(q_options):
                col_target = quick_cols[idx % 3]
                with col_target:
                    if st.button(q_text, key=f"quick_btn_{idx}"):
                        triggered_quick_query = q_text

            user_question = st.chat_input("Apna sawal yahan puchein...", key="chat_input")
            
            final_query_to_process = user_question if user_question else triggered_quick_query

            if final_query_to_process:
                st.session_state.questions_left = max(0, st.session_state.questions_left - 1)
                
                conn = sqlite3.connect('users.db')
                cursor = conn.cursor()
                cursor.execute('UPDATE users SET questions_left = ? WHERE phone = ?', (st.session_state.questions_left, active_phone))
                conn.commit()
                conn.close()

                st.session_state.chat_history.append({"role": "user", "content": final_query_to_process})
                with st.chat_message("user"):
                    st.markdown(final_query_to_process)

                ans, err = get_clean_response(
                    final_query_to_process, 
                    dasha=st.session_state.get("dasha"), 
                    transit=st.session_state.get("transit"), 
                    planet_details=st.session_state.get("planet_details")
                )
                if ans:
                    st.session_state.chat_history.append({"role": "assistant", "content": ans})
                    st.rerun()
                else:
                    st.error(f"AI Response Error: {err}")
        else:
            st.warning("🔒 **Chat Locked :** Aapka sawal poora ho chuka hai aur chat lock ho gayi hai. Naya sawal poochne ke liye niche diye gaye plan mein se koi ek chunein:")
            
            col_p1, col_p2, col_p3 = st.columns(3)
            
            with col_p1:
                st.markdown("### 🧪 Testing Pack")
                st.markdown("**₹5** - 1 Question (Testing)")
                if st.button("Pay ₹5 Plan", key="pay_5"):
                    try:
                        rzp_key_id = st.secrets["razorpay"]["key_id"]
                        rzp_key_secret = st.secrets["razorpay"]["key_secret"]
                        client = razorpay.Client(auth=(rzp_key_id, rzp_key_secret))

                        link_resp = client.payment_link.create({
                            "amount": 500,  # 500 paise = ₹5
                            "currency": "INR",
                            "description": "Lal Kitab AI - 1 Question Testing Pack (₹5)",
                            "customer": {"name": "User", "email": "user@gmail.com", "contact": active_phone},
                            "callback_url": "http://localhost:8501/",
                            "callback_method": "get"
                        })
                        chat_link_id = link_resp.get("id")
                        short_url = link_resp.get("short_url")

                        conn = sqlite3.connect('users.db')
                        cursor = conn.cursor()
                        cursor.execute('UPDATE users SET chat_link_id = ? WHERE phone = ?', (chat_link_id, active_phone))
                        conn.commit()
                        conn.close()

                        st.success("✅ Testing Link Ready!")
                        st.markdown(f"👉 **[Click Here to Pay ₹5 (Test)]({short_url})**")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

            with col_p2:
                st.markdown("### 🥈 Silver Pack")
                st.markdown("**₹21** - 6 Questions")
                if st.button("Pay ₹21 Plan", key="pay_21"):
                    try:
                        rzp_key_id = st.secrets["razorpay"]["key_id"]
                        rzp_key_secret = st.secrets["razorpay"]["key_secret"]
                        client = razorpay.Client(auth=(rzp_key_id, rzp_key_secret))

                        link_resp = client.payment_link.create({
                            "amount": 2100, 
                            "currency": "INR",
                            "description": "Lal Kitab AI - 6 Questions Pack (₹21)",
                            "customer": {"name": "User", "email": "user@gmail.com", "contact": active_phone},
                            "callback_url": "http://localhost:8501/",
                            "callback_method": "get"
                        })
                        chat_link_id = link_resp.get("id")
                        short_url = link_resp.get("short_url")

                        conn = sqlite3.connect('users.db')
                        cursor = conn.cursor()
                        cursor.execute('UPDATE users SET chat_link_id = ? WHERE phone = ?', (chat_link_id, active_phone))
                        conn.commit()
                        conn.close()

                        st.success("✅ Link Ready!")
                        st.markdown(f"👉 **[Click Here to Pay ₹21]({short_url})**")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

            with col_p3:
                st.markdown("### 🥇 Gold Pack")
                st.markdown("**₹41** - 12 Questions + Free Report")
                if st.button("Pay ₹41 Plan", key="pay_41"):
                    try:
                        rzp_key_id = st.secrets["razorpay"]["key_id"]
                        rzp_key_secret = st.secrets["razorpay"]["key_secret"]
                        client = razorpay.Client(auth=(rzp_key_id, rzp_key_secret))

                        link_resp = client.payment_link.create({
                            "amount": 4100, 
                            "currency": "INR",
                            "description": "Lal Kitab AI - 12 Questions + Free Report Token (₹41)",
                            "customer": {"name": "User", "email": "user@gmail.com", "contact": active_phone},
                            "callback_url": "http://localhost:8501/",
                            "callback_method": "get"
                        })
                        chat_link_id = link_resp.get("id")
                        short_url = link_resp.get("short_url")

                        conn = sqlite3.connect('users.db')
                        cursor = conn.cursor()
                        cursor.execute('UPDATE users SET chat_link_id = ? WHERE phone = ?', (chat_link_id, active_phone))
                        conn.commit()
                        conn.close()

                        st.success("✅ Link Ready!")
                        st.markdown(f"👉 **[Click Here to Pay ₹41]({short_url})**")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

            st.markdown("---")
            if st.button("🔄 Verify Payment Status (After Payment)", type="primary"):
                try:
                    if not current_chat_link:
                        st.warning("⚠️ Pehle upar diye gaye kisi bhi plan ka link generate karein!")
                    else:
                        rzp_key_id = st.secrets["razorpay"]["key_id"]
                        rzp_key_secret = st.secrets["razorpay"]["key_secret"]
                        client = razorpay.Client(auth=(rzp_key_id, rzp_key_secret))

                        link_details = client.payment_link.fetch(current_chat_link)
                        if link_details.get("status") == "paid":
                            amt = link_details.get("amount", 0)
                            exact_q = 0
                            new_free_token = current_free_token
                            if amt == 500:  # ₹5
                                exact_q = 1
                            elif amt == 2100:
                                exact_q = 6
                            elif amt == 4100:
                                exact_q = 12
                                new_free_token = 1

                            st.session_state.questions_left = exact_q
                            
                            conn = sqlite3.connect('users.db')
                            cursor = conn.cursor()
                            cursor.execute('UPDATE users SET questions_left = ?, free_report_token = ? WHERE phone = ?', 
                                           (exact_q, new_free_token, active_phone))
                            conn.commit()
                            conn.close()
                            
                            st.success(f"🎉 Payment Verified! Aapke account mein naye sawal add kar diye gaye hain.")
                            st.rerun()
                        else:
                            st.warning("⚠️ Abhi payment 'paid' nahi hui hai ya pending hai. Kripya payment poori karein.")
                except Exception as e:
                    st.error(f"Verification Error: {str(e)}")
    else:
        # Agar Report Generate Nahi hui hai
        st.markdown("---")
        st.warning("⚠️ **Pehle Kundli Report Generate Karein:** Chat/Question poochne ki option use karne ke liye pehle upar diye gaye form mein apni details bhar kar **'Save Details & Calculate Kundli'** button par click karein.")
