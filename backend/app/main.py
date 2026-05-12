from datetime import datetime, timedelta, timezone
import os
import secrets

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel

app = FastAPI(title="JWT FastAPI Example")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 300
SECRET_KEY = os.getenv("SECRET_KEY")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable is required")

security = HTTPBearer()


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


def create_access_token(username: str) -> str:
    """Create a signed JWT access token for the given username."""
    expire = datetime.now(timezone.utc) + timedelta(seconds=ACCESS_TOKEN_EXPIRE_SECONDS)
    payload = {"sub": username, "exp": expire, "type": "access"}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def validate_token(token: str) -> str:
    """Validate JWT token and return the authorized username."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        token_type = payload.get("type")
        if not username or token_type != "access":
            raise credentials_exception
        return username
    except JWTError as exc:
        raise credentials_exception from exc


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/token", response_model=TokenResponse)
def login(data: LoginRequest) -> TokenResponse:
    valid_username = secrets.compare_digest(data.username, ADMIN_USERNAME)
    valid_password = secrets.compare_digest(data.password, ADMIN_PASSWORD)
    if not valid_username or not valid_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    token = create_access_token(data.username)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_SECONDS,
    )


@app.post("/refresh", response_model=TokenResponse)
def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> TokenResponse:
    username = validate_token(credentials.credentials)
    if not secrets.compare_digest(username, ADMIN_USERNAME):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    token = create_access_token(username)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_SECONDS,
    )
