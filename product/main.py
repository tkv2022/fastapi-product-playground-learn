from fastapi import FastAPI
# FastAPI: main application class that creates the ASGI app and exposes routing/docs features.

from .database import engine
# engine: SQLAlchemy Engine instance configured in product/database.py used to connect to the DB.
# Importing the engine here lets us call metadata.create_all(...) below to ensure tables exist.

from .routers import product, seller, login
# Import router modules so we can include them on the FastAPI app.
# Each module should expose an APIRouter instance named `router`.
# Using a package-relative import (leading dot) keeps this package portable.

from . import models
# Import models module to register SQLAlchemy model classes with the Base metadata.
# models.Base (declarative base) holds the Table metadata for all defined models.

# Ensure database tables exist by creating any missing tables defined in models.Base.
# This runs synchronously at app import time; for production you might run migrations instead.
models.Base.metadata.create_all(bind=engine)


# Create the FastAPI application instance with optional metadata used by the docs.
# Title/description/terms_of_service/contact/license_info are shown in the OpenAPI docs.
app = FastAPI(
    title="Products Api",
    description="Get details for all the products on the website",
    terms_of_service='http://www.google.com',
    contact={
        'name': 'Thomas K Varghese',
        'website': 'http://www.google.com',
        'email': 'thomas.varghese@example.com'
    },
    license_info={
        'name': 'MIT',
        'url': 'http://www.google.com'
    },
    # You can customize docs URLs. For example:
    # docs_url='/documentation',      # move Swagger UI to /documentation
    # redoc_url=None                 # disable ReDoc if you don't want it
)


# Mount routers (APIRouter instances) onto the main app.
# Each router typically defines a group of endpoints and their own prefix/tags.
# Including routers keeps routes modular and easier to maintain.
app.include_router(product.router)
app.include_router(seller.router)
app.include_router(login.router)

# Notes / recommendations:
# - Running create_all at import-time is OK for development and learning, but use migrations
#   (Alembic) in production to manage schema changes safely.
# - Keep secrets/config (DB URL, credentials) outside source code (e.g., environment variables).
# - When adding new routers, import them above and call app.include_router(new.router).
# - The `app` object in this file is what Uvicorn/ASGI