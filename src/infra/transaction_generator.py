import random
import datetime
from faker import Faker
from datetime import datetime

fake = Faker()

# Category + merchant mapping
CATEGORY_MERCHANTS = {
    "Groceries": ["Walmart", "Trader Joe's", "Whole Foods", "Costco"],
    "Restaurants": ["Chipotle", "McDonald's", "Starbucks", "Panera Bread"],
    "Travel": ["Uber", "Lyft", "Delta Airlines", "Airbnb"],
    "Entertainment": ["Spotify", "Netflix", "AMC Theatres", "Xbox Live"],
    "Healthcare": ["CVS Pharmacy", "Walgreens", "Rite Aid"],
    "Shopping": ["Amazon", "Target", "BestBuy", "Home Depot"],
    "Utilities": ["Comcast", "AT&T", "Verizon"],
    "Rent": ["Apartment Rent"],
    "Subscriptions": ["HBO Max", "Apple Music", "NYTimes"],
}

def generate_fake_transactions(n: int = 10, currency: str = "USD"):
    transactions = []
    for _ in range(n):
        category = random.choice(list(CATEGORY_MERCHANTS.keys()))
        merchant = random.choice(CATEGORY_MERCHANTS[category])
        amount = round(random.uniform(5, 500), 2)
        if category == "Rent":  # rent is usually higher
            amount = round(random.uniform(800, 2500), 2)

        date = fake.date_between(start_date="-7d", end_date="today").isoformat()

        tx = {
            "amount": amount,
            "date_posted": datetime.strptime(date, '%Y-%m-%d').date(),
            "date_transacted": datetime.strptime(date, '%Y-%m-%d').date(),
            "description": merchant,
            "iso_currency_code": currency
        }
        print(tx)
        transactions.append(tx)
    return transactions
