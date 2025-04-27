from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles  # ✨ Added for serving CSS
from pydantic import BaseModel
import uvicorn
import joblib

# Initialize FastAPI app
app = FastAPI()

# Mount the static directory to serve CSS/JS files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set the templates directory for HTML files
templates = Jinja2Templates(directory="templates")

# Load your trained model and vectorizer
model = joblib.load('expenses_model2.pkl')
vectorizer = joblib.load('vectorizers2.pkl')

# Define category mappings
category_mapping = {
    0: 'Food',
    1: 'Entertainment',
    2: 'Transportation',
    3: 'Shopping',
    4: 'Groceries',
    5: 'Healthcare',
    6: 'Bills'
}

# Manual corrections based on keywords
manual_corrections = {
    "grocery": "Groceries",
    "supermarket": "Groceries",
    "food": "Groceries",
    "restaurant": "Groceries",
    "hospital": "Healthcare",
    "clinic": "Healthcare",
    "medical": "Healthcare",
    "rent": "Housing",
    "mortgage": "Housing",
    "apartment": "Housing",
    "house": "Housing",
    "taxi": "Transport",
    "bus": "Transport",
    "car": "Transport",
    "fuel": "Transport",
    "uber": "Transport",
    "train": "Transport",
    "flight": "Travel",
    "movie": "Entertainment",
    "theater": "Entertainment",
    "concert": "Entertainment",
    "event": "Entertainment",
    "show": "Entertainment",
    "sports": "Entertainment",
    "game": "Entertainment",
    "leisure": "Entertainment",
    "electricity": "Utilities",
    "water": "Utilities",
    "gas": "Utilities",
    "internet": "Utilities",
    "phone": "Utilities",
    "cable": "Utilities",
    "tuition": "Education",
    "fees": "Education",
    "college": "Education",
    "school": "Education",
    "textbooks": "Education",
    "study": "Education",
    "online course": "Education",
    "hotel": "Travel",
    "vacation": "Travel",
    "trip": "Travel",
    "accommodation": "Travel",
    "tickets": "Travel",
    "holiday": "Travel",
    "clothes": "Shopping",
    "electronics": "Shopping",
    "shoes": "Shopping",
    "apparel": "Shopping",
    "accessories": "Shopping",
    "online store": "Shopping",
    "purchase": "Shopping",
    "subscription": "Bills/Subscriptions",
    "netflix": "Bills/Subscriptions",
    "spotify": "Bills/Subscriptions",
    "insurance": "Bills/Subscriptions",
    "premium": "Bills/Subscriptions",
    "memberships": "Bills/Subscriptions"
}

# Saving tips based on categories
saving_tips = {
    'Food': "Try meal prepping to save ₹1000/month!",
    'Entertainment': "Limit movie outings to once a month!",
    'Transportation': "Consider carpooling or public transport!",
    'Shopping': "Set a monthly shopping budget and stick to it!",
    'Groceries': "Use coupons and bulk buying to save money!",
    'Healthcare': "Consider health insurance to save on emergencies!",
    'Bills': "Unplug unused devices to lower electricity bills!"
}

# BaseModel for input validation
class ExpenseInput(BaseModel):
    message: str
    amount: float

# Home Route - Renders the chatbot page
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("chat_bot.html", {"request": request})

# Helper function to apply manual corrections
def apply_manual_corrections(description: str) -> str:
    for keyword, corrected_category in manual_corrections.items():
        if keyword.lower() in description.lower():
            return corrected_category
    return None

# Prediction Route
@app.post("/predict", response_class=JSONResponse)
async def predict_expense(data: ExpenseInput):
    try:
        message = data.message
        amount = data.amount

        # Apply manual corrections first
        corrected_category = apply_manual_corrections(message)
        if corrected_category:
            category_name = corrected_category
        else:
            # If no manual correction found, use ML model
            input_vector = vectorizer.transform([message])
            prediction = model.predict(input_vector)[0]
            category_name = category_mapping.get(prediction, "Unknown")

        # Analyze the amount and give spending feedback
        if amount > 3000:
            status = f"You spent ₹{amount} on {category_name}. That's quite high!"
        elif amount < 500:
            status = f"You spent ₹{amount} on {category_name}. That's a small and smart spending!"
        else:
            status = f"You spent ₹{amount} on {category_name}."

        # Get a saving tip
        tip = saving_tips.get(category_name, "Spend wisely!")

        response = {
            "category": category_name,
            "status": status,
            "saving_tip": tip
        }
        return JSONResponse(content=response)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Run the server
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
