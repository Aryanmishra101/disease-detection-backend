from fastapi import APIRouter, HTTPException
from auth.schemas import UserCreate, UserLogin
from auth.utils import hash_password, verify_password, create_token
from pymongo import MongoClient

# Correct MongoDB Connection (SAME AS main.py)
client = MongoClient(
    "mongodb+srv://aryanmishraa18_db_user:Peace%4001@cluster0.qigxmce.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
    tls=True,
    tlsAllowInvalidCertificates=True
)

db = client["diseaseDB"]   
user_collection = db["users"]

router = APIRouter()

@router.post("/register")
def register(user: UserCreate):
    if user_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = hash_password(user.password)

    user_collection.insert_one({
        "username": user.username,
        "email": user.email,
        "password": hashed_pw,
        "role": "user"
    })

    return {"message": "User registered successfully!"}


@router.post("/login")
def login(user: UserLogin):
    db_user = user_collection.find_one({"email": user.email})

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Invalid password")

    token = create_token({"email": user.email, "role": db_user["role"]})

    return {
        "message": "Login successful!",
        "token": token,
        "role": db_user["role"]
    }
