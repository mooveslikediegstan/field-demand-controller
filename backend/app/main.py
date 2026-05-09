# -*- coding: utf-8 -*-
from fastapi import FastAPI
from backend.app.routers import demand_router, technician_router

app = FastAPI(
    title="Gestão de Agenda Técnica",
    version="1.0.0",
)

app.include_router(demand_router.router)
app.include_router(technician_router.router)


@app.get("/health")
def health():
    return {"status": "ok"}