# -*- coding: utf-8 -*-
from dataclasses import dataclass


@dataclass
class Customer:

    customer_id: str
    customer_name: str
    short_name: str
    city_id: int
    address: str
    segment: str
    sub_segment: str
    region: str

    def __post_init__(self):
        self._normalize()
        self._validate()

    def _normalize(self):
        self.customer_id = self.customer_id.strip()
        self.customer_name = self.customer_name.strip()
        self.short_name = self.short_name.strip()
        self.address = self.address.strip()
        self.segment = self.segment.strip()
        self.sub_segment = self.sub_segment.strip()
        self.region = self.region.strip()

    def _validate(self):
        if not self.customer_id:
            raise ValueError("ID do cliente nao pode ser vazio")
        if not self.customer_name:
            raise ValueError("Nome do cliente nao pode ser vazio")
        if not self.short_name:
            raise ValueError("Nome curto nao pode ser vazio")
        if not self.address:
            raise ValueError("Endereco nao pode ser vazio")

        valid_segments = ["Farm", "Commercial"]
        if self.segment not in valid_segments:
            raise ValueError("Segmento invalido")

        valid_sub_segments = ["Farm", "Commercial", "Feed", "Fertilizer", "Fuel"]
        if self.sub_segment not in valid_sub_segments:
            raise ValueError("Sub-segmento invalido")
        
        valid_regions = ["MA/PI", "TO/BA", "MT", "MG/GO", "MS/SP", "PR,SC,RS"]
        if self.region not in valid_regions:
            raise ValueError("Regiao invalida")