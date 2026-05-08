# -*- coding: utf-8 -*-
from dataclasses import dataclass

@dataclass
class Project:

    project_id: str
    project_name: str
    customer_id: str

    def __post_init__(self):
        self._normalize()
        self._validate()

    def _normalize(self):
        self.project_id = self.project_id.strip()
        self.project_name = self.project_name.strip()
        self.customer_id = self.customer_id.strip()

    def _validate(self):
        if not self.project_id:
            raise ValueError("ID do projeto nao pode ser vazio")
        if not self.project_name:
            raise ValueError("Nome do projeto nao pode ser vazio")
        if not self.customer_id:
            raise ValueError("ID do cliente nao pode ser vazio")