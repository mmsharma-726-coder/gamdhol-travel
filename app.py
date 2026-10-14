import streamlit as st
import sqlite3
import random

# --- PAGE SETUP ---
st.set_page_config(page_title="Gamdhol Travel", page_icon="🚌", layout="centered")

# --- DATABASE INITIALIZATION ---
def init_db():
    conn = sqlite3.connect("gamdhol_travel.db")
    c = conn.cursor()
    # Users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            phone TEXT PRIMARY KEY
        )
    """)
    # Bookings table
    c.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT,
            passenger_name TEXT,
            route TEXT,
            bus_name TEXT,
            seat_number INTEGER
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Helper Functions
def add_user(phone):
    conn = sqlite3.connect("gamdhol_travel.db")
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (phone) VALUES (?)", (phone,))
    conn.commit()
    conn.close()

def get_booked_seats(route, bus_name):
    conn = sqlite3.connect("gamdhol_travel.db")
    c = conn.cursor()
    c.execute("SELECT seat_number FROM bookings WHERE route=? AND bus_name=?", (route, bus_name))
    seats = [row[0] for row in c.fetchall()]
    conn.close()
    return seats

def save_booking(phone, passenger_name, route, bus_name, seat_number):
    conn = sqlite3.connect("gamdhol_travel.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO bookings (phone, passenger_name, route, bus_name, seat_number)
        VALUES (?, ?, ?, ?, ?)
    """, (phone, passenger_name, route, bus_name, seat_number))
    conn.commit()
    conn.close()

def get_user_bookings(phone):
    conn = sqlite3.connect("gamdhol_travel.db")
    c = conn.cursor()
    c.execute("SELECT passenger_name, route, bus_name, seat_number FROM bookings WHERE phone=?", (phone,))
    records = c.fetchall()
    conn.close()
    return records

# --- SESSION STATE ---
if "user_logged_in" not in st.session_state:
    st.session_state.user_logged_in = False
    st.session_state.user_phone = ""

if "otp_sent" not in st.session_state:
    st.session_state.otp_sent = False
    st.session_state.generated_otp = None

BUS_SCHEDULE = {
    "Mandi ➔ Gamdhol": [
        {"name": "Bus Sunil", "time": "7:00 AM"},
        {"name": "Bus Arjun", "time": "9:00 AM"},
        {"name": "Bus Batahan", "time": "10:00 AM"},
    ],
    "Gamdhol ➔ Mandi": [
        {"name": "Bus Sunil", "time": "1:00 PM"},
        {"name": "Bus Arjun", "time": "2:00 PM"},
        {"name": "Bus Batahan", "time": "3:00 PM"},
        {"name": "Bus Sunil (Evening)", "time": "4:00 PM"},
        {"name": "Bus Arjun (Evening)", "time": "5:00 PM"},
        {"name": "Bus Batahan (Evening)", "time": "6:00 PM"},
    ]
}

st.title("🚌 Gamdhol Travel")

# --- SCREEN 1: LOGIN / OTP ---
if not st.session_state.user_logged_in:
    st.subheader("Login / Register with Phone Number")
    phone = st.text_input("Enter 10-Digit Mobile Number:", max_chars=10)
    
    if st.button("Send OTP") and len(phone) == 10:
        st.session_state.generated_otp = str(random.randint(1000, 9999))
        st.session_state.otp_sent = True
        st.session_state.user_phone = phone
        st.info(f"🔑 Your Login OTP: **{st.session_state.generated_otp}**")
        
    if st.session_state.otp_sent:
        user_otp = st.text_input("Enter 4-Digit OTP:", max_chars=4)
        if st.button("Verify & Login"):
            if user_otp == st.session_state.generated_otp:
                add_user(st.session_state.user_phone)
                st.session_state.user_logged_in = True
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid OTP. Try again.")

# --- SCREEN 2: BOOKING SYSTEM ---
else:
    st.sidebar.write(f"Logged in as: **+91 {st.session_state.user_phone}**")
    if st.sidebar.button("Logout"):
        st.session_state.user_logged_in = False
        st.rerun()

    st.subheader("Book Your Bus Ticket (Free Fare)")
    
    route = st.selectbox("Select Route Direction:", list(BUS_SCHEDULE.keys()))
    available_buses = BUS_SCHEDULE[route]
    bus_options = [f"{b['name']} ({b['time']})" for b in available_buses]
    selected_bus = st.selectbox("Select Bus & Departure Time:", bus_options)
    
    st.divider()
    st.write("### 💺 Select Your Seat (1 to 30)")
    
    # Query Database for booked seats
    booked_seats = get_booked_seats(route, selected_bus)
    
    selected_seat = None
    cols = st.columns(5)
    for seat_num in range(1, 31):
        col = cols[(seat_num - 1) % 5]
        is_booked = seat_num in booked_seats
        
        if is_booked:
            col.button(f"🔴 #{seat_num}", key=f"s_{seat_num}", disabled=True)
        else:
            if col.button(f"🟢 #{seat_num}", key=f"s_{seat_num}"):
                selected_seat = seat_num

    if selected_seat:
        st.success(f"Selected Seat Number: **#{selected_seat}**")
        passenger_name = st.text_input("Passenger Name:")
        
        if st.button("Confirm Booking"):
            if passenger_name:
                save_booking(
                    st.session_state.user_phone, 
                    passenger_name, 
                    route, 
                    selected_bus, 
                    selected_seat
                )
                st.balloons()
                st.success(f"🎉 Ticket Booked for {passenger_name} on {selected_bus}!")
                st.rerun()
            else:
                st.warning("Please enter passenger name.")

    st.divider()
    st.subheader("🎟️ Your Active Tickets")
    user_tickets = get_user_bookings(st.session_state.user_phone)
    
    if user_tickets:
        for t in user_tickets:
            st.write(f"• **Passenger:** {t[0]} | **Route:** {t[1]} | **Bus:** {t[2]} | **Seat:** #{t[3]}")
    else:
        st.caption("No tickets booked yet.")
