import base64
import hashlib
import hmac
import json
import secrets
import time
from fastapi import HTTPException, Request, status
from app.config import settings
from app.database import db
from app.models import User

ALGORITHM = "HS256"
ITERATIONS = 310_000

def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERATIONS)
    return f"pbkdf2_sha256${ITERATIONS}${base64.urlsafe_b64encode(salt).decode()}${base64.urlsafe_b64encode(digest).decode()}"

def verify_password(password: str, encoded: str) -> bool:
    try:
        scheme, iterations, salt_b64, digest_b64 = encoded.split("$")
        if scheme != "pbkdf2_sha256":
            return False
        salt = base64.urlsafe_b64decode(salt_b64.encode())
        expected = base64.urlsafe_b64decode(digest_b64.encode())
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, int(iterations))
        return hmac.compare_digest(actual, expected)
    except Exception:
        return False

def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def _ub64(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))

def create_access_token(user_id: int) -> str:
    header = _b64(json.dumps({"alg":ALGORITHM,"typ":"JWT"}, separators=(",",":")).encode())
    payload = _b64(json.dumps({"sub":str(user_id),"exp":int(time.time()) + settings.access_token_expire_minutes*60}, separators=(",",":")).encode())
    signing = f"{header}.{payload}".encode()
    signature = _b64(hmac.new(settings.secret_key.encode(), signing, hashlib.sha256).digest())
    return f"{header}.{payload}.{signature}"

def decode_token(token: str) -> int:
    try:
        header, payload, signature = token.split(".")
        signing = f"{header}.{payload}".encode()
        expected = _b64(hmac.new(settings.secret_key.encode(), signing, hashlib.sha256).digest())
        if not hmac.compare_digest(signature, expected):
            raise ValueError
        data = json.loads(_ub64(payload))
        if int(data["exp"]) < int(time.time()):
            raise ValueError
        return int(data["sub"])
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

def get_current_user(request: Request) -> User:
    token = request.cookies.get("access_token") or request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")
    user_id = decode_token(token)
    with db() as conn:
        row = conn.execute("SELECT id, email FROM users WHERE id = ?", (user_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=401, detail="User not found")
    return User(id=row["id"], email=row["email"])
