import os
from contextlib import asynccontextmanager
from bson import ObjectId
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from pymongo import MongoClient

client = MongoClient(os.getenv("MONGO_URL", "mongodb://localhost:27017"))
db = client[os.getenv("MONGO_DATABASE", "ecommerce")]
products = db.products

SAMPLE_PRODUCTS = [
    {"name": "Mechanical Keyboard", "description": "Hot-swappable keyboard", "price": 79.99, "stock": 20},
    {"name": "Wireless Mouse", "description": "Ergonomic productivity mouse", "price": 39.99, "stock": 35},
    {"name": "USB-C Hub", "description": "Seven-port USB-C hub", "price": 49.99, "stock": 15},
]

class ProductInput(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: str = ""
    price: float = Field(gt=0)
    stock: int = Field(ge=0)

def serialize(product):
    return {"id": str(product["_id"]), "name": product["name"], "description": product.get("description", ""), "price": product["price"], "stock": product["stock"]}

@asynccontextmanager
async def lifespan(_: FastAPI):
    client.admin.command("ping")
    if products.count_documents({}) == 0:
        products.insert_many(SAMPLE_PRODUCTS)
    yield
    client.close()

app = FastAPI(title="Product Service", version="1.0.0", lifespan=lifespan)

@app.get("/health")
def health():
    client.admin.command("ping")
    return {"status": "healthy", "service": "product-service"}

@app.get("/products")
def list_products():
    return [serialize(item) for item in products.find()]

@app.get("/products/{product_id}")
def get_product(product_id: str):
    if not ObjectId.is_valid(product_id):
        raise HTTPException(400, "Invalid product ID")
    product = products.find_one({"_id": ObjectId(product_id)})
    if not product:
        raise HTTPException(404, "Product not found")
    return serialize(product)

@app.post("/products", status_code=201)
def create_product(payload: ProductInput):
    result = products.insert_one(payload.model_dump())
    return serialize(products.find_one({"_id": result.inserted_id}))

@app.put("/products/{product_id}")
def update_product(product_id: str, payload: ProductInput):
    if not ObjectId.is_valid(product_id):
        raise HTTPException(400, "Invalid product ID")
    result = products.update_one({"_id": ObjectId(product_id)}, {"$set": payload.model_dump()})
    if result.matched_count == 0:
        raise HTTPException(404, "Product not found")
    return serialize(products.find_one({"_id": ObjectId(product_id)}))

