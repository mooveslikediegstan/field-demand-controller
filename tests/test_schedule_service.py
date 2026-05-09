# tests/test_schedule_service.py
import pytest
from datetime import date, datetime, timezone
from unittest.mock import MagicMock

from backend.app.services.schedule_service import ScheduleService
from backend.app.models.technician import Technician
from backend.app.models.demand_queue import DemandQueue
from backend.app.models.demand_manager import DemandManager
from backend.app.models.demand import Demand
from backend.app.models.project import Project
from backend.app.models.customer import Customer
from backend.app.models.city import City
from backend.app.models.planning_version import PlanningVersion

# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def service():
    svc = ScheduleService(db=MagicMock())
    svc.dm_repo               = MagicMock()
    svc.planning_version_repo = MagicMock()
    svc.schedule_item_repo    = MagicMock()
    svc.schedule_gantt_repo   = MagicMock()
    svc.city_repo             = MagicMock()
    svc.demand_repo           = MagicMock()
    svc.project_repo          = MagicMock()
    svc.customer_repo         = MagicMock()
    return svc

@pytest.fixture
def technician():
    return Technician(
        technician_id=10,
        technician_name="Carlos Silva",
        creation_date=date(2024, 1, 15),
        status="ativo",
        base_location_city_id=1,
        current_location_city_id=1,
        daily_capacity=8.0,
        position="Lider"
    )

@pytest.fixture
def city():
    return City(
        city_id=1,
        city_name="Sao Paulo",
        state="SP",
        country="Brasil",
        geolocation_lat=-23.5505,
        geolocation_lon=-46.6333
    )

@pytest.fixture
def demand_queue():
    dm1 = DemandManager(demand_id=1, technician_id=10, status="Pendente", demand_manager_id=1)
    dm2 = DemandManager(demand_id=2, technician_id=10, status="Pendente", demand_manager_id=2)
    queue = DemandQueue(technician_id=10, head_id=1, demands=[dm1, dm2])
    queue.rebuild_links()
    return queue

@pytest.fixture
def mock_demand():
    def _make(demand_id, project_id="PROJ-001", estimated_time=4.0):
        return Demand(
            demand_id=demand_id,
            demand_title="Falha",
            problem_description="Desc",
            project_id=project_id,
            status="Aberta",
            responsible_id=1,
            request_date=date(2026, 1, 1),
            estimated_time=estimated_time,
            technical_visit_reason="Visita Técnica",
            causal_sector="Fornecedor",
            causal_area="Fornecedor",
            root_cause="Atraso na entrega",
            equipment="Elevadores Agrícolas",
        )
    return _make

@pytest.fixture
def mock_project():
    return Project(project_id="PROJ-001", project_name="Projeto A", customer_id="CUST-001")

@pytest.fixture
def mock_customer():
    return Customer(
        customer_id="CUST-001", customer_name="Coop A", short_name="A",
        city_id=1, address="Rua X", segment="Farm", sub_segment="Feed", region="MT"
    )

@pytest.fixture
def new_version():
    return PlanningVersion(version_id=99, technician_id=10,
                           created_at=datetime.now(timezone.utc), is_active=True)

# ── Helper ────────────────────────────────────────────────────────────────────

def setup_service_mocks(service, technician, city, mock_demand, mock_project, mock_customer, new_version):
    service.city_repo.get_by_id.return_value         = city
    service.planning_version_repo.create.return_value = new_version
    service.demand_repo.get_by_id.side_effect        = lambda did: mock_demand(did)
    service.project_repo.get_by_id.return_value      = mock_project
    service.customer_repo.get_by_id.return_value     = mock_customer

# ── Testes: save_sequence ─────────────────────────────────────────────────────

def test_save_sequence_returns_planning_version(
        service, technician, city, mock_demand, mock_project, mock_customer, demand_queue, new_version):
    setup_service_mocks(service, technician, city, mock_demand, mock_project, mock_customer, new_version)
    result = service.save_sequence(technician, demand_queue, date(2026, 5, 7))
    assert result.version_id == 99

def test_save_sequence_deactivates_previous_version(
        service, technician, city, mock_demand, mock_project, mock_customer, demand_queue, new_version):
    setup_service_mocks(service, technician, city, mock_demand, mock_project, mock_customer, new_version)
    service.save_sequence(technician, demand_queue, date(2026, 5, 7))
    service.planning_version_repo.deactivate_all_by_technician.assert_called_once_with(technician.technician_id)

