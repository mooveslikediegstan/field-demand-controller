# backend/app/services/demand_service.py
from datetime import date
from sqlalchemy.orm import Session

from backend.app.models.demand import Demand
from backend.app.models.demand_manager import DemandManager
from backend.app.database.repository import DemandRepository, DemandManagerRepository


class DemandService:

    def __init__(self, db: Session):
        self.db         = db
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

    # ── Alocação ──────────────────────────────────────────────────────────────

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

    # ── Desalocação ───────────────────────────────────────────────────────────

    def deallocate_technician(self, demand_id: int, technician_id: int) -> Demand:
        demand = self.get_demand(demand_id)
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