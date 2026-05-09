# -*- coding: utf-8 -*-
"""
Testes do QueueService.

Estratégia: mock do banco de dados — sem conexão real ao PostgreSQL.
O QueueService recebe uma Session; nos testes passamos um MagicMock no lugar.
Isso mantém os testes rápidos, isolados e sem dependência de infraestrutura.
"""
import pytest
from unittest.mock import MagicMock, patch
from datetime import date

from backend.app.services.queue_service import QueueService
from backend.app.schemas.schedule_schemas import SaveSequenceRequest


# ── HELPERS DE FIXTURE ─────────────────────────────────────────────────────────

def make_dm_orm(demand_manager_id, demand_id, technician_id=10,
                next_id=None, status="Pendente",
                start_date=None, finish_date=None,
                travel_time=None, travel_distance=None,
                is_deleted=False):
    """Cria um objeto simples que imita DemandManagerORM."""
    obj = MagicMock()
    obj.demand_manager_id      = demand_manager_id
    obj.demand_id              = demand_id
    obj.technician_id          = technician_id
    obj.next_demand_manager_id = next_id
    obj.status                 = status
    obj.start_date             = start_date
    obj.finish_date            = finish_date
    obj.travel_time            = travel_time
    obj.travel_distance        = travel_distance
    obj.is_deleted             = is_deleted
    return obj


def make_demand_orm(demand_id, demand_title="Demanda Teste",
                    project_id="PROJ-001", estimated_time=8.0):
    """Cria um objeto simples que imita DemandORM."""
    obj = MagicMock()
    obj.demand_id      = demand_id
    obj.demand_title   = demand_title
    obj.project_id     = project_id
    obj.estimated_time = estimated_time
    return obj


def make_service_with_queue(rows: list[tuple]) -> QueueService:
    """
    Cria um QueueService com o banco mockado.
    `rows` é uma lista de tuplas (dm_orm, demand_orm) — resultado do JOIN.
    """
    db = MagicMock()
    # Encadeia os mocks para imitar db.query(...).join(...).filter(...).all()
    db.query.return_value.join.return_value.filter.return_value.all.return_value = rows
    return QueueService(db)


# ── FIXTURES ───────────────────────────────────────────────────────────────────

@pytest.fixture
def dm1():
    return make_dm_orm(demand_manager_id=1, demand_id=10, next_id=2)

@pytest.fixture
def dm2():
    return make_dm_orm(demand_manager_id=2, demand_id=20, next_id=3)

@pytest.fixture
def dm3():
    return make_dm_orm(demand_manager_id=3, demand_id=30, next_id=None)

@pytest.fixture
def d1():
    return make_demand_orm(demand_id=10, demand_title="Demanda A", project_id="PROJ-001", estimated_time=8.0)

@pytest.fixture
def d2():
    return make_demand_orm(demand_id=20, demand_title="Demanda B", project_id="PROJ-002", estimated_time=16.0)

@pytest.fixture
def d3():
    return make_demand_orm(demand_id=30, demand_title="Demanda C", project_id="PROJ-003", estimated_time=4.0)


# ── GET_QUEUE ──────────────────────────────────────────────────────────────────

def test_get_queue_returns_correct_count(dm1, dm2, dm3, d1, d2, d3):
    service = make_service_with_queue([(dm1, d1), (dm2, d2), (dm3, d3)])
    result  = service.get_queue(technician_id=10)
    assert len(result) == 3

def test_get_queue_returns_empty_for_no_demands():
    service = make_service_with_queue([])
    result  = service.get_queue(technician_id=10)
    assert result == []

def test_get_queue_first_item_is_head(dm1, dm2, dm3, d1, d2, d3):
    # dm1 -> dm2 -> dm3; head deve ser dm1
    service = make_service_with_queue([(dm3, d3), (dm1, d1), (dm2, d2)])
    result  = service.get_queue(technician_id=10)
    assert result[0].demand_manager_id == 1

def test_get_queue_order_matches_linked_list(dm1, dm2, dm3, d1, d2, d3):
    service = make_service_with_queue([(dm3, d3), (dm1, d1), (dm2, d2)])
    result  = service.get_queue(technician_id=10)
    ids     = [r.demand_manager_id for r in result]
    assert ids == [1, 2, 3]

def test_get_queue_demand_title_is_populated(dm1, d1):
    service = make_service_with_queue([(dm1, d1)])
    result  = service.get_queue(technician_id=10)
    assert result[0].demand_title == "Demanda A"

def test_get_queue_project_id_is_populated(dm1, d1):
    service = make_service_with_queue([(dm1, d1)])
    result  = service.get_queue(technician_id=10)
    assert result[0].project_id == "PROJ-001"

def test_get_queue_estimated_time_is_populated(dm1, d1):
    service = make_service_with_queue([(dm1, d1)])
    result  = service.get_queue(technician_id=10)
    assert result[0].estimated_time == 8.0

def test_get_queue_status_is_populated(dm1, d1):
    service = make_service_with_queue([(dm1, d1)])
    result  = service.get_queue(technician_id=10)
    assert result[0].status == "Pendente"

def test_get_queue_single_item_has_correct_demand_manager_id(dm1, d1):
    service = make_service_with_queue([(dm1, d1)])
    result  = service.get_queue(technician_id=10)
    assert result[0].demand_manager_id == 1


