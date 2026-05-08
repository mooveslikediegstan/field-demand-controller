# -*- coding: utf-8 -*-
import pytest
from backend.app.models.demand_queue import DemandQueue
from backend.app.models.demand_manager import DemandManager

@pytest.fixture
def dm1():
    return DemandManager(demand_id=1, technician_id=10, status="Pendente", demand_manager_id=1, next_demand_manager_id=2)

@pytest.fixture
def dm2():
    return DemandManager(demand_id=2, technician_id=10, status="Pendente", demand_manager_id=2, next_demand_manager_id=3)

@pytest.fixture
def dm3():
    return DemandManager(demand_id=3, technician_id=10, status="Pendente", demand_manager_id=3, next_demand_manager_id=None)

@pytest.fixture
def valid_queue(dm1, dm2, dm3):
    return DemandQueue(technician_id=10, head_id=1, demands=[dm1, dm2, dm3])

# --- criacao basica ---

def test_queue_created_with_valid_fields(valid_queue):
    assert valid_queue.technician_id == 10
    assert valid_queue.head_id == 1
    assert len(valid_queue.demands) == 3

# --- sort ---

def test_sort_returns_correct_order(dm1, dm2, dm3):
    shuffled = DemandQueue(technician_id=10, head_id=1, demands=[dm3, dm1, dm2])
    shuffled.sort()
    assert shuffled.demands[0].demand_manager_id == 1
    assert shuffled.demands[1].demand_manager_id == 2
    assert shuffled.demands[2].demand_manager_id == 3

def test_sort_single_item_queue():
    dm = DemandManager(demand_id=1, technician_id=10, status="Pendente", demand_manager_id=1)
    queue = DemandQueue(technician_id=10, head_id=1, demands=[dm])
    queue.sort()
    assert len(queue.demands) == 1

def test_sort_empty_queue():
    queue = DemandQueue(technician_id=10, head_id=None, demands=[])
    queue.sort()
    assert queue.demands == []

# --- rebuild_links ---

def test_rebuild_links_updates_next_ids(dm1, dm2, dm3):
    queue = DemandQueue(technician_id=10, head_id=1, demands=[dm1, dm2, dm3])
    queue.rebuild_links()
    assert queue.demands[0].next_demand_manager_id == 2
    assert queue.demands[1].next_demand_manager_id == 3
    assert queue.demands[2].next_demand_manager_id is None

def test_rebuild_links_updates_head_id(dm1, dm2, dm3):
    queue = DemandQueue(technician_id=10, head_id=3, demands=[dm1, dm2, dm3])
    queue.rebuild_links()
    assert queue.head_id == dm1.demand_manager_id

# --- append ---

def test_append_adds_to_tail(valid_queue):
    new_dm = DemandManager(demand_id=4, technician_id=10, status="Pendente", demand_manager_id=4)
    valid_queue.append(new_dm)
    assert valid_queue.demands[-1].demand_manager_id == 4
    assert valid_queue.demands[-2].next_demand_manager_id == 4

def test_append_to_empty_queue():
    queue = DemandQueue(technician_id=10, head_id=None, demands=[])
    dm = DemandManager(demand_id=1, technician_id=10, status="Pendente", demand_manager_id=1)
    queue.append(dm)
    assert queue.head_id == 1
    assert len(queue.demands) == 1