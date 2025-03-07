from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
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
async def register(request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{USER_SERVICE_URL}/register",
            content=await request.body(),
            headers=request.headers
        )
    return JSONResponse(content=response.json(), status_code=response.status_code)

@app.post("/api/v1/token")
async def login(request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{USER_SERVICE_URL}/token",
            content=await request.body(),
            headers=request.headers
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
