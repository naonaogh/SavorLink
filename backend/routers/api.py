from fastapi import APIRouter

from backend.routers.products import router as products_router
from backend.routers.cart import router as cart_router
from backend.routers.orders import router as orders_router
from backend.routers.chats import router as chats_router
from backend.routers.auth import router as auth_router
from backend.routers.users import router as users_router
from backend.routers.enterprises import router as enterprises_router


api_router = APIRouter()
api_router.include_router(products_router)
api_router.include_router(cart_router)
api_router.include_router(orders_router)
api_router.include_router(chats_router)
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(enterprises_router)

