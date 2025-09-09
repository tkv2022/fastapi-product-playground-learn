from fastapi import APIRouter, status, Response, HTTPException
# APIRouter: create a modular set of routes; status/HTTPException used for HTTP responses and errors
from sqlalchemy.orm import Session
# Session: SQLAlchemy ORM session type for DB access
from fastapi.params import Depends
# Depends: inject dependencies (DB session, OAuth form, token extraction)
from ..database import get_db
# get_db: dependency that yields a DB session (defined in product/database.py)
from .. import models, schemas
# models: SQLAlchemy models; schemas: Pydantic request/response schemas
from passlib.context import CryptContext
# CryptContext: helper to hash & verify passwords (we configure bcrypt below)
from datetime import datetime, timedelta
# datetime, timedelta: create expiry timestamps for tokens
from jose import JWTError, jwt
# jose.jwt: encode/decode JWTs; JWTError used to catch verification failures
from fastapi.security import OAuth2PasswordBearer
# OAuth2PasswordBearer: extracts bearer token from Authorization header (dependency)
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
# OAuth2PasswordRequestForm: dependency to parse form fields 'username' and 'password'

# Secret and algorithm configuration for JWT
# NOTE: In production keep SECRET_KEY in environment variables or a secrets manager.
SECRET_KEY = "1d3cfb274f62bb76681c38d656fb62af977db37922b7d2740dd817a8fb33550b"
# ALGORYTHM is spelled inconsistently but used consistently below; consider renaming to ALGORITHM.
ALGORYTHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 20
# Token expiration time in minutes

# Router setup: prefix all endpoints with /login and tag them for docs
router = APIRouter(tags=["Login"], prefix="/login")

# Password hashing context: configure which hashing schemes to use and policy
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# - schemes=["bcrypt"]: use bcrypt algorithm
# - deprecated="auto": allow automatic handling of deprecated schemes

# OAuth2 scheme helper: used by dependencies to read the Bearer token
# tokenUrl is the endpoint where clients obtain a token (relative to API root)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def generate_token(data: dict) -> str:
    """
    Create a JWT token containing `data` as payload and an expiry claim.
    - Copies the input dict to avoid mutating the caller's object.
    - Adds an "exp" (expiry) claim set to now + ACCESS_TOKEN_EXPIRE_MINUTES.
    - Encodes with jose.jwt using SECRET_KEY and ALGORYTHM.
    Returns the encoded JWT string.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # 'exp' claim must be a UTC timestamp; jose accepts datetime objects and converts them.
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORYTHM)
    return encoded_jwt

@router.post('')
def login(
    request: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Login endpoint.
    - Uses OAuth2PasswordRequestForm dependency to read 'username' and 'password' from form data.
      (This matches the standard OAuth2 password grant form data.)
    - Fetches the seller/user by username from the DB.
    - Verifies the provided password against the hashed password using pwd_context.verify().
    - On success, generates and returns a JWT access token.
    """
    # OAuth2PasswordRequestForm exposes .username and .password attributes
    seller = db.query(models.Seller).filter(models.Seller.username == request.username).first()
    if not seller:
        # 404 here means authentication failed (you may prefer 401 for auth failures)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found/Invalid User",
        )
    # Verify the plaintext password against the stored hashed password
    if not pwd_context.verify(request.password, seller.password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid Password",
        )
    # Generate JWT token with subject set to the seller's username
    access_token = generate_token(data={"sub": seller.username})
    return {"access_token": access_token, "token_type": "bearer"}

def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Dependency that:
    - Extracts the token from the Authorization: Bearer <token> header (via oauth2_scheme).
    - Decodes and verifies the token using jose.jwt and the SECRET_KEY/ALGORYTHM.
    - Extracts the 'sub' claim (username) and wraps it in a TokenData schema.
    - Raises a 401 HTTPException on any validation problem.
    - Returns a TokenData instance (or you can change to return the actual user model).
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode validates the signature and the 'exp' claim automatically
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORYTHM])
        username: str = payload.get("sub")
        if username is None:
            # Missing subject claim → invalid token
            raise credentials_exception
        # Create a Pydantic TokenData object (defined in product/schemas.py)
        token_data = schemas.TokenData(username=username)
    except JWTError:
        # Any JWT-related error (signature, expiry, malformed) -> unauthorized
        raise credentials_exception
    # Return the token_data so route handlers can receive it via dependency injection
    return token_data