def test_save_sequence_creates_new_version(
        service, technician, city, mock_demand, mock_project, mock_customer, demand_queue, new_version):
    setup_service_mocks(service, technician, city, mock_demand, mock_project, mock_customer, new_version)
    service.save_sequence(technician, demand_queue, date(2026, 5, 7))
    service.planning_version_repo.create.assert_called_once()

def test_save_sequence_persists_schedule_items(
        service, technician, city, mock_demand, mock_project, mock_customer, demand_queue, new_version):
    setup_service_mocks(service, technician, city, mock_demand, mock_project, mock_customer, new_version)
    service.save_sequence(technician, demand_queue, date(2026, 5, 7))
    service.schedule_item_repo.create_batch.assert_called_once()

def test_save_sequence_persists_gantt(
        service, technician, city, mock_demand, mock_project, mock_customer, demand_queue, new_version):
    setup_service_mocks(service, technician, city, mock_demand, mock_project, mock_customer, new_version)
    service.save_sequence(technician, demand_queue, date(2026, 5, 7))
    service.schedule_gantt_repo.create_batch.assert_called_once()

def test_save_sequence_commits(
        service, technician, city, mock_demand, mock_project, mock_customer, demand_queue, new_version):
    setup_service_mocks(service, technician, city, mock_demand, mock_project, mock_customer, new_version)
    service.save_sequence(technician, demand_queue, date(2026, 5, 7))
    service.db.commit.assert_called_once()

def test_save_sequence_rollback_on_error(service, technician, demand_queue):
    service.planning_version_repo.deactivate_all_by_technician.side_effect = Exception("db error")
    with pytest.raises(Exception):
        service.save_sequence(technician, demand_queue, date(2026, 5, 7))
    service.db.rollback.assert_called_once()

# ── Testes: _build_gantt ──────────────────────────────────────────────────────

def test_build_gantt_start_date_includes_travel(service):
    from backend.app.models.schedule_item import ScheduleItem
    items = [
        ScheduleItem(demand_manager_id=1, technician_id=10,
                     scheduled_date=date(2026, 5, 7), action="Deslocamento",
                     work_time=3.0, sequence_position=1, distance=200),
        ScheduleItem(demand_manager_id=1, technician_id=10,
                     scheduled_date=date(2026, 5, 7), action="Prestacao de Servico",
                     work_time=5.0, sequence_position=2, distance=0),
    ]
    gantt = service._build_gantt(version_id=1, technician_id=10, items=items)
    assert gantt[0].start_date == date(2026, 5, 7)

def test_build_gantt_finish_date_is_last_service_date(service):
    from backend.app.models.schedule_item import ScheduleItem
    items = [
        ScheduleItem(demand_manager_id=1, technician_id=10,
                     scheduled_date=date(2026, 5, 7), action="Deslocamento",
                     work_time=3.0, sequence_position=1, distance=200),
        ScheduleItem(demand_manager_id=1, technician_id=10,
                     scheduled_date=date(2026, 5, 8), action="Prestacao de Servico",
                     work_time=8.0, sequence_position=2, distance=0),
        ScheduleItem(demand_manager_id=1, technician_id=10,
                     scheduled_date=date(2026, 5, 9), action="Prestacao de Servico",
                     work_time=8.0, sequence_position=3, distance=0),
    ]
    gantt = service._build_gantt(version_id=1, technician_id=10, items=items)
    assert gantt[0].finish_date == date(2026, 5, 9)

def test_build_gantt_generates_one_entry_per_demand(service):
    from backend.app.models.schedule_item import ScheduleItem
    items = [
        ScheduleItem(demand_manager_id=1, technician_id=10,
                     scheduled_date=date(2026, 5, 7), action="Prestacao de Servico",
                     work_time=4.0, sequence_position=1, distance=0),
        ScheduleItem(demand_manager_id=2, technician_id=10,
                     scheduled_date=date(2026, 5, 8), action="Prestacao de Servico",
                     work_time=4.0, sequence_position=2, distance=0),
    ]
    gantt = service._build_gantt(version_id=1, technician_id=10, items=items)
    assert len(gantt) == 2