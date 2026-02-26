from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import HTTPException, status

SECRET_KEY="travellosecret"
ALGORITHM="HS256"

def create_token (data : dict) : 
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=2)
    to_encode.update({"exp" : expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token (token : str) : 
    try : 
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        return payload
    except JWTError :
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expires token"
        )
