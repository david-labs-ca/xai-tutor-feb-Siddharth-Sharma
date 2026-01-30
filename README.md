# Backend Exercise API

A FastAPI backend project with SQLite database using raw SQL queries (no ORM).

## Features

- FastAPI web framework
- SQLite database with raw SQL queries
- Database migrations without ORM
- Health check endpoint
- Items listing endpoint

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── database.py          # Database connection utilities
│   └── routes/
│       ├── __init__.py
│       ├── health.py        # Health check endpoint
│       └── items.py         # Items endpoint
├── migrations/              # Database migration files
│   └── 001_create_items_table.py
├── migrate.py               # Migration runner script
├── requirements.txt         # Python dependencies
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Quick Start (Docker)

The easiest way to run the application:

```bash
docker-compose up --build
```

This will:
- Build the Docker image
- Run database migrations automatically
- Start the API server at `http://localhost:8000`

To stop the application:

```bash
docker-compose down
```

## Manual Setup (Without Docker)

### 1. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run database migrations

```bash
python migrate.py upgrade
```

### 4. Start the server

```bash
uvicorn app.main:app --reload
```

Or run directly:

```bash
python -m app.main
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health Check

```
GET /health
```

Response:
```json
{"status": "healthy"}
```

### Items CRUD

#### List All Items

```
GET /items
```

Response:
```json
{
  "items": [
    {"id": 1, "name": "Apple"},
    {"id": 2, "name": "Banana"},
    {"id": 3, "name": "Cherry"}
  ]
}
```

#### Get Single Item

```
GET /items/{id}
```

Response:
```json
{"id": 1, "name": "Apple"}
```

#### Create Item

```
POST /items
Content-Type: application/json

{"name": "Orange"}
```

Response (201 Created):
```json
{"id": 4, "name": "Orange"}
```

#### Update Item

```
PUT /items/{id}
Content-Type: application/json

{"name": "Updated Name"}
```

Response:
```json
{"id": 1, "name": "Updated Name"}
```

#### Delete Item

```
DELETE /items/{id}
```

Response: 204 No Content

## Database Migrations

### Migration File Structure

Migration files are located in the `migrations/` directory and follow this naming convention:

```
{version}_{description}.py
```

Example: `001_create_items_table.py`

### Creating a New Migration

1. Create a new file in the `migrations/` directory with the next version number:

```bash
touch migrations/002_add_description_column.py
```

2. Use this template for your migration:

```python
"""
Migration: Add description column to items
Version: 002
Description: Adds a description column to the items table
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
    
    # Check if this migration has already been applied
    cursor.execute("SELECT 1 FROM _migrations WHERE name = ?", ("002_add_description_column",))
    if cursor.fetchone():
        print("Migration 002_add_description_column already applied. Skipping.")
        conn.close()
        return
    
    # Your upgrade SQL here
    cursor.execute("ALTER TABLE items ADD COLUMN description TEXT")
    
    # Record this migration
    cursor.execute("INSERT INTO _migrations (name) VALUES (?)", ("002_add_description_column",))
    
    conn.commit()
    conn.close()
    print("Migration 002_add_description_column applied successfully.")


def downgrade():
    """Revert the migration."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # SQLite doesn't support DROP COLUMN directly
    # You would need to recreate the table without the column
    
    # Remove migration record
    cursor.execute("DELETE FROM _migrations WHERE name = ?", ("002_add_description_column",))
    
    conn.commit()
    conn.close()
    print("Migration 002_add_description_column reverted successfully.")


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
```

### Running Migrations

**Apply all pending migrations:**
```bash
python migrate.py upgrade
```

**Revert all migrations:**
```bash
python migrate.py downgrade
```

**List migration status:**
```bash
python migrate.py list
```

**Run a specific migration:**
```bash
python migrations/001_create_items_table.py upgrade
python migrations/001_create_items_table.py downgrade
```

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
