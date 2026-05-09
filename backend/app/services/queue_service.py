# -*- coding: utf-8 -*-
from sqlalchemy.orm import Session

from backend.app.database.orm_models import DemandManagerORM, DemandORM
from backend.app.models.demand_manager import DemandManager
from backend.app.models.demand_queue import DemandQueue
from backend.app.schemas.schedule_schemas import QueueItemResponse, SaveSequenceRequest
from backend.app.database.repository import DemandManagerRepository


class QueueService:

    def __init__(self, db: Session):
        self.db     = db
        self.dm_repo = DemandManagerRepository(db)

    # ── GET QUEUE ──────────────────────────────────────────────────────────────

    def get_queue(self, technician_id: int) -> list[QueueItemResponse]:
        """
        Retorna a fila ordenada de um técnico com dados enriquecidos da demanda.
        Usa JOIN para evitar o problema N+1.
        """
        rows = (
            self.db.query(DemandManagerORM, DemandORM)
            .join(DemandORM, DemandManagerORM.demand_id == DemandORM.demand_id)
            .filter(
                DemandManagerORM.technician_id == technician_id,
                DemandManagerORM.is_deleted    == False
            )
            .all()
        )

        if not rows:
            return []

        # Monta a DemandQueue para ordenar via linked-list
        dm_models = [self._orm_to_dm_model(dm_orm) for dm_orm, _ in rows]
        head_id   = self._find_head(dm_models)

        queue = DemandQueue(
            technician_id = technician_id,
            head_id       = head_id,
            demands       = dm_models
        )
        queue.sort()

        # Índice para montar a resposta na ordem da fila
        demand_by_dm_id = {
            dm_orm.demand_manager_id: demand_orm
            for dm_orm, demand_orm in rows
        }

        result = []
        for dm in queue.demands:
            demand_orm = demand_by_dm_id[dm.demand_manager_id]
            result.append(QueueItemResponse(
                demand_manager_id = dm.demand_manager_id,
                demand_id         = dm.demand_id,
                demand_title      = demand_orm.demand_title,
                project_id        = demand_orm.project_id,
                status            = dm.status,
                estimated_time    = demand_orm.estimated_time
            ))

        return result

    # ── SAVE SEQUENCE ──────────────────────────────────────────────────────────

    def save_sequence(self, technician_id: int, payload: SaveSequenceRequest) -> list[QueueItemResponse]:
        """
        Recebe a nova ordem dos IDs, reconstrói os links da fila e persiste.
        Retorna a fila já na nova ordem para o frontend atualizar sem segunda chamada.
        """
        ordered_ids = payload.ordered_demand_manager_ids

        # Busca apenas os DemandManagers deste técnico (sem JOIN — não precisa de demand aqui)
        dm_rows = (
            self.db.query(DemandManagerORM)
            .filter(
                DemandManagerORM.technician_id == technician_id,
                DemandManagerORM.is_deleted    == False
            )
            .all()
        )

        dm_by_id = {row.demand_manager_id: row for row in dm_rows}

        # Valida que todos os IDs recebidos pertencem a este técnico
        for dm_id in ordered_ids:
            if dm_id not in dm_by_id:
                raise ValueError(
                    f"demand_manager_id {dm_id} nao pertence ao tecnico {technician_id}"
                )

        # Reconstrói os links na nova ordem
        for i, dm_id in enumerate(ordered_ids):
            row = dm_by_id[dm_id]
            row.next_demand_manager_id = (
                ordered_ids[i + 1] if i < len(ordered_ids) - 1 else None
            )

        self.db.commit()

        # Retorna a fila já atualizada (reutiliza get_queue)
        return self.get_queue(technician_id)

    # ── HELPERS ────────────────────────────────────────────────────────────────

    def _find_head(self, dm_models: list[DemandManager]) -> int | None:
        """
        Identifica o head da linked-list: o item que nenhum outro aponta.
        """
        all_ids  = {dm.demand_manager_id for dm in dm_models}
        pointed  = {dm.next_demand_manager_id for dm in dm_models if dm.next_demand_manager_id}
        heads    = all_ids - pointed

        if not heads:
            return None

        # Em condições normais há exatamente um head
        return heads.pop()

    def _orm_to_dm_model(self, row: DemandManagerORM) -> DemandManager:
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