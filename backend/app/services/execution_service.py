# backend/app/services/execution_service.py
from sqlalchemy.orm import Session

from backend.app.models.execution_input import ExecutionInput
from backend.app.models.execution_log import ExecutionLog
from backend.app.models.demand_manager import DemandManager
from backend.app.database.repository import (
    ExecutionLogRepository,
    DemandManagerRepository,
    DemandRepository,
)


class ExecutionService:

    def __init__(self, db: Session):
        self.db         = db
        self.el_repo     = ExecutionLogRepository(db)
        self.dm_repo     = DemandManagerRepository(db)
        self.demand_repo = DemandRepository(db)

    def conclude(
        self,
        demand_manager_id: int,
        inputs: list[ExecutionInput]
    ) -> DemandManager:

        dm = self.dm_repo.get_by_id(demand_manager_id)
        if not dm:
            raise ValueError(f"DemandManager {demand_manager_id} não encontrado")
        if dm.status == "Concluido":
            raise ValueError("Essa alocação já foi concluída")
        if not inputs:
            raise ValueError("Nenhum registro de execução informado")

        try:
            # 1. Persiste um ExecutionLog por input
            logs = [
                ExecutionLog(
                    demand_manager_id = demand_manager_id,
                    technician_id     = dm.technician_id,
                    execution_date    = inp.execution_date,
                    action            = inp.action,
                    worked_hours      = inp.worked_hours,
                    distance          = inp.distance,
                )
                for inp in inputs
            ]
            self.el_repo.create_batch(logs)

            # 2. Conclui o DemandManager
            dm.status = "Concluido"
            self.dm_repo.update(dm)

            # 3. Verifica se a demanda toda fecha
            all_dms = self.dm_repo.get_by_demand(dm.demand_id)
            if all(d.status == "Concluido" for d in all_dms):
                demand = self.demand_repo.get_by_id(dm.demand_id)
                demand.status = "Concluída"
                self.demand_repo.update(demand)

            self.db.commit()
            return dm

        except Exception:
            self.db.rollback()
            raise