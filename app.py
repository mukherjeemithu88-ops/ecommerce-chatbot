from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import pandas as pd

app = FastAPI()

# Serve UI
@app.get("/", response_class=HTMLResponse)
def serve_ui():
    with open("index.html", "r") as f:
        return f.read()

# Allow frontend calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Excel once
df = pd.read_excel("data.xlsx")
df = df.fillna("").astype(str)

@app.post("/chat")
async def chat(data: dict):
    user = data.get("message", "").lower()

    categories = {
        "smartphones": ["phone", "smartphone", "iphone"],
        "earbuds": ["earbuds", "buds", "wireless"],
        "smartwatch": ["watch", "smartwatch"],
        "kitchen": ["kitchen", "appliance"],
        "accessories": ["accessory", "charger", "cable"],
        "decor": ["decor", "home decor"],
        "health": ["health", "wellness"]
    }

    matched_category = None

    for cat, keywords in categories.items():
        if any(word in user for word in keywords):
            matched_category = cat
            break

    if matched_category:
        filtered = df[df.apply(lambda row: matched_category in row.to_string().lower(), axis=1)]

        if not filtered.empty:
            response = f"🔎 {matched_category.title()} Results:\n\n"

            for _, row in filtered.iterrows():
                response += f"Product: {row.get('Product','')}\n"
                response += f"Amazon: {row.get('Amazon','')}\n"
                response += f"Flipkart: {row.get('Flipkart','')}\n"
                response += f"Croma: {row.get('Croma','')}\n\n"

            return {"response": response}

    return {"response": "Try categories like smartphones, earbuds, kitchen, decor, health"}
