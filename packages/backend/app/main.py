from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings

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

@app.get('/')
async def root() -> dict[str, str]:
    return {'message': 'College Counseling Platform API', 'version': '1.0.0'}

@app.get('/health')
async def health() -> dict[str, str]:
    return {'status': 'healthy'}
