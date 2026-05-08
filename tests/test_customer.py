# -*- coding: utf-8 -*-
import pytest
from backend.app.models.customer import Customer

@pytest.fixture
def valid_customer():
    return Customer(
        customer_id="CUST-001",
        customer_name="Cooperativa Exemplo Ltda",
        short_name="Exemplo",
        city_id=1,
        address="Rua das Flores, 123",
        segment="Farm",
        sub_segment="Feed",
        region="MT"
    )

def make_customer(valid_customer, **overrides):
    return Customer(**{**valid_customer.__dict__, **overrides})

# --- criacao basica ---

def test_customer_created_with_valid_fields(valid_customer):
    assert valid_customer.customer_id == "CUST-001"
    assert valid_customer.customer_name == "Cooperativa Exemplo Ltda"
    assert valid_customer.segment == "Farm"
    assert valid_customer.region == "MT"

# --- campos obrigatorios ---

def test_empty_customer_id_should_fail(valid_customer):
    with pytest.raises(ValueError, match="ID do cliente nao pode ser vazio"):
        make_customer(valid_customer, customer_id="")

def test_empty_customer_name_should_fail(valid_customer):
    with pytest.raises(ValueError, match="Nome do cliente nao pode ser vazio"):
        make_customer(valid_customer, customer_name="")

def test_empty_short_name_should_fail(valid_customer):
    with pytest.raises(ValueError, match="Nome curto nao pode ser vazio"):
        make_customer(valid_customer, short_name="")

def test_empty_address_should_fail(valid_customer):
    with pytest.raises(ValueError, match="Endereco nao pode ser vazio"):
        make_customer(valid_customer, address="")

# --- listas fechadas ---

def test_invalid_segment_should_fail(valid_customer):
    with pytest.raises(ValueError, match="Segmento invalido"):
        make_customer(valid_customer, segment="Industrial")

def test_all_valid_segments_are_accepted(valid_customer):
    for segment in ["Farm", "Commercial"]:
        c = make_customer(valid_customer, segment=segment)
        assert c.segment == segment

def test_invalid_sub_segment_should_fail(valid_customer):
    with pytest.raises(ValueError, match="Sub-segmento invalido"):
        make_customer(valid_customer, sub_segment="Pharma")

def test_all_valid_sub_segments_are_accepted(valid_customer):
    for sub in ["Farm", "Commercial", "Feed", "Fertilizer", "Fuel"]:
        c = make_customer(valid_customer, sub_segment=sub)
        assert c.sub_segment == sub

def test_invalid_region_should_fail(valid_customer):
    with pytest.raises(ValueError, match="Regiao invalida"):
        make_customer(valid_customer, region="SP")

def test_all_valid_regions_are_accepted(valid_customer):
    for region in ["MA/PI", "TO/BA", "MT", "MG/GO", "MS/SP", "PR,SC,RS"]:
        c = make_customer(valid_customer, region=region)
        assert c.region == region