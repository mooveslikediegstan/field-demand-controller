# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, Float, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database.session import Base


class CityORM(Base):
    __tablename__ = "city"

    city_id          = Column(Integer, primary_key=True, autoincrement=True)
    city_name        = Column(String, nullable=False)
    state            = Column(String, nullable=False)
    country          = Column(String, nullable=False)
    geolocation_lat  = Column(Float, nullable=False)
    geolocation_lon  = Column(Float, nullable=False)


class AnalystORM(Base):
    __tablename__ = "analyst"

    analyst_id      = Column(Integer, primary_key=True, autoincrement=True)
    analyst_name    = Column(String, nullable=False)
    email           = Column(String, nullable=False, unique=True)
    contact         = Column(String, nullable=False)
    creation_date   = Column(Date, nullable=False)
    status          = Column(String, nullable=False, default="active")
    valid_to_date   = Column(Date, nullable=True)


class CustomerORM(Base):
    __tablename__ = "customer"

    customer_id     = Column(String, primary_key=True)
    customer_name   = Column(String, nullable=False)
    short_name      = Column(String, nullable=False)
    city_id         = Column(Integer, ForeignKey("city.city_id"), nullable=False)
    address         = Column(String, nullable=False)
    segment         = Column(String, nullable=False)
    sub_segment     = Column(String, nullable=False)
    region          = Column(String, nullable=False)

    city            = relationship("CityORM")
    projects        = relationship("ProjectORM", back_populates="customer")


class ProjectORM(Base):
    __tablename__ = "project"

    project_id      = Column(String, primary_key=True)
    project_name    = Column(String, nullable=False)
    customer_id     = Column(String, ForeignKey("customer.customer_id"), nullable=False)

    customer        = relationship("CustomerORM", back_populates="projects")
    demands         = relationship("DemandORM", back_populates="project")


class TechnicianORM(Base):
    __tablename__ = "technician"

    technician_id             = Column(Integer, primary_key=True, autoincrement=True)
    technician_name           = Column(String, nullable=False)
    creation_date             = Column(Date, nullable=False)
    status                    = Column(String, nullable=False)
    dismiss_date              = Column(Date, nullable=True)
    position                  = Column(String, nullable=False)
    base_location_city_id     = Column(Integer, ForeignKey("city.city_id"), nullable=False)
    current_location_city_id  = Column(Integer, ForeignKey("city.city_id"), nullable=False)
    daily_capacity            = Column(Float, nullable=False)

    base_city                 = relationship("CityORM", foreign_keys=[base_location_city_id])
    current_city              = relationship("CityORM", foreign_keys=[current_location_city_id])
    demand_managers           = relationship("DemandManagerORM", back_populates="technician")


class DemandORM(Base):
    __tablename__ = "demand"

    demand_id               = Column(Integer, primary_key=True, autoincrement=True)
    demand_title            = Column(String, nullable=False)
    problem_description     = Column(String, nullable=False)
    request_date            = Column(Date, nullable=False)
    responsible_id          = Column(Integer, ForeignKey("analyst.analyst_id"), nullable=False)
    project_id              = Column(String, ForeignKey("project.project_id"), nullable=False)
    estimated_time          = Column(Float, nullable=False)
    actual_time             = Column(Float, nullable=True)
    technical_visit_reason  = Column(String, nullable=False)
    causal_sector           = Column(String, nullable=False)
    causal_area             = Column(String, nullable=False)
    root_cause              = Column(String, nullable=False)
    equipment               = Column(String, nullable=False)
    status                  = Column(String, nullable=False)

    project                 = relationship("ProjectORM", back_populates="demands")
    analyst                 = relationship("AnalystORM")
    demand_managers         = relationship("DemandManagerORM", back_populates="demand")


class DemandManagerORM(Base):
    __tablename__ = "demand_manager"

    demand_manager_id       = Column(Integer, primary_key=True, autoincrement=True)
    demand_id               = Column(Integer, ForeignKey("demand.demand_id"), nullable=False)
    technician_id           = Column(Integer, ForeignKey("technician.technician_id"), nullable=False)
    next_demand_manager_id  = Column(Integer, ForeignKey("demand_manager.demand_manager_id"), nullable=True)
    status                  = Column(String, nullable=False)
    start_date              = Column(Date, nullable=True)
    finish_date             = Column(Date, nullable=True)
    travel_time             = Column(Float, nullable=True)
    travel_distance         = Column(Float, nullable=True)
    is_deleted              = Column(Boolean, nullable=False, default=False)

    demand                  = relationship("DemandORM", back_populates="demand_managers")
    technician              = relationship("TechnicianORM", back_populates="demand_managers")