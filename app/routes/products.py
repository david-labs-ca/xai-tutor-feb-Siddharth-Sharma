"""
Products API (read-only). List available products with prices.
"""

from fastapi import APIRouter, HTTPException

from app.database import get_db
from pydantic import BaseModel

router = APIRouter(prefix="/products", tags=["products"])


class ProductResponse(BaseModel):
    id: int
    name: str
    price: float


@router.get("", response_model=list[ProductResponse])
def list_products():
    """
    List all available products with id, name, and price.
    Read-only; products are seeded via migrations.
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, price FROM products ORDER BY id")
            rows = cursor.fetchall()
            return [
                {"id": row["id"], "name": row["name"], "price": row["price"]}
                for row in rows
            ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
