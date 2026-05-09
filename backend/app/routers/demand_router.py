# -*- coding: utf-8 -*-
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.demand import Demand
from backend.app.services.demand_service import DemandService
from backend.app.schemas.demand_schemas import (
    DemandCreateRequest,
    DemandUpdateRequest,
    DemandResponse,
)
from backend.app.schemas.demand_manager_schemas import (
    AllocateRequest,
    DemandManagerResponse,
    ConclusionDataResponse,
    ConcludeRequest,
)

router = APIRouter(prefix="/api/demands", tags=["Demands"])


# ── CRIAR DEMANDA ─────────────────────────────────────────────────────────────

@router.post("/", response_model=DemandResponse, status_code=201)
def create_demand(payload: DemandCreateRequest, db: Session = Depends(get_db)):
    service = DemandService(db)
    try:
        demand = Demand(
            demand_title           = payload.demand_title,
            problem_description    = payload.problem_description,
            project_id             = payload.project_id,
            responsible_id         = payload.responsible_id,
            estimated_time         = payload.estimated_time,
            technical_visit_reason = payload.technical_visit_reason,
            causal_sector          = payload.causal_sector,
            causal_area            = payload.causal_area,
            root_cause             = payload.root_cause,
            equipment              = payload.equipment,
            # campos gerados pelo backend — frontend não controla
            status                 = "Aberta",
            request_date           = date.today(),
        )
        return service.create_demand(demand)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


# ── ATUALIZAR DEMANDA ─────────────────────────────────────────────────────────

@router.put("/{demand_id}", response_model=DemandResponse)
def update_demand(demand_id: int, payload: DemandUpdateRequest, db: Session = Depends(get_db)):
    service = DemandService(db)
    try:
        existing = service.get_demand(demand_id)
        # Atualiza apenas os campos editáveis — preserva os imutáveis do banco
        updated = Demand(
            demand_id              = demand_id,
            demand_title           = payload.demand_title,
            problem_description    = payload.problem_description,
            project_id             = existing.project_id,
            responsible_id         = existing.responsible_id,
            request_date           = existing.request_date,
            estimated_time         = payload.estimated_time,
            actual_time            = payload.actual_time,
            technical_visit_reason = payload.technical_visit_reason,
            causal_sector          = payload.causal_sector,
            causal_area            = payload.causal_area,
            root_cause             = payload.root_cause,
            equipment              = payload.equipment,
            status                 = payload.status,
        )
        return service.update_demand(updated)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


# ── CANCELAR DEMANDA ──────────────────────────────────────────────────────────

@router.delete("/{demand_id}", response_model=DemandResponse)
def cancel_demand(demand_id: int, db: Session = Depends(get_db)):
    service = DemandService(db)
    try:
        return service.cancel_demand(demand_id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


# ── ALOCAR TÉCNICO ────────────────────────────────────────────────────────────

@router.post("/{demand_id}/allocate", response_model=DemandManagerResponse, status_code=201)
def allocate_technician(demand_id: int, payload: AllocateRequest, db: Session = Depends(get_db)):
    service = DemandService(db)
    try:
        return service.allocate_technician(demand_id, payload.technician_id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


# ── DESALOCAR TÉCNICO ─────────────────────────────────────────────────────────

@router.delete("/{demand_id}/allocate/{technician_id}", response_model=DemandResponse)
def deallocate_technician(demand_id: int, technician_id: int, db: Session = Depends(get_db)):
    service = DemandService(db)
    try:
        return service.deallocate_technician(demand_id, technician_id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


# ── DADOS DE CONCLUSÃO ────────────────────────────────────────────────────────

@router.get("/{dm_id}/conclusion-data", response_model=ConclusionDataResponse)
def get_conclusion_data(dm_id: int, db: Session = Depends(get_db)):
    service = DemandService(db)
    try:
        return service.get_conclusion_data(dm_id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


# ── CONCLUIR ORDEM ────────────────────────────────────────────────────────────

@router.post("/{dm_id}/conclude", response_model=DemandResponse)
def conclude_demand(dm_id: int, payload: ConcludeRequest, db: Session = Depends(get_db)):
    service = DemandService(db)
    try:
        return service.conclude_demand_manager(
            demand_manager_id = dm_id,
            actual_time       = payload.actual_time,
            travel_time       = payload.travel_time,
            travel_distance   = payload.travel_distance,
            finish_date       = payload.finish_date,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))