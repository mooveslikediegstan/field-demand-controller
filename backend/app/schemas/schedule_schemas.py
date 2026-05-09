# backend/app/schemas/schedule_schemas.py

from pydantic import BaseModel
from datetime import date
from typing import Optional


class QueueItemResponse(BaseModel):
    demand_manager_id: int
    demand_id: int
    demand_title: str
    project_id: str
    status: str
    estimated_time: float

    model_config = {"from_attributes": True}


class SaveSequenceRequest(BaseModel):
    ordered_demand_manager_ids: list[int]


class GanttItemResponse(BaseModel):
    demand_manager_id: int
    demand_title: str
    start_date: date
    finish_date: date