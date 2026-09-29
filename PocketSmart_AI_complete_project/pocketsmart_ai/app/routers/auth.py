from fastapi import APIRouter, Depends, HTTPException, Request, Response
from app.database import db
from app.schemas import RegisterRequest, LoginRequest
from app.security import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register")
def register(data: RegisterRequest):
    email = data.email.strip().lower()
    with db() as conn:
        if conn.execute("SELECT 1 FROM users WHERE email=?", (email,)).fetchone():
            raise HTTPException(409, "An account with that email already exists")
        cur = conn.execute("INSERT INTO users(email,password_hash) VALUES(?,?)", (email, hash_password(data.password)))
        user_id = cur.lastrowid
    return {"message":"Registration successful", "user_id":user_id}

@router.post("/login")
def login(data: LoginRequest, response: Response):
    email = data.email.strip().lower()
    with db() as conn:
        row = conn.execute("SELECT id,email,password_hash FROM users WHERE email=?", (email,)).fetchone()
    if not row or not verify_password(data.password, row["password_hash"]):
        raise HTTPException(401, "Invalid email or password")
    token = create_access_token(row["id"])
    response.set_cookie("access_token", token, httponly=True, samesite="lax", secure=False, max_age=86400)
    return {"message":"Login successful", "email":row["email"]}

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message":"Logged out"}

@router.get("/me")
def me(user=Depends(get_current_user)):
    return {"id":user.id, "email":user.email}
