import uvicorn
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from core.database import engine
from models import Base
from auth.routes import auth_router
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from core.rate_limiter import limiter

@asynccontextmanager
async def lifespan(app:FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
app = FastAPI(title="Auth based Recipe App", lifespan=lifespan)


# Initialize the limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

 
@app.get("/api")
def Home():
    return f"Welcome to my Recipe API" 

app.include_router(auth_router, prefix="/api/auth")
