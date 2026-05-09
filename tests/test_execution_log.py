# -*- coding: utf-8 -*-
from datetime import date
import pytest
from backend.app.models.execution_log import ExecutionLog

@pytest.fixture
def valid_execution_log():
    return ExecutionLog(
        demand_manager_id=10,
        technician_id=5,
        execution_date=date(2026, 5, 8),
        action="Prestacao de Servico",
        worked_hours=6.5,
        distance=0
    )

def make_execution_log(valid_execution_log, **overrides):
    return ExecutionLog(**{**valid_execution_log.__dict__, **overrides})

# --- criacao basica ---

def test_execution_log_created_with_valid_fields(valid_execution_log):
    assert valid_execution_log.demand_manager_id == 10
    assert valid_execution_log.technician_id == 5
    assert valid_execution_log.execution_date == date(2026, 5, 8)
    assert valid_execution_log.action == "Prestacao de Servico"
    assert valid_execution_log.worked_hours == 6.5
    assert valid_execution_log.distance == 0
    assert valid_execution_log.execution_log_id is None

# --- demand_manager_id ---

def test_zero_demand_manager_id_should_fail(valid_execution_log):
    with pytest.raises(ValueError, match="Demand Manager ID deve ser maior que zero"):
        make_execution_log(valid_execution_log, demand_manager_id=0)

def test_negative_demand_manager_id_should_fail(valid_execution_log):
    with pytest.raises(ValueError, match="Demand Manager ID deve ser maior que zero"):
        make_execution_log(valid_execution_log, demand_manager_id=-10)

# --- technician_id ---

def test_zero_technician_id_should_fail(valid_execution_log):
    with pytest.raises(ValueError, match="Technician ID deve ser maior que zero"):
        make_execution_log(valid_execution_log, technician_id=0)

def test_negative_technician_id_should_fail(valid_execution_log):
    with pytest.raises(ValueError, match="Technician ID deve ser maior que zero"):
        make_execution_log(valid_execution_log, technician_id=-5)

# --- action ---

def test_invalid_action_should_fail(valid_execution_log):
    with pytest.raises(ValueError, match="Acao invalida"):
        make_execution_log(valid_execution_log, action="Refeicao")

def test_all_valid_actions_are_accepted(valid_execution_log):
    for action in ["Deslocamento", "Prestacao de Servico"]:
        el = make_execution_log(valid_execution_log, action=action)
        assert el.action == action

def test_action_with_whitespace_is_normalized(valid_execution_log):
    """Espaços em branco são removidos."""
    el = make_execution_log(valid_execution_log, action="  Deslocamento  ")
    assert el.action == "Deslocamento"

# --- worked_hours ---

def test_negative_worked_hours_should_fail(valid_execution_log):
    with pytest.raises(ValueError, match="Horas de trabalho nao podem ser negativas"):
        make_execution_log(valid_execution_log, worked_hours=-2.0)

def test_zero_worked_hours_is_accepted(valid_execution_log):
    """Zero horas é válido — pode ser um deslocamento sem trabalho."""
    el = make_execution_log(valid_execution_log, worked_hours=0.0)
    assert el.worked_hours == 0.0

def test_fractional_worked_hours_is_accepted(valid_execution_log):
    el = make_execution_log(valid_execution_log, worked_hours=4.75)
    assert el.worked_hours == 4.75

def test_full_day_worked_hours_is_accepted(valid_execution_log):
    """Dia completo de trabalho."""
    el = make_execution_log(valid_execution_log, worked_hours=8.8)
    assert el.worked_hours == 8.8

# --- distance ---

def test_negative_distance_should_fail(valid_execution_log):
    with pytest.raises(ValueError, match="Distancia nao pode ser negativa"):
        make_execution_log(valid_execution_log, distance=-100)

def test_zero_distance_is_accepted(valid_execution_log):
    """Distância zero é válida — ação pode ser local."""
    el = make_execution_log(valid_execution_log, distance=0)
    assert el.distance == 0

