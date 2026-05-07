# -*- coding: utf-8 -*-
from datetime import date
import pytest

from backend.app.models.demand import Demand

@pytest.fixture
def valid_demand():
    return Demand(
        request_date=date(2026, 5, 6),
        responsible_id=1,
        project_id="PROJ-001",
        estimated_time=36.0,
        demand_title="Falha no acionamento do elevador",
        problem_description="Equipamento com falha no acionamento",
        technical_visit_reason="Manutencao Corretiva",
        causal_sector="Fornecedor",
        causal_area="Fornecedor",
        root_cause="Atraso na entrega",
        equipment="Elevadores Agrícolas",
        status="Aberta"
    )

def make_demand(valid_demand, **overrides):
    return Demand(**{**valid_demand.__dict__, **overrides})

# --- criacao basica ---

def test_demand_created_with_valid_fields(valid_demand):
    assert valid_demand.demand_title == "Falha no acionamento do elevador"
    assert valid_demand.problem_description == "Equipamento com falha no acionamento"
    assert valid_demand.project_id == "PROJ-001"
    assert valid_demand.status == "Aberta"
    assert valid_demand.estimated_time == 36.0


# --- status ---

def test_invalid_status_should_fail(valid_demand):
    with pytest.raises(ValueError, match="Status invalido"):
        make_demand(valid_demand, status="Pendente")

def test_all_valid_statuses_are_accepted(valid_demand):
    for status in ["Aberta", "Em Andamento", "Concluida", "Cancelada"]:
        demand = make_demand(valid_demand, status=status)
        assert demand.status == status

# --- estimated_time ---

def test_zero_estimated_time_should_fail(valid_demand):
    with pytest.raises(ValueError, match="Tempo estimado deve ser maior que zero"):
        make_demand(valid_demand, estimated_time=0.0)

def test_negative_estimated_time_should_fail(valid_demand):
    with pytest.raises(ValueError, match="Tempo estimado deve ser maior que zero"):
        make_demand(valid_demand, estimated_time=-2.0)

# --- actual_time ---

def test_actual_time_zero_is_accepted(valid_demand):
    demand = make_demand(valid_demand, actual_time=0.0)
    assert demand.actual_time == 0.0

def test_actual_time_none_is_accepted(valid_demand):
    demand = make_demand(valid_demand, actual_time=None)
    assert demand.actual_time is None

def test_actual_time_valid_is_accepted(valid_demand):
    demand = make_demand(valid_demand, actual_time=3.5)
    assert demand.actual_time == 3.5

# --- technical_visit_reason ---

def test_invalid_technical_visit_reason_should_fail(valid_demand):
    with pytest.raises(ValueError, match="Motivo da visita invalido"):
        make_demand(valid_demand, technical_visit_reason="Qualquer motivo")

def test_empty_technical_visit_reason_should_fail(valid_demand):
    with pytest.raises(ValueError, match="Motivo da visita nao pode ser vazio"):
        make_demand(valid_demand, technical_visit_reason="")

# --- equipment ---

def test_invalid_equipment_should_fail(valid_demand):
    with pytest.raises(ValueError, match="Equipamento invalido"):
        make_demand(valid_demand, equipment="Motor Eletrico")

def test_valid_equipment_is_accepted(valid_demand):
    demand = make_demand(valid_demand, equipment="Silos Planos / Elevados / Expedição / Aeração")
    assert demand.equipment == "Silos Planos / Elevados / Expedição / Aeração"

# --- hierarquia de problemas ---

def test_invalid_causal_sector_should_fail(valid_demand):
    with pytest.raises(ValueError, match="Setor causador invalido"):
        make_demand(valid_demand, causal_sector="RH")

def test_causal_area_incompatible_with_sector_should_fail(valid_demand):
    with pytest.raises(ValueError, match="Area causadora invalida para o setor informado"):
        make_demand(valid_demand, causal_sector="Fornecedor", causal_area="Comercial - Peças")

def test_root_cause_incompatible_with_area_should_fail(valid_demand):
    with pytest.raises(ValueError, match="Causa raiz invalida para a area informada"):
        make_demand(valid_demand, causal_sector="Fornecedor", causal_area="Fornecedor", root_cause="Coleta de Dados")

def test_valid_hierarchy_is_accepted(valid_demand):
    demand = make_demand(
        valid_demand,
        causal_sector="Engenharia",
        causal_area="Engenharia de Produto",
        root_cause="Melhoria de Produto"
    )
    assert demand.causal_sector == "Engenharia"
    assert demand.causal_area == "Engenharia de Produto"
    assert demand.root_cause == "Melhoria de Produto"

# --- campos obrigatorios ---

def test_empty_problem_description_should_fail(valid_demand):
    with pytest.raises(ValueError, match="Descricao do problema nao pode ser vazia"):
        make_demand(valid_demand, problem_description="")

def test_empty_project_id_should_fail(valid_demand):
    with pytest.raises(ValueError, match="Projeto nao pode ser vazio"):
        make_demand(valid_demand, project_id="")

def test_demand_title_empty_should_fail(valid_demand):
    with pytest.raises(ValueError, match="Titulo da demanda nao pode ser vazio"):
        make_demand(valid_demand, demand_title="")

def main():
    test_demand_created_with_valid_fields(
        Demand(
            request_date=date(2026, 5, 6),
            responsible_id=1,
            project_id="PROJ-001",
            estimated_time=36.0,
            demand_title="Falha no acionamento do elevador",
            problem_description="Equipamento com falha no acionamento",
            technical_visit_reason="Manutencao Corretiva",
            causal_sector="Fornecedor",
            causal_area="Fornecedor",
            root_cause="Atraso na entrega",
            equipment="Elevadores Agrícolas",
            status="Aberta"
        )
    )

main()