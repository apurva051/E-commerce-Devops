import os
from contextlib import contextmanager
from datetime import datetime, timezone
import psycopg2
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://ecommerce:ecommerce@localhost:5432/orders")
app = FastAPI(title="Order Service", version="1.0.0")

@contextmanager
def connection():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def initialize():
    with connection() as conn, conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                username VARCHAR(40) NOT NULL,
                product_id VARCHAR(50) NOT NULL,
                product_name VARCHAR(100) NOT NULL,
                quantity INTEGER NOT NULL CHECK (quantity > 0),
                total NUMERIC(10, 2) NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'PLACED',
                created_at TIMESTAMPTZ NOT NULL
            )
        """)

class OrderInput(BaseModel):
    username: str = Field(min_length=3, max_length=40)
    product_id: str
    product_name: str
    quantity: int = Field(gt=0)
    total: float = Field(gt=0)

@app.on_event("startup")
def startup():
    initialize()

@app.get("/health")
def health():
    with connection() as conn, conn.cursor() as cursor:
        cursor.execute("SELECT 1")
    return {"status": "healthy", "service": "order-service"}

@app.post("/orders", status_code=201)
def create_order(payload: OrderInput):
    created_at = datetime.now(timezone.utc)
    with connection() as conn, conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO orders (username, product_id, product_name, quantity, total, created_at) VALUES (%s,%s,%s,%s,%s,%s) RETURNING id",
            (payload.username.lower(), payload.product_id, payload.product_name, payload.quantity, payload.total, created_at),
        )
        order_id = cursor.fetchone()[0]
    return {"id": order_id, **payload.model_dump(), "status": "PLACED", "created_at": created_at}

@app.get("/orders/{username}")
def list_orders(username: str):
    with connection() as conn, conn.cursor() as cursor:
        cursor.execute("SELECT id, product_id, product_name, quantity, total, status, created_at FROM orders WHERE username=%s ORDER BY id DESC", (username.lower(),))
        rows = cursor.fetchall()
    return [{"id": row[0], "product_id": row[1], "product_name": row[2], "quantity": row[3], "total": float(row[4]), "status": row[5], "created_at": row[6]} for row in rows]

@app.get("/orders/id/{order_id}")
def get_order(order_id: int):
    with connection() as conn, conn.cursor() as cursor:
        cursor.execute("SELECT id, username, product_id, product_name, quantity, total, status, created_at FROM orders WHERE id=%s", (order_id,))
        row = cursor.fetchone()
    if not row:
        raise HTTPException(404, "Order not found")
    return {"id": row[0], "username": row[1], "product_id": row[2], "product_name": row[3], "quantity": row[4], "total": float(row[5]), "status": row[6], "created_at": row[7]}

