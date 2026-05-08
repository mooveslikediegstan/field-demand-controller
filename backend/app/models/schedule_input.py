# -*- coding: utf-8 -*-
from dataclasses import dataclass

@dataclass
class ScheduleInput:

    demand_manager_id: int
    demand_id:         int
    estimated_time:    float       # horas de trabalho
    city_lat:          float       # já resolvido pelo Service
    city_lon:          float       # já resolvido pelo Service
