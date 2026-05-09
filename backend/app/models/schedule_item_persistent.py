# -*- coding: utf-8 -*-
from dataclasses import dataclass
from datetime import date
from typing import Optional

VALID_ACTIONS = ["Deslocamento", "Prestacao de Servico"]

@dataclass
class ScheduleItemPersistent:
    """
    Representa um bloco atômico de planejamento — um item por ação por dia.
    Resultado direto do SchedulePlanner persistido no banco.
    Muda apenas quando o planejamento é recalculado (nova planning_version).
    """
    version_id: int
    demand_manager_id: int
    technician_id: int
    scheduled_date: date
    action: str
    worked_hours: float
    distance: int = 0
    schedule_item_id: Optional[int] = None

    def __post_init__(self):
        self._normalize()
        self._validate()

    def _normalize(self):
        self.action = self.action.strip()

    def _validate(self):
        if self.version_id <= 0:
            raise ValueError("Version ID deve ser maior que zero")
        if self.demand_manager_id <= 0:
            raise ValueError("Demand Manager ID deve ser maior que zero")
        if self.technician_id <= 0:
            raise ValueError("Technician ID deve ser maior que zero")
        if self.action not in VALID_ACTIONS:
            raise ValueError("Acao invalida")
        if self.worked_hours < 0:
            raise ValueError("Horas de trabalho nao podem ser negativas")
        if self.distance < 0:
            raise ValueError("Distancia nao pode ser negativa")