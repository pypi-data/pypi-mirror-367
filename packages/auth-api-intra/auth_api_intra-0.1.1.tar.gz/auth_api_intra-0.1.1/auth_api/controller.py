from fastapi import APIRouter, HTTPException
from .models import LoginRequest, Token
from .service import AuthService

router = APIRouter()
auth_service = AuthService()

@router.post("/login", response_model=Token)
def login(data: LoginRequest):
    if not auth_service.verify_user(data.username, data.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = auth_service.create_jwt(data.username)
    return {"access_token": token, "token_type": "bearer"}
