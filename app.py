from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

# Load Excel
df = pd.read_excel("data.xlsx", header=None)
df = df.iloc[3:]
df.columns = ["Category","Product","Amazon","Flipkart","Croma","JioMart","TataCliq","Features"]

def normalize(text):
    return str(text).lower().replace(" ", "")

def extract_price(text):
    if pd.isna(text):
        return None
    match = re.search(r"₹[\d,]+", str(text))
    return match.group() if match else "N/A"

@app.post("/chat")
def chat(req: ChatRequest):
    user_msg = req.message

    # Find product
    row = df[df["Product"].apply(
        lambda x: normalize(x) in normalize(user_msg) if isinstance(x, str) else False
    )]

    if row.empty:
        return {"reply": "Sorry, I couldn't find that product."}

    row = row.iloc[0]

    # Build response manually (NO AI yet)
    reply = f"{row['Product']} prices:\n"
    reply += f"Amazon: {extract_price(row['Amazon'])}\n"
    reply += f"Flipkart: {extract_price(row['Flipkart'])}\n"
    reply += f"Croma: {extract_price(row['Croma'])}\n"
    reply += f"JioMart: {extract_price(row['JioMart'])}\n"
    reply += f"TataCliq: {extract_price(row['TataCliq'])}"

    return {"reply": reply}