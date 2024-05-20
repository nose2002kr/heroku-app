from fastapi import FastAPI,         \
                    Depends,         \
                    HTTPException,   \
                    status
from fastapi.security import APIKeyHeader
from fastapi.security import HTTPBasic, HTTPBasicCredentials, HTTPBearer
import secrets
import jwt
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel
import os
from datetime import datetime, timedelta

ACCESS_TOKEN_EXPIRE_MINUTES = 30
SECRET_KEY="WHAT_TO_EAT_FOR_LUNCH"

protocol = HTTPBearer(auto_error=False, scheme_name="Bearer")

app = FastAPI()

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
settings = Settings()

api_key_header = APIKeyHeader(name="Token")
security = HTTPBasic()


async def get_current_user(token: any = Depends(protocol)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Unable to validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms="HS256")
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except Exception as e:
        raise credentials_exception
    return username

# Class to represent access token data
class Token(BaseModel):
    access_token: str
    token_type: str

# Function to generate a JWT access token
def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt

#def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
def get_current_username(username: str, password: str):
    correct_username = secrets.compare_digest(username, os.environ["ENV_USERNAME"])
    correct_password = secrets.compare_digest(password, os.environ["ENV_PASSWORD"])
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    return True


# Route for authentication and access token generation
@app.post("/api/login", response_model=Token)
#@app.post("/api/login", response_model=Token)
async def login_for_access_token(username: str, password: str, credentials = Depends(get_current_username)):
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "Bearer"}

#app.include_router(router=user_router)
