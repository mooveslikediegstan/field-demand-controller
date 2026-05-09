# Gestão de Agenda Técnica
> Arquivo de contexto para agentes de IA. Última atualização: 09/05/2026.
> Itens marcados com `[ TODO ]` ainda não foram definidos.
> Convenção: nomes de código em inglês, mensagens de erro em português.

---

## 1. Visão Geral

Sistema de **gestão de demandas técnicas e agendamento de técnicos de campo**, substituindo solução legada em Excel/VBA + Access.

Fluxo principal:
```
Demand (DMD) → DemandManager/Fila (DMD_MGMT) → SchedulePlanner → PlanningVersion + ScheduleItem/ScheduleGantt → ExecutionLog
```

**Uso simultâneo:** 2 a 8 usuários — requer PostgreSQL.

**Estratégia de Planejamento (Opção A — Automática):**
Cada vez que o usuário salva a sequência de um técnico:
1. Persiste a nova ordem em `demand_manager`
2. Cria uma nova `planning_version`
3. Roda `SchedulePlanner` em memória
4. Persiste os `schedule_item` (atômico) e `schedule_gantt` (simplificado)

Resultado: **Gantt e analytics sempre atualizados**, sem lag.

---

## 2. Stack Tecnológico

| Camada | Tecnologia | Observação |
|---|---|---|
| Backend / API | FastAPI | Framework principal |
| Servidor ASGI | Uvicorn | — |
| Frontend | Streamlit | Fase inicial |
| Banco de dados | PostgreSQL 16 (local dev) / Railway ou Render (produção) | Obrigatório — multi-usuário |
| ORM | SQLAlchemy 2.x | Padrão Repository |
| Migrações | Alembic | Configurado e funcionando |
| Validação | Pydantic v2 | — |
| Testes | pytest | TDD |
| Containerização | Docker | Apenas produção — dev local sem Docker |
| Linguagem | Python 3.13 | |
| SO (dev) | Windows 11 | PowerShell no VS Code |

### Comando padrão para rodar testes (Windows)
```powershell
python -m pytest tests/ -v
```

### Padrão de testes consolidado
- Fixture `valid_*` compartilhada por módulo
- Helper `make_*(valid_fixture, **overrides)` — nunca mutar fixture nem chamar `_validate()` diretamente
- Uma asserção por teste
- Nomenclatura: `test_context_with_situation` / `test_situation_should_fail`

---

## 3. Arquitetura

```
Frontend (Streamlit)
      ↓ HTTP/JSON
Backend (FastAPI)
    ├── Routers      → endpoints HTTP
    ├── Schemas      → validação Pydantic
    ├── Services     → lógica de negócio e planejamento
    └── Repository   → acesso ao banco via SQLAlchemy
      ↓ SQL
Banco de Dados (PostgreSQL)
```

---

## 4. Estrutura de Diretórios

