"""
Migration: Create cart and cart_items tables
Version: 004
Description: Cart (user_id, total, status) and CartItems (cart_id, product_id, quantity)
"""

import sqlite3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import DATABASE_PATH


def upgrade():
    """Apply the migration."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS _migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("SELECT 1 FROM _migrations WHERE name = ?", ("004_create_cart_tables",))
    if cursor.fetchone():
        print("Migration 004_create_cart_tables already applied. Skipping.")
        conn.close()
        return

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            total REAL NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'active',
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cart_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cart_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (cart_id) REFERENCES cart(id),
            FOREIGN KEY (product_id) REFERENCES products(id),
            UNIQUE(cart_id, product_id)
        )
    """)

    cursor.execute("INSERT INTO _migrations (name) VALUES (?)", ("004_create_cart_tables",))

    conn.commit()
    conn.close()
    print("Migration 004_create_cart_tables applied successfully.")


def downgrade():
    """Revert the migration."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS cart_items")
    cursor.execute("DROP TABLE IF EXISTS cart")
    cursor.execute("DELETE FROM _migrations WHERE name = ?", ("004_create_cart_tables",))

    conn.commit()
    conn.close()
    print("Migration 004_create_cart_tables reverted successfully.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run database migration")
    parser.add_argument(
        "action",
        choices=["upgrade", "downgrade"],
        help="Migration action to perform"
    )
    args = parser.parse_args()

    if args.action == "upgrade":
        upgrade()
    elif args.action == "downgrade":
        downgrade()
