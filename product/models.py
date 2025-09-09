# Importing necessary modules from SQLAlchemy
# Column: Used to define a column in the database table
# Integer, String, Float: Data types for the columns
from sqlalchemy import Column, Integer, String, Float, ForeignKey

# Importing the Base class from the database module
# Base is the declarative base class that maintains a catalog of classes and tables
from .database import Base

from sqlalchemy.orm import relationship

# Defining the Product class, which represents a table in the database
# This class inherits from the Base class provided by SQLAlchemy
class Product(Base):
    # Setting the name of the database table to 'products'
    __tablename__ = 'products'

    # Defining the columns of the table
    # id: Primary key column, unique identifier for each record, indexed for faster lookups
    id = Column(Integer, primary_key=True, index=True)

    # name: Column to store the name of the product, uses String data type
    name = Column(String)

    # description: Column to store a description of the product, uses String data type
    description = Column(String)

    # price: Column to store the price of the product, uses Integer data type
    price = Column(Integer)

    seller_id = Column(Integer, ForeignKey("sellers.id"))

    seller=relationship("Seller",back_populates="products")

class Seller(Base):
    __tablename__="sellers"
    id=Column(Integer,primary_key=True,index=True)
    username=Column(String)
    email=Column(String)
    password=Column(String)
    products =relationship('Product',back_populates='seller')