from pydantic  import BaseModel, EmailStr, constr


class UserCreate(BaseModel):
    email:EmailStr
    name: str
    password : str

class UserResponse(BaseModel):
    id:int
    email: str

    class Config:
        from_attributes :True
    
class UserSignIn(BaseModel):
    email: str 
    password: str


class VerifyCodeInput(BaseModel):
    email: EmailStr
    code: str = constr(strict=True, min_length=6, max_length=6)

class ResendCodeInput(BaseModel):
    email: EmailStr


