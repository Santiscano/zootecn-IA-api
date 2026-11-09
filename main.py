from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    ensure_schema()
    if ENVIRONMENT == "development":
        with SessionLocal() as db:
            seed_roles(db)
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