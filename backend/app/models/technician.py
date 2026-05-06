
from dataclasses import dataclass
from typing import Optional
from datetime import date

@dataclass
class Technician:

    technician_name: str
    creation_date: date
    status: str
    base_location_city_id: int
    current_location_city_id: int
    daily_capacity: float
    position: str
    dismiss_date: Optional[date] = None
    technician_id: Optional[int] = None

    def __post_init__(self):
        self._normalize()
        self._validate()

    def _normalize(self):
        self.technician_name = self.technician_name.strip()
        self.status          = self.status.strip().lower()
        self.position        = self.position.strip().title()

    def _validate(self):
        if not self.technician_name:
            raise ValueError("Nome do tecnico nao pode ser vazio")
        if self.status not in {"ativo", "inativo"}:
            raise ValueError("Status invalido")
        if self.position not in {"Lider", "Supervisor", "Coordenador"}:
            raise ValueError("Cargo invalido")
        if self.dismiss_date and self.status != "inativo":
            raise ValueError("Tecnico ativo nao pode ter data de demissao")
        if self.daily_capacity <= 0:
            raise ValueError("Capacidade diaria deve ser maior que zero")