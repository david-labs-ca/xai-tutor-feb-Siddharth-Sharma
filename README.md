# Shopping Cart API - Backend Assessment

**Time Limit: 90 minutes**

## Important Instructions

> **1. Fork this repo into your personal account**
> 
> **2. Do not raise Pull Request in the original repo**
> 
> **3. Application must be runnable with `docker-compose up` command**
> 
> **4. Complete as many APIs as possible within the 90-minute time limit**
> 
> **5. Prioritize working functionality - do not submit broken code that fails to run with `docker-compose up`**

### Tips
- Focus on core functionality first, then add features incrementally
- Test your application with `docker-compose up` before final submission
- A partially complete but working solution is better than a complete but broken one

---

A FastAPI backend project with SQLite database using raw SQL queries (no ORM).

## Objective

Create a backend for a simple e-commerce shopping cart where users can add items, view their cart, and checkout.

## Functional Requirements

### User Authentication
- User registration
- User login with JWT access token
- Multi-user support (each user has their own cart)

### Cart Management
- Add products to a cart
- Update quantity of products
- Remove products
- Calculate total price

### Product Catalog (Read-only)
- List available products with prices
- Products table should be seeded with sample data on application startup

## Required APIs

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/register` | Register a new user |
| `POST` | `/auth/login` | Login and receive JWT access token |

### Products
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/products` | List available products |

### Cart (Protected - requires JWT)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/cart/items` | Add item to cart (payload: `product_id`, `quantity`) |
| `GET` | `/cart` | View current cart details and total |
| `PUT` | `/cart/items/{itemId}` | Update quantity |
| `DELETE` | `/cart/items/{itemId}` | Remove item |
| `POST` | `/cart/checkout` | "Purchase" items and clear cart |

## Data Models

### Users
| Field | Type | Description |
|-------|------|-------------|
| `id` | INTEGER | Primary key, auto-increment |
| `email` | TEXT | Unique, user's email address |
| `password` | TEXT | Hashed password |

### Products
| Field | Type | Description |
|-------|------|-------------|
| `id` | INTEGER | Primary key, auto-increment |
| `name` | TEXT | Product name |
| `price` | REAL | Product price |

### Cart
| Field | Type | Description |
|-------|------|-------------|
| `id` | INTEGER | Primary key, auto-increment |
| `user_id` | INTEGER | Foreign key to Users |
| `total` | REAL | Total price of cart |
| `status` | TEXT | Cart status (e.g., "active", "checked_out") |

### CartItems
| Field | Type | Description |
|-------|------|-------------|
| `id` | INTEGER | Primary key, auto-increment |
| `cart_id` | INTEGER | Foreign key to Cart |
| `product_id` | INTEGER | Foreign key to Products |
| `quantity` | INTEGER | Quantity of the product |

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

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Database Migrations

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
