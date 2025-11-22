# auth/routes.py
from fastapi import APIRouter, HTTPException
from auth.schemas import UserCreate, UserLogin
from auth.utils import hash_password, verify_password, create_token
from pymongo import MongoClient
import os

router = APIRouter()

# -------------------------------
# MongoDB (Render Environment Variable)
# -------------------------------
MONGO_URL = os.getenv("MONGO_URL")

client = MongoClient(MONGO_URL, tls=True, tlsAllowInvalidCertificates=True)
db = client["diseaseDB"]
user_collection = db["users"]

# -------------------------------
# REGISTER
# -------------------------------
@router.post("/register")
def register(user: UserCreate):

    # Check existing
    if user_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = hash_password(user.password)

    new_user = {
        "username": user.username,
        "email": user.email,
        "password": hashed_pw,
        "role": "user"
    }

    user_collection.insert_one(new_user)

    return {"message": "User registered successfully"}

# -------------------------------
# LOGIN
# -------------------------------
@router.post("/login")
def login(user: UserLogin):

    db_user = user_collection.find_one({"email": user.email})

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Invalid password")

    token = create_token({"email": user.email, "role": db_user["role"]})

    return {
        "message": "Login successful",
        "token": token,
        "role": db_user["role"]
    }
# -------------------------------