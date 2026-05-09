# backend/app/models/execution_input.py
from dataclasses import dataclass
from datetime import date
from backend.app.models.schedule_item import VALID_ACTIONS

@dataclass
class ExecutionInput:
    execution_date: date
    action:         str
    worked_hours:   float
    distance:       int = 0

    def __post_init__(self):
        if self.action not in VALID_ACTIONS:
            raise ValueError("Acao invalida")
        if self.worked_hours < 0:
            raise ValueError("Horas trabalhadas nao podem ser negativas")
        if self.distance < 0:
            raise ValueError("Distancia nao pode ser negativa")