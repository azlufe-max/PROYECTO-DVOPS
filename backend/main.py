"""
main.py – Punto de entrada de la API Guest-Pass.
FastAPI · Puerto 8000 · Endpoint POST /api/v1/checkin

Spec: SPEC_TECNICA.md §§ 2, 3, 4
"""

import json
import sys

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import engine, get_db, Base
from models import Visitante
from schemas import CheckinRequest, CheckinResponse

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
# Helper: log JSON estructurado → STDOUT (Spec § 4)
# ---------------------------------------------------------------
def log_checkin(nombre: str, origen: str, success: bool = True) -> None:
    """Imprime el log en el formato exacto definido en la Spec § 4."""
    entry = {
        "level": "INFO" if success else "ERROR",
        "event": "visitor_checkin",
        "user": nombre,
        "source": origen,
        "status": "success" if success else "error",
    }
    print(json.dumps(entry, ensure_ascii=False), flush=True, file=sys.stdout)


# ---------------------------------------------------------------
# Endpoint principal
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

        # Log obligatorio – formato exacto de Spec § 4
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
# Health-check (útil para Kubernetes/Docker readiness probes)
# ---------------------------------------------------------------
@app.get("/health", status_code=status.HTTP_200_OK, include_in_schema=False)
def health():
    return {"status": "ok"}
