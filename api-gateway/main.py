from datetime import date, datetime
from typing import Optional, Dict, Any
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, validator
from starlette.responses import JSONResponse
import httpx
import uuid

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


async def validate_token(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{USER_SERVICE_URL}/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    return response.json()

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
    
    if response.status_code != 200:
        content = response.json()
        raise HTTPException(
            status_code=response.status_code,
            detail=content.get("detail", "Authentication failed")
        )
        
    return JSONResponse(content=response.json(), status_code=response.status_code)

@app.get("/api/v1/me")
async def get_profile(user_data: Dict[str, Any] = Depends(validate_token)):
    return user_data

class UserUpdateRequest(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    birth_date: Optional[str] = None
    password: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
        if v is not None and len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v
    
    @validator('birth_date')
    def validate_birth_date(cls, v):
        if v is not None:
            try:
                datetime.fromisoformat(v)
            except ValueError:
                raise ValueError("Invalid date format. Use YYYY-MM-DD")
        return v

@app.put("/api/v1/me")
async def update_profile(
    user_update: UserUpdateRequest,
    token: str = Depends(oauth2_scheme)
):
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{USER_SERVICE_URL}/me",
            headers={"Authorization": f"Bearer {token}"},
            json=user_update.dict(exclude_unset=True)
        )
        
    if response.status_code != 200:
        content = response.json()
        raise HTTPException(
            status_code=response.status_code,
            detail=content.get("detail", "Failed to update profile")
        )
        
    return response.json()
