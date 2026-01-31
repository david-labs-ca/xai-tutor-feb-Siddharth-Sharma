"""
Cart API (JWT-protected). Add items, view cart, update/remove items, checkout.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.auth import get_current_user_id
from app.database import get_db

router = APIRouter(prefix="/cart", tags=["cart"])


class AddItemRequest(BaseModel):
    product_id: int
    quantity: int


class UpdateItemRequest(BaseModel):
    quantity: int


def _get_or_create_active_cart(conn, user_id: int) -> int:
    """Return active cart id for user; create one if none exists."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM cart WHERE user_id = ? AND status = 'active' LIMIT 1",
        (user_id,),
    )
    row = cursor.fetchone()
    if row:
        return row["id"]
    cursor.execute(
        "INSERT INTO cart (user_id, total, status) VALUES (?, 0, 'active')",
        (user_id,),
    )
    return cursor.lastrowid


def _recalc_cart_total(conn, cart_id: int) -> None:
    """Update cart.total from sum of (product price * quantity) for all items."""
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE cart SET total = (
            SELECT COALESCE(SUM(p.price * ci.quantity), 0)
            FROM cart_items ci
            JOIN products p ON p.id = ci.product_id
            WHERE ci.cart_id = ?
        ) WHERE id = ?
        """,
        (cart_id, cart_id),
    )


def _ensure_cart_owned_by_user(conn, cart_id: int, user_id: int) -> None:
    """Raise 404 if cart does not exist or does not belong to user."""
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM cart WHERE id = ? AND user_id = ?", (cart_id, user_id))
    if cursor.fetchone() is None:
        raise HTTPException(status_code=404, detail="Cart not found")


def _ensure_item_in_user_cart(conn, item_id: int, user_id: int) -> tuple[int, int]:
    """Raise 404 if item not found or not in user's active cart. Returns (cart_id, product_id)."""
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT ci.cart_id, ci.product_id FROM cart_items ci
        JOIN cart c ON c.id = ci.cart_id
        WHERE ci.id = ? AND c.user_id = ? AND c.status = 'active'
        """,
        (item_id, user_id),
    )
    row = cursor.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return row["cart_id"], row["product_id"]


@router.post("/items", status_code=status.HTTP_201_CREATED)
def add_cart_item(
    body: AddItemRequest,
    user_id: int = Depends(get_current_user_id),
):
    """Add item to cart (product_id, quantity). Creates active cart if needed."""
    if body.quantity < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity must be at least 1",
        )
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, price FROM products WHERE id = ?", (body.product_id,))
        product = cursor.fetchone()
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")

        cart_id = _get_or_create_active_cart(conn, user_id)

        cursor.execute(
            "SELECT id, quantity FROM cart_items WHERE cart_id = ? AND product_id = ?",
            (cart_id, body.product_id),
        )
        existing = cursor.fetchone()
        if existing:
            new_qty = existing["quantity"] + body.quantity
            cursor.execute(
                "UPDATE cart_items SET quantity = ? WHERE id = ?",
                (new_qty, existing["id"]),
            )
            item_id = existing["id"]
        else:
            cursor.execute(
                "INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (?, ?, ?)",
                (cart_id, body.product_id, body.quantity),
            )
            item_id = cursor.lastrowid

        _recalc_cart_total(conn, cart_id)

    return {"id": item_id, "product_id": body.product_id, "quantity": body.quantity if not existing else new_qty}


@router.get("")
def get_cart(user_id: int = Depends(get_current_user_id)):
    """View current cart details and total."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, total, status FROM cart WHERE user_id = ? AND status = 'active' LIMIT 1",
            (user_id,),
        )
        cart_row = cursor.fetchone()
        if cart_row is None:
            return {"items": [], "total": 0.0, "status": "active"}

        cart_id = cart_row["id"]
        cursor.execute(
            """
            SELECT ci.id, ci.product_id, p.name AS product_name, p.price, ci.quantity,
                   (p.price * ci.quantity) AS subtotal
            FROM cart_items ci
            JOIN products p ON p.id = ci.product_id
            WHERE ci.cart_id = ?
            ORDER BY ci.id
            """,
            (cart_id,),
        )
        rows = cursor.fetchall()
        items = [
            {
                "id": r["id"],
                "product_id": r["product_id"],
                "product_name": r["product_name"],
                "price": r["price"],
                "quantity": r["quantity"],
                "subtotal": r["subtotal"],
            }
            for r in rows
        ]
        total = float(cart_row["total"])
    return {"items": items, "total": total, "status": "active"}


@router.put("/items/{item_id}")
def update_cart_item(
    item_id: int,
    body: UpdateItemRequest,
    user_id: int = Depends(get_current_user_id),
):
    """Update quantity of a cart item."""
    if body.quantity < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity must be at least 1",
        )
    with get_db() as conn:
        _ensure_item_in_user_cart(conn, item_id, user_id)
        cursor = conn.cursor()
        cursor.execute("UPDATE cart_items SET quantity = ? WHERE id = ?", (body.quantity, item_id))
        cursor.execute("SELECT cart_id FROM cart_items WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        if row:
            _recalc_cart_total(conn, row["cart_id"])
    return {"id": item_id, "quantity": body.quantity}


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_cart_item(
    item_id: int,
    user_id: int = Depends(get_current_user_id),
):
    """Remove item from cart."""
    with get_db() as conn:
        cart_id, _ = _ensure_item_in_user_cart(conn, item_id, user_id)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cart_items WHERE id = ?", (item_id,))
        _recalc_cart_total(conn, cart_id)
    return None


@router.post("/checkout")
def checkout(user_id: int = Depends(get_current_user_id)):
    """Purchase items and clear cart (set cart status to checked_out)."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM cart WHERE user_id = ? AND status = 'active' LIMIT 1",
            (user_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return {"message": "Cart is empty", "total": 0.0}
        cart_id = row["id"]
        cursor.execute("SELECT total FROM cart WHERE id = ?", (cart_id,))
        total = cursor.fetchone()["total"]
        cursor.execute("UPDATE cart SET status = 'checked_out' WHERE id = ?", (cart_id,))
    return {"message": "Checkout successful", "total": float(total)}
