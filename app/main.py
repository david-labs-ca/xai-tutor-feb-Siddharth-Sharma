from fastapi import FastAPI

from app.routes import auth_router, health_router, items_router, products_router, cart_router

app = FastAPI(title="Backend Exercise API", version="1.0.0")

# Register routers
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(products_router)
app.include_router(cart_router)
app.include_router(items_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
