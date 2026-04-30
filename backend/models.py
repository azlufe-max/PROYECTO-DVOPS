"""
models.py – Modelo ORM que representa la tabla 'visitantes'.
Esquema según SPEC_TECNICA.md § 3.
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime

from database import Base


class Visitante(Base):
    __tablename__ = "visitantes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    empresa = Column(String(100), nullable=True)
    motivo = Column(Text, nullable=True)
    origen = Column(String(20), nullable=True)
    fecha_registro = Column(DateTime, default=datetime.utcnow)
