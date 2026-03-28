from fastapi import APIRouter

try:
    from backend.database import SessionLocal
    from backend.models import User
except ModuleNotFoundError:
    from database import SessionLocal
    from models import User

try:
    from backend.utils.auth import hash_password, verify_password
except ModuleNotFoundError as exc:
    if exc.name not in {"backend", "backend.utils", "backend.utils.auth"}:
        raise
    from utils.auth import hash_password, verify_password

router = APIRouter()


@router.get("/check-user/")
def check_user():
    db = SessionLocal()
    user = db.query(User).first()
    db.close()

    return {
        "exists": True if user else False
    }


@router.post("/setup-profile/")
def setup_profile(data: dict):
    db = SessionLocal()

    existing = db.query(User).first()
    if existing:
        db.close()
        return {"error": "User already exists"}

    user = User(
        name=data["name"],
        dob=data["dob"],
        phone=data["phone"],
        email=data.get("email"),
        location_permission=data.get("location_permission", "denied"),
        password=None,
    )

    db.add(user)
    db.commit()
    db.close()

    return {"message": "Profile created"}


@router.post("/set-password/")
def set_password(data: dict):
    db = SessionLocal()

    user = db.query(User).first()
    if not user:
        db.close()
        return {"error": "User not found"}

    user.password = hash_password(data["password"])

    db.commit()
    db.close()

    return {"message": "Password set"}


@router.post("/unlock/")
def unlock(data: dict):
    db = SessionLocal()

    user = db.query(User).first()
    db.close()

    if not user or not user.password:
        return {"error": "No password set"}

    if not verify_password(data["password"], user.password):
        return {"error": "Wrong password"}

    return {"message": "Access granted"}


@router.get("/get-profile/")
def get_profile():
    db = SessionLocal()

    user = db.query(User).first()
    db.close()

    if not user:
        return {"error": "No user"}

    return {
        "name": user.name,
        "dob": user.dob,
        "phone": user.phone,
        "email": user.email,
        "location_permission": user.location_permission,
    }


@router.put("/update-profile/")
def update_profile(data: dict):
    db = SessionLocal()

    user = db.query(User).first()
    if not user:
        db.close()
        return {"error": "No user"}

    user.name = data.get("name", user.name)
    user.dob = data.get("dob", user.dob)
    user.phone = data.get("phone", user.phone)
    user.email = data.get("email", user.email)
    user.location_permission = data.get("location_permission", user.location_permission)

    db.commit()
    db.close()

    return {"message": "Profile updated"}
