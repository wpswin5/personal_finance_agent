import os
import pyodbc
import datetime
from dotenv import load_dotenv

load_dotenv()
conn = pyodbc.connect(os.getenv("AZURE_SQL_CONN"))
cursor = conn.cursor()

# Lookup categories
cursor.execute("SELECT id, name FROM categories")
category_map = {row.name: row.id for row in cursor.fetchall()}

sample_data = [
    ("user1", datetime.date(2025, 8, 1), 54.99, "USD", "Walmart", "Weekly groceries", "Groceries"),
    ("user1", datetime.date(2025, 8, 2), 1200.00, "USD", "Landlord", "August rent", "Rent"),
    ("user1", datetime.date(2025, 8, 3), 12.99, "USD", "Spotify", "Music subscription", "Subscriptions"),
    ("user1", datetime.date(2025, 8, 4), 32.50, "USD", "Chipotle", "Dinner with friends", "Dining"),
    ("user1", datetime.date(2025, 8, 5), 80.00, "USD", "Uber", "Ride to airport", "Transportation"),
    ("user1", datetime.date(2025, 8, 10), 65.00, "USD", "National Grid", "Electricity bill", "Utilities"),
    ("user1", datetime.date(2025, 8, 12), 250.00, "USD", "Amazon", "Back-to-school shopping", "Shopping"),
    ("user1", datetime.date(2025, 8, 15), 100.00, "USD", "AMC Theaters", "Movie night", "Entertainment"),
    ("user1", datetime.date(2025, 8, 20), 900.00, "USD", "Delta Airlines", "Flight to Boston", "Travel"),
    ("user1", datetime.date(2025, 8, 25), 45.00, "USD", "CVS Pharmacy", "Prescriptions", "Healthcare")
]

for user_id, date, amount, cur, merchant, desc, cat in sample_data:
    cursor.execute(
        """INSERT INTO transactions (user_id, posted_at, amount, currency, merchant_name, description, category_id, category_pred, category_conf)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (user_id, date, amount, cur, merchant, desc, category_map[cat], cat, 0.95)
    )

conn.commit()
print("✅ Seed data inserted")
