# tests/test_demand_service.py
import pytest
from datetime import date
from unittest.mock import MagicMock

from backend.app.services.demand_service import DemandService
from backend.app.models.demand import Demand
from backend.app.models.demand_manager import DemandManager


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def service():
    svc = DemandService(db=MagicMock())
    svc.demand_repo = MagicMock()
    svc.dm_repo     = MagicMock()
    return svc

@pytest.fixture
def valid_demand():
    return Demand(
        demand_id=1,
        demand_title="Falha no elevador",
        problem_description="Equipamento com falha",
        project_id="PROJ-001",
        status="Aberta",
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
def valid_dm():
    return DemandManager(
        demand_manager_id=1,
        demand_id=1,
        technician_id=10,
        status="Pendente"
    )


# ── create_demand ─────────────────────────────────────────────────────────────

def test_create_demand_calls_repository(service, valid_demand):
    service.demand_repo.create.return_value = valid_demand
    service.create_demand(valid_demand)
    service.demand_repo.create.assert_called_once_with(valid_demand)

def test_create_demand_with_wrong_status_should_fail(service, valid_demand):
    valid_demand.status = "Em Andamento"
    with pytest.raises(ValueError, match="Nova demanda deve ter status 'Aberta'"):
        service.create_demand(valid_demand)

# ── get_demand ────────────────────────────────────────────────────────────────

def test_get_demand_returns_demand(service, valid_demand):
    service.demand_repo.get_by_id.return_value = valid_demand
    result = service.get_demand(1)
    assert result.demand_id == 1

def test_get_demand_not_found_should_fail(service):
    service.demand_repo.get_by_id.return_value = None
    with pytest.raises(ValueError, match="não encontrada"):
        service.get_demand(99)

# ── update_demand ─────────────────────────────────────────────────────────────

def test_update_demand_calls_repository(service, valid_demand):
    service.demand_repo.get_by_id.return_value = valid_demand
    service.demand_repo.update.return_value = valid_demand
    service.update_demand(valid_demand)
    service.demand_repo.update.assert_called_once_with(valid_demand)

def test_update_demand_not_found_should_fail(service, valid_demand):
    service.demand_repo.get_by_id.return_value = None
    with pytest.raises(ValueError, match="não encontrada"):
        service.update_demand(valid_demand)

# ── allocate_technician ───────────────────────────────────────────────────────

def test_allocate_technician_creates_demand_manager(service, valid_demand, valid_dm):
    service.demand_repo.get_by_id.return_value = valid_demand
    service.dm_repo.get_by_demand.return_value = []
    service.dm_repo.create.return_value = valid_dm
    service.allocate_technician(1, 10)
    service.dm_repo.create.assert_called_once()

def test_allocate_technician_sets_status_em_andamento(service, valid_demand, valid_dm):
    service.demand_repo.get_by_id.return_value = valid_demand
    service.dm_repo.get_by_demand.return_value = []
    service.dm_repo.create.return_value = valid_dm
    service.allocate_technician(1, 10)
    assert valid_demand.status == "Em Andamento"

def test_allocate_technician_already_allocated_should_fail(service, valid_demand, valid_dm):
    service.demand_repo.get_by_id.return_value = valid_demand
    service.dm_repo.get_by_demand.return_value = [valid_dm]
    with pytest.raises(ValueError, match="já está alocado"):
        service.allocate_technician(1, 10)

def test_allocate_technician_on_concluded_demand_should_fail(service, valid_demand):
    valid_demand.status = "Concluída"
    service.demand_repo.get_by_id.return_value = valid_demand
    with pytest.raises(ValueError, match="concluída"):
        service.allocate_technician(1, 10)

def test_allocate_technician_on_cancelled_demand_should_fail(service, valid_demand):
    valid_demand.status = "Cancelada"
    service.demand_repo.get_by_id.return_value = valid_demand
    with pytest.raises(ValueError, match="cancelada"):
        service.allocate_technician(1, 10)

def test_allocate_technician_rollback_on_error(service, valid_demand):
    service.demand_repo.get_by_id.return_value = valid_demand
    service.dm_repo.get_by_demand.return_value = []
    service.dm_repo.create.side_effect = Exception("db error")
    with pytest.raises(Exception):
        service.allocate_technician(1, 10)
    service.db.rollback.assert_called_once()

# ── deallocate_technician ─────────────────────────────────────────────────────

def test_deallocate_only_technician_sets_status_aberta(service, valid_demand, valid_dm):
    service.demand_repo.get_by_id.return_value = valid_demand
    service.dm_repo.get_by_demand.return_value = [valid_dm]
    result = service.deallocate_technician(1, 10)
    assert result.status == "Aberta"

def test_deallocate_technician_not_allocated_should_fail(service, valid_demand):
    service.demand_repo.get_by_id.return_value = valid_demand
    service.dm_repo.get_by_demand.return_value = []
    with pytest.raises(ValueError, match="não está alocado"):
        service.deallocate_technician(1, 10)

def test_deallocate_concluded_technician_should_fail(service, valid_demand, valid_dm):
    valid_dm.status = "Concluido"
    service.demand_repo.get_by_id.return_value = valid_demand
    service.dm_repo.get_by_demand.return_value = [valid_dm]
    with pytest.raises(ValueError, match="já concluiu"):
        service.deallocate_technician(1, 10)

def test_deallocate_technician_others_concluded_sets_status_concluida(service, valid_demand, valid_dm):
    other_dm = DemandManager(demand_manager_id=2, demand_id=1, technician_id=20, status="Concluido")
    service.demand_repo.get_by_id.return_value = valid_demand
    service.dm_repo.get_by_demand.return_value = [valid_dm, other_dm]
    result = service.deallocate_technician(1, 10)
    assert result.status == "Concluída"

def test_deallocate_technician_others_pending_keeps_status_em_andamento(service, valid_demand, valid_dm):
    other_dm = DemandManager(demand_manager_id=2, demand_id=1, technician_id=20, status="Pendente")
    valid_demand.status = "Em Andamento"
    service.demand_repo.get_by_id.return_value = valid_demand
    service.dm_repo.get_by_demand.return_value = [valid_dm, other_dm]
    result = service.deallocate_technician(1, 10)
    assert result.status == "Em Andamento"

def test_deallocate_technician_rollback_on_error(service, valid_demand, valid_dm):
    service.demand_repo.get_by_id.return_value = valid_demand
    service.dm_repo.get_by_demand.return_value = [valid_dm]
    service.dm_repo.soft_delete.side_effect = Exception("db error")
    with pytest.raises(Exception):
        service.deallocate_technician(1, 10)
    service.db.rollback.assert_called_once()