from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware 
from api.routers.database import generated_api_router
from api.responses.handlers import setup_exception_handlers

app = FastAPI(title="TAI API", version="0.1.0")

app.include_router(generated_api_router)

setup_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)