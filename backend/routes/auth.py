from fastapi import APIRouter
from database import SessionLocal
from models import User
from utils.auth import hash_password, verify_password

router = APIRouter()

@router.post("/register/")
def register(data: dict):
    db = SessionLocal()

    user = User(
        email=data["email"],
        password=hash_password(data["password"])
    )

    db.add(user)
    db.commit()
    db.close()

    return {"message": "User created"}


@router.post("/login/")
def login(data: dict):
    db = SessionLocal()

    user = db.query(User).filter(User.email == data["email"]).first()

    if not user or not verify_password(data["password"], user.password):
        return {"error": "Invalid credentials"}

    return {"user_id": user.id}