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
    version="1.0.0",
    swagger_ui_oauth2_redirect_url="/oauth2-redirect",
    swagger_ui_init_oauth={
        "clientId": "gateway-client",
        "usePkceWithAuthorizationCodeGrant": True
    },
    components={
        "securitySchemes": {
            "oauth2": {
                "type": "oauth2",
                "flows": {
                    "password": {
                        "tokenUrl": "/api/v1/token",
                        "scopes": {}
                    }
                }
            }
        }
    }
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token")
USER_SERVICE_URL = "http://user-service:8000"

# Request schemas mirroring user service
class UserRegisterRequest(BaseModel):
    login: str
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    birth_date: Optional[str] = None

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


async def validate_token(token: str = Depends(oauth2_scheme)) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{USER_SERVICE_URL}/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    return token

@app.post("/api/v1/register")
async def register(user: UserRegisterRequest):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{USER_SERVICE_URL}/register",
            json=user.dict()
        )
    content = response.json()
    content["token_type"] = "Bearer"  # Ensure proper case for Swagger
    return JSONResponse(content=content, status_code=response.status_code)

@app.post("/api/v1/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{USER_SERVICE_URL}/token",
            data={
                "username": form_data.username,
                "password": form_data.password,
                "grant_type": "password"
            }
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
