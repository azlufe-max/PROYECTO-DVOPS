"""
main.py – Punto de entrada de la API Guest-Pass.
FastAPI · Puerto 8000

Spec: SPEC_TECNICA.md §§ 2, 3, 4
"""

import json
import logging
import sys
from typing import List

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import engine, get_db, Base
from models import Visitante
from schemas import CheckinRequest, CheckinResponse


# ---------------------------------------------------------------
# Logging Estructurado en JSON – Cloud-Native (Spec § 4)
# ---------------------------------------------------------------
class JSONFormatter(logging.Formatter):
    """Formatea cada registro de log como una línea JSON válida."""

    def format(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        log_entry = {
            "level": record.levelname,
            "event": getattr(record, "event", record.getMessage()),
        }
        # Campos extra opcionales (user, source, status)
        for field in ("user", "source", "status"):
            if hasattr(record, field):
                log_entry[field] = getattr(record, field)
        return json.dumps(log_entry, ensure_ascii=False)


def _configure_logging() -> logging.Logger:
    """Configura el logger raíz para emitir JSON a STDOUT."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())

    root = logging.getLogger()
    root.handlers.clear()          # evita handlers duplicados en recarga de uvicorn
    root.addHandler(handler)
    root.setLevel(logging.INFO)

    return logging.getLogger("guest_pass")


logger = _configure_logging()

# ---------------------------------------------------------------
# Crear tablas si no existen (modo desarrollo; producción usa migrations)
# ---------------------------------------------------------------
Base.metadata.create_all(bind=engine)

# ---------------------------------------------------------------
# Aplicación FastAPI
# ---------------------------------------------------------------
app = FastAPI(
    title="Guest-Pass API",
    description="Sistema de Registro de Visitantes",
    version="1.0.0",
)

# ---------------------------------------------------------------
# CORS – permite que el frontend web consuma la API
# ---------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------
# Helper: log JSON estructurado → STDOUT (Spec § 4)
# ---------------------------------------------------------------
def log_checkin(nombre: str, origen: str, success: bool = True) -> None:
    """
    Emite un log con el formato exacto de la Spec § 4:
      {"level": "INFO/ERROR", "event": "visitor_checkin",
       "user": "...", "source": "...", "status": "success/failure"}
    """
    extra = {
        "event": "visitor_checkin",
        "user": nombre,
        "source": origen,
        "status": "success" if success else "failure",
    }
    if success:
        logger.info("visitor_checkin", extra=extra)
    else:
        logger.error("visitor_checkin", extra=extra)


# ---------------------------------------------------------------
# POST /api/v1/checkin – Registrar visitante
# ---------------------------------------------------------------
@app.post(
    "/api/v1/checkin",
    response_model=CheckinResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar la entrada de un visitante",
)
def checkin(payload: CheckinRequest, db: Session = Depends(get_db)):
    """
    Recibe los datos del visitante, los persiste en PostgreSQL
    y emite un log JSON en STDOUT conforme a la Spec.
    """
    try:
        visitante = Visitante(
            nombre=payload.nombre,
            empresa=payload.empresa,
            motivo=payload.motivo,
            origen=payload.origen,
        )
        db.add(visitante)
        db.commit()
        db.refresh(visitante)

        log_checkin(nombre=visitante.nombre, origen=visitante.origen, success=True)
        return visitante

    except Exception as exc:
        db.rollback()
        log_checkin(nombre=payload.nombre, origen=payload.origen, success=False)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al registrar visitante: {exc}",
        )


# ---------------------------------------------------------------
# GET /api/v1/checkins – Listar todos los visitantes
# ---------------------------------------------------------------
@app.get(
    "/api/v1/checkins",
    response_model=List[CheckinResponse],
    status_code=status.HTTP_200_OK,
    summary="Obtener listado de visitantes registrados",
)
def list_checkins(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retorna todos los registros de visitantes ordenados por fecha descendente."""
    visitantes = (
        db.query(Visitante)
        .order_by(Visitante.fecha_registro.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return visitantes


# ---------------------------------------------------------------
# Health-check (útil para Kubernetes/Docker readiness probes)
# ---------------------------------------------------------------
@app.get("/health", status_code=status.HTTP_200_OK, include_in_schema=False)
def health():
    return {"status": "ok"}

