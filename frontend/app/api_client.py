# frontend/app/api_client.py
import requests
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("API_URL", "http://localhost:8000/api")

# ── DEMANDS ────────────────────────────s───────────────────────────────────────

def create_demand(payload: dict) -> dict:
    r = requests.post(f"{BASE_URL}/demands/", json=payload)
    r.raise_for_status()
    return r.json()

def get_demand(demand_id: int) -> dict:
    r = requests.get(f"{BASE_URL}/demands/{demand_id}")
    r.raise_for_status()
    return r.json()

def list_demands(status: Optional[str] = None) -> list:
    params = {"status": status} if status else {}
    r = requests.get(f"{BASE_URL}/demands/", params=params)
    r.raise_for_status()
    return r.json()

def update_demand(demand_id: int, payload: dict) -> dict:
    r = requests.put(f"{BASE_URL}/demands/{demand_id}", json=payload)
    r.raise_for_status()
    return r.json()

def cancel_demand(demand_id: int) -> dict:
    r = requests.delete(f"{BASE_URL}/demands/{demand_id}")
    r.raise_for_status()
    return r.json()

# ── ALLOCATION ────────────────────────────────────────────────────────────────

def allocate_technician(demand_id: int, technician_id: int) -> dict:
    r = requests.post(f"{BASE_URL}/demands/{demand_id}/allocate", json={"technician_id": technician_id})
    r.raise_for_status()
    return r.json()

def deallocate_technician(demand_id: int, technician_id: int) -> dict:
    r = requests.delete(f"{BASE_URL}/demands/{demand_id}/allocate/{technician_id}")
    r.raise_for_status()
    return r.json()

# ── QUEUE ─────────────────────────────────────────────────────────────────────

def get_queue(technician_id: int) -> list:
    r = requests.get(f"{BASE_URL}/technicians/{technician_id}/queue")
    r.raise_for_status()
    return r.json()

def save_sequence(technician_id: int, ordered_ids: list[int]) -> list:
    r = requests.post(
        f"{BASE_URL}/technicians/{technician_id}/save-sequence",
        json={"ordered_demand_manager_ids": ordered_ids}
    )
    r.raise_for_status()
    return r.json()

# ── GANTT ─────────────────────────────────────────────────────────────────────

def get_gantt(technician_id: int) -> list:
    r = requests.get(f"{BASE_URL}/technicians/{technician_id}/schedule")
    r.raise_for_status()
    return r.json()

# ── CONCLUSION ────────────────────────────────────────────────────────────────

def get_conclusion_data(demand_manager_id: int) -> dict:
    r = requests.get(f"{BASE_URL}/demands/{demand_manager_id}/conclusion-data")
    r.raise_for_status()
    return r.json()

def conclude_demand(demand_manager_id: int, payload: dict) -> dict:
    r = requests.post(f"{BASE_URL}/demands/{demand_manager_id}/conclude", json=payload)
    r.raise_for_status()
    return r.json()