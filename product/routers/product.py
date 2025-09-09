from fastapi import APIRouter, status, Response, HTTPException
# APIRouter: groups endpoints under a common prefix/tags for the main app.
# status, Response, HTTPException: helpers for HTTP codes, custom responses and raising errors.

from sqlalchemy.orm import Session
# Session: SQLAlchemy ORM session type injected via dependency to talk to the DB.

from fastapi.params import Depends
# Depends: FastAPI dependency injection helper for DB/session/auth dependencies.

from product.routers.login import get_current_user
# Import the authentication dependency (returns token/user info).
# NOTE: this is an absolute import; ensure the package layout supports it.
# Alternative: use relative import if structure requires (from .login import get_current_user).

from ..database import get_db
# get_db: dependency that yields a DB session (defined in product/database.py).

from ..import models, schemas
# Intention: import local modules 'models' and 'schemas'.
# GOTCHA: this line is likely a typo — it should be `from .. import models, schemas`
# (space required between .. and import). If kept as-is Python will raise a SyntaxError.

from typing import List
# List: typing helper used for response_model annotation.

# Create an APIRouter instance for all product-related endpoints.
# prefix="/product" means every path here will be under /product (e.g., /product/{id}).
router = APIRouter(tags=["Products"], prefix="/product")


@router.delete('/{id}')
def delete(id: int, db: Session = Depends(get_db)):
    """
    Delete a product by id.
    - id: path parameter parsed as int.
    - db: injected SQLAlchemy Session from get_db dependency.
    Behavior:
    - Performs a filtered delete and commits.
    - Returns a simple JSON message on success.
    Edge cases:
    - Currently does not check if product existed before deletion.
    - Consider returning 404 if no rows deleted.
    """
    db.query(models.Product).filter(models.Product.id == id).delete(synchronize_session=False)
    db.commit()
    return {'product deleted'}


@router.get('s', response_model=List[schemas.DisplayProduct])
def products(current_user: schemas.Seller = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    List products.
    - response_model: List[DisplayProduct] (Pydantic schema used to shape response).
    - current_user: protected by get_current_user dependency (ensures caller is authenticated).
      The type annotation `schemas.Seller` here means FastAPI will try to use it as
      a response/request model unless get_current_user returns that exact type.
    GOTCHA:
    - The path is written as 's' which resolves to '/product s' (missing leading '/').
      It should probably be '/s' or better '/products' or simply '/'.
    """
    products = db.query(models.Product).all()
    return products


@router.get('/{id}', response_model=schemas.DisplayProduct)
def product(id: int, response: Response, db: Session = Depends(get_db)):
    """
    Retrieve a single product by id.
    - If product not found, raises 404 HTTPException with a helpful message.
    - response param (fastapi.Response) is available if you prefer to set status codes manually.
    """
    product = db.query(models.Product).filter(models.Product.id == id).first()
    if not product:
        # Raising HTTPException lets FastAPI return a proper JSON error response and status.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'product with the id {id} is not available'
        )
    return product


@router.put('/{id}')
def update(id: int, request: schemas.Product, db: Session = Depends(get_db)):
    """
    Update a product.
    - request: Pydantic `schemas.Product` parsed from request body.
    - Finds the row, updates it with request.model_dump() (Pydantic v2).
    - Commits and returns a success message.
    Edge cases:
    - If no product exists, current code does nothing (pass). Consider raising 404.
    - Using `request.model_dump()` assumes Pydantic v2; for v1 use `request.dict()`.
    """
    product = db.query(models.Product).filter(models.Product.id == id)
    if not product.first():
        pass  # consider: raise HTTPException(status_code=404, ...)
    else:
        product.update(request.model_dump())
        db.commit()
        return {'Product successfully updated'}


@router.post('', status_code=status.HTTP_201_CREATED)
def add(request: schemas.Product, db: Session = Depends(get_db)):
    """
    Create a new product.
    - request: Pydantic `schemas.Product` parsed from JSON body.
    - Creates and commits a new SQLAlchemy `models.Product`.
    - Currently sets seller_id=1 statically — replace with the authenticated user's id.
    - Returns the request DTO; consider returning the created DB object or response_model instead.
    """
    new_product = models.Product(
        name=request.name,
        description=request.description,
        price=request.price,
        seller_id=1  # placeholder: replace with actual seller id from auth dependency
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return request