# ── _FIND_HEAD ─────────────────────────────────────────────────────────────────

def test_find_head_identifies_correct_node(dm1, dm2, dm3):
    db      = MagicMock()
    service = QueueService(db)
    from backend.app.models.demand_manager import DemandManager
    models  = [
        DemandManager(demand_id=10, technician_id=10, status="Pendente", demand_manager_id=1, next_demand_manager_id=2),
        DemandManager(demand_id=20, technician_id=10, status="Pendente", demand_manager_id=2, next_demand_manager_id=3),
        DemandManager(demand_id=30, technician_id=10, status="Pendente", demand_manager_id=3, next_demand_manager_id=None),
    ]
    head = service._find_head(models)
    assert head == 1

def test_find_head_returns_none_for_empty_list():
    db      = MagicMock()
    service = QueueService(db)
    head    = service._find_head([])
    assert head is None


# ── SAVE_SEQUENCE ──────────────────────────────────────────────────────────────

def _make_service_for_save(dm_orms: list, queue_rows: list[tuple]) -> QueueService:
    """
    Mock especializado para save_sequence:
    - Primeira query (filter sem JOIN): retorna dm_orms
    - Segunda query (get_queue interno): retorna queue_rows
    """
    db = MagicMock()

    # save_sequence faz db.query(DemandManagerORM).filter(...).all()
    filter_mock = MagicMock()
    filter_mock.all.return_value = dm_orms

    # get_queue faz db.query(DemandManagerORM, DemandORM).join(...).filter(...).all()
    join_filter_mock = MagicMock()
    join_filter_mock.all.return_value = queue_rows

    join_mock = MagicMock()
    join_mock.filter.return_value = join_filter_mock

    def query_side_effect(*args):
        mock = MagicMock()
        if len(args) == 1:
            # query(DemandManagerORM) — usado no save_sequence
            mock.filter.return_value = filter_mock
        else:
            # query(DemandManagerORM, DemandORM) — usado no get_queue
            mock.join.return_value = join_mock
        return mock

    db.query.side_effect = query_side_effect
    return QueueService(db)


def test_save_sequence_updates_next_links(d1, d2, d3):
    dm_a = make_dm_orm(demand_manager_id=1, demand_id=10, next_id=2)
    dm_b = make_dm_orm(demand_manager_id=2, demand_id=20, next_id=3)
    dm_c = make_dm_orm(demand_manager_id=3, demand_id=30, next_id=None)

    service = _make_service_for_save(
        dm_orms    = [dm_a, dm_b, dm_c],
        queue_rows = [(dm_c, d3), (dm_b, d2), (dm_a, d1)]   # nova ordem: 3->2->1
    )
    payload = SaveSequenceRequest(ordered_demand_manager_ids=[3, 2, 1])
    service.save_sequence(technician_id=10, payload=payload)

    # dm_c (id=3) agora aponta para dm_b (id=2)
    assert dm_c.next_demand_manager_id == 2

def test_save_sequence_last_item_next_is_none(d1, d2, d3):
    dm_a = make_dm_orm(demand_manager_id=1, demand_id=10, next_id=2)
    dm_b = make_dm_orm(demand_manager_id=2, demand_id=20, next_id=3)
    dm_c = make_dm_orm(demand_manager_id=3, demand_id=30, next_id=None)

    service = _make_service_for_save(
        dm_orms    = [dm_a, dm_b, dm_c],
        queue_rows = [(dm_a, d1), (dm_b, d2), (dm_c, d3)]
    )
    payload = SaveSequenceRequest(ordered_demand_manager_ids=[3, 2, 1])
    service.save_sequence(technician_id=10, payload=payload)

    # dm_a (id=1) é o último — next deve ser None
    assert dm_a.next_demand_manager_id is None

def test_save_sequence_commits_to_db(d1):
    dm_a    = make_dm_orm(demand_manager_id=1, demand_id=10)
    service = _make_service_for_save(
        dm_orms    = [dm_a],
        queue_rows = [(dm_a, d1)]
    )
    payload = SaveSequenceRequest(ordered_demand_manager_ids=[1])
    service.save_sequence(technician_id=10, payload=payload)

    service.db.commit.assert_called_once()

def test_save_sequence_raises_for_foreign_dm_id(d1):
    dm_a    = make_dm_orm(demand_manager_id=1, demand_id=10)
    service = _make_service_for_save(
        dm_orms    = [dm_a],
        queue_rows = [(dm_a, d1)]
    )
    # ID 99 não pertence ao técnico 10
    payload = SaveSequenceRequest(ordered_demand_manager_ids=[1, 99])
    with pytest.raises(ValueError, match="nao pertence ao tecnico"):
        service.save_sequence(technician_id=10, payload=payload)

def test_save_sequence_returns_updated_queue(d1, d2):
    dm_a = make_dm_orm(demand_manager_id=1, demand_id=10, next_id=2)
    dm_b = make_dm_orm(demand_manager_id=2, demand_id=20, next_id=None)

    service = _make_service_for_save(
        dm_orms    = [dm_a, dm_b],
        queue_rows = [(dm_b, d2), (dm_a, d1)]
    )
    payload = SaveSequenceRequest(ordered_demand_manager_ids=[2, 1])
    result  = service.save_sequence(technician_id=10, payload=payload)

    assert isinstance(result, list)
    assert len(result) == 2