# -*- coding: utf-8 -*-
from datetime import date
import pytest
from backend.app.models.schedule_gantt import ScheduleGantt

@pytest.fixture
def valid_schedule_gantt():
    return ScheduleGantt(
        version_id=1,
        demand_manager_id=10,
        technician_id=5,
        start_date=date(2026, 5, 8),
        finish_date=date(2026, 5, 12)
    )

def make_schedule_gantt(valid_schedule_gantt, **overrides):
    return ScheduleGantt(**{**valid_schedule_gantt.__dict__, **overrides})

# --- criacao basica ---

def test_schedule_gantt_created_with_valid_fields(valid_schedule_gantt):
    assert valid_schedule_gantt.version_id == 1
    assert valid_schedule_gantt.demand_manager_id == 10
    assert valid_schedule_gantt.technician_id == 5
    assert valid_schedule_gantt.start_date == date(2026, 5, 8)
    assert valid_schedule_gantt.finish_date == date(2026, 5, 12)
    assert valid_schedule_gantt.schedule_gantt_id is None

# --- version_id ---

def test_zero_version_id_should_fail(valid_schedule_gantt):
    with pytest.raises(ValueError, match="Version ID deve ser maior que zero"):
        make_schedule_gantt(valid_schedule_gantt, version_id=0)

def test_negative_version_id_should_fail(valid_schedule_gantt):
    with pytest.raises(ValueError, match="Version ID deve ser maior que zero"):
        make_schedule_gantt(valid_schedule_gantt, version_id=-1)

# --- demand_manager_id ---

def test_zero_demand_manager_id_should_fail(valid_schedule_gantt):
    with pytest.raises(ValueError, match="Demand Manager ID deve ser maior que zero"):
        make_schedule_gantt(valid_schedule_gantt, demand_manager_id=0)

def test_negative_demand_manager_id_should_fail(valid_schedule_gantt):
    with pytest.raises(ValueError, match="Demand Manager ID deve ser maior que zero"):
        make_schedule_gantt(valid_schedule_gantt, demand_manager_id=-10)

# --- technician_id ---

def test_zero_technician_id_should_fail(valid_schedule_gantt):
    with pytest.raises(ValueError, match="Technician ID deve ser maior que zero"):
        make_schedule_gantt(valid_schedule_gantt, technician_id=0)

def test_negative_technician_id_should_fail(valid_schedule_gantt):
    with pytest.raises(ValueError, match="Technician ID deve ser maior que zero"):
        make_schedule_gantt(valid_schedule_gantt, technician_id=-5)

# --- start_date e finish_date ---

def test_finish_date_before_start_date_should_fail(valid_schedule_gantt):
    with pytest.raises(ValueError, match="Data de conclusao nao pode ser anterior a data de inicio"):
        make_schedule_gantt(
            valid_schedule_gantt,
            start_date=date(2026, 5, 12),
            finish_date=date(2026, 5, 8)
        )

def test_start_date_equals_finish_date_is_accepted(valid_schedule_gantt):
    """Uma demanda pode ser completada no mesmo dia."""
    sg = make_schedule_gantt(
        valid_schedule_gantt,
        start_date=date(2026, 5, 8),
        finish_date=date(2026, 5, 8)
    )
    assert sg.start_date == sg.finish_date

def test_multi_day_span_is_accepted(valid_schedule_gantt):
    """Demandas que duram vários dias são o caso comum."""
    sg = make_schedule_gantt(
        valid_schedule_gantt,
        start_date=date(2026, 5, 8),
        finish_date=date(2026, 5, 22)
    )
    assert sg.finish_date > sg.start_date

# --- schedule_gantt_id ---

def test_schedule_gantt_id_defaults_to_none(valid_schedule_gantt):
    assert valid_schedule_gantt.schedule_gantt_id is None

def test_schedule_gantt_id_can_be_set_after_creation(valid_schedule_gantt):
    valid_schedule_gantt.schedule_gantt_id = 50
    assert valid_schedule_gantt.schedule_gantt_id == 50

# --- cenarios de negocio ---

def test_gantt_item_represents_demand_scheduling():
    """Um ScheduleGantt resume toda a execução de uma demanda no gráfico Gantt."""
    sg = ScheduleGantt(
        version_id=1,
        demand_manager_id=10,
        technician_id=5,
        start_date=date(2026, 5, 8),
        finish_date=date(2026, 5, 15)
    )
    days_scheduled = (sg.finish_date - sg.start_date).days
    assert days_scheduled == 7  # 8 dias inclusive

def test_multiple_gantt_items_same_technician_different_demands():
    """Um técnico pode ter múltiplas demandas em paralelo ou sequência."""
    tech_id = 5
    sg1 = ScheduleGantt(
        version_id=1, demand_manager_id=10, technician_id=tech_id,
        start_date=date(2026, 5, 8), finish_date=date(2026, 5, 12)
    )
    sg2 = ScheduleGantt(
        version_id=1, demand_manager_id=11, technician_id=tech_id,
        start_date=date(2026, 5, 13), finish_date=date(2026, 5, 17)
    )
    assert sg1.technician_id == sg2.technician_id
    assert sg1.demand_manager_id != sg2.demand_manager_id
    assert sg1.finish_date < sg2.start_date  # sequência

def test_gantt_for_single_day_demand():
    """Demandas rápidas podem caber em um único dia."""
    sg = ScheduleGantt(
        version_id=1,
        demand_manager_id=10,
        technician_id=5,
        start_date=date(2026, 5, 8),
        finish_date=date(2026, 5, 8)
    )
    assert sg.start_date == sg.finish_date
    assert (sg.finish_date - sg.start_date).days == 0

def test_gantt_different_versions_same_demand():
    """Ao replanejar, uma demanda pode ter diferentes datas em versões diferentes."""
    sg_v1 = ScheduleGantt(
        version_id=1, demand_manager_id=10, technician_id=5,
        start_date=date(2026, 5, 8), finish_date=date(2026, 5, 12)
    )
    sg_v2 = ScheduleGantt(
        version_id=2, demand_manager_id=10, technician_id=5,
        start_date=date(2026, 5, 10), finish_date=date(2026, 5, 14)
    )
    # Mesma demanda, versões diferentes, datas diferentes
    assert sg_v1.demand_manager_id == sg_v2.demand_manager_id
    assert sg_v1.version_id != sg_v2.version_id
    assert sg_v1.start_date != sg_v2.start_date