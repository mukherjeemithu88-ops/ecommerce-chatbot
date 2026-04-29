from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import pandas as pd
import re
import os

app = FastAPI()

# ---------- Serve UI ----------
@app.get("/", response_class=HTMLResponse)
def serve_ui():
    # Works locally and on Render
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "index.html")
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

# ---------- CORS (allow your HTML to call /chat) ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Request model ----------
class ChatRequest(BaseModel):
    message: str

# ---------- Load data (optional) ----------
# If you have an Excel file like data.xlsx, it will load it.
# If not, app still works with fallback responses.
DATA = None
for fname in ["data.xlsx", "data.xls"]:
    if os.path.exists(fname):
        try:
            DATA = pd.read_excel(fname)
            break
        except Exception:
            DATA = None

def normalize(text: str) -> str:
    return re.sub(r"\s+", "", str(text).lower())

# ---------- Chat endpoint ----------
@app.post("/chat")
async def chat(data: dict):
    try:
        user_input = data.get("message", "").lower()

        if "iphone17" in user_input:
            return {
                "response": "Here is comparison for iPhone 17:\n\nAmazon: ₹79,999\nFlipkart: ₹78,500\nCroma: ₹80,200\n\n👉 Best deal: Flipkart"
            }

        elif "smartwatch" in user_input:
            return {
                "response": "Top Smartwatch:\n\nNoise: ₹2,999\nBoat: ₹2,499\nFirebolt: ₹2,199\n\n👉 Best: Firebolt"
            }

        else:
            return {
                "response": "I can help compare products. Try: compare iphone17"
            }

    except Exception as e:
        return {"response": "Something went wrong. Please try again."}

    # ---- Simple intents ----
    if "compare" in user:
        # try to extract product name after 'compare'
        parts = user.split("compare", 1)
        query = normalize(parts[1]) if len(parts) > 1 else ""

        # If we have data, try to find matching rows
        if DATA is not None and "product" in [c.lower() for c in DATA.columns]:
            # find product column name (case-insensitive)
            prod_col = next(c for c in DATA.columns if c.lower() == "product")
            matches = DATA[DATA[prod_col].astype(str).str.lower().str.contains(query, na=False)]

            if len(matches) > 0:
                # build a simple comparison text
                lines = []
                for _, r in matches.iterrows():
                    row_txt = []
                    for c in DATA.columns:
                        val = r[c]
                        if pd.notna(val):
                            row_txt.append(f"{c}: {val}")
                    lines.append(" | ".join(row_txt))
                return {"response": "Here’s what I found:\n\n" + "\n".join(lines)}

        # fallback
        return {"response": f"I couldn't find '{query}'. Try exact name like 'compare iphone17'."}

    if "price" in user:
        return {"response": "Tell me the product name, e.g., 'price iphone17 on amazon'."}

    # default
    return {"response": "I can help compare products. Try: 'compare iphone17'."}
