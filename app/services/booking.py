import sqlite3
from app.models import BookingRequest

DB_PATH = "bookings.db"

def init_db():
    """Creates the booking table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            date TEXT,
            time TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_booking(booking: BookingRequest):
    """Saves a booking record to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO bookings (name, email, date, time) VALUES (?, ?, ?, ?)",
        (booking.name, booking.email, booking.date, booking.time)
    )
    conn.commit()
    conn.close()
    return True