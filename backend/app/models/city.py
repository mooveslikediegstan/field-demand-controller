# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import Optional

VALID_STATES = {
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO",
    "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI",
    "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO",
    "EX"
}

@dataclass
class City:
    city_name:       str
    state:           str
    country:         str
    geolocation_lat: float
    geolocation_lon: float
    city_id:         Optional[int] = None

    def __post_init__(self):
        self._normalize()
        self._validate()

    def _normalize(self):
        self.city_name = self.city_name.strip()
        self.state     = self.state.strip().upper()
        self.country   = self.country.strip()

    def _validate(self):
        if not self.city_name:
            raise ValueError("Nome da cidade nao pode ser vazio")
        if not self.country:
            raise ValueError("Pais nao pode ser vazio")
        if self.state not in VALID_STATES:
            raise ValueError("Estado invalido")
        if not -90 <= self.geolocation_lat <= 90:
            raise ValueError("Latitude invalida")
        if not -180 <= self.geolocation_lon <= 180:
            raise ValueError("Longitude invalida")