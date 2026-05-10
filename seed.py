# -*- coding: utf-8 -*-
"""
Script de seed — dados fictícios para desenvolvimento e testes manuais.
Execute na raiz do projeto:
    python seed.py
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from datetime import date
from backend.app.database.session import SessionLocal
from backend.app.database.orm_models import (
    CityORM, AnalystORM, CustomerORM,
    ProjectORM, TechnicianORM, DemandORM, DemandManagerORM
)


def seed():
    db = SessionLocal()
    try:
        # ── CITIES ────────────────────────────────────────────────────────────
        cities = [
            CityORM(city_name="Sorriso",         state="MT", country="Brasil", geolocation_lat=-12.5444, geolocation_lon=-55.7211),
            CityORM(city_name="Lucas do Rio Verde", state="MT", country="Brasil", geolocation_lat=-13.0568, geolocation_lon=-55.9044),
            CityORM(city_name="Rondonópolis",     state="MT", country="Brasil", geolocation_lat=-16.4705, geolocation_lon=-54.6358),
            CityORM(city_name="Dourados",         state="MS", country="Brasil", geolocation_lat=-22.2211, geolocation_lon=-54.8056),
            CityORM(city_name="Maringá",          state="PR", country="Brasil", geolocation_lat=-23.4205, geolocation_lon=-51.9331),
            CityORM(city_name="São Paulo",        state="SP", country="Brasil", geolocation_lat=-23.5505, geolocation_lon=-46.6333),
        ]
        db.add_all(cities)
        db.flush()  # gera os city_id sem commitar

        # Referência por nome para facilitar
        city = {c.city_name: c for c in cities}

        # ── ANALYSTS ──────────────────────────────────────────────────────────
        analysts = [
            AnalystORM(analyst_name="Ana Paula Ferreira", email="ana.ferreira@agi.com",
                       contact="+55 11 91111-0001", creation_date=date(2023, 3, 1), status="active"),
            AnalystORM(analyst_name="Roberto Campos",     email="roberto.campos@agi.com",
                       contact="+55 11 91111-0002", creation_date=date(2023, 3, 1), status="active"),
        ]
        db.add_all(analysts)
        db.flush()

        analyst = {a.analyst_name: a for a in analysts}

        # ── CUSTOMERS ─────────────────────────────────────────────────────────
        customers = [
            CustomerORM(customer_id="COOP-MT-001", customer_name="Cooperativa Agropecuária Sorriso",
                        short_name="COOPASSO", city_id=city["Sorriso"].city_id,
                        address="Rod. BR-163, Km 742, Sorriso-MT",
                        segment="Farm", sub_segment="Farm", region="MT"),
            CustomerORM(customer_id="COOP-MT-002", customer_name="Cooperativa Lucas Agrícola",
                        short_name="COALUCA", city_id=city["Lucas do Rio Verde"].city_id,
                        address="Av. das Nações, 1500, Lucas do Rio Verde-MT",
                        segment="Farm", sub_segment="Feed", region="MT"),
            CustomerORM(customer_id="AGRO-MS-001", customer_name="Agropecuária Dourados Sul",
                        short_name="AGROSUL", city_id=city["Dourados"].city_id,
                        address="Rod. MS-156, Km 12, Dourados-MS",
                        segment="Farm", sub_segment="Farm", region="MS/SP"),
        ]
        db.add_all(customers)
        db.flush()

        # ── PROJECTS ──────────────────────────────────────────────────────────
        projects = [
            ProjectORM(project_id="20240001-COOPASSO", project_name="Instalação Silo Plano 5000t",
                       customer_id="COOP-MT-001"),
            ProjectORM(project_id="20240002-COOPASSO", project_name="Reforma Elevadores Linha A",
                       customer_id="COOP-MT-001"),
            ProjectORM(project_id="20240003-COALUCA", project_name="Start-up Secador Rotativo",
                       customer_id="COOP-MT-002"),
            ProjectORM(project_id="20240004-AGROSUL", project_name="Manutenção Transportadores",
                       customer_id="AGRO-MS-001"),
        ]
        db.add_all(projects)
        db.flush()

        # ── TECHNICIANS ───────────────────────────────────────────────────────
        technicians = [
            TechnicianORM(
                technician_name="Carlos Eduardo Silva",
                creation_date=date(2022, 1, 10), status="ativo",
                position="Lider",
                base_location_city_id    = city["São Paulo"].city_id,
                current_location_city_id = city["São Paulo"].city_id,
                daily_capacity=8.0,
            ),
            TechnicianORM(
                technician_name="Marcelo Ribeiro Santos",
                creation_date=date(2022, 6, 1), status="ativo",
                position="Supervisor",
                base_location_city_id    = city["Maringá"].city_id,
                current_location_city_id = city["Maringá"].city_id,
                daily_capacity=8.0,
            ),
        ]
        db.add_all(technicians)
        db.flush()

        tech = {t.technician_name: t for t in technicians}

        # ── DEMANDS ───────────────────────────────────────────────────────────
        demands = [
            DemandORM(
                demand_title        = "Avaria no transportador de correia linha 2",
                problem_description = "Correia desalinhada causando perda de grãos no transportador da linha 2.",
                request_date        = date(2026, 4, 28),
                responsible_id      = analyst["Ana Paula Ferreira"].analyst_id,
                project_id          = "20240001-COOPASSO",
                estimated_time      = 16.0,
                technical_visit_reason = "Manutenção Corretiva",
                causal_sector       = "Fornecedor",
                causal_area         = "Fornecedor",
                root_cause          = "Material fora do padrão de Qualidade",
                equipment           = "Transportadores de Correia",
                status              = "Em Andamento",
            ),
            DemandORM(
                demand_title        = "Verificação de performance do secador",
                problem_description = "Cliente relata capacidade abaixo do especificado em 15%.",
                request_date        = date(2026, 5, 2),
                responsible_id      = analyst["Ana Paula Ferreira"].analyst_id,
                project_id          = "20240003-COALUCA",
                estimated_time      = 9.0,
                technical_visit_reason = "Verificação",
                causal_sector       = "Engenharia",
                causal_area         = "Engenharia de Produto",
                root_cause          = "Melhoria de Produto",
                equipment           = "Secador / Fornalha",
                status              = "Em Andamento",
            ),
            DemandORM(
                demand_title        = "Identificação incorreta de peças no silo",
                problem_description = "Peças recebidas sem identificação correta, impossibilitando a montagem.",
                request_date        = date(2026, 5, 5),
                responsible_id      = analyst["Roberto Campos"].analyst_id,
                project_id          = "20240004-AGROSUL",
                estimated_time      = 18.0,
                technical_visit_reason = "Visita Técnica",
                causal_sector       = "Manufatura",
                causal_area         = "Silo",
                root_cause          = "Identificação incorreta",
                equipment           = "Silos Planos / Elevados / Expedição / Aeração",
                status              = "Aberta",
            ),
            DemandORM(
                demand_title        = "Falha na solda do elevador agrícola",
                problem_description = "Trincas identificadas na estrutura soldada do elevador da linha B.",
                request_date        = date(2026, 5, 6),
                responsible_id      = analyst["Roberto Campos"].analyst_id,
                project_id          = "20240002-COOPASSO",
                estimated_time      = 27.0,
                technical_visit_reason = "Manutenção Corretiva",
                causal_sector       = "Manufatura",
                causal_area         = "Solda",
                root_cause          = "Material fora do padrão de qualidade",
                equipment           = "Elevadores Agrícolas",
                status              = "Em Andamento",
            ),
        ]
        db.add_all(demands)
        db.flush()

        # ── DEMAND MANAGERS ───────────────────────────────────────────────────
        # Carlos: demandas 1 e 2 (fila: 1 → 2)
        # Marcelo: demandas 3 e 4 (fila: 3 → 4)
        dm1 = DemandManagerORM(
            demand_id     = demands[0].demand_id,
            technician_id = tech["Carlos Eduardo Silva"].technician_id,
            status        = "Pendente",
        )
        dm2 = DemandManagerORM(
            demand_id     = demands[1].demand_id,
            technician_id = tech["Carlos Eduardo Silva"].technician_id,
            status        = "Pendente",
        )
        dm3 = DemandManagerORM(
            demand_id     = demands[2].demand_id,
            technician_id = tech["Marcelo Ribeiro Santos"].technician_id,
            status        = "Pendente",
        )
        dm4 = DemandManagerORM(
            demand_id     = demands[3].demand_id,
            technician_id = tech["Marcelo Ribeiro Santos"].technician_id,
            status        = "Pendente",
        )
        db.add_all([dm1, dm2, dm3, dm4])
        db.flush()

        # Monta os links da linked-list
        dm1.next_demand_manager_id = dm2.demand_manager_id
        dm2.next_demand_manager_id = None
        dm3.next_demand_manager_id = dm4.demand_manager_id
        dm4.next_demand_manager_id = None

        db.commit()
        print("✅ Seed concluído com sucesso!")
        print(f"   Cidades:         {len(cities)}")
        print(f"   Analistas:       {len(analysts)}")
        print(f"   Clientes:        {len(customers)}")
        print(f"   Projetos:        {len(projects)}")
        print(f"   Técnicos:        {len(technicians)}")
        print(f"   Demandas:        {len(demands)}")
        print(f"   DemandManagers:  4")
        print()
        print("IDs úteis para testar no Swagger:")
        print(f"   Técnico Carlos:  technician_id = {tech['Carlos Eduardo Silva'].technician_id}")
        print(f"   Técnico Marcelo: technician_id = {tech['Marcelo Ribeiro Santos'].technician_id}")
        for i, d in enumerate(demands):
            print(f"   Demanda {i+1}:       demand_id = {d.demand_id}  ({d.demand_title[:40]})")

    except Exception as e:
        db.rollback()
        print(f"❌ Erro no seed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()