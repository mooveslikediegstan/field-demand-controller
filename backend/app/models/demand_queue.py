from dataclasses import dataclass, field
from typing import Optional

@dataclass
class DemandQueue:

    technician_id: int
    head_id: Optional[int] = None
    demands: list = field(default_factory=list)

    def __post_init__(self):
        if self.demands is None:
            self.demands = []

    def sort(self):
        if not self.demands:
            return
        id_to_demand = {d.demand_manager_id: d for d in self.demands}
        sorted_demands = []
        current_id = self.head_id
        while current_id is not None:
            demand = id_to_demand.get(current_id)
            if demand is None:
                break
            sorted_demands.append(demand)
            current_id = demand.next_demand_manager_id
        self.demands = sorted_demands

    def rebuild_links(self):
        if not self.demands:
            self.head_id = None
            return
        for i in range(len(self.demands) - 1):
            self.demands[i].next_demand_manager_id = self.demands[i + 1].demand_manager_id
        self.demands[-1].next_demand_manager_id = None
        self.head_id = self.demands[0].demand_manager_id
    
    def append(self, demand_manager):
        self.demands.append(demand_manager)
        self.rebuild_links()