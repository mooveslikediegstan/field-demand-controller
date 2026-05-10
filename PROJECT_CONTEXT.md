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

### Comando para subir o servidor
```powershell
python -m uvicorn backend.app.main:app --reload
```

### Padrão de testes consolidado
- Fixture `valid_*` compartilhada por módulo
- Helper `make_*(valid_fixture, **overrides)` — nunca mutar fixture nem chamar `_validate()` diretamente
- Uma asserção por teste
- Nomenclatura: `test_context_with_situation` / `test_situation_should_fail`
- Testes de service usam `MagicMock` — sem conexão real ao banco

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
├── seed.py                              ✅ (dados fictícios para dev)
├── alembic.ini                          ✅
├── migrations/                          ✅
│   ├── env.py
│   └── versions/
│       └── 002_add_planning_tables.py   ✅
├── backend/
│   ├── requirements.txt
│   ├── Dockerfile                       [ TODO — apenas produção ]
│   └── app/
│       ├── main.py                      ✅
│       ├── models/
│       │   ├── city.py                  ✅
│       │   ├── technician.py            ✅
│       │   ├── demand.py                ✅
│       │   ├── demand_manager.py        ✅
│       │   ├── demand_queue.py          ✅
│       │   ├── schedule_input.py        ✅
│       │   ├── schedule_item.py         ✅
│       │   ├── schedule_planner.py      ✅
│       │   ├── geo_utils.py             ✅
│       │   ├── customer.py              ✅
│       │   ├── project.py               ✅
│       │   ├── analyst.py               ✅
│       │   ├── planning_version.py      ✅
│       │   ├── schedule_item_persistent.py ✅
│       │   ├── schedule_gantt.py        ✅
│       │   └── execution_log.py         ✅
│       ├── database/
│       │   ├── session.py               ✅
│       │   ├── orm_models.py            ✅
│       │   ├── init_db.py               ✅
│       │   └── repository.py            ✅
│       ├── services/
│       │   ├── demand_service.py        ✅
│       │   ├── queue_service.py         ✅
│       │   └── schedule_service.py      ✅
│       ├── routers/
│       │   ├── demand_router.py         ✅
│       │   └── technician_router.py     ✅
│       └── schemas/
│           ├── demand_schemas.py        ✅
│           ├── demand_manager_schemas.py ✅
│           └── schedule_schemas.py      ✅
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
    ├── test_planning_version.py         ✅
    ├── test_schedule_item_persistent.py ✅
    ├── test_schedule_gantt.py           ✅
    ├── test_execution_log.py            ✅
    └── test_queue_service.py            ✅
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

### Domínio Principal
- `City`, `Analyst`, `Customer`, `Project`, `Technician` ✅
- `Demand`, `DemandManager`, `DemandQueue` ✅
- `ScheduleInput`, `ScheduleItem` (memória), `SchedulePlanner`, `geo_utils` ✅

### Persistência e Execução
- `PlanningVersion`, `ScheduleItemPersistent`, `ScheduleGantt`, `ExecutionLog` ✅

---

## 7. ORM + Repository ✅

| Entidade | Model | ORM | Repository |
|---|---|---|---|
| `city` | `City` | `CityORM` | `CityRepository` |
| `analyst` | `Analyst` | `AnalystORM` | `AnalystRepository` |
| `customer` | `Customer` | `CustomerORM` | `CustomerRepository` |
| `project` | `Project` | `ProjectORM` | `ProjectRepository` |
| `technician` | `Technician` | `TechnicianORM` | `TechnicianRepository` |
| `demand` | `Demand` | `DemandORM` | `DemandRepository` |
| `demand_manager` | `DemandManager` | `DemandManagerORM` | `DemandManagerRepository` |
| `planning_version` | `PlanningVersion` | `PlanningVersionORM` | `PlanningVersionRepository` |
| `schedule_item` | `ScheduleItemPersistent` | `ScheduleItemORM` | `ScheduleItemRepository` |
| `schedule_gantt` | `ScheduleGantt` | `ScheduleGanttORM` | `ScheduleGanttRepository` |
| `execution_log` | `ExecutionLog` | `ExecutionLogORM` | `ExecutionLogRepository` |

---

## 8. Services ✅

### DemandService (`demand_service.py`)
- `create_demand(demand)` → Demand
- `get_demand(demand_id)` → Demand
- `update_demand(demand)` → Demand
- `cancel_demand(demand_id)` → Demand — só cancela se não houver técnicos alocados
- `allocate_technician(demand_id, technician_id)` → DemandManager — adiciona ao final da fila via linked-list
- `deallocate_technician(demand_id, technician_id)` → Demand — reconstrói links da fila após remoção
- `get_conclusion_data(demand_manager_id)` → dict
- `conclude_demand_manager(demand_manager_id, actual_time, travel_time, travel_distance, finish_date)` → Demand

