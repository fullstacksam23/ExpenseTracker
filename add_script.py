import pandas as pd
import random
from datetime import datetime, timedelta
from app import app, db, Expenses  # 🛑 Also import app

# Generate a random date within the last month
def generate_random_date():
    today = datetime.today()
    start_date = today - timedelta(days=30)
    random_number_of_days = random.randint(0, 30)
    random_date = start_date + timedelta(days=random_number_of_days)
    return random_date.date()

def load_expenses_from_excel(file_path):
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)  # 🛠️ Read as CSV
    else:
        df = pd.read_excel(file_path)  # If you give an .xlsx later

    with app.app_context():
        for index, row in df.iterrows():
            random_date = generate_random_date()

            expense = Expenses(
                amount=row['amount'],
                date=random_date,
                description=row['description'],
                category=row['category'],
                transaction_type=row['type'].capitalize()
            )

            db.session.add(expense)

        db.session.commit()
        print("All expenses added successfully!")

# Example usage
if __name__ == "__main__":
    load_expenses_from_excel("C:/Users/Samuel Oommen/PycharmProjects/ExpenseTracker/data.csv")
