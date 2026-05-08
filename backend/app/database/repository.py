# -*- coding: utf-8 -*-
from sqlalchemy.orm import Session
from backend.app.database.orm_models import (
    CityORM, AnalystORM, CustomerORM,
    ProjectORM, TechnicianORM, DemandORM, DemandManagerORM
)
from backend.app.models.city import City
from backend.app.models.analyst import Analyst
from backend.app.models.customer import Customer
from backend.app.models.project import Project
from backend.app.models.technician import Technician
from backend.app.models.demand import Demand
from backend.app.models.demand_manager import DemandManager
from typing import Optional


# ── CITY ──────────────────────────────────────────────────────────────────────

class CityRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, city_id: int) -> Optional[City]:
        row = self.db.query(CityORM).filter(CityORM.city_id == city_id).first()
        return self._to_model(row) if row else None

    def get_all(self) -> list[City]:
        rows = self.db.query(CityORM).all()
        return [self._to_model(r) for r in rows]

    def create(self, city: City) -> City:
        row = CityORM(
            city_name       = city.city_name,
            state           = city.state,
            country         = city.country,
            geolocation_lat = city.geolocation_lat,
            geolocation_lon = city.geolocation_lon
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        city.city_id = row.city_id
        return city

    def update(self, city: City) -> City:
        row = self.db.query(CityORM).filter(CityORM.city_id == city.city_id).first()
        if not row:
            raise ValueError(f"Cidade com id {city.city_id} nao encontrada")
        row.city_name       = city.city_name
        row.state           = city.state
        row.country         = city.country
        row.geolocation_lat = city.geolocation_lat
        row.geolocation_lon = city.geolocation_lon
        self.db.commit()
        self.db.refresh(row)
        return city

    def delete(self, city_id: int) -> None:
        row = self.db.query(CityORM).filter(CityORM.city_id == city_id).first()
        if row:
            self.db.delete(row)
            self.db.commit()

    def _to_model(self, row: CityORM) -> City:
        return City(
            city_id         = row.city_id,
            city_name       = row.city_name,
            state           = row.state,
            country         = row.country,
            geolocation_lat = row.geolocation_lat,
            geolocation_lon = row.geolocation_lon
        )


# ── ANALYST ───────────────────────────────────────────────────────────────────

class AnalystRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, analyst_id: int) -> Optional[Analyst]:
        row = self.db.query(AnalystORM).filter(AnalystORM.analyst_id == analyst_id).first()
        return self._to_model(row) if row else None

    def get_all_active(self) -> list[Analyst]:
        rows = self.db.query(AnalystORM).filter(AnalystORM.status == "active").all()
        return [self._to_model(r) for r in rows]

    def create(self, analyst: Analyst) -> Analyst:
        row = AnalystORM(
            analyst_name  = analyst.analyst_name,
            email         = analyst.email,
            contact       = analyst.contact,
            creation_date = analyst.creation_date,
            status        = analyst.status,
            valid_to_date = analyst.valid_to_date
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        analyst.analyst_id = row.analyst_id
        return analyst

    def update(self, analyst: Analyst) -> Analyst:
        row = self.db.query(AnalystORM).filter(AnalystORM.analyst_id == analyst.analyst_id).first()
        if not row:
            raise ValueError(f"Analista com id {analyst.analyst_id} nao encontrado")
        row.analyst_name  = analyst.analyst_name
        row.email         = analyst.email
        row.contact       = analyst.contact
        row.status        = analyst.status
        row.valid_to_date = analyst.valid_to_date
        self.db.commit()
        self.db.refresh(row)
        return analyst

    def _to_model(self, row: AnalystORM) -> Analyst:
        return Analyst(
            analyst_id    = row.analyst_id,
            analyst_name  = row.analyst_name,
            email         = row.email,
            contact       = row.contact,
            creation_date = row.creation_date,
            status        = row.status,
            valid_to_date = row.valid_to_date
        )


# ── CUSTOMER ──────────────────────────────────────────────────────────────────

class CustomerRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, customer_id: str) -> Optional[Customer]:
        row = self.db.query(CustomerORM).filter(CustomerORM.customer_id == customer_id).first()
        return self._to_model(row) if row else None

    def get_all(self) -> list[Customer]:
        rows = self.db.query(CustomerORM).all()
        return [self._to_model(r) for r in rows]

    def create(self, customer: Customer) -> Customer:
        row = CustomerORM(
            customer_id   = customer.customer_id,
            customer_name = customer.customer_name,
            short_name    = customer.short_name,
            city_id       = customer.city_id,
            address       = customer.address,
            segment       = customer.segment,
            sub_segment   = customer.sub_segment,
            region        = customer.region
        )
        self.db.add(row)
        self.db.commit()
        return customer

    def update(self, customer: Customer) -> Customer:
        row = self.db.query(CustomerORM).filter(CustomerORM.customer_id == customer.customer_id).first()
        if not row:
            raise ValueError(f"Cliente {customer.customer_id} nao encontrado")
        row.customer_name = customer.customer_name
        row.short_name    = customer.short_name
        row.city_id       = customer.city_id
        row.address       = customer.address
        row.segment       = customer.segment
        row.sub_segment   = customer.sub_segment
        row.region        = customer.region
        self.db.commit()
        return customer

    def _to_model(self, row: CustomerORM) -> Customer:
        return Customer(
            customer_id   = row.customer_id,
            customer_name = row.customer_name,
            short_name    = row.short_name,
            city_id       = row.city_id,
            address       = row.address,
            segment       = row.segment,
            sub_segment   = row.sub_segment,
            region        = row.region
        )


