from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.schemas.product import ProductCreate

app = FastAPI(title="Product Catalog API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allows your Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (POST, GET, etc.)
    allow_headers=["*"],  # Allows all headers
)

@app.post("/products", status_code=201)
def create_product(product: ProductCreate):
    return {
        "status": "success",
        "message": "Product passed automated Pydantic validation successfully!",
        "data": product
    }