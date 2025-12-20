from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title='College Counseling Platform API',
    description='Backend API for AI-powered college counseling',
    version='1.0.0',
    docs_url='/docs',
    redoc_url='/redoc'
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],  # Frontend dev server
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.get('/')
async def root():
    return {'message': 'College Counseling Platform API', 'version': '1.0.0'}

@app.get('/health')
async def health():
    return {'status': 'healthy'}
