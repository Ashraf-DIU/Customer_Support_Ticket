import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import Base, engine
from .routers import analytics, demo, health, predict, tickets
from .services.prediction import predictor

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    predictor.load()
    yield


app = FastAPI(title="SupportIQ AI API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.frontend_urls),
    allow_origin_regex=r"https://.*\.vercel\.app" if settings.allow_vercel_previews else None,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)

for r in (health.router, predict.router, tickets.router, analytics.router, demo.router):
    app.include_router(r)


@app.get("/")
def root():
    return {"name": "SupportIQ AI API", "docs": "/docs", "health": "/api/health"}
