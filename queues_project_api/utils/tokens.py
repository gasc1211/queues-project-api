import logging
import os
import jwt
import pytz

from functools import wraps
from dotenv import load_dotenv
from fastapi import HTTPException
from datetime import datetime, timedelta
from jwt import PyJWTError

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
FUNCTION_SECRET_KEY = os.getenv("FUNCTIONAPP_SECRET_KEY")

# Configure console logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to create a new JWT Token
def create_jwt_token(created_at: datetime, first_name:str, last_name:str, email: str, is_verified: bool):
    expiration = datetime.now(pytz.timezone('UTC')) + timedelta(hours=1)  # Set expiration datetime to 1hr
    token = jwt.encode(
        {
            "created_at": created_at,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "is_verified": is_verified,
            "expires": expiration.isoformat(),
            "issued_at": datetime.now(pytz.timezone('UTC')).isoformat()
        },
        SECRET_KEY,
        algorithm="HS256"
    )
    return token

# Decorator to validate a JWT Token
def validate(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request = kwargs.get('request')
        if not request:
            raise HTTPException(status_code=400, detail="Request object not found")

        authorization_header: str = request.headers.get("Authorization")
        if not authorization_header:
            raise HTTPException(status_code=400, detail="Authorization header missing")

        scheme, token = authorization_header.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=400, detail="Invalid authentication scheme")

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

            created_at = payload.get("created_at")
            email = payload.get("email")
            expires = payload.get("expires")
            is_verified = payload.get("is_verified")
            first_name = payload.get("first_name")
            last_name = payload.get("last_name")

            if email is None or expires is None or is_verified is None:
                raise HTTPException(status_code=400, detail="Invalid token")

            if datetime.fromisoformat(expires).replace(tzinfo=pytz.timezone('UTC')) < datetime.now(pytz.timezone('UTC')):
                logger.info(datetime.fromisoformat(expires).replace(tzinfo=pytz.timezone('UTC')) > datetime.now(pytz.timezone('UTC')))
                raise HTTPException(status_code=401, detail="Expired token")

            if not is_verified:
                raise HTTPException(status_code=403, detail="Not verified user")

            # Inject user data into request
            request.state.email = email
            request.state.first_name = first_name
            request.state.last_name = last_name
            request.state.created_at = created_at
            
        except PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        return await func(*args, **kwargs)
    return wrapper

# Decorator to validate an inactive accounts
def validate_for_inactive(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request = kwargs.get('request')
        if not request:
            raise HTTPException(status_code=400, detail="Request object not found")

        authorization: str = request.headers.get("Authorization")
        if not authorization:
            raise HTTPException(status_code=400, detail="Authorization header missing")

        try:
            scheme, token = authorization.split()
            if scheme.lower() != "bearer":
                raise HTTPException(status_code=400, detail="Invalid authentication scheme")

            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

            email = payload.get("email")
            issued_at = payload.get("issued_at")

            if email is None or issued_at is None:
                raise HTTPException(status_code=400, detail="Invalid token")

            if datetime.fromtimestamp(issued_at, tz=pytz.timezone('UTC')) < datetime.now(pytz.timezone('UTC')):
                raise HTTPException(status_code=401, detail="Expired token")

            # Inyectar el email en el objeto request
            request.state.email = email

        except PyJWTError:
            raise HTTPException(status_code=403, detail="Invalid or expired token")

        return await func(*args, **kwargs)
    return wrapper

# Decorator to verify authorization header
def validate_func(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request = kwargs.get('request')
        if not request:
            raise HTTPException(status_code=400, detail="Request object not found")

        authorization_header: str = request.headers.get("Authorization")
        if not authorization_header:
            raise HTTPException(status_code=403, detail="Authorization header missing")

        if authorization_header != FUNCTION_SECRET_KEY:
            raise HTTPException(status_code=403, detail="Wrong function key")

        return await func(*args, **kwargs)
    return wrapper