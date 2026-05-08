# -*- coding: utf-8 -*-

from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class Analyst:

    analyst_name: str
    email: str
    contact: str
    creation_date: date
    status: str = "active"    
    valid_to_date: Optional[date] = None
    analyst_id: Optional[int] = None

    def __post_init__(self):
        self._normalize()
        self._validate()

    def _normalize(self):
        self.analyst_name = self.analyst_name.strip()
        self.email = self.email.strip().lower()
        self.contact = self.contact.strip()
        self.status = self.status.strip().lower()

    def _validate(self):
        if not self.analyst_name:
            raise ValueError("Nome do analista nao pode ser vazio")
        if not self.email:
            raise ValueError("Email nao pode ser vazio")
        if not self.contact:
            raise ValueError("Contato nao pode ser vazio")
        if self.status not in ["active", "inactive"]:
            raise ValueError("Status invalido")
        if self.valid_to_date and self.valid_to_date <= self.creation_date:
            raise ValueError("Data de validade nao pode ser anterior")