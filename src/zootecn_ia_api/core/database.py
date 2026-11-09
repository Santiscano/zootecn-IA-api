from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from zootecn_ia_api.core.config import DATABASE_URL


# CONFIGURAR MOTOR
engine = create_engine(
    DATABASE_URL, # URL database.
    pool_pre_ping=True, # verifica la conexión antes de usarla.
)

# Fábrica de sesiones para interactuar con la BD en cada petición
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase base de la cual heredarán tus modelos de SQLAlchemy
Base = declarative_base()

# Dependencia (Dependency Injection) para FastAPI que abre y cierra la sesión por petición
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
