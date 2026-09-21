from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import products
from app.database import engine, Base
from app.models import product

app = FastAPI(title="Product Catalog API", version="1.0")

# WHY: This commands SQLAlchemy to check for the SQLite file and create tables if they don't exist yet.
product.Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allows your Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (POST, GET, etc.)
    allow_headers=["*"],  # Allows all headers
)

app.include_router(products.router)

@app.get("/")
def root():
    return {"message": "Welcome to the Fullstack Journey API!"}