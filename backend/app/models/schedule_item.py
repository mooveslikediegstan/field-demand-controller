# -*- coding: utf-8 -*-
from dataclasses import dataclass
from datetime import date

VALID_ACTIONS = ["Deslocamento", "Prestacao de Servico"]

@dataclass
class ScheduleItem:
    demand_manager_id: int
    technician_id:     int
    scheduled_date:    date
    action:            str
    work_time:         float
    sequence_position: int
    distance:          int = 0

    def __post_init__(self):
        if self.action not in VALID_ACTIONS:
            raise ValueError("Acao invalida")