from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import pandas as pd

app = FastAPI()

# ---------- SIMPLE AI LAYER ----------
def map_query_to_category(user_input):
    user_input = user_input.lower()

    if any(word in user_input for word in ["phone", "iphone", "mobile"]):
        return "smartphones"

    elif any(word in user_input for word in ["earbud", "buds", "airpods"]):
        return "earbuds"

    elif any(word in user_input for word in ["watch", "smartwatch", "watches"]):
        return "smartwatches"

    elif any(word in user_input for word in ["kitchen", "mixer", "grinder", "appliance"]):
        return "kitchen"

    elif any(word in user_input for word in ["charger", "cable", "accessory"]):
        return "accessories"

    elif any(word in user_input for word in ["decor", "home", "lamp"]):
        return "decor"

    elif any(word in user_input for word in ["health", "fitness", "wellness"]):
        return "health"

    return user_input


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


# ---------- CHAT API ----------
@app.post("/chat")
async def chat(data: dict):
    try:
        user = data.get("message", "").lower()

        # map user query
        mapped_category = map_query_to_category(user)

        matched_rows = []

        # ✅ SEARCH ENTIRE ROW (NOT JUST ONE COLUMN)
        for _, row in df.iterrows():
            row_text = " ".join([str(v).lower() for v in row.values])

            if mapped_category in row_text:
                matched_rows.append(row)

        if matched_rows:
            response = f"🔎 {mapped_category.title()} Results:\n\n"

            # ✅ LIMIT TO TOP 3 RESULTS
            for row in matched_rows[:3]:
                product = str(row.iloc[0])

                response += f"🛍 {product}\n"

                # ✅ ONLY SHOW 5 PLATFORMS
                platforms = ["Amazon", "Flipkart", "Croma", "JioMart", "TataCliq"]

                for i, platform in enumerate(platforms):
                    if len(row) > i + 2:
                        value = str(row.iloc[i + 2])

                        # clean unwanted text
                        if value and "unnamed" not in value.lower():
                            response += f"{platform}: {value}\n"

                response += "\n"

            return {"response": response}

        return {"response": "No matching products found. Try smartphones, decor, kitchen, etc."}

    except Exception as e:
        return {"response": f"Error: {str(e)}"}
