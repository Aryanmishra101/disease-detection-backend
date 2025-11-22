# main.py
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
import joblib
import numpy as np

from auth.routes import router as auth_router
import os

# ----------------------------------------
# FASTAPI APP
# ----------------------------------------
app = FastAPI()

# ----------------------------------------
# CORS (Frontend Hosted Separately)
# ----------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Allow all origins (React, Render, etc.)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------
# STATIC FILES & TEMPLATE SETUP
# ----------------------------------------
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ----------------------------------------
# MONGODB CONNECTION (Render Environment Variable)
# ----------------------------------------
MONGO_URL = os.getenv("MONGO_URL")

client = MongoClient(MONGO_URL, tls=True, tlsAllowInvalidCertificates=True)
db = client["diseaseDB"]
collection = db["predictions"]

# ----------------------------------------
# LOAD ML MODEL
# ----------------------------------------
model = joblib.load("diabetes_best_model.pkl")

# ----------------------------------------
# INCLUDE AUTH ROUTES
# ----------------------------------------
app.include_router(auth_router, prefix="/auth")

# ----------------------------------------
# HOME PAGE (ONLY FOR TESTING)
# ----------------------------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ----------------------------------------
# PREDICT API
# ----------------------------------------
@app.post("/predict")
async def predict(request: Request):
    data = await request.json()

    # Convert to numpy
    values = np.array(list(data.values())).reshape(1, -1)

    # Predict
    prediction = int(model.predict(values)[0])

    # Save to MongoDB
    collection.insert_one({
        "input": data,
        "prediction": prediction
    })

    return {"prediction": prediction}
# ----------------------------------------