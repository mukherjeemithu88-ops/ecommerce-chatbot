from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import pandas as pd

app = FastAPI()

# ---------- SERVE UI ----------
@app.get("/", response_class=HTMLResponse)
def serve_ui():
    with open("index.html", "r") as f:
        return f.read()

# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- LOAD DATA ----------
df = pd.read_excel("data.xlsx")
df = df.fillna("").astype(str)

# ---------- SIMPLE CATEGORY DETECTION ----------
def detect_category(user):
    user = user.lower()

    if any(x in user for x in ["phone", "iphone"]):
        return "smartphones"

    if any(x in user for x in ["earbud", "buds"]):
        return "earbuds"

    if any(x in user for x in ["watch"]):
        return "smartwatch"

    if any(x in user for x in ["kitchen"]):
        return "kitchen"

    if any(x in user for x in ["decor", "home"]):
        return "decor"

    if any(x in user for x in ["health", "fitness"]):
        return "health"

    return None

# ---------- CHAT API ----------
@app.post("/chat")
async def chat(data: dict):
    user = data.get("message", "").lower()

    category = detect_category(user)

    if not category:
        return {"response": "Try categories like smartphones, decor, kitchen, health"}

    results = []

    for _, row in df.iterrows():
        row_text = " ".join(row.values).lower()

        if category in row_text:
            results.append(row)

    if not results:
        return {"response": "No matching products found"}

    response = f"{category.upper()} RESULTS:\n\n"

    # show only top 3
    for row in results[:3]:
        # Try to pick meaningful product name (not category or empty)
product = ""

for val in row.values:
    text = str(val).strip()

    if text and "unnamed" not in text.lower() and len(text) > 5:
        product = text
        break

if not product:
    product = "Product"

        response += f"{product}\n"

        # show only platform prices (columns 3 onwards)
        platforms = ["Amazon", "Flipkart", "Croma", "JioMart", "TataCliq"]

for i, platform in enumerate(platforms):
    if len(row) > i + 2:
        value = row.iloc[i + 2]

        if value and "unnamed" not in str(value).lower():
            response += f"{platform}: {value}\n"
    return {"response": response}
