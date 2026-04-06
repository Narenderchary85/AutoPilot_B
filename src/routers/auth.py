from fastapi import APIRouter, HTTPException, Depends
from src.models.user import UserCreate, UserLogin
from src.db.mongo import users_collection
from src.auth.password import hash_password, verify_password
from src.auth.jwt import create_access_token
from src.auth.dependencies import get_current_user
from pydantic import BaseModel, EmailStr
from bson import ObjectId

router = APIRouter(prefix="/auth", tags=["Auth"])

class VerificationStatusResponse(BaseModel):
    isVerified: bool

@router.post("/signup")
def signup(user: UserCreate):
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="User already exists")

    newuser=users_collection.insert_one({
        "name": user.name,
        "email": user.email,
        "password": hash_password(user.password)
    })

    token=create_access_token({"user_id": str(newuser.inserted_id)})

    return {"message": "Signup successful","token":token}

@router.post("/login")
def login(user: UserLogin):
    print("Login attempt for email:", user.email)
    print(user.password)
    db_user = users_collection.find_one({"email": user.email})
    
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    print("User authenticated successfully:", db_user["email"])

    token = create_access_token({"user_id": str(db_user["_id"])})

    return {"access_token": token}


@router.get("/verification-status", response_model=VerificationStatusResponse)
def verification_status(current_user_id: str = Depends(get_current_user)):
    user = users_collection.find_one({"_id": ObjectId(current_user_id)})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "isVerified": user.get("isVerified", False)
    }