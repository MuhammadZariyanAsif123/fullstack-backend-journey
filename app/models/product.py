from sqlalchemy import Column, Integer, String, Float
from app.database import Base

class ProductModel(Base):
    # WHY: Explicitly name the table in the database
    __tablename__ = "products"

    # WHY: Define columns with precise SQL data types and constraints
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, index=True, nullable=False)
    price = Column(Float, nullable=False)
    stock_quantity = Column(Integer, default=0)
