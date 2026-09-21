from fastapi import APIRouter
from app.api.v1.endpoints import health, clothing, recommendations, weather, auth, preferences, outfits

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(clothing.router, prefix="/clothing", tags=["clothing"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
api_router.include_router(weather.router, prefix="/weather", tags=["weather"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(preferences.router, prefix="/preferences", tags=["preferences"])
api_router.include_router(outfits.router, prefix="/outfits", tags=["outfits"])
