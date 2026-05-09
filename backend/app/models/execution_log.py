# -*- coding: utf-8 -*-
from dataclasses import dataclass
from datetime import date
from typing import Optional

VALID_ACTIONS = ["Deslocamento", "Prestacao de Servico"]

@dataclass
class ExecutionLog:
    """
    Representa o que de fato aconteceu na execução — um registro por linha por dia.
    Lançado manualmente pelo usuário ao concluir uma demanda.
    Um DemandManager pode ter múltiplos ExecutionLog (um por dia entre start_date e finish_date).
    Permanente — nunca é deletado ou alterado após criado (apenas para auditoria).
    """
    demand_manager_id: int
    technician_id: int
    execution_date: date
    action: str
    worked_hours: float
    distance: int = 0
    execution_log_id: Optional[int] = None

    def __post_init__(self):
        self._normalize()
        self._validate()

    def _normalize(self):
        self.action = self.action.strip()

    def _validate(self):
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