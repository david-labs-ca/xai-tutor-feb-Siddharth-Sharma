from fastapi import APIRouter, HTTPException

from app.database import get_db

router = APIRouter()


@router.get("/items")
def list_items():
    """
    List all items from the database.
    Uses raw SQL query (no ORM).
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM items ORDER BY id")
            rows = cursor.fetchall()
            items = [{"id": row["id"], "name": row["name"]} for row in rows]
            return {"items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