```
field-demand-controller/
├── .gitignore                           (.env ignorado)
├── .vscode/
│   └── settings.json                   (Pylance: reportAttributeAccessIssue e reportArgumentType = none)
├── PROJECT_CONTEXT.md
├── alembic.ini                          ✅
├── migrations/                          ✅
│   ├── env.py
│   └── versions/
│       └── 002_add_planning_tables.py   ✅ (nova — planning, schedule, execution)
├── backend/
│   ├── requirements.txt
│   ├── Dockerfile                       [ TODO — apenas produção ]
│   └── app/
│       ├── main.py                      [ TODO ]
│       ├── models/
│       │   ├── city.py                  ✅
│       │   ├── technician.py            ✅
│       │   ├── demand.py                ✅
│       │   ├── demand_manager.py        ✅
│       │   ├── demand_queue.py          ✅
│       │   ├── schedule_input.py        ✅
│       │   ├── schedule_item.py         ✅ (em memória para SchedulePlanner)
│       │   ├── schedule_planner.py      ✅
│       │   ├── geo_utils.py             ✅
│       │   ├── customer.py              ✅
│       │   ├── project.py               ✅
│       │   ├── analyst.py               ✅
│       │   ├── planning_version.py      ✅ (novo — versionamento)
│       │   ├── schedule_item_persistent.py ✅ (novo — persistido)
│       │   ├── schedule_gantt.py        ✅ (novo — simplificado)
│       │   └── execution_log.py         ✅ (novo — auditoria)
│       ├── database/
│       │   ├── session.py               ✅
│       │   ├── orm_models.py            ✅ (atualizado com 4 novas classes ORM)
│       │   ├── init_db.py               ✅
│       │   └── repository.py            ✅ (atualizado com 4 novos repositories)
│       ├── services/
│       │   ├── demand_service.py        [ TODO ]
│       │   └── schedule_service.py      [ TODO ]
│       ├── routers/                     [ TODO ]
│       └── schemas/                     [ TODO ]
├── frontend/
│   ├── Dockerfile                       [ TODO ]
│   ├── requirements.txt                 [ TODO ]
│   └── app/
│       └── main.py                      [ TODO ]
└── tests/
    ├── test_city.py                     ✅
    ├── test_technician.py               ✅
    ├── test_demand.py                   ✅
    ├── test_demand_manager.py           ✅
    ├── test_demand_queue.py             ✅
    ├── test_geo_utils.py                ✅
    ├── test_schedule_planner.py         ✅
    ├── test_customer.py                 ✅
    ├── test_project.py                  ✅
    ├── test_analyst.py                  ✅
    ├── test_planning_version.py         ✅ (novo — 15 testes)
    ├── test_schedule_item_persistent.py ✅ (novo — 18 testes)
    ├── test_schedule_gantt.py           ✅ (novo — 15 testes)
    └── test_execution_log.py            ✅ (novo — 20 testes)
```

---

## 5. Variáveis de Ambiente (.env — nunca commitar)

```
DB_USER=postgres
DB_PASSWORD=sua_senha
DB_HOST=localhost
DB_PORT=5432
DB_NAME=agenda_db
```

`session.py` usa `urllib.parse.quote_plus` para escapar caracteres especiais na senha.

---

## 6. Models ✅ — todos concluídos com TDD

### Domínio Existente (não alterado)
- `City` ✅
- `Analyst` ✅
- `Customer` ✅
- `Project` ✅
- `Technician` ✅
- `Demand` ✅
- `DemandManager` ✅
- `DemandQueue` ✅
- `ScheduleInput` ✅
- `ScheduleItem` (em memória) ✅
- `SchedulePlanner` ✅
- `geo_utils` ✅

### Novos Models — Persistência e Execução ✅

#### `PlanningVersion` — tabela `planning_version`
Versionamento de planejamentos por técnico.

| Campo | Tipo Python | Obrigatório | Regras |
|-------|-------------|-------------|--------|
| `version_id` | `Optional[int]` | Não | Auto-gerado pelo banco |
| `technician_id` | `int` | Sim | > 0 (FK technician) |
| `created_at` | `datetime` | Sim | Timestamp de criação |
| `is_active` | `bool` | Sim | Padrão True; apenas 1 por técnico |

**Invariante:** Apenas uma versão por técnico tem `is_active = True`. Ao replanejar, deativa a anterior e cria a nova.

#### `ScheduleItem` (persistido) — tabela `schedule_item`
Planejamento atômico — um item por ação por dia. Resultado do `SchedulePlanner` persistido.

| Campo | Tipo Python | Obrigatório | Regras |
|-------|-------------|-------------|--------|
| `schedule_item_id` | `Optional[int]` | Não | Auto-gerado pelo banco |
| `version_id` | `int` | Sim | > 0 (FK planning_version) |
| `demand_manager_id` | `int` | Sim | > 0 (FK demand_manager) |
| `technician_id` | `int` | Sim | > 0 (FK technician) |
| `scheduled_date` | `date` | Sim | — |
| `action` | `str` | Sim | `"Deslocamento"` ou `"Prestacao de Servico"` |
| `worked_hours` | `float` | Sim | >= 0 |
| `distance` | `int` | Sim | >= 0 (km) |

