# backend/app/schemas/demand_schemas.py

from pydantic import BaseModel
from datetime import date
from typing import Optional


class DemandCreateRequest(BaseModel):
    demand_title: str
    problem_description: str
    project_id: str
    responsible_id: int
    estimated_time: float
    technical_visit_reason: str
    causal_sector: str
    causal_area: str
    root_cause: str
    equipment: str


class DemandUpdateRequest(BaseModel):
    demand_title: str
    problem_description: str
    estimated_time: float
    technical_visit_reason: str
    causal_sector: str
    causal_area: str
    root_cause: str
    equipment: str
    status: str
    actual_time: Optional[float] = None


class DemandResponse(BaseModel):
    demand_id: int
    demand_title: str
    problem_description: str
    project_id: str
    responsible_id: int
    request_date: date
    estimated_time: float
    actual_time: Optional[float]
    technical_visit_reason: str
    causal_sector: str
    causal_area: str
    root_cause: str
    equipment: str
    status: str

    model_config = {"from_attributes": True}