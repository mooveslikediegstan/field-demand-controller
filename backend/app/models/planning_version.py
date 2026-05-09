# -*- coding: utf-8 -*-
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
 
@dataclass
class PlanningVersion:
    """
    Representa uma versão de planejamento para um técnico.
    Cada vez que o usuário salva a sequência, uma nova versão é criada.
    Apenas uma versão por técnico é ativa (is_active = True) por vez.
    """
    technician_id: int
    created_at: datetime
    is_active: bool = True
    version_id: Optional[int] = None
 
    def __post_init__(self):
        self._validate()
 
    def _validate(self):
        if self.technician_id <= 0:
            raise ValueError("Technician ID deve ser maior que zero")
        if self.created_at is None:
            raise ValueError("Data de criacao nao pode ser vazia")