def test_large_distance_is_accepted(valid_execution_log):
    el = make_execution_log(valid_execution_log, distance=1500)
    assert el.distance == 1500

# --- execution_log_id ---

def test_execution_log_id_defaults_to_none(valid_execution_log):
    assert valid_execution_log.execution_log_id is None

def test_execution_log_id_can_be_set_after_creation(valid_execution_log):
    valid_execution_log.execution_log_id = 200
    assert valid_execution_log.execution_log_id == 200

# --- cenarios de negocio ---

def test_execution_log_records_actual_travel():
    """Um registro de deslocamento real."""
    el = ExecutionLog(
        demand_manager_id=10,
        technician_id=5,
        execution_date=date(2026, 5, 8),
        action="Deslocamento",
        worked_hours=0.0,
        distance=250
    )
    assert el.action == "Deslocamento"
    assert el.worked_hours == 0.0
    assert el.distance == 250

def test_execution_log_records_actual_work():
    """Um registro de trabalho real."""
    el = ExecutionLog(
        demand_manager_id=10,
        technician_id=5,
        execution_date=date(2026, 5, 8),
        action="Prestacao de Servico",
        worked_hours=7.2,
        distance=0
    )
    assert el.action == "Prestacao de Servico"
    assert el.worked_hours == 7.2
    assert el.distance == 0

def test_execution_log_day_with_both_actions():
    """Um dia típico tem deslocamento + serviço."""
    morning_travel = ExecutionLog(
        demand_manager_id=10,
        technician_id=5,
        execution_date=date(2026, 5, 8),
        action="Deslocamento",
        worked_hours=1.0,
        distance=150
    )
    afternoon_work = ExecutionLog(
        demand_manager_id=10,
        technician_id=5,
        execution_date=date(2026, 5, 8),
        action="Prestacao de Servico",
        worked_hours=7.0,
        distance=0
    )
    # Mesma demanda, mesmo dia, duas ações
    assert morning_travel.demand_manager_id == afternoon_work.demand_manager_id
    assert morning_travel.execution_date == afternoon_work.execution_date
    assert morning_travel.action != afternoon_work.action
    # Total do dia: 1h viagem + 7h trabalho = 8h
    total_hours = morning_travel.worked_hours + afternoon_work.worked_hours
    total_distance = morning_travel.distance + afternoon_work.distance
    assert total_hours == 8.0
    assert total_distance == 150

def test_multiple_execution_logs_same_demand_different_days():
    """Uma demanda pode ter múltiplos logs em dias diferentes."""
    el1 = ExecutionLog(
        demand_manager_id=10, technician_id=5, execution_date=date(2026, 5, 8),
        action="Prestacao de Servico", worked_hours=8.0, distance=100
    )
    el2 = ExecutionLog(
        demand_manager_id=10, technician_id=5, execution_date=date(2026, 5, 9),
        action="Prestacao de Servico", worked_hours=8.0, distance=0
    )
    el3 = ExecutionLog(
        demand_manager_id=10, technician_id=5, execution_date=date(2026, 5, 10),
        action="Prestacao de Servico", worked_hours=5.0, distance=100
    )
    # Mesma demanda, dias diferentes
    assert el1.demand_manager_id == el2.demand_manager_id == el3.demand_manager_id
    assert el1.execution_date < el2.execution_date < el3.execution_date
    # Total de 21h de trabalho em 3 dias
    total_hours = el1.worked_hours + el2.worked_hours + el3.worked_hours
    assert total_hours == 21.0

def test_execution_log_permanence():
    """Registros de execução são permanentes — nunca deletados."""
    el = ExecutionLog(
        demand_manager_id=10,
        technician_id=5,
        execution_date=date(2026, 5, 8),
        action="Prestacao de Servico",
        worked_hours=8.0,
        distance=100
    )
    el.execution_log_id = 1000
    # Não há operação de delete — é só auditoria
    assert el.execution_log_id == 1000
    assert el.execution_date == date(2026, 5, 8)