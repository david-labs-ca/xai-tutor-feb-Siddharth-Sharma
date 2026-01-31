"""
Migration: Create products table
Version: 003
Description: Creates products table (id, name, price) and seeds sample data
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

    cursor.execute("SELECT 1 FROM _migrations WHERE name = ?", ("003_create_products_table",))
    if cursor.fetchone():
        print("Migration 003_create_products_table already applied. Skipping.")
        conn.close()
        return

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL
        )
    """)

    sample_products = [
        ("Laptop", 999.99),
        ("Wireless Mouse", 29.99),
        ("Keyboard", 79.99),
        ("Monitor", 249.99),
        ("USB-C Hub", 49.99),
        ("Headphones", 89.99),
        ("Webcam", 59.99),
        ("Desk Lamp", 34.99),
    ]
    cursor.executemany(
        "INSERT INTO products (name, price) VALUES (?, ?)",
        sample_products,
    )

    cursor.execute("INSERT INTO _migrations (name) VALUES (?)", ("003_create_products_table",))

    conn.commit()
    conn.close()
    print("Migration 003_create_products_table applied successfully.")


def downgrade():
    """Revert the migration."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS products")
    cursor.execute("DELETE FROM _migrations WHERE name = ?", ("003_create_products_table",))

    conn.commit()
    conn.close()
    print("Migration 003_create_products_table reverted successfully.")


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
