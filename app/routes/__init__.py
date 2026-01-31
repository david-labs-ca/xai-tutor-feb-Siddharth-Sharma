from app.routes.health import router as health_router
from app.routes.items import router as items_router
from app.routes.auth import router as auth_router
from app.routes.products import router as products_router
from app.routes.cart import router as cart_router

__all__ = ["health_router", "items_router", "auth_router", "products_router", "cart_router"]