### QueueService (`queue_service.py`)
- `get_queue(technician_id)` → list[QueueItemResponse] — JOIN com demand, ordenado pela linked-list
- `save_sequence(technician_id, payload)` → list[QueueItemResponse] — reordena links e persiste
- `_find_head(dm_models)` → int | None
- `_orm_to_dm_model(row)` → DemandManager

### ScheduleService (`schedule_service.py`)
- `replan(technician_id)` → PlanningVersion — ponto de entrada do router; resolve tudo internamente
- `save_sequence(technician, demand_queue, start_date)` → PlanningVersion — orquestração completa
- `get_gantt(technician_id)` → list[GanttItemResponse] — JOIN triplo: schedule_gantt → demand_manager → demand
- `_build_schedule_inputs(demand_queue)` → list[ScheduleInput]
- `_build_gantt(version_id, technician_id, items)` → list[ScheduleGantt]
- `_find_head(dm_models)` → int | None

---

## 9. Schemas Pydantic ✅

### demand_schemas.py
- `DemandCreateRequest` — campos editáveis; status/request_date/actual_time gerados pelo backend
- `DemandUpdateRequest` — campos editáveis + status
- `DemandResponse` — objeto completo; reutilizado em todas as rotas de demanda

### demand_manager_schemas.py
- `AllocateRequest` — technician_id
- `DemandManagerResponse` — campos do DemandManager
- `ConclusionDataResponse` — dados para montar tela de conclusão
- `ConcludeRequest` — actual_time, travel_time, travel_distance, finish_date

### schedule_schemas.py
- `QueueItemResponse` — dados enriquecidos da fila (JOIN demand_manager + demand)
- `SaveSequenceRequest` — ordered_demand_manager_ids: list[int]
- `GanttItemResponse` — demand_manager_id, demand_title, start_date, finish_date

---

## 10. Routers FastAPI ✅

### demand_router.py — prefix: `/api/demands`

| Método | Rota | Ação |
|---|---|---|
| POST | `/` | Criar demanda |
| PUT | `/{demand_id}` | Atualizar demanda |
| DELETE | `/{demand_id}` | Cancelar demanda (só sem técnicos alocados) |
| POST | `/{demand_id}/allocate` | Alocar técnico |
| DELETE | `/{demand_id}/allocate/{technician_id}` | Desalocar técnico + replan automático |
| GET | `/{dm_id}/conclusion-data` | Dados para tela de conclusão |
| POST | `/{dm_id}/conclude` | Concluir ordem |

### technician_router.py — prefix: `/api/technicians`

| Método | Rota | Ação |
|---|---|---|
| GET | `/{tech_id}/queue` | Listar fila ordenada |
| POST | `/{tech_id}/save-sequence` | Salvar sequência + replan automático |
| GET | `/{tech_id}/schedule` | Visualizar Gantt |

### main.py
- Registra ambos os routers
- Expõe `GET /health`
- Swagger disponível em `http://localhost:8000/docs`

---

## 11. Decisões de Design

| Decisão | Motivo | Status |
|---|---|---|
| PostgreSQL obrigatório | 2-8 usuários simultâneos | ✅ |
| Dev local sem Docker | Virtualização desabilitada | ✅ |
| Deploy em nuvem (Railway/Render) | Sem acesso admin | ✅ |
| Fila como linked-list | Reordenação eficiente | ✅ |
| `ServiceOrder` eliminado | DemandManager suficiente | ✅ |
| DomainQueue/SchedulePlanner em memória | Construídos durante request | ✅ |
| Opção A — Replanejamento Automático | Planejamento gerado a cada mudança na fila | ✅ |
| `planning_version` por técnico | Replaneja a fila inteira atomicamente | ✅ |
| `schedule_item` atômico + `schedule_gantt` simplificado | Dual-view: analytics + UI | ✅ |
| `execution_log` permanente | Auditoria, nunca deletado | ✅ |
| Transações atômicas no banco | Tudo persiste junto ou nada | ✅ |
| `distance_between_coordinates` com fator 1.35 | Aproximação suficiente; API externa no futuro | ✅ |
| `cancel_demand` só permite cancelar sem técnicos alocados | Consistência da fila | ✅ |
| `allocate_technician` adiciona ao final da linked-list | Fila sempre consistente | ✅ |
| `deallocate_technician` reconstrói links após remoção | Evita nós órfãos na fila | ✅ |
| `deallocate` dispara replan automático via router | Gantt sempre atualizado | ✅ |
| Router orquestra services; services não se conhecem | Single Responsibility | ✅ |
| Testes de service com MagicMock | Sem dependência de infraestrutura | ✅ |
| `customer_id` e `project_id` como string manual | [ TODO ] Avaliar migração para int auto-gerado | — |

