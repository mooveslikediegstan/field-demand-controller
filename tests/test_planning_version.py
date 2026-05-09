# -*- coding: utf-8 -*-
from datetime import datetime
import pytest
from backend.app.models.planning_version import PlanningVersion

@pytest.fixture
def valid_planning_version():
    return PlanningVersion(
        technician_id=1,
        created_at=datetime(2026, 5, 8, 10, 30, 0),
        is_active=True
    )

def make_planning_version(valid_planning_version, **overrides):
    return PlanningVersion(**{**valid_planning_version.__dict__, **overrides})

# --- criacao basica ---

def test_planning_version_created_with_valid_fields(valid_planning_version):
    assert valid_planning_version.technician_id == 1
    assert valid_planning_version.created_at == datetime(2026, 5, 8, 10, 30, 0)
    assert valid_planning_version.is_active == True
    assert valid_planning_version.version_id is None

# --- technician_id ---

def test_zero_technician_id_should_fail(valid_planning_version):
    with pytest.raises(ValueError, match="Technician ID deve ser maior que zero"):
        make_planning_version(valid_planning_version, technician_id=0)

def test_negative_technician_id_should_fail(valid_planning_version):
    with pytest.raises(ValueError, match="Technician ID deve ser maior que zero"):
        make_planning_version(valid_planning_version, technician_id=-5)

def test_positive_technician_id_is_accepted(valid_planning_version):
    pv = make_planning_version(valid_planning_version, technician_id=99)
    assert pv.technician_id == 99

# --- created_at ---

def test_none_created_at_should_fail(valid_planning_version):
    with pytest.raises(ValueError, match="Data de criacao nao pode ser vazia"):
        make_planning_version(valid_planning_version, created_at=None)

def test_valid_created_at_is_accepted(valid_planning_version):
    dt = datetime(2025, 1, 1, 0, 0, 0)
    pv = make_planning_version(valid_planning_version, created_at=dt)
    assert pv.created_at == dt

# --- is_active ---

def test_is_active_defaults_to_true(valid_planning_version):
    assert valid_planning_version.is_active == True

def test_is_active_can_be_false():
    pv = PlanningVersion(
        technician_id=1,
        created_at=datetime(2026, 5, 8, 10, 30, 0),
        is_active=False
    )
    assert pv.is_active == False

def test_is_active_can_be_toggled(valid_planning_version):
    pv = make_planning_version(valid_planning_version, is_active=False)
    assert pv.is_active == False

# --- version_id ---

def test_version_id_defaults_to_none(valid_planning_version):
    assert valid_planning_version.version_id is None

def test_version_id_can_be_set_after_creation(valid_planning_version):
    valid_planning_version.version_id = 42
    assert valid_planning_version.version_id == 42

# --- cenarios de negocio ---

def test_new_version_always_starts_active(valid_planning_version):
    """Ao criar uma nova versão, ela sempre começa ativa."""
    assert valid_planning_version.is_active == True
    assert valid_planning_version.version_id is None

def test_multiple_versions_same_technician_can_exist():
    """Múltiplas versões do mesmo técnico podem existir (só uma ativa por vez)."""
    tech_id = 5
    pv1 = PlanningVersion(
        technician_id=tech_id,
        created_at=datetime(2026, 5, 1, 10, 0, 0),
        is_active=False
    )
    pv2 = PlanningVersion(
        technician_id=tech_id,
        created_at=datetime(2026, 5, 8, 10, 0, 0),
        is_active=True
    )
    assert pv1.technician_id == pv2.technician_id
    assert pv1.is_active == False
    assert pv2.is_active == True

def test_planning_version_tracks_creation_time(valid_planning_version):
    """A criação deve registrar exatamente quando o planejamento foi feito."""
    creation_time = datetime(2026, 5, 8, 14, 30, 15)
    pv = make_planning_version(valid_planning_version, created_at=creation_time)
    assert pv.created_at == creation_time