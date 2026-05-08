# -*- coding: utf-8 -*-
import pytest
from backend.app.models.project import Project

@pytest.fixture
def valid_project():
    return Project(
        project_id="PROJ-001",
        project_name="Projeto Exemplo",
        customer_id="CUST-001"
    )

def make_project(valid_project, **overrides):
    return Project(**{**valid_project.__dict__, **overrides})

# --- criacao basica ---

def test_project_created_with_valid_fields(valid_project):
    assert valid_project.project_id == "PROJ-001"
    assert valid_project.project_name == "Projeto Exemplo"
    assert valid_project.customer_id == "CUST-001"

# --- campos obrigatorios ---

def test_empty_project_id_should_fail(valid_project):
    with pytest.raises(ValueError, match="ID do projeto nao pode ser vazio"):
        make_project(valid_project, project_id="")

def test_empty_project_name_should_fail(valid_project):
    with pytest.raises(ValueError, match="Nome do projeto nao pode ser vazio"):
        make_project(valid_project, project_name="")

def test_empty_customer_id_should_fail(valid_project):
    with pytest.raises(ValueError, match="ID do cliente nao pode ser vazio"):
        make_project(valid_project, customer_id="")