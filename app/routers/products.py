from typing import Optional
from fastapi import Query,APIRouter
from app.schemas.product import ProductCreate

# Mock database for now (we'll replace this with SQLite/SQLAlchemy soon)
fake_products_db = [
    {"id": 1, "title": "Mechanical Keyboard", "price": 129.99, "stock_quantity": 15},
    {"id": 2, "title": "Ergonomic Mouse", "price": 59.99, "stock_quantity": 30},
    {"id": 3, "title": "Ultra-Wide Monitor", "price": 399.99, "stock_quantity": 5},
]

router = APIRouter(
    prefix="/products",  # Automatically prefixes all routes here with /products
    tags=["Products"]    # Groups them nicely in the Swagger UI docs!
)


@router.post("/", status_code=201)
def create_product(product: ProductCreate):
    return {
        "status": "success",
        "message": "Product passed automated Pydantic validation successfully!",
        "data": product
    }

@router.get("/getProducts" 
"")
def get_products(
    search: Optional[str] = Query(None, description="Filter products by title"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter")
):
    """
    WHY: Handles collection filtering dynamically.
    HOW: Uses optional query parameters with validation (ge=0 ensures no negative prices).
    """
    results = fake_products_db

    if search:
        # Case-insensitive title filtering
        results = [p for p in results if search.lower() in p["title"].lower()]

    if min_price is not None:
        results = [p for p in results if p["price"] >= min_price]

    return {
        "status": "success",
        "count": len(results),
        "data": results
    }

@router.get("/{product_id}")
def get_single_product(product_id: int):
    """
    WHY: Targets a single unique resource via its path identifier.
    HOW: Path parameter is type-hinted as an int, auto-validated by FastAPI.
    """
    for product in fake_products_db:
        if product["id"] == product_id:
            return {"status": "success", "data": product}
            
    return {"status": "error", "message": "Product not found"}, 404
