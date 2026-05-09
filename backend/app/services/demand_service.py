# -*- coding: utf-8 -*-
from datetime import date
from sqlalchemy.orm import Session

from backend.app.models.demand import Demand
from backend.app.models.demand_manager import DemandManager
from backend.app.database.repository import DemandRepository, DemandManagerRepository


class DemandService:

    def __init__(self, db: Session):
        self.db          = db
        self.demand_repo = DemandRepository(db)
        self.dm_repo     = DemandManagerRepository(db)

    # ── CRUD ──────────────────────────────────────────────────────────────────

    def create_demand(self, demand: Demand) -> Demand:
        if demand.status != "Aberta":
            raise ValueError("Nova demanda deve ter status 'Aberta'")
        return self.demand_repo.create(demand)

    def get_demand(self, demand_id: int) -> Demand:
        demand = self.demand_repo.get_by_id(demand_id)
        if not demand:
            raise ValueError(f"Demanda {demand_id} não encontrada")
        return demand

    def update_demand(self, demand: Demand) -> Demand:
        self.get_demand(demand.demand_id)
        return self.demand_repo.update(demand)

    def cancel_demand(self, demand_id: int) -> Demand:
        demand = self.get_demand(demand_id)
        if demand.status == "Concluída":
            raise ValueError("Não é possível cancelar uma demanda já concluída")
        if demand.status == "Cancelada":
            raise ValueError("Demanda já está cancelada")

        # Soft-delete em todos os DemandManagers ativos
        active_dms = self.dm_repo.get_by_demand(demand_id)
        try:
            for dm in active_dms:
                self.dm_repo.soft_delete(dm.demand_manager_id)

            demand.status = "Cancelada"
            self.demand_repo.update(demand)
            self.db.commit()
            return demand
        except Exception:
            self.db.rollback()
            raise

    # ── ALOCAÇÃO ──────────────────────────────────────────────────────────────

    def allocate_technician(self, demand_id: int, technician_id: int) -> DemandManager:
        demand = self.get_demand(demand_id)
        if demand.status == "Concluída":
            raise ValueError("Não é possível alocar técnico em demanda concluída")
        if demand.status == "Cancelada":
            raise ValueError("Não é possível alocar técnico em demanda cancelada")

        existing_dms = self.dm_repo.get_by_demand(demand_id)
        if any(dm.technician_id == technician_id for dm in existing_dms):
            raise ValueError("Técnico já está alocado nessa demanda")

        try:
            dm = self.dm_repo.create(DemandManager(
                demand_id     = demand_id,
                technician_id = technician_id,
                status        = "Pendente",
            ))
            demand.status = "Em Andamento"
            self.demand_repo.update(demand)
            self.db.commit()
            return dm
        except Exception:
            self.db.rollback()
            raise

    # ── DESALOCAÇÃO ───────────────────────────────────────────────────────────

    def deallocate_technician(self, demand_id: int, technician_id: int) -> Demand:
        demand  = self.get_demand(demand_id)
        all_dms = self.dm_repo.get_by_demand(demand_id)

        target = next((dm for dm in all_dms if dm.technician_id == technician_id), None)
        if not target:
            raise ValueError("Técnico não está alocado nessa demanda")
        if target.status == "Concluido":
            raise ValueError("Não é possível remover técnico que já concluiu sua parte")

        others = [dm for dm in all_dms if dm.technician_id != technician_id]

        try:
            self.dm_repo.soft_delete(target.demand_manager_id)

            if not others:
                demand.status = "Aberta"
            elif all(dm.status == "Concluido" for dm in others):
                demand.status = "Concluída"

            self.demand_repo.update(demand)
            self.db.commit()
            return demand
        except Exception:
            self.db.rollback()
            raise

    # ── CONCLUSÃO ─────────────────────────────────────────────────────────────

    def get_conclusion_data(self, demand_manager_id: int) -> dict:
        dm = self.dm_repo.get_by_id(demand_manager_id)
        if not dm:
            raise ValueError(f"DemandManager {demand_manager_id} não encontrado")
        if dm.status == "Concluido":
            raise ValueError("Essa ordem já foi concluída")

        demand = self.get_demand(dm.demand_id)
        return {
            "demand_manager_id": dm.demand_manager_id,
            "demand_title":      demand.demand_title,
            "project_id":        demand.project_id,
            "technician_id":     dm.technician_id,
            "estimated_time":    demand.estimated_time,
        }

    def conclude_demand_manager(
        self,
        demand_manager_id: int,
        actual_time:       float,
        travel_time:       float,
        travel_distance:   float,
        finish_date:       date,
    ) -> Demand:
        dm = self.dm_repo.get_by_id(demand_manager_id)
        if not dm:
            raise ValueError(f"DemandManager {demand_manager_id} não encontrado")
        if dm.status == "Concluido":
            raise ValueError("Essa ordem já foi concluída")

        demand  = self.get_demand(dm.demand_id)
        all_dms = self.dm_repo.get_by_demand(dm.demand_id)

        try:
            dm.status          = "Concluido"
            dm.travel_time     = travel_time
            dm.travel_distance = travel_distance
            dm.finish_date     = finish_date
            self.dm_repo.update(dm)

            demand.actual_time = actual_time
            others = [d for d in all_dms if d.demand_manager_id != demand_manager_id]
            if all(d.status == "Concluido" for d in others):
                demand.status = "Concluída"
            self.demand_repo.update(demand)

            self.db.commit()
            return demand
        except Exception:
            self.db.rollback()
            raise