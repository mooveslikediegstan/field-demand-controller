# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.services.queue_service import QueueService
from backend.app.services.schedule_service import ScheduleService
from backend.app.schemas.schedule_schemas import (
    QueueItemResponse,
    SaveSequenceRequest,
    GanttItemResponse,
)

router = APIRouter(prefix="/api/technicians", tags=["Technicians"])


# ── LISTAR FILA ───────────────────────────────────────────────────────────────

@router.get("/{tech_id}/queue", response_model=list[QueueItemResponse])
def get_queue(tech_id: int, db: Session = Depends(get_db)):
    service = QueueService(db)
    try:
        return service.get_queue(tech_id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


# ── SALVAR SEQUÊNCIA ──────────────────────────────────────────────────────────

@router.post("/{tech_id}/save-sequence", response_model=list[QueueItemResponse])
def save_sequence(tech_id: int, payload: SaveSequenceRequest, db: Session = Depends(get_db)):
    queue_service    = QueueService(db)
    schedule_service = ScheduleService(db)
    try:
        # 1. Reordena a fila e persiste os novos links
        updated_queue = queue_service.save_sequence(tech_id, payload)

        # 2. Gera novo planejamento com a ordem atualizada (Opção A)
        schedule_service.replan(tech_id)

        return updated_queue
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


# ── VISUALIZAR GANTT ──────────────────────────────────────────────────────────

@router.get("/{tech_id}/schedule", response_model=list[GanttItemResponse])
def get_schedule(tech_id: int, db: Session = Depends(get_db)):
    service = ScheduleService(db)
    try:
        return service.get_gantt(tech_id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))