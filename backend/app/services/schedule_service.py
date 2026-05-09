# -*- coding: utf-8 -*-
from datetime import date, datetime, timezone
from sqlalchemy.orm import Session

from backend.app.models.technician import Technician
from backend.app.models.demand_queue import DemandQueue
from backend.app.models.demand_manager import DemandManager
from backend.app.models.planning_version import PlanningVersion
from backend.app.models.schedule_input import ScheduleInput
from backend.app.models.schedule_item_persistent import ScheduleItemPersistent
from backend.app.models.schedule_planner import SchedulePlanner
from backend.app.models.schedule_gantt import ScheduleGantt

from backend.app.database.orm_models import (
    DemandManagerORM,
    DemandORM,
    ScheduleGanttORM,
    PlanningVersionORM,
)
from backend.app.database.repository import (
    CityRepository,
    CustomerRepository,
    DemandManagerRepository,
    DemandRepository,
    PlanningVersionRepository,
    ProjectRepository,
    ScheduleGanttRepository,
    ScheduleItemRepository,
    TechnicianRepository,
)
from backend.app.schemas.schedule_schemas import GanttItemResponse

TRAVEL_SPEED_KMH = 80.0


class ScheduleService:

    def __init__(self, db: Session):
        self.db                    = db
        self.technician_repo       = TechnicianRepository(db)
        self.dm_repo               = DemandManagerRepository(db)
        self.planning_version_repo = PlanningVersionRepository(db)
        self.schedule_item_repo    = ScheduleItemRepository(db)
        self.schedule_gantt_repo   = ScheduleGanttRepository(db)
        self.city_repo             = CityRepository(db)
        self.demand_repo           = DemandRepository(db)
        self.project_repo          = ProjectRepository(db)
        self.customer_repo         = CustomerRepository(db)

    # ── REPLAN ────────────────────────────────────────────────────────────────

    def replan(self, technician_id: int) -> PlanningVersion:
        """
        Ponto de entrada chamado pelo router após save_sequence.
        Resolve tudo internamente: busca técnico, monta fila, roda planejamento.
        """
        technician = self.technician_repo.get_by_id(technician_id)
        if not technician:
            raise ValueError(f"Técnico {technician_id} não encontrado")

        dm_rows = self.dm_repo.get_by_technician(technician_id)
        if not dm_rows:
            raise ValueError(f"Técnico {technician_id} não possui demandas na fila")

        head_id   = self._find_head(dm_rows)
        queue     = DemandQueue(
            technician_id = technician_id,
            head_id       = head_id,
            demands       = dm_rows
        )
        queue.sort()

        return self.save_sequence(
            technician   = technician,
            demand_queue = queue,
            start_date   = date.today(),
        )

    # ── SAVE SEQUENCE (orquestração completa) ─────────────────────────────────

    def save_sequence(
        self,
        technician:   Technician,
        demand_queue: DemandQueue,
        start_date:   date,
    ) -> PlanningVersion:

        try:
            # 1. Persiste a nova ordem na fila
            demand_queue.rebuild_links()
            for dm in demand_queue.demands:
                self.dm_repo.update(dm)

            # 2. Desativa versão anterior e cria nova
            self.planning_version_repo.deactivate_all_by_technician(technician.technician_id)
            new_version = self.planning_version_repo.create(PlanningVersion(
                technician_id = technician.technician_id,
                created_at    = datetime.now(timezone.utc),
                is_active     = True,
            ))

            # 3. Monta inputs para o SchedulePlanner
            origin_city     = self.city_repo.get_by_id(technician.current_location_city_id)
            schedule_inputs = self._build_schedule_inputs(demand_queue)

            # 4. Roda o planejamento em memória
            planner = SchedulePlanner(
                technician_id        = technician.technician_id,
                initial_start_date   = start_date,
                daily_capacity_hours = technician.daily_capacity,
                travel_speed_kmh     = TRAVEL_SPEED_KMH,
                origin_lat           = origin_city.geolocation_lat,
                origin_lon           = origin_city.geolocation_lon,
            )
            planner.plan(schedule_inputs)

            # 5. Persiste schedule_items
            persistent_items = [
                ScheduleItemPersistent(
                    version_id        = new_version.version_id,
                    demand_manager_id = item.demand_manager_id,
                    technician_id     = technician.technician_id,
                    scheduled_date    = item.scheduled_date,
                    action            = item.action,
                    worked_hours      = item.work_time,
                    distance          = item.distance,
                )
                for item in planner.scheduled_items
            ]
            self.schedule_item_repo.create_batch(persistent_items)

            # 6. Deriva e persiste schedule_gantt
            gantt_items = self._build_gantt(
                new_version.version_id, technician.technician_id, planner.scheduled_items
            )
            self.schedule_gantt_repo.create_batch(gantt_items)

            self.db.commit()
            return new_version

        except Exception:
            self.db.rollback()
            raise

    # ── GET GANTT ─────────────────────────────────────────────────────────────

    def get_gantt(self, technician_id: int) -> list[GanttItemResponse]:
        """
        Retorna o Gantt ativo do técnico com demand_title enriquecido via JOIN.
        Caminho: schedule_gantt → demand_manager → demand → demand_title.
        """
        active_version = self.planning_version_repo.get_active_by_technician(technician_id)
        if not active_version:
            return []

        rows = (
            self.db.query(ScheduleGanttORM, DemandORM)
            .join(DemandManagerORM,
                  ScheduleGanttORM.demand_manager_id == DemandManagerORM.demand_manager_id)
            .join(DemandORM,
                  DemandManagerORM.demand_id == DemandORM.demand_id)
            .filter(ScheduleGanttORM.version_id == active_version.version_id)
            .order_by(ScheduleGanttORM.start_date)
            .all()
        )

        return [
            GanttItemResponse(
                demand_manager_id = gantt_orm.demand_manager_id,
                demand_title      = demand_orm.demand_title,
                start_date        = gantt_orm.start_date,
                finish_date       = gantt_orm.finish_date,
            )
            for gantt_orm, demand_orm in rows
        ]

    # ── HELPERS ───────────────────────────────────────────────────────────────

    def _build_schedule_inputs(self, demand_queue: DemandQueue) -> list[ScheduleInput]:
        inputs = []
        for dm in demand_queue.demands:
            demand   = self.demand_repo.get_by_id(dm.demand_id)
            project  = self.project_repo.get_by_id(demand.project_id)
            customer = self.customer_repo.get_by_id(project.customer_id)
            city     = self.city_repo.get_by_id(customer.city_id)
            inputs.append(ScheduleInput(
                demand_manager_id = dm.demand_manager_id,
                demand_id         = dm.demand_id,
                estimated_time    = demand.estimated_time,
                city_lat          = city.geolocation_lat,
                city_lon          = city.geolocation_lon,
            ))
        return inputs

    def _build_gantt(
        self,
        version_id:    int,
        technician_id: int,
        items:         list,
    ) -> list[ScheduleGantt]:
        from itertools import groupby
        key_fn = lambda i: i.demand_manager_id
        gantt  = []
        for dm_id, group in groupby(sorted(items, key=key_fn), key=key_fn):
            group_items = list(group)
            gantt.append(ScheduleGantt(
                version_id        = version_id,
                demand_manager_id = dm_id,
                technician_id     = technician_id,
                start_date        = min(i.scheduled_date for i in group_items),
                finish_date       = max(i.scheduled_date for i in group_items),
            ))
        return gantt

    def _find_head(self, dm_models: list[DemandManager]) -> int | None:
        all_ids = {dm.demand_manager_id for dm in dm_models}
        pointed = {dm.next_demand_manager_id for dm in dm_models if dm.next_demand_manager_id}
        heads   = all_ids - pointed
        return heads.pop() if heads else None