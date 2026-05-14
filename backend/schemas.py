"""
schemas.py – Modelos Pydantic para validación del request/response.
Contrato de API según SPEC_TECNICA.md § 2.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field
from typing import Optional

class CheckinRequest(BaseModel):
    nombre: str = Field(..., max_length=100)
    empresa: Optional[str] = Field(default=None, max_length=100)
    motivo: Optional[str] = Field(default=None, max_length=200)
    origen: Literal["web", "local"]
    timestamp: datetime  # ISO 8601 validado automáticamente por Pydantic


class CheckinResponse(BaseModel):
    id: int
    nombre: str
    empresa: Optional[str] = Field(default=None, max_length=100)
    motivo: Optional[str] = Field(default=None, max_length=100)
    origen: str
    fecha_registro: datetime

    class Config:
        from_attributes = True
