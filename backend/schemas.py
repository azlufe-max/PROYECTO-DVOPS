"""
schemas.py – Modelos Pydantic para validación del request/response.
Contrato de API según SPEC_TECNICA.md § 2.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class CheckinRequest(BaseModel):
    nombre: str = Field(..., max_length=100)
    empresa: str | None = Field(default=None, max_length=100)
    motivo: str | None = None
    origen: Literal["web", "local"]
    timestamp: datetime  # ISO 8601 validado automáticamente por Pydantic


class CheckinResponse(BaseModel):
    id: int
    nombre: str
    empresa: str | None
    motivo: str | None
    origen: str
    fecha_registro: datetime

    class Config:
        from_attributes = True
