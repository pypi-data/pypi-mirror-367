from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

class AuthService:
    def verify_user(self, username: str, password: str) -> bool:
        return username == "admin" and password == "admin123"

    def create_jwt(self, username: str) -> str:
        expire = datetime.utcnow() + timedelta(hours=1)
        to_encode = {"sub": username, "exp": expire}
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
