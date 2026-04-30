"""
database.py – Gestión de la conexión a PostgreSQL con SQLAlchemy.
Credenciales según SPEC_TECNICA.md § 3.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# ---------------------------------------------------------------
# Cadena de conexión
# Host = nombre del contenedor Terraform (guest_pass_db)
# ---------------------------------------------------------------
DATABASE_URL = (
    "postgresql://admin:ChangeMe123!@guest_pass_db:5432/guestpass"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency para inyectar la sesión de BD en los endpoints de FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
