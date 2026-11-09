from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from zootecn_ia_api.api.auth.auth_router import user_router
from zootecn_ia_api.core.config import CORS_ORIGINS, ENVIRONMENT
from zootecn_ia_api.core.database import Base, SessionLocal, engine
from zootecn_ia_api.seed.seed_service import load_seeds

@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    if ENVIRONMENT == "development":
        with SessionLocal() as db:
            load_seeds(db)
    yield

app = FastAPI(
    title="Hatofi API",
    description="API for Hatofi application",
    version="0.0.1",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)




@app.get("/")
def read_root():
    return {"Hello": "World"}