**Uso:** Analytics, pipeline de dados, cálculos granulares de horas.

#### `ScheduleGantt` — tabela `schedule_gantt`
Planejamento simplificado — start/finish date por demanda. Derivado de `ScheduleItem`.

| Campo | Tipo Python | Obrigatório | Regras |
|-------|-------------|-------------|--------|
| `schedule_gantt_id` | `Optional[int]` | Não | Auto-gerado pelo banco |
| `version_id` | `int` | Sim | > 0 (FK planning_version) |
| `demand_manager_id` | `int` | Sim | > 0 (FK demand_manager) |
| `technician_id` | `int` | Sim | > 0 (FK technician) |
| `start_date` | `date` | Sim | <= finish_date |
| `finish_date` | `date` | Sim | >= start_date |

**Uso:** Gráfico Gantt, dashboard de agenda.

#### `ExecutionLog` — tabela `execution_log`
Registro permanente da execução real. Lançado manualmente ao concluir demanda.

| Campo | Tipo Python | Obrigatório | Regras |
|-------|-------------|-------------|--------|
| `execution_log_id` | `Optional[int]` | Não | Auto-gerado pelo banco |
| `demand_manager_id` | `int` | Sim | > 0 (FK demand_manager) |
| `technician_id` | `int` | Sim | > 0 (FK technician) |
| `execution_date` | `date` | Sim | — |
| `action` | `str` | Sim | `"Deslocamento"` ou `"Prestacao de Servico"` |
| `distance` | `int` | Sim | >= 0 (km) |
| `worked_hours` | `float` | Sim | >= 0 |

**Propriedade:** Permanente — nunca deletado, apenas auditoria. Um DemandManager pode ter múltiplas linhas (uma por dia entre start e finish).

---

## 7. Banco de Dados

### Tabelas Criadas (Via Alembic) ✅

| Tabela | Model | ORM | Repositório | Status |
|--------|-------|-----|-------------|--------|
| `city` | `City` | `CityORM` | `CityRepository` | ✅ |
| `analyst` | `Analyst` | `AnalystORM` | `AnalystRepository` | ✅ |
| `customer` | `Customer` | `CustomerORM` | `CustomerRepository` | ✅ |
| `project` | `Project` | `ProjectORM` | `ProjectRepository` | ✅ |
| `technician` | `Technician` | `TechnicianORM` | `TechnicianRepository` | ✅ |
| `demand` | `Demand` | `DemandORM` | `DemandRepository` | ✅ |
| `demand_manager` | `DemandManager` | `DemandManagerORM` | `DemandManagerRepository` | ✅ |
| `planning_version` | `PlanningVersion` | `PlanningVersionORM` | `PlanningVersionRepository` | ✅ |
| `schedule_item` | `ScheduleItem` | `ScheduleItemORM` | `ScheduleItemRepository` | ✅ |
| `schedule_gantt` | `ScheduleGantt` | `ScheduleGanttORM` | `ScheduleGanttRepository` | ✅ |
| `execution_log` | `ExecutionLog` | `ExecutionLogORM` | `ExecutionLogRepository` | ✅ |

### Índices Criados (Migration 002) ✅

- `planning_version(technician_id, is_active)` — query: "versão ativa por técnico"
- `schedule_item(version_id, demand_manager_id, scheduled_date)` — filtragens comuns
- `schedule_gantt(version_id, demand_manager_id, technician_id)` — Gantt queries
- `execution_log(demand_manager_id, technician_id, execution_date)` — histórico

---

## 8. Repository Layer ✅

