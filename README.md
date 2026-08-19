# gamdhol-travel
A bus booking application in the local area 
# 🚌 Gamdhol Travel - Bus Booking System

A lightweight, interactive web application built with Python and Streamlit for booking local bus tickets between Mandi and Gamdhol. 

This app allows passengers to log in via mobile number and OTP, select route directions, view real-time bus schedules, and pick available seats on a visual grid.

---

## 📌 Features

- **Phone + OTP Authentication:** Simulates quick mobile login/registration.
- **Route & Bus Schedule Selection:** Supports round-trips between Mandi and Gamdhol across multiple daily departure times:
  - **Mandi ➔ Gamdhol:** Bus Sunil (7:00 AM), Bus Arjun (9:00 AM), Bus Batahan (10:00 AM)
  - **Gamdhol ➔ Mandi:** Afternoon & Evening departures (1:00 PM to 6:00 PM)
- **Interactive 2D Seat Selection:** Visual seat map displaying available (🟢) and booked (🔴) seats (30 seats per bus).
- **Persistent Data:** Powered by an **SQLite** database (`gamdhol_travel.db`) to preserve user accounts and ticket bookings across sessions.
- **Ticket Summary:** View confirmed active bookings directly in your profile dashboard.

---

## 🛠️ Tech Stack

- **Frontend & Web Framework:** [Streamlit](https://streamlit.io/)
- **Backend & Logic:** Python 3
- **Database:** SQLite3

---

## 🚀 How to Run Locally

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_GITHUB_USERNAME/gamdhol-travel.git](https://github.com/YOUR_GITHUB_USERNAME/gamdhol-travel.git)
   cd gamdhol-travel
