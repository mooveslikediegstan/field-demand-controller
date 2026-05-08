# -*- coding: utf-8 -*-
from dataclasses import dataclass,field
from datetime import date, timedelta
from backend.app.models.schedule_item import ScheduleItem
from backend.app.models.geo_utils import distance_between_coordinates

@dataclass
class SchedulePlanner:

    technician_id: int
    initial_start_date: date
    daily_capacity_hours: float
    travel_speed_kmh: float
    origin_lat: float
    origin_lon: float
    scheduled_items: list = field(default_factory=list)

    def __post_init__(self):
        if self.daily_capacity_hours <= 0:
            raise ValueError("Capacidade diaria deve ser maior que zero")
        if self.travel_speed_kmh <= 0:
            raise ValueError("Velocidade de deslocamento deve ser maior que zero")
    
    def _next_workday(self, current: date) -> date:
        """Avança para o próximo dia útil (seg-sex)."""
        next_day = current + timedelta(days=1)
        while next_day.weekday() >= 5:  # 5=sab, 6=dom
            next_day += timedelta(days=1)
        return next_day

    def plan(self, demand_inputs: list) -> None:
        self.scheduled_items = []

        current_date    = self.initial_start_date
        remaining_hours = self.daily_capacity_hours
        current_lat     = self.origin_lat
        current_lon     = self.origin_lon
        sequence        = 1

        def consume_hours(hours_needed: float, action: str,
                        demand_manager_id: int, distance: int = 0):
            """Consome horas em fatias diárias, gerando um ScheduleItem por fatia."""
            nonlocal current_date, remaining_hours, sequence

            remaining = hours_needed
            while remaining > 0:
                if remaining_hours <= 0:
                    current_date    = self._next_workday(current_date)
                    remaining_hours = self.daily_capacity_hours

                consume          = min(remaining, remaining_hours)
                remaining       -= consume
                remaining_hours -= consume

                self.scheduled_items.append(ScheduleItem(
                    demand_manager_id = demand_manager_id,
                    technician_id     = self.technician_id,
                    scheduled_date    = current_date,
                    action            = action,
                    work_time         = round(consume, 4),
                    sequence_position = sequence,
                    distance          = distance if action == "Deslocamento" else 0
                ))
                sequence += 1
                distance  = 0  # distancia só no primeiro item de deslocamento

        for item in demand_inputs:
            distance_km  = distance_between_coordinates(
                current_lat, current_lon, item.city_lat, item.city_lon)
            travel_hours = distance_km / self.travel_speed_kmh

            if travel_hours > 0:
                consume_hours(travel_hours, "Deslocamento",
                            item.demand_manager_id, round(distance_km))

            consume_hours(item.estimated_time, "Prestacao de Servico",
                        item.demand_manager_id)

            current_lat = item.city_lat
            current_lon = item.city_lon