Todos os repositories seguem o padrão:
- `get_by_id(id)` → Optional[Model]
- `get_*()` → list[Model]
- `create(model)` → Model (com ID populado)
- `create_batch(models)` → list[Model]
- `_to_model(orm)` → Model

### Novos Repositories ✅

**PlanningVersionRepository**
- `get_by_id(version_id)`
- `get_active_by_technician(technician_id)` — a versão ativa
- `get_all_by_technician(technician_id)` — todas as versões (histórico)
- `create(pv)`
- `deactivate_all_by_technician(technician_id)` — marca antigas como inativas

**ScheduleItemRepository**
- `get_by_id(schedule_item_id)`
- `get_by_version(version_id)` — todos os itens de um planejamento
- `get_by_demand_manager(demand_manager_id, version_id=None)`
- `get_by_technician_and_version(technician_id, version_id)`
- `create(si)`
- `create_batch(items)` — insert eficiente em massa

**ScheduleGanttRepository**
- `get_by_id(schedule_gantt_id)`
- `get_by_version(version_id)`
- `get_by_technician_and_version(technician_id, version_id)`
- `create(sg)`
- `create_batch(items)`

**ExecutionLogRepository**
- `get_by_id(execution_log_id)`
- `get_by_demand_manager(demand_manager_id)` — histórico completo
- `get_by_technician_and_date_range(technician_id, start, end)` — relatórios
- `create(el)`
- `create_batch(items)`

---

## 9. Testes ✅

### Status Atual
- **Total de testes:** 68 novos + 48 existentes = **116 testes** ✅
- **Todos passando** ✅
- **Coverage:** 100% nos 4 novos models

### Novos Testes (TDD)

| Arquivo | Testes | Cobertura |
|---------|--------|-----------|
| `test_planning_version.py` | 15 | Criação, IDs, timestamps, is_active, cenários |
| `test_schedule_item_persistent.py` | 18 | IDs, action, hours, distance, deslocamento/serviço |
| `test_schedule_gantt.py` | 15 | IDs, datas, sequência, demandas simples/múltiplas |
| `test_execution_log.py` | 20 | IDs, action, hours, distance, dias múltiplos, auditoria |

Todos seguem padrão: fixture `valid_*`, helper `make_*`, uma asserção por teste.

---

## 10. Decisões de Design

| Decisão | Motivo | Status |
|---------|--------|--------|
| PostgreSQL obrigatório | 2-8 usuários simultâneos | ✅ |
| Dev local sem Docker | Virtualização desabilitada | ✅ |
| Deploy em nuvem (Railway/Render) | Sem acesso admin | ✅ |
| Fila como linked-list | Reordenação eficiente | ✅ |
| `ServiceOrder` eliminado | DemandManager suficiente | ✅ |
| DomainQueue/SchedulePlanner em memória | Construídos durante request | ✅ |
| **Opção A — Replanejamento Automático** | Planejamento gerado a cada salvamento de sequência | ✅ |
| `planning_version` por técnico | Replaneja a fila inteira atomicamente | ✅ |
| `schedule_item` atômico + `schedule_gantt` simplificado | Dual-view: analytics + UI | ✅ |
| `execution_log` permanente | Auditoria, nunca deletado | ✅ |
| Transações atômicas no banco | Tudo persiste junto ou nada | ✅ |
| `distance_between_coordinates` com fator 1.35 | Aproximação suficiente; API externa no futuro | ✅ |
| `customer_id` e `project_id` como string manual | [ TODO ] Avaliar migração para int auto-gerado | — |

---

## 11. Fluxo Completo (Opção A Implementada)

