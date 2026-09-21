from typing import Optional
from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.product import ProductModel
from app.schemas.product import ProductCreate

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

@router.get("/", status_code=200)
def get_products(
    search: Optional[str] = Query(None, description="Filter products by title"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    db: Session = Depends(get_db)  # <--- Injected DB Session per request!
):
    """
    REST Endpoint: GET /products
    Fetches all products from the SQLite database with optional query filtering.
    """
    # 1. Start with a base query targeting the ProductModel table
    query = db.query(ProductModel)

    # 2. Apply filters dynamically on the database level
    if search:
        query = query.filter(ProductModel.title.ilike(f"%{search}%"))
    if min_price is not None:
        query = query.filter(ProductModel.price >= min_price)

    # 3. Execute the query and fetch all matching records from SQLite
    products = query.all()

    return {
        "status": "success",
        "count": len(products),
        "data": products
    }

@router.get("/{product_id}", status_code=200)
def get_single_product(product_id: int, db: Session = Depends(get_db)):
    """
    REST Endpoint: GET /products/{product_id}
    Fetches a single unique product from the database by its primary key.
    """
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    return {"status": "success", "data": product}

@router.post("/", status_code=201)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """
    REST Endpoint: POST /products
    Saves a new product directly into the SQLite database file permanently.
    """
    # 1. Instantiate our SQLAlchemy model using data validated by Pydantic
    new_product = ProductModel(
        title=product.title,
        price=product.price,
        stock_quantity=product.stock_quantity
    )

    # 2. Add the object to the current database session workspace
    db.add(new_product)
    
    # 3. Commit the transaction to permanently write it to 'sql_app.db'
    db.commit()
    
    # 4. Refresh the instance so we grab its newly generated primary key (id) and defaults
    db.refresh(new_product)

    return {
        "status": "success",
        "message": "Product saved permanently to the database!",
        "data": new_product
    }

@router.delete('/{product_id}')
def delete_product(product_id: int, db: Session = Depends(get_db)):

 product =  db.query(ProductModel).filter(ProductModel.id == product_id).first()

 if not product:
     raise HTTPException(status_code=404, detail='Product Not Found')

 db.delete(product)
 db.commit() 
 return {"status": 202 , "message":"Product Has Been Removed Successfully"}
 

 
