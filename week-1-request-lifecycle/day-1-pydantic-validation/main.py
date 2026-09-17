from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Product Catalog API", version="1.0")

# The "Why": Pydantic models act as automated bouncers, ensuring data integrity 
# before it ever hits business logic or a database.
class ProductCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length = 5, description="Product name")
    price: float = Field(..., gt=0, description="Price must be a positive float")
    description: str | None = Field(default=None, description="Optional product details")
    stock_quantity: int = Field(..., ge=0)
    is_active: bool | None = Field(default=True)

@app.post("/products", status_code=201)
def create_product(product: ProductCreate):
    return {
        "status": "success",
        "message": "Product passed automated Pydantic validation successfully!",
        "data": product
    }