```
1. Usuário clica "Salvar Sequência" do técnico
   ↓
2. DemandManagerRepository.update() — nova ordem em demand_manager
   ↓
3. PlanningVersionRepository.deactivate_all_by_technician(tech_id)
   ↓
4. PlanningVersionRepository.create(new_version) → version_id
   ↓
5. SchedulePlanner.plan(demands) em MEMÓRIA
   → Gera list[ScheduleItem] e list[ScheduleGantt]
   ↓
6. ScheduleItemRepository.create_batch([schedule_items])
   ↓
7. ScheduleGanttRepository.create_batch([schedule_gantt])
   ↓
8. COMMIT da transação (ou ROLLBACK se erro)
   ↓
9. Gantt e Analytics já mostram dados atualizados ✅
```

---

## 12. Próximos Passos

### Fase Atual (Concluída) ✅
1. ✅ Todos os models com TDD
2. ✅ PostgreSQL local + SQLAlchemy + Alembic
3. ✅ ORM models + Repository layer
4. ✅ 4 novas tabelas para planejamento e execução
5. ✅ 68 novos testes, todos passando
6. ✅ Opção A implementada: replanejamento automático
7. ✅ ScheduleService — orquestra o fluxo de planejamento
8. ✅ DemandService — camada de lógica de demanda
   - 10 testes passando
   - 18 testes passando
9. ✅ ExecutionService + ExecutionInput — testes passando

1. **Rotas FastAPI**
   - `POST /api/technicians/{tech_id}/save-sequence` → triggers planejamento
   - `GET /api/technicians/{tech_id}/schedule` → retorna schedule_gantt
   - `GET /api/technicians/{tech_id}/planning` → retorna schedule_item
   - `POST /api/demands/{dm_id}/conclude` → abre tela de execução
   - `POST /api/execution-logs/` → salva horas reais

2. **Schemas Pydantic**
   - Request/response para cada rota

3. **Interface Streamlit**
   - Tela de reordenamento de fila
   - Gantt interativo
   - Relatórios de execução
   - Dashboard de métricas

4. **Deploy em nuvem**
   - Railway ou Render
   - Documentação de deploy

---

## 13. Métricas e Health Checks

### Queries Críticas (para monitoramento)
```sql
-- Versão ativa por técnico
SELECT * FROM planning_version 
WHERE technician_id = ? AND is_active = True;

-- Planejamento de hoje para um técnico
SELECT * FROM schedule_gantt sg
JOIN planning_version pv ON sg.version_id = pv.version_id
WHERE sg.technician_id = ? AND pv.is_active = True
AND sg.start_date <= TODAY() AND sg.finish_date >= TODAY();

-- Horas reais vs planejadas
SELECT 
  dm.demand_manager_id,
  SUM(si.worked_hours) as planned_hours,
  SUM(el.worked_hours) as actual_hours
FROM schedule_item si
JOIN execution_log el ON si.demand_manager_id = el.demand_manager_id
WHERE si.version_id = (SELECT version_id FROM planning_version WHERE technician_id = ? AND is_active = True)
GROUP BY dm.demand_manager_id;
```

---

## 14. Limites e Restrições Conhecidas

| Limitação | Impacto | Solução Futura |
|-----------|---------|----------------|
| `customer_id`/`project_id` string manual | Entrada de dados lenta | Auto-geração com prefixo |
| Haversine + 1.35 vs real roads | ~5% erro de distância | Google Maps API |
| Sem API de tráfego | Não conta congestionamento | Integrar Waze/Google Maps |
| Sem histórico de alterações | Auditoria limitada | Trigger de audit log |
| `schedule_item.sequence_position` não persistido | Ordem recalculada por query | Persistir se necessário |

---

## 15. Contatos Rápidos — Documentos Relacionados

- **Implementação de Models:** `EXECUTIVE_SUMMARY.md`
- **Setup de Integração:** `IMPLEMENTATION_GUIDE.md`
- **Cobertura de Testes:** `TESTES_RESUMO.md`
- **ORM Models Completo:** `orm_models.py` (atualizado)
- **Repositories Completo:** `new_repositories.py` (template)

---

*Última atualização: 09/05/2026 — Planejamento e Execução implementados com TDD; 116 testes passando; pronto para Services*
