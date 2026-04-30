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

    elif any(word in user_input for word in ["watch", "smartwatch"]):
        return "smartwatch"

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

        # Apply simple AI mapping
        mapped_category = map_query_to_category(user)

        categories = {
            "smartphones": ["phone", "smartphone", "iphone"],
            "earbuds": ["earbuds", "buds", "wireless"],
            "smartwatch": ["watch", "smartwatch"],
            "kitchen": ["kitchen", "appliance"],
            "accessories": ["accessory", "charger", "cable"],
            "decor": ["decor", "home"],
            "health": ["health", "wellness"]
        }

        matched_category = None

        for cat, keywords in categories.items():
            if cat in mapped_category or any(word in mapped_category for word in keywords):
                matched_category = cat
                break

        if matched_category:
            filtered = df[df.apply(lambda row: matched_category in row.to_string().lower(), axis=1)]

            if not filtered.empty:
                response = f"🔎 {matched_category.title()} Results:\n\n"

                # ✅ LIMIT RESULTS
                filtered = filtered.head(3)

                for _, row in filtered.iterrows():
                    product = str(row.iloc[0])

                    response += f"🛍 {product}\n"

                    # ✅ ONLY PLATFORM COLUMNS
                    for col_name, value in row.items():
                        col = col_name.lower()

                        if any(p in col for p in ["amazon", "flipkart", "croma", "jiomart", "tatacliq"]):
                            if value and value != "nan":
                                response += f"{col_name}: {value}\n"

                    response += "\n"

                return {"response": response}

        return {"response": "Try categories like smartphones, earbuds, kitchen, decor, health"}

    except Exception as e:
        return {"response": f"Error: {str(e)}"}
