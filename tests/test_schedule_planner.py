# -*- coding: utf-8 -*-
from datetime import date
import pytest
from backend.app.models.schedule_planner import SchedulePlanner
from backend.app.models.schedule_input import ScheduleInput

SP_LAT, SP_LON = -23.5505, -46.6333
RJ_LAT, RJ_LON = -22.9068, -43.1729
BH_LAT, BH_LON = -19.9167, -43.9345

@pytest.fixture
def planner():
    return SchedulePlanner(
        technician_id=10,
        initial_start_date=date(2026, 5, 7),  # quinta
        daily_capacity_hours=8.0,
        travel_speed_kmh=80.0,
        origin_lat=SP_LAT,
        origin_lon=SP_LON
    )

@pytest.fixture
def same_city_input():
    """Demanda na mesma cidade — sem deslocamento."""
    return [ScheduleInput(demand_manager_id=1, demand_id=1,
                          estimated_time=4.0, city_lat=SP_LAT, city_lon=SP_LON)]

# --- criacao basica ---

def test_planner_created_with_valid_fields(planner):
    assert planner.technician_id == 10
    assert planner.daily_capacity_hours == 8.0
    assert planner.scheduled_items == []

def test_zero_daily_capacity_should_fail():
    with pytest.raises(ValueError, match="Capacidade diaria deve ser maior que zero"):
        SchedulePlanner(technician_id=10, initial_start_date=date(2026, 5, 7),
                        daily_capacity_hours=0.0, travel_speed_kmh=80.0,
                        origin_lat=SP_LAT, origin_lon=SP_LON)

def test_zero_travel_speed_should_fail():
    with pytest.raises(ValueError, match="Velocidade de deslocamento deve ser maior que zero"):
        SchedulePlanner(technician_id=10, initial_start_date=date(2026, 5, 7),
                        daily_capacity_hours=8.0, travel_speed_kmh=0.0,
                        origin_lat=SP_LAT, origin_lon=SP_LON)

# --- same city: sem deslocamento ---

def test_same_city_generates_no_travel_item(planner, same_city_input):
    planner.plan(same_city_input)
    actions = [i.action for i in planner.scheduled_items]
    assert "Deslocamento" not in actions

def test_same_city_starts_on_initial_date(planner, same_city_input):
    planner.plan(same_city_input)
    assert planner.scheduled_items[0].scheduled_date == date(2026, 5, 7)

# --- deslocamento gera item proprio ---

def test_travel_generates_deslocamento_item(planner):
    inputs = [ScheduleInput(demand_manager_id=1, demand_id=1,
                            estimated_time=4.0, city_lat=RJ_LAT, city_lon=RJ_LON)]
    planner.plan(inputs)
    assert planner.scheduled_items[0].action == "Deslocamento"

def test_service_item_follows_travel(planner):
    inputs = [ScheduleInput(demand_manager_id=1, demand_id=1,
                            estimated_time=4.0, city_lat=RJ_LAT, city_lon=RJ_LON)]
    planner.plan(inputs)
    actions = [i.action for i in planner.scheduled_items]
    assert "Prestacao de Servico" in actions

# --- exemplo pratico do enunciado ---

def test_practical_example():
    """
    07/05 | 8h/dia | 80km/h
    Demanda1: 16h trabalho, 400km (5h deslocamento)
    Demanda2: 8h trabalho, 200km (2.5h deslocamento)
    Demanda3: 12h trabalho, 200km (2.5h deslocamento)
    """
    planner = SchedulePlanner(
        technician_id=10,
        initial_start_date=date(2026, 5, 7),
        daily_capacity_hours=8.0,
        travel_speed_kmh=80.0,
        origin_lat=0.0, origin_lon=0.0
    )
    # coordenadas artificiais que geram exatamente as distâncias do exemplo
    # 400km / 6371km * (180/pi) ~= 3.597 graus
    inputs = [
        ScheduleInput(demand_manager_id=1, demand_id=1, estimated_time=16.0,
                      city_lat=3.597, city_lon=0.0),
        ScheduleInput(demand_manager_id=2, demand_id=2, estimated_time=8.0,
                      city_lat=5.396, city_lon=0.0),
        ScheduleInput(demand_manager_id=3, demand_id=3, estimated_time=12.0,
                      city_lat=7.194, city_lon=0.0),
    ]
    planner.plan(inputs)

    dates = [i.scheduled_date for i in planner.scheduled_items]
    assert date(2026, 5, 7)  in dates  # quinta
    assert date(2026, 5, 8)  in dates  # sexta
    assert date(2026, 5, 9)  not in dates  # sabado — skip
    assert date(2026, 5, 10) not in dates  # domingo — skip
    assert date(2026, 5, 11) in dates  # segunda

# --- reset ---

def test_plan_resets_previous_results(planner, same_city_input):
    planner.plan(same_city_input)
    count_first = len(planner.scheduled_items)
    planner.plan(same_city_input)
    assert len(planner.scheduled_items) == count_first

# --- dias uteis ---

def test_plan_skips_saturday_and_sunday():
    planner = SchedulePlanner(
        technician_id=10,
        initial_start_date=date(2026, 5, 15),  # sexta
        daily_capacity_hours=2.0,
        travel_speed_kmh=80.0,
        origin_lat=SP_LAT, origin_lon=SP_LON
    )
    inputs = [
        ScheduleInput(demand_manager_id=1, demand_id=1, estimated_time=2.0,
                      city_lat=SP_LAT, city_lon=SP_LON),
        ScheduleInput(demand_manager_id=2, demand_id=2, estimated_time=2.0,
                      city_lat=SP_LAT, city_lon=SP_LON),
    ]
    planner.plan(inputs)
    dates = [i.scheduled_date for i in planner.scheduled_items]
    assert date(2026, 5, 15) in dates   # sexta
    assert date(2026, 5, 16) not in dates  # sabado
    assert date(2026, 5, 17) not in dates  # domingo
    assert date(2026, 5, 18) in dates   # segunda