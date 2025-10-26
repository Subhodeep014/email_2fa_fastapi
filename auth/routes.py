from fastapi import HTTPException, Response, Depends, APIRouter, status, Request
from datetime import timedelta, datetime, timezone
from core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from auth.jwt  import create_access_token
from sqlalchemy.future import select
from .hashing import hash_password, verify_password
from models import User 
import random
from schemas import UserCreate, UserResponse, UserSignIn, VerifyCodeInput, ResendCodeInput
from utils.email_utils import send_verification_code_email
from slowapi.util import get_remote_address
from core.rate_limiter import limiter

auth_router = APIRouter()
ACCESS_TOKEN_EXPIRE = 30

@auth_router.post("/signup")
async def signup(user:UserCreate, db:AsyncSession=Depends(get_db)):
    # 1. Check if user already exists
    result = await db.execute(select(User).where(User.email==user.email))
    user_data = result.scalars().first()
    
    if user_data:
        raise HTTPException(
            status_code= status.HTTP_409_CONFLICT,
            detail="User already exists"
        )
    
    # 2. Hash password
    hashed_password = hash_password(plain_password=user.password)

    # 3. Generate 6-digit code and expiry
    code = str(random.randint(100000, 999999))
    expiry = datetime.now(timezone.utc) + timedelta(minutes=3)


    # 4. Create new user
    new_user = User(
        email=user.email,
        name=user.name,
        hashed_password=hashed_password,
        is_verified=False,
        verification_code=code,
        code_expiry=expiry
    )

    db.add(new_user)
    await db.commit()

    # 5. Send email
    send_verification_code_email(to_email=user.email, code=code)
    
    return {"message": "User created. Verification code sent to email."}


@auth_router.post("/verify-code")
@limiter.limit("5/minute")  # allow max 5 attempts per minute
async def verify_code(request:Request,data: VerifyCodeInput, db: AsyncSession = Depends(get_db)):
    user = await db.execute(select(User).where(User.email==data.email))
    user_data = user.scalars().first()
    if not user_data or not user_data.verification_code:
        raise HTTPException(status_code=404, detail="Invalid email or code")

    if user_data.verification_code != data.code:
        raise HTTPException(status_code=400, detail="Incorrect code")

    if user_data.code_expiry and user_data.code_expiry < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Code expired")

    user_data.is_verified = True 
    user_data.verification_code = None
    user_data.code_expiry = None
    await db.commit()

    return {"msg": "Email successfully verified"}


@auth_router.post("/resend-code")
async def resend_verification_code(data: ResendCodeInput, db: AsyncSession = Depends(get_db)):
    # 1. Get user
    result = await db.execute(select(User).where(User.email == data.email))
    user_data = result.scalars().first()

    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")

    if user_data.is_verified:
        raise HTTPException(status_code=400, detail="User already verified")

    # 2. Generate and update new code
    code = str(random.randint(100000,999999))
    user_data.verification_code = code
    user_data.code_expiry = datetime.now(timezone.utc) + timedelta(minutes=3)

    await db.commit()

    # Send email
    send_verification_code_email(to_email=user_data.email, code=code)
    
    return {"msg": "Code resend succesfully"}



@auth_router.post("/signin")
async def signin(user:UserSignIn, response:Response=Response(), db:AsyncSession=Depends(get_db)):
    result = await db.execute(select(User).where(User.email==user.email))
    user_data = result.scalars().first()
    if not user_data or not verify_password(user.password, user_data.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid Credential/User not exists')
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE)
    access_token = create_access_token({"sub":user_data.email}, access_token_expires)

    response.set_cookie(
        key = "access_token",
        value=access_token,
        httponly=True
    )

    return {"message":"User Signed in Succesfully,"}

@auth_router.post("/signout")
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message":"User signed out successfully"}