# backend/app/schemas/demand_manager_schemas.py

from pydantic import BaseModel
from datetime import date
from typing import Optional


class AllocateRequest(BaseModel):
    technician_id: int


class DemandManagerResponse(BaseModel):
    demand_manager_id: int
    demand_id: int
    technician_id: int
    status: str
    start_date: Optional[date]
    finish_date: Optional[date]
    travel_time: Optional[float]
    travel_distance: Optional[float]

    model_config = {"from_attributes": True}


class ConclusionDataResponse(BaseModel):
    demand_manager_id: int
    demand_title: str
    project_id: str
    technician_id: int
    estimated_time: float


class ConcludeRequest(BaseModel):
    actual_time: float
    travel_time: float
    travel_distance: float
    finish_date: date