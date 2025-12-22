from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import health
from app.routers.auth import auth_router
from app.routers.admin_auth import admin_auth_router
from app.routers import counselors
from app.routers import voice
from app.routers import sessions
from app.routers import video

settings = get_settings()

app = FastAPI(
    title='College Counseling Platform API',
    description='Backend API for AI-powered college counseling',
    version='1.0.0',
    docs_url='/docs',
    redoc_url='/redoc'
)

# CORS Configuration - origins from settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(','),
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Register routers
app.include_router(health.router)
app.include_router(auth_router)
app.include_router(admin_auth_router)
app.include_router(counselors.router, prefix='/api/v1')
app.include_router(voice.router, prefix='/api/v1')
app.include_router(sessions.router, prefix='/api/v1')
app.include_router(video.router, prefix='/api/v1')

@app.get('/')
async def root() -> dict[str, str]:
    return {'message': 'College Counseling Platform API', 'version': '1.0.0'}