---

## 12. Fluxo Completo (Opção A Implementada)

```
1. Usuário clica "Salvar Sequência" do técnico
   ↓
2. QueueService.save_sequence() — reordena links da linked-list
   ↓
3. ScheduleService.replan(technician_id)
   ↓
4. PlanningVersionRepository.deactivate_all_by_technician(tech_id)
   ↓
5. PlanningVersionRepository.create(new_version) → version_id
   ↓
6. SchedulePlanner.plan(demands) em MEMÓRIA
   → Gera list[ScheduleItem] e list[ScheduleGantt]
   ↓
7. ScheduleItemRepository.create_batch([schedule_items])
   ↓
8. ScheduleGanttRepository.create_batch([schedule_gantt])
   ↓
9. COMMIT da transação (ou ROLLBACK se erro)
   ↓
10. Gantt e Analytics já mostram dados atualizados ✅
```

---

## 13. Testes ✅

### Status Atual
- **Total:** 116 testes (models) + 16 testes (QueueService) = **132 testes**
- **Todos passando** ✅

### Cobertura
| Arquivo | Testes | Tipo |
|---|---|---|
| `test_city.py` | — | Model |
| `test_technician.py` | — | Model |
| `test_demand.py` | — | Model |
| `test_demand_manager.py` | — | Model |
| `test_demand_queue.py` | — | Model |
| `test_geo_utils.py` | — | Model |
| `test_schedule_planner.py` | — | Model |
| `test_customer.py` | — | Model |
| `test_project.py` | — | Model |
| `test_analyst.py` | — | Model |
| `test_planning_version.py` | — | Model |
| `test_schedule_item_persistent.py` | — | Model |
| `test_schedule_gantt.py` | — | Model |
| `test_execution_log.py` | — | Model |
| `test_queue_service.py` | 16 | Service (MagicMock) |

---

## 14. Próximos Passos

### Fase Atual (Concluída) ✅
1. ✅ Todos os models com TDD
2. ✅ PostgreSQL local + SQLAlchemy + Alembic
3. ✅ ORM models + Repository layer
4. ✅ 4 novas tabelas para planejamento e execução
5. ✅ Services: DemandService, QueueService, ScheduleService
6. ✅ Schemas Pydantic (request/response)
7. ✅ Routers FastAPI
8. ✅ API testada de ponta a ponta via Swagger
9. ✅ seed.py para dados fictícios de desenvolvimento

### Próxima Fase — Frontend Streamlit [ TODO ]
- [ ] Definir telas e fluxo do usuário
- [ ] Tela de listagem e gestão de demandas
- [ ] Tela de fila do técnico com reordenamento
- [ ] Visualização do Gantt
- [ ] Tela de conclusão de ordem
- [ ] Dashboard de métricas

### Fases Futuras
- [ ] Deploy em nuvem (Railway ou Render)
- [ ] Docker para produção
- [ ] Documentação de deploy

---

## 15. Bugs Corrigidos

| Bug | Causa | Correção |
|---|---|---|
| Nova demanda alocada não aparecia na fila | `allocate_technician` não atualizava links da linked-list | Busca a cauda e conecta o novo nó |
| Desalocação deixava nós órfãos na fila | `deallocate_technician` não reconstrói links após soft-delete | Busca o nó anterior e reconecta ao próximo |
| Gantt desatualizado após desalocação | Router não chamava `replan` após `deallocate` | Router chama `schedule_service.replan()` após desalocação |

---

## 16. Limites e Restrições Conhecidas

| Limitação | Impacto | Solução Futura |
|-----------|---------|----------------|
| `customer_id`/`project_id` string manual | Entrada de dados lenta | Auto-geração com prefixo |
| Haversine + 1.35 vs real roads | ~5% erro de distância | Google Maps API |
| Sem API de tráfego | Não conta congestionamento | Integrar Waze/Google Maps |
| Sem histórico de alterações | Auditoria limitada | Trigger de audit log |
| `schedule_item.sequence_position` não persistido | Ordem recalculada por query | Persistir se necessário |

---

*Última atualização: 09/05/2026 — API completa, testada e funcionando; 132 testes passando; pronto para Frontend Streamlit*
