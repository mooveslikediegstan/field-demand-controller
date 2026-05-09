# -*- coding: utf-8 -*-
from datetime import date
import pytest
from backend.app.models.schedule_item_persistent import ScheduleItemPersistent as ScheduleItem

@pytest.fixture
def valid_schedule_item():
    return ScheduleItem(
        version_id=1,
        demand_manager_id=10,
        technician_id=5,
        scheduled_date=date(2026, 5, 8),
        action="Prestacao de Servico",
        worked_hours=4.5,
        distance=0
    )

def make_schedule_item(valid_schedule_item, **overrides):
    return ScheduleItem(**{**valid_schedule_item.__dict__, **overrides})

# --- criacao basica ---

def test_schedule_item_created_with_valid_fields(valid_schedule_item):
    assert valid_schedule_item.version_id == 1
    assert valid_schedule_item.demand_manager_id == 10
    assert valid_schedule_item.technician_id == 5
    assert valid_schedule_item.scheduled_date == date(2026, 5, 8)
    assert valid_schedule_item.action == "Prestacao de Servico"
    assert valid_schedule_item.worked_hours == 4.5
    assert valid_schedule_item.distance == 0
    assert valid_schedule_item.schedule_item_id is None

# --- version_id ---

def test_zero_version_id_should_fail(valid_schedule_item):
    with pytest.raises(ValueError, match="Version ID deve ser maior que zero"):
        make_schedule_item(valid_schedule_item, version_id=0)

def test_negative_version_id_should_fail(valid_schedule_item):
    with pytest.raises(ValueError, match="Version ID deve ser maior que zero"):
        make_schedule_item(valid_schedule_item, version_id=-1)

# --- demand_manager_id ---

def test_zero_demand_manager_id_should_fail(valid_schedule_item):
    with pytest.raises(ValueError, match="Demand Manager ID deve ser maior que zero"):
        make_schedule_item(valid_schedule_item, demand_manager_id=0)

def test_negative_demand_manager_id_should_fail(valid_schedule_item):
    with pytest.raises(ValueError, match="Demand Manager ID deve ser maior que zero"):
        make_schedule_item(valid_schedule_item, demand_manager_id=-10)

# --- technician_id ---

def test_zero_technician_id_should_fail(valid_schedule_item):
    with pytest.raises(ValueError, match="Technician ID deve ser maior que zero"):
        make_schedule_item(valid_schedule_item, technician_id=0)

def test_negative_technician_id_should_fail(valid_schedule_item):
    with pytest.raises(ValueError, match="Technician ID deve ser maior que zero"):
        make_schedule_item(valid_schedule_item, technician_id=-5)

# --- action ---

def test_invalid_action_should_fail(valid_schedule_item):
    with pytest.raises(ValueError, match="Acao invalida"):
        make_schedule_item(valid_schedule_item, action="Pausa")

def test_all_valid_actions_are_accepted(valid_schedule_item):
    for action in ["Deslocamento", "Prestacao de Servico"]:
        si = make_schedule_item(valid_schedule_item, action=action)
        assert si.action == action

def test_action_with_whitespace_is_normalized(valid_schedule_item):
    """Espaços em branco são removidos."""
    si = make_schedule_item(valid_schedule_item, action="  Deslocamento  ")
    assert si.action == "Deslocamento"

# --- worked_hours ---

def test_negative_worked_hours_should_fail(valid_schedule_item):
    with pytest.raises(ValueError, match="Horas de trabalho nao podem ser negativas"):
        make_schedule_item(valid_schedule_item, worked_hours=-1.5)

def test_zero_worked_hours_is_accepted(valid_schedule_item):
    """Zero horas é válido — pode ser um deslocamento sem serviço."""
    si = make_schedule_item(valid_schedule_item, worked_hours=0.0)
    assert si.worked_hours == 0.0

def test_fractional_worked_hours_is_accepted(valid_schedule_item):
    si = make_schedule_item(valid_schedule_item, worked_hours=3.25)
    assert si.worked_hours == 3.25

# --- distance ---

def test_negative_distance_should_fail(valid_schedule_item):
    with pytest.raises(ValueError, match="Distancia nao pode ser negativa"):
        make_schedule_item(valid_schedule_item, distance=-50)

def test_zero_distance_is_accepted(valid_schedule_item):
    """Distância zero é válida — ação pode ser local."""
    si = make_schedule_item(valid_schedule_item, distance=0)
    assert si.distance == 0

def test_large_distance_is_accepted(valid_schedule_item):
    si = make_schedule_item(valid_schedule_item, distance=2500)
    assert si.distance == 2500

# --- schedule_item_id ---

def test_schedule_item_id_defaults_to_none(valid_schedule_item):
    assert valid_schedule_item.schedule_item_id is None

def test_schedule_item_id_can_be_set_after_creation(valid_schedule_item):
    valid_schedule_item.schedule_item_id = 100
    assert valid_schedule_item.schedule_item_id == 100

# --- cenarios de negocio ---

def test_deslocamento_without_worked_hours():
    """Um deslocamento puro tem 0 horas de trabalho, mas distância."""
    si = ScheduleItem(
        version_id=1,
        demand_manager_id=10,
        technician_id=5,
        scheduled_date=date(2026, 5, 8),
        action="Deslocamento",
        worked_hours=0.0,
        distance=150
    )
    assert si.action == "Deslocamento"
    assert si.worked_hours == 0.0
    assert si.distance == 150

def test_prestacao_de_servico_without_distance():
    """Um serviço puro tem 0 distância, mas horas."""
    si = ScheduleItem(
        version_id=1,
        demand_manager_id=10,
        technician_id=5,
        scheduled_date=date(2026, 5, 8),
        action="Prestacao de Servico",
        worked_hours=8.0,
        distance=0
    )
    assert si.action == "Prestacao de Servico"
    assert si.worked_hours == 8.0
    assert si.distance == 0

def test_multiple_schedule_items_same_demand_manager():
    """Uma demanda pode gerar múltiplos itens (um por dia)."""
    dm_id = 10
    si1 = ScheduleItem(
        version_id=1, demand_manager_id=dm_id, technician_id=5,
        scheduled_date=date(2026, 5, 8), action="Deslocamento",
        worked_hours=1.0, distance=100
    )
    si2 = ScheduleItem(
        version_id=1, demand_manager_id=dm_id, technician_id=5,
        scheduled_date=date(2026, 5, 8), action="Prestacao de Servico",
        worked_hours=7.0, distance=0
    )
    assert si1.demand_manager_id == si2.demand_manager_id
    assert si1.scheduled_date == si2.scheduled_date
    assert si1.action != si2.action