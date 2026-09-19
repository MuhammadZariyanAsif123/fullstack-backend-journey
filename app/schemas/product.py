from pydantic import BaseModel, Field

# The "Why": Pydantic models act as automated bouncers, ensuring data integrity 
# before it ever hits business logic or a database.
class ProductCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length = 5, description="Product name")
    price: float = Field(..., gt=0, description="Price must be a positive float")
    description: str | None = Field(default=None, description="Optional product details")
    stock_quantity: int = Field(..., ge=0)
    is_active: bool | None = Field(default=True)