from dataclasses import dataclass
from typing import Optional
from datetime import date

VALID_STATUSES = ["Pendente", "Em Execucao", "Concluido"]

@dataclass
class DemandManager:
    demand_id: int
    technician_id: int
    status: str    
    demand_manager_id: Optional[int] = None
    next_demand_manager_id: Optional[int] = None
    start_date: Optional[date] = None
    finish_date: Optional[date] = None
    travel_time: Optional[float] = None
    travel_distance: Optional[float] = None
    is_deleted: bool = False


    def __post_init__(self):
        self._normalize()
        self._validate()

    def _normalize(self):
        self.status = self.status.strip().title()

    def _validate(self):
        if self.status not in VALID_STATUSES:
            raise ValueError("Status invalido")
        if self.start_date is None and self.finish_date is not None:
            raise ValueError("Data de conclusao exige data de inicio")
        if self.start_date and self.finish_date and self.start_date > self.finish_date:
            raise ValueError("Data de conclusao nao pode ser anterior a data de inicio")
        if self.travel_time is not None and self.travel_time < 0.0:
            raise ValueError("Tempo de deslocamento nao pode ser negativo")
        if self.travel_distance is not None and self.travel_distance < 0.0:
            raise ValueError("Distancia de deslocamento nao pode ser negativa")