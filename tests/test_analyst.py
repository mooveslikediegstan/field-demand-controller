# -*- coding: utf-8 -*-
from datetime import date
from typing import Optional
import pytest
from backend.app.models.analyst import Analyst

@pytest.fixture
def valid_analyst():
    return Analyst(
        analyst_name="Maria Silva",
        email="maria.silva@empresa.com",
        contact="+55 11 99999-9999",
        creation_date=date(2024, 1, 15),
        status="active"
    )

def make_analyst(valid_analyst, **overrides):
    return Analyst(**{**valid_analyst.__dict__, **overrides})

# --- criacao basica ---

def test_analyst_created_with_valid_fields(valid_analyst):
    assert valid_analyst.analyst_name == "Maria Silva"
    assert valid_analyst.status == "active"
    assert valid_analyst.analyst_id is None
    assert valid_analyst.valid_to_date is None

# --- status ---

def test_invalid_status_should_fail(valid_analyst):
    with pytest.raises(ValueError, match="Status invalido"):
        make_analyst(valid_analyst, status="pending")

def test_all_valid_statuses_are_accepted(valid_analyst):
    for status in ["active", "inactive"]:
        a = make_analyst(valid_analyst, status=status)
        assert a.status == status

# --- valid_to_date ---

def test_inactive_analyst_with_valid_to_date_is_accepted(valid_analyst):
    a = make_analyst(valid_analyst, status="inactive",
                     valid_to_date=date(2026, 1, 1))
    assert a.valid_to_date == date(2026, 1, 1)

def test_active_analyst_with_valid_to_date_is_accepted(valid_analyst):
    a = make_analyst(valid_analyst, valid_to_date=date(2099, 12, 31))
    assert a.valid_to_date == date(2099, 12, 31)

def test_valid_to_date_before_creation_date_should_fail(valid_analyst):
    with pytest.raises(ValueError, match="Data de validade nao pode ser anterior"):
        make_analyst(valid_analyst, valid_to_date=date(2023, 1, 1))

def test_valid_to_date_equal_to_creation_date_should_fail(valid_analyst):
    with pytest.raises(ValueError, match="Data de validade nao pode ser anterior"):
        make_analyst(valid_analyst, valid_to_date=date(2024, 1, 15))

# --- campos obrigatorios ---

def test_empty_name_should_fail(valid_analyst):
    with pytest.raises(ValueError, match="Nome do analista nao pode ser vazio"):
        make_analyst(valid_analyst, analyst_name="")

def test_empty_email_should_fail(valid_analyst):
    with pytest.raises(ValueError, match="Email nao pode ser vazio"):
        make_analyst(valid_analyst, email="")

def test_empty_contact_should_fail(valid_analyst):
    with pytest.raises(ValueError, match="Contato nao pode ser vazio"):
        make_analyst(valid_analyst, contact="")

# --- normalizacao ---

def test_status_normalized_to_lowercase(valid_analyst):
    a = make_analyst(valid_analyst, status="ACTIVE")
    assert a.status == "active"

def test_email_normalized_to_lowercase(valid_analyst):
    a = make_analyst(valid_analyst, email="Maria.Silva@Empresa.COM")
    assert a.email == "maria.silva@empresa.com"