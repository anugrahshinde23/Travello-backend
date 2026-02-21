from fastapi import APIRouter, HTTPException, Depends
from app.schemas.user_schema import UserRegister, UserLogin
from app.db.database import db
from app.utils.hash_pass import hash_pwd, verify_pwd
from app.utils.jwt_handler import create_token
from app.utils.depedencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
async def registerUser(user : UserRegister) : 
    existingUser = await db.users.find_one({
        "email" : user.email
    })

    if existingUser :
        raise HTTPException(status_code=400, detail="User already exist")
    
    hash_password = hash_pwd(user.password)

    user_dict = user.model_dump()
    user_dict["password"] = hash_password

    result = await db.users.insert_one(user_dict)

    return {
        "success" : True,
        "message" : "User Registered successfully",
        "user_id": str(result.inserted_id)
    }


@router.post("/login")  
async def loginUser(user : UserLogin) : 
    user_exist = await db.users.find_one({
        "email" : user.email
    })

    if not user_exist : 
        raise HTTPException(status_code=400, detail="Invalid Credentials")
    
    passIsCorrect = verify_pwd(user.password, user_exist["password"])

    if not passIsCorrect : 
        raise HTTPException(status_code=400, detail="Invalid Credentials")

    user_exist["_id"] = str(user_exist["_id"])

    if 'password' in user_exist : 
        del user_exist['password']
    
    token = create_token({
        "email" : user_exist["email"],
        "user_id" : user_exist["_id"],
        "role" : user_exist["role"]
        }
        )

        

    return {
        "success":True,
        "user" : user_exist,
        "message" : "User logged in successfully",
        "access_token" : token
    }

@router.get("/profile")
async def profile(current_user=Depends(get_current_user)) : 
    return {
        "message": "Protected route access ",
        "user" : current_user
    }
 