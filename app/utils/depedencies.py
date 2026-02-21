from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.utils.jwt_handler import verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user (token: str = Depends(oauth2_scheme)) :
    payload = verify_token(token)
    return payload

def role_required(role: str):
    async def role_checker(current_user=Depends(get_current_user)):
        if current_user["role"] != role:
            raise HTTPException(status_code=403, detail="Not allowed")
        return current_user
    return role_checker
