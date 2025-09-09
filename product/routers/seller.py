from fastapi import APIRouter
# APIRouter: groups related endpoints so they can be mounted on the main FastAPI app.

from sqlalchemy.orm import Session
# Session: SQLAlchemy ORM session type; used for DB access injected via dependency.

from .. import models, schemas
# models: SQLAlchemy models (database tables).
# schemas: Pydantic request/response schemas.
# NOTE: keep the space: `from .. import ...` — otherwise Python raises a SyntaxError.

from passlib.context import CryptContext
# CryptContext: helper from passlib to hash and verify passwords using configured schemes.

from fastapi.params import Depends
# Depends: FastAPI dependency injection helper (e.g., for DB session).

from ..database import get_db
# get_db: dependency that yields a DB session (defined in product/database.py).

# Create a router scoped to seller-related endpoints
router = APIRouter(tags=["Seller"])

# Configure password hashing: use bcrypt and allow auto-handling of deprecated schemes.
# - schemes=["bcrypt"] chooses bcrypt
# - deprecated="auto" keeps compatibility and policy handling
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post('/seller', response_model=schemas.DisplaySeller)
def create_seller(request: schemas.Seller, db: Session = Depends(get_db)):
    """
    Create a new seller (user).
    - request: Pydantic model `schemas.Seller` parsed from request body (contains username, email, password).
    - db: SQLAlchemy Session injected by get_db dependency.
    Steps:
    1. Hash the plaintext password using pwd_context.hash(...) before storing.
       This ensures the DB never stores plaintext passwords.
    2. Create a new models.Seller instance with the hashed password.
    3. Add, commit, refresh to persist and populate generated fields (e.g., id).
    4. Return the created seller instance which will be serialized using the response_model.
    Security / privacy:
    - response_model=schemas.DisplaySeller should NOT include the password field so the API response omits it.
    - Never return or log plaintext passwords.
    """
    # Hash the incoming plaintext password
    hashedpassword = pwd_context.hash(request.password)

    # Create the SQLAlchemy model with hashed password
    new_seller = models.Seller(
        username=request.username,
        email=request.email,
        password=hashedpassword
    )

    # Persist to DB
    db.add(new_seller)
    db.commit()
    db.refresh(new_seller)

    # Return the created DB object; response_model controls which fields are sent back
    return new_seller