# ── PROJECT ───────────────────────────────────────────────────────────────────

class ProjectRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, project_id: str) -> Optional[Project]:
        row = self.db.query(ProjectORM).filter(ProjectORM.project_id == project_id).first()
        return self._to_model(row) if row else None

    def get_by_customer(self, customer_id: str) -> list[Project]:
        rows = self.db.query(ProjectORM).filter(ProjectORM.customer_id == customer_id).all()
        return [self._to_model(r) for r in rows]

    def create(self, project: Project) -> Project:
        row = ProjectORM(
            project_id   = project.project_id,
            project_name = project.project_name,
            customer_id  = project.customer_id
        )
        self.db.add(row)
        self.db.commit()
        return project

    def update(self, project: Project) -> Project:
        row = self.db.query(ProjectORM).filter(ProjectORM.project_id == project.project_id).first()
        if not row:
            raise ValueError(f"Projeto {project.project_id} nao encontrado")
        row.project_name = project.project_name
        row.customer_id  = project.customer_id
        self.db.commit()
        return project

    def _to_model(self, row: ProjectORM) -> Project:
        return Project(
            project_id   = row.project_id,
            project_name = row.project_name,
            customer_id  = row.customer_id
        )


# ── TECHNICIAN ────────────────────────────────────────────────────────────────

class TechnicianRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, technician_id: int) -> Optional[Technician]:
        row = self.db.query(TechnicianORM).filter(TechnicianORM.technician_id == technician_id).first()
        return self._to_model(row) if row else None

    def get_all_active(self) -> list[Technician]:
        rows = self.db.query(TechnicianORM).filter(TechnicianORM.status == "ativo").all()
        return [self._to_model(r) for r in rows]

    def create(self, technician: Technician) -> Technician:
        row = TechnicianORM(
            technician_name          = technician.technician_name,
            creation_date            = technician.creation_date,
            status                   = technician.status,
            dismiss_date             = technician.dismiss_date,
            position                 = technician.position,
            base_location_city_id    = technician.base_location_city_id,
            current_location_city_id = technician.current_location_city_id,
            daily_capacity           = technician.daily_capacity
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        technician.technician_id = row.technician_id
        return technician

    def update(self, technician: Technician) -> Technician:
        row = self.db.query(TechnicianORM).filter(TechnicianORM.technician_id == technician.technician_id).first()
        if not row:
            raise ValueError(f"Tecnico com id {technician.technician_id} nao encontrado")
        row.technician_name          = technician.technician_name
        row.status                   = technician.status
        row.dismiss_date             = technician.dismiss_date
        row.position                 = technician.position
        row.current_location_city_id = technician.current_location_city_id
        row.daily_capacity           = technician.daily_capacity
        self.db.commit()
        return technician

    def _to_model(self, row: TechnicianORM) -> Technician:
        return Technician(
            technician_id            = row.technician_id,
            technician_name          = row.technician_name,
            creation_date            = row.creation_date,
            status                   = row.status,
            dismiss_date             = row.dismiss_date,
            position                 = row.position,
            base_location_city_id    = row.base_location_city_id,
            current_location_city_id = row.current_location_city_id,
            daily_capacity           = row.daily_capacity
        )


# ── DEMAND ────────────────────────────────────────────────────────────────────

class DemandRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, demand_id: int) -> Optional[Demand]:
        row = self.db.query(DemandORM).filter(DemandORM.demand_id == demand_id).first()
        return self._to_model(row) if row else None

    def get_by_status(self, status: str) -> list[Demand]:
        rows = self.db.query(DemandORM).filter(DemandORM.status == status).all()
        return [self._to_model(r) for r in rows]

    def get_by_project(self, project_id: str) -> list[Demand]:
        rows = self.db.query(DemandORM).filter(DemandORM.project_id == project_id).all()
        return [self._to_model(r) for r in rows]

    def create(self, demand: Demand) -> Demand:
        row = DemandORM(
            demand_title           = demand.demand_title,
            problem_description    = demand.problem_description,
            request_date           = demand.request_date,
            responsible_id         = demand.responsible_id,
            project_id             = demand.project_id,
            estimated_time         = demand.estimated_time,
            actual_time            = demand.actual_time,
            technical_visit_reason = demand.technical_visit_reason,
            causal_sector          = demand.causal_sector,
            causal_area            = demand.causal_area,
            root_cause             = demand.root_cause,
            equipment              = demand.equipment,
            status                 = demand.status
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        demand.demand_id = row.demand_id
        return demand

    def update(self, demand: Demand) -> Demand:
        row = self.db.query(DemandORM).filter(DemandORM.demand_id == demand.demand_id).first()
        if not row:
            raise ValueError(f"Demanda com id {demand.demand_id} nao encontrada")
        row.demand_title           = demand.demand_title
        row.problem_description    = demand.problem_description
        row.estimated_time         = demand.estimated_time
        row.actual_time            = demand.actual_time
        row.technical_visit_reason = demand.technical_visit_reason
        row.causal_sector          = demand.causal_sector
        row.causal_area            = demand.causal_area
        row.root_cause             = demand.root_cause
        row.equipment              = demand.equipment
        row.status                 = demand.status
        self.db.commit()
        return demand

    def _to_model(self, row: DemandORM) -> Demand:
        return Demand(
            demand_id              = row.demand_id,
            demand_title           = row.demand_title,
            problem_description    = row.problem_description,
            request_date           = row.request_date,
            responsible_id         = row.responsible_id,
            project_id             = row.project_id,
            estimated_time         = row.estimated_time,
            actual_time            = row.actual_time,
            technical_visit_reason = row.technical_visit_reason,
            causal_sector          = row.causal_sector,
            causal_area            = row.causal_area,
            root_cause             = row.root_cause,
            equipment              = row.equipment,
            status                 = row.status
        )


# ── DEMAND MANAGER ────────────────────────────────────────────────────────────

class DemandManagerRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, demand_manager_id: int) -> Optional[DemandManager]:
        row = self.db.query(DemandManagerORM).filter(
            DemandManagerORM.demand_manager_id == demand_manager_id).first()
        return self._to_model(row) if row else None

    def get_by_technician(self, technician_id: int) -> list[DemandManager]:
        """Retorna todos os registros ativos de um técnico — base para montar a DemandQueue."""
        rows = self.db.query(DemandManagerORM).filter(
            DemandManagerORM.technician_id == technician_id,
            DemandManagerORM.is_deleted == False
        ).all()
        return [self._to_model(r) for r in rows]

    def create(self, dm: DemandManager) -> DemandManager:
        row = DemandManagerORM(
            demand_id              = dm.demand_id,
            technician_id          = dm.technician_id,
            next_demand_manager_id = dm.next_demand_manager_id,
            status                 = dm.status,
            start_date             = dm.start_date,
            finish_date            = dm.finish_date,
            travel_time            = dm.travel_time,
            travel_distance        = dm.travel_distance,
            is_deleted             = dm.is_deleted
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        dm.demand_manager_id = row.demand_manager_id
        return dm

    def update(self, dm: DemandManager) -> DemandManager:
        row = self.db.query(DemandManagerORM).filter(
            DemandManagerORM.demand_manager_id == dm.demand_manager_id).first()
        if not row:
            raise ValueError(f"DemandManager com id {dm.demand_manager_id} nao encontrado")
        row.next_demand_manager_id = dm.next_demand_manager_id
        row.status                 = dm.status
        row.start_date             = dm.start_date
        row.finish_date            = dm.finish_date
        row.travel_time            = dm.travel_time
        row.travel_distance        = dm.travel_distance
        row.is_deleted             = dm.is_deleted
        self.db.commit()
        return dm

    def soft_delete(self, demand_manager_id: int) -> None:
        row = self.db.query(DemandManagerORM).filter(
            DemandManagerORM.demand_manager_id == demand_manager_id).first()
        if row:
            row.is_deleted = True
            self.db.commit()

    def _to_model(self, row: DemandManagerORM) -> DemandManager:
        return DemandManager(
            demand_manager_id      = row.demand_manager_id,
            demand_id              = row.demand_id,
            technician_id          = row.technician_id,
            next_demand_manager_id = row.next_demand_manager_id,
            status                 = row.status,
            start_date             = row.start_date,
            finish_date            = row.finish_date,
            travel_time            = row.travel_time,
            travel_distance        = row.travel_distance,
            is_deleted             = row.is_deleted
        )