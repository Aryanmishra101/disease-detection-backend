from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pymongo import MongoClient
import joblib
import numpy as np
from auth.routes import router as auth_router
from fastapi.middleware.cors import CORSMiddleware

# ----------------------------------------
# FASTAPI APP SETUP
# ----------------------------------------
app = FastAPI()

# CORS FIX for React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # allow React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication routes
app.include_router(auth_router, prefix="/auth")



# Static + Templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ----------------------------------------
# LOAD ML MODEL
# ----------------------------------------
model = joblib.load("diabetes_best_model.pkl")

# ----------------------------------------
# CONNECT TO MONGODB
# ----------------------------------------
client = MongoClient(
    "mongodb+srv://aryanmishraa18_db_user:Peace%4001@cluster0.qigxmce.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
    tls=True,
    tlsAllowInvalidCertificates=True
)

db = client["diseaseDB"]
collection = db["predictions"]

# ----------------------------------------
# HOME PAGE
# ----------------------------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ----------------------------------------
# PREDICTION API
# ----------------------------------------
@app.post("/predict")
async def predict(request: Request):
    data = await request.json()

    input_values = np.array(list(data.values())).reshape(1, -1)
    prediction = int(model.predict(input_values)[0])

    collection.insert_one({
        "input_data": data,
        "prediction": prediction
    })

    return {"prediction": prediction}
