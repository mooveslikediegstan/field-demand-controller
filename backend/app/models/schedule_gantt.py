# -*- coding: utf-8 -*-
from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class ScheduleGantt:
    """
    Representa a visão simplificada do planejamento — start e finish date por demanda.
    Derivado do planejamento atômico (ScheduleItem).
    Consumido pelo gráfico Gantt e pelo dashboard.
    Muda apenas quando o planejamento é recalculado (nova planning_version).
    """
    version_id: int
    demand_manager_id: int
    technician_id: int
    start_date: date
    finish_date: date
    schedule_gantt_id: Optional[int] = None

    def __post_init__(self):
        self._validate()

    def _validate(self):
        if self.version_id <= 0:
            raise ValueError("Version ID deve ser maior que zero")
        if self.demand_manager_id <= 0:
            raise ValueError("Demand Manager ID deve ser maior que zero")
        if self.technician_id <= 0:
            raise ValueError("Technician ID deve ser maior que zero")
        if self.start_date > self.finish_date:
            raise ValueError("Data de conclusao nao pode ser anterior a data de inicio")