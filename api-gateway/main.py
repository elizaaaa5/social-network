from datetime import date
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, validator
from starlette.requests import Request
from starlette.responses import JSONResponse
import httpx

app = FastAPI(
    title="API Gateway",
    description="Routes requests to backend services",
    version="1.0.0"
)

SECURITY = HTTPBearer()
USER_SERVICE_URL = "http://user-service:8000"

# Request schemas mirroring user service
class UserRegisterRequest(BaseModel):
    login: str
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    birth_date: Optional[date] = None

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

class UserLoginRequest(BaseModel):
    username: str
    password: str

async def validate_token(request: Request) -> str:
    credentials: HTTPAuthorizationCredentials = await SECURITY(request)
    if not credentials.scheme == "Bearer":
        raise HTTPException(status_code=403, detail="Invalid authentication scheme")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{USER_SERVICE_URL}/me",
            headers={"Authorization": f"Bearer {credentials.credentials}"}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    return credentials.credentials

@app.post("/api/v1/register")
async def register(user: UserRegisterRequest):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{USER_SERVICE_URL}/register",
            json=user.dict()
        )
    return JSONResponse(content=response.json(), status_code=response.status_code)

@app.post("/api/v1/token")
async def login(form_data: UserLoginRequest):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{USER_SERVICE_URL}/token",
            data=form_data.dict()
        )
    return JSONResponse(content=response.json(), status_code=response.status_code)

@app.get("/api/v1/me")
async def get_profile(token: str = Depends(validate_token)):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{USER_SERVICE_URL}/me",
            headers={"Authorization": f"Bearer {token}"}
        )
    return response.json()
