# tests/test_execution_service.py
import pytest
from datetime import date
from unittest.mock import MagicMock

from backend.app.services.execution_service import ExecutionService
from backend.app.models.execution_input import ExecutionInput
from backend.app.models.demand_manager import DemandManager
from backend.app.models.demand import Demand


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def service():
    svc = ExecutionService(db=MagicMock())
    svc.el_repo     = MagicMock()
    svc.dm_repo     = MagicMock()
    svc.demand_repo = MagicMock()
    return svc

@pytest.fixture
def valid_dm():
    return DemandManager(
        demand_manager_id=1,
        demand_id=1,
        technician_id=10,
        status="Pendente"
    )

@pytest.fixture
def valid_demand():
    return Demand(
        demand_id=1,
        demand_title="Falha no elevador",
        problem_description="Equipamento com falha",
        project_id="PROJ-001",
        status="Em Andamento",
        responsible_id=1,
        request_date=date(2026, 1, 1),
        estimated_time=8.0,
        technical_visit_reason="Visita Técnica",
        causal_sector="Fornecedor",
        causal_area="Fornecedor",
        root_cause="Atraso na entrega",
        equipment="Elevadores Agrícolas",
    )

@pytest.fixture
def valid_inputs():
    return [
        ExecutionInput(execution_date=date(2026, 5, 7),
                       action="Deslocamento", worked_hours=3.2, distance=276),
        ExecutionInput(execution_date=date(2026, 5, 7),
                       action="Prestacao de Servico", worked_hours=5.6, distance=0),
        ExecutionInput(execution_date=date(2026, 5, 8),
                       action="Prestacao de Servico", worked_hours=8.8, distance=0),
    ]


# ── ExecutionInput ────────────────────────────────────────────────────────────

def test_execution_input_invalid_action_should_fail():
    with pytest.raises(ValueError, match="Acao invalida"):
        ExecutionInput(execution_date=date(2026, 5, 7), action="Invalido", worked_hours=4.0)

def test_execution_input_negative_hours_should_fail():
    with pytest.raises(ValueError, match="Horas trabalhadas nao podem ser negativas"):
        ExecutionInput(execution_date=date(2026, 5, 7), action="Deslocamento", worked_hours=-1.0)

def test_execution_input_negative_distance_should_fail():
    with pytest.raises(ValueError, match="Distancia nao pode ser negativa"):
        ExecutionInput(execution_date=date(2026, 5, 7), action="Deslocamento",
                       worked_hours=3.0, distance=-1)

def test_execution_input_valid_is_accepted():
    inp = ExecutionInput(execution_date=date(2026, 5, 7),
                         action="Prestacao de Servico", worked_hours=8.8)
    assert inp.worked_hours == 8.8


# ── conclude ─────────────────────────────────────────────────────────────────

def test_conclude_dm_not_found_should_fail(service, valid_inputs):
    service.dm_repo.get_by_id.return_value = None
    with pytest.raises(ValueError, match="não encontrado"):
        service.conclude(99, valid_inputs)

def test_conclude_already_concluded_should_fail(service, valid_dm, valid_inputs):
    valid_dm.status = "Concluido"
    service.dm_repo.get_by_id.return_value = valid_dm
    with pytest.raises(ValueError, match="já foi concluída"):
        service.conclude(1, valid_inputs)

def test_conclude_empty_inputs_should_fail(service, valid_dm):
    service.dm_repo.get_by_id.return_value = valid_dm
    with pytest.raises(ValueError, match="Nenhum registro"):
        service.conclude(1, [])

def test_conclude_persists_execution_logs(service, valid_dm, valid_demand, valid_inputs):
    service.dm_repo.get_by_id.return_value = valid_dm
    service.dm_repo.get_by_demand.return_value = [valid_dm]
    service.demand_repo.get_by_id.return_value = valid_demand
    service.conclude(1, valid_inputs)
    service.el_repo.create_batch.assert_called_once()

def test_conclude_creates_correct_number_of_logs(service, valid_dm, valid_demand, valid_inputs):
    service.dm_repo.get_by_id.return_value = valid_dm
    service.dm_repo.get_by_demand.return_value = [valid_dm]
    service.demand_repo.get_by_id.return_value = valid_demand
    service.conclude(1, valid_inputs)
    logs = service.el_repo.create_batch.call_args[0][0]
    assert len(logs) == 3

def test_conclude_sets_dm_status_concluido(service, valid_dm, valid_demand, valid_inputs):
    service.dm_repo.get_by_id.return_value = valid_dm
    service.dm_repo.get_by_demand.return_value = [valid_dm]
    service.demand_repo.get_by_id.return_value = valid_demand
    service.conclude(1, valid_inputs)
    assert valid_dm.status == "Concluido"

def test_conclude_closes_demand_when_all_dms_concluded(service, valid_dm, valid_demand, valid_inputs):
    valid_dm.status = "Pendente"
    service.dm_repo.get_by_id.return_value = valid_dm
    service.dm_repo.get_by_demand.return_value = [valid_dm]
    service.demand_repo.get_by_id.return_value = valid_demand
    service.conclude(1, valid_inputs)
    assert valid_demand.status == "Concluída"

def test_conclude_keeps_demand_open_when_other_dm_pending(service, valid_dm, valid_demand, valid_inputs):
    other_dm = DemandManager(demand_manager_id=2, demand_id=1, technician_id=20, status="Pendente")
    service.dm_repo.get_by_id.return_value = valid_dm
    service.dm_repo.get_by_demand.return_value = [valid_dm, other_dm]
    service.demand_repo.get_by_id.return_value = valid_demand
    service.conclude(1, valid_inputs)
    assert valid_demand.status == "Em Andamento"

def test_conclude_commits(service, valid_dm, valid_demand, valid_inputs):
    service.dm_repo.get_by_id.return_value = valid_dm
    service.dm_repo.get_by_demand.return_value = [valid_dm]
    service.demand_repo.get_by_id.return_value = valid_demand
    service.conclude(1, valid_inputs)
    service.db.commit.assert_called_once()

def test_conclude_rollback_on_error(service, valid_dm, valid_inputs):
    service.dm_repo.get_by_id.return_value = valid_dm
    service.el_repo.create_batch.side_effect = Exception("db error")
    with pytest.raises(Exception):
        service.conclude(1, valid_inputs)
    service.db.rollback.assert_called_once()