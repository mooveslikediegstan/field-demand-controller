# Gestão de Agenda Técnica
> Arquivo de contexto para agentes de IA. Última atualização: 08/05/2026.
> Itens marcados com `[ TODO ]` ainda não foram definidos.
> Convenção: nomes de código em inglês, mensagens de erro em português.

---

## 1. Visão Geral

Sistema de **gestão de demandas técnicas e agendamento de técnicos de campo**, substituindo solução legada em Excel/VBA + Access.

Fluxo principal:
```
Demand (DMD) → DemandManager/Fila (DMD_MGMT) → SchedulePlanner → Agenda dia-a-dia
```

**Uso simultâneo:** 2 a 8 usuários — requer PostgreSQL.

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
│       │   ├── schedule_item.py         ✅
│       │   ├── schedule_planner.py      ✅
│       │   ├── geo_utils.py             ✅
│       │   ├── customer.py              ✅
│       │   ├── project.py               ✅
│       │   └── analyst.py               ✅
│       ├── database/
│       │   ├── session.py               ✅
│       │   ├── orm_models.py            ✅
│       │   ├── init_db.py               ✅
│       │   └── repository.py            ✅
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
    └── test_analyst.py                  ✅
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

### `City` — tabela `city`
| Campo | Tipo Python | Obrigatório | Regras |
|---|---|---|---|
| `city_id` | `Optional[int]` | Não | Auto-gerado pelo banco |
| `city_name` | `str` | Sim | Não vazio |
| `state` | `str` | Sim | Siglas válidas + "EX" |
| `country` | `str` | Sim | Não vazio |
| `geolocation_lat` | `float` | Sim | Entre -90 e 90 |
| `geolocation_lon` | `float` | Sim | Entre -180 e 180 |

### `Analyst` — tabela `analyst`
| Campo | Tipo Python | Obrigatório | Regras |
|---|---|---|---|
| `analyst_id` | `Optional[int]` | Não | Auto-gerado pelo banco |
| `analyst_name` | `str` | Sim | Não vazio |
| `email` | `str` | Sim | Não vazio; normalizado para lowercase |
| `contact` | `str` | Sim | Não vazio |
| `creation_date` | `date` | Sim | — |
| `status` | `str` | Sim | `"active"`, `"inactive"` |
| `valid_to_date` | `Optional[date]` | Não | Deve ser > creation_date quando preenchido |

### `Customer` — tabela `customer`
| Campo | Tipo Python | Obrigatório | Regras |
|---|---|---|---|
| `customer_id` | `str` | Sim | Gerado manualmente; não vazio |
| `customer_name` | `str` | Sim | Não vazio |
| `short_name` | `str` | Sim | Não vazio |
| `city_id` | `int` | Sim | FK para city |
| `address` | `str` | Sim | Não vazio |
| `segment` | `str` | Sim | `"Farm"`, `"Commercial"` |
| `sub_segment` | `str` | Sim | `"Farm"`, `"Commercial"`, `"Feed"`, `"Fertilizer"`, `"Fuel"` |
| `region` | `str` | Sim | `"MA/PI"`, `"TO/BA"`, `"MT"`, `"MG/GO"`, `"MS/SP"`, `"PR,SC,RS"` |

### `Project` — tabela `project`
City herdada do Customer — Project não tem city_id próprio.

| Campo | Tipo Python | Obrigatório | Regras |
|---|---|---|---|
| `project_id` | `str` | Sim | Gerado manualmente; não vazio |
| `project_name` | `str` | Sim | Não vazio |
| `customer_id` | `str` | Sim | FK para customer |

### `Technician` — tabela `technician`
| Campo | Tipo Python | Obrigatório | Regras |
|---|---|---|---|
| `technician_id` | `Optional[int]` | Não | Auto-gerado pelo banco |
| `technician_name` | `str` | Sim | Não vazio |
| `creation_date` | `date` | Sim | — |
| `status` | `str` | Sim | `"ativo"`, `"inativo"` |
| `dismiss_date` | `Optional[date]` | Não | Obrigatório se inativo |
| `position` | `str` | Sim | `"Lider"`, `"Supervisor"`, `"Coordenador"` |
| `base_location_city_id` | `int` | Sim | FK para city |
| `current_location_city_id` | `int` | Sim | FK para city — origem no SchedulePlanner |
| `daily_capacity` | `float` | Sim | > 0 |

### `Demand` — tabela `demand`
| Campo | Tipo Python | Obrigatório | Regras |
|---|---|---|---|
| `demand_id` | `Optional[int]` | Não | Auto-gerado pelo banco |
| `demand_title` | `str` | Sim | Não vazio |
| `problem_description` | `str` | Sim | Não vazio |
| `request_date` | `date` | Sim | — |
| `responsible_id` | `int` | Sim | FK para analyst |
| `project_id` | `str` | Sim | FK para project |
| `estimated_time` | `float` | Sim | > 0 |
| `actual_time` | `Optional[float]` | Não | Validar > 0 na conclusão via `conclude()` |
| `technical_visit_reason` | `str` | Sim | Lista fechada |
| `causal_sector` | `str` | Sim | Lista fechada |
| `causal_area` | `str` | Sim | Dependente de causal_sector |
| `root_cause` | `str` | Sim | Dependente de causal_area |
| `equipment` | `str` | Sim | Lista fechada |
| `status` | `str` | Sim | `"Aberta"`, `"Em Andamento"`, `"Concluida"`, `"Cancelada"` |

**Hierarquia de problemas:** dicionário `PROBLEM_HIERARCHY` em `demand.py`.
**Transição pendente:** método `conclude()` — valida `actual_time > 0`.

### `DemandManager` — tabela `demand_manager`
Linked-list por técnico. `ServiceOrder` eliminado.

| Campo | Tipo Python | Obrigatório | Regras |
|---|---|---|---|
| `demand_manager_id` | `Optional[int]` | Não | Auto-gerado pelo banco |
| `demand_id` | `int` | Sim | FK para demand |
| `technician_id` | `int` | Sim | FK para technician |
| `next_demand_manager_id` | `Optional[int]` | Não | None = tail da fila |
| `status` | `str` | Sim | `"Pendente"`, `"Em Execucao"`, `"Concluido"` |
| `start_date` | `Optional[date]` | Não | Após execução |
| `finish_date` | `Optional[date]` | Não | Requer start_date; não pode ser anterior |
| `travel_time` | `Optional[float]` | Não | >= 0 |
| `travel_distance` | `Optional[float]` | Não | >= 0 |
| `is_deleted` | `bool` | Sim | Soft delete, default False |

### `DemandQueue` — objeto de domínio (não é tabela)
| Campo | Tipo Python | Descrição |
|---|---|---|
| `technician_id` | `int` | Técnico dono da fila |
| `head_id` | `Optional[int]` | ID do primeiro DemandManager |
| `demands` | `list[DemandManager]` | Lista ordenada |

Métodos: `sort()`, `rebuild_links()`, `append(dm)`

### `ScheduleInput` — objeto de domínio (não é tabela)
| Campo | Tipo Python | Descrição |
|---|---|---|
| `demand_manager_id` | `int` | — |
| `demand_id` | `int` | — |
| `estimated_time` | `float` | Horas de trabalho |
| `city_lat` | `float` | Resolvida via Demand→Project→Customer→City |
| `city_lon` | `float` | Resolvida via Demand→Project→Customer→City |

### `ScheduleItem` — objeto de domínio (não é tabela) + futura tabela `schedule_item`
| Campo | Tipo Python | Descrição |
|---|---|---|
| `demand_manager_id` | `int` | — |
| `technician_id` | `int` | — |
| `scheduled_date` | `date` | Data do bloco |
| `action` | `str` | `"Deslocamento"` ou `"Prestacao de Servico"` |
| `work_time` | `float` | Horas do bloco |
| `sequence_position` | `int` | Posição global |
| `distance` | `int` | Km — só no primeiro item de deslocamento |
| `is_deleted` | `bool` | Soft delete ao replanejar |

### `SchedulePlanner` — objeto de domínio (não é tabela)
Planejamento atômico e contínuo — um `ScheduleItem` por bloco de horas.

| Campo | Tipo Python | Descrição |
|---|---|---|
| `technician_id` | `int` | — |
| `initial_start_date` | `date` | — |
| `daily_capacity_hours` | `float` | > 0 |
| `travel_speed_kmh` | `float` | > 0 |
| `origin_lat` | `float` | current_location do técnico |
| `origin_lon` | `float` | current_location do técnico |
| `scheduled_items` | `list[ScheduleItem]` | Resultado do plan() |

### `geo_utils` — utilitário
- `distance_between_coordinates(lat_o, lon_o, lat_d, lon_d, apply_correction=True)`
- Haversine + fator 1.35
- Futuro: substituir por API Google Maps

---

## 7. Banco de Dados

### Tabelas existentes (criadas via `init_db.py`)
| Tabela | Model | Status |
|---|---|---|
| `city` | `City` | ✅ |
| `analyst` | `Analyst` | ✅ |
| `customer` | `Customer` | ✅ |
| `project` | `Project` | ✅ |
| `technician` | `Technician` | ✅ |
| `demand` | `Demand` | ✅ |
| `demand_manager` | `DemandManager` | ✅ |

### Tabelas a criar (via Alembic migration)
| Tabela | Descrição | Status |
|---|---|---|
| `schedule_item` | Planejamento atômico persistido — soft-delete ao replanejar | [ TODO ] |
| `schedule_gantt` | Planejamento agrupado (start/finish por demanda/técnico) para Gantt — soft-delete ao replanejar | [ TODO ] |
| `execution_log` | Histórico real de execução — permanente, nunca soft-deleted | [ TODO ] |

---

## 8. Novas Funcionalidades Pendentes de Definição

### 8.1 Execução Real (`execution_log`)
Input manual do técnico dia a dia — o que de fato aconteceu.
**Perguntas em aberto:**
- Um registro por dia por técnico por demanda, com horas de deslocamento e serviço separadas?
- A tela gera cards por dia (igual ao VBA) baseado em `start_date` e `finish_date` informados pelo usuário?

### 8.2 Planejamento Atômico Persistido (`schedule_item`)
Resultado do `SchedulePlanner` salvo no banco.
- Soft-delete ao replanejar — só o último planejamento é válido
- **Pergunta em aberto:** abordagem mais eficiente que soft-delete? (ex: tabela com `planning_version_id`)

### 8.3 Planejamento Agrupado (`schedule_gantt`)
Derivado do planejamento atômico — `start_date` e `finish_date` por demanda/técnico.
- **Pergunta em aberto:** calculado automaticamente ou ajustável manualmente?

---

## 9. Repository Layer ✅

`backend/app/database/repository.py` — CRUD completo para todos os models:
- `CityRepository`
- `AnalystRepository`
- `CustomerRepository`
- `ProjectRepository`
- `TechnicianRepository`
- `DemandRepository`
- `DemandManagerRepository`

Padrão: `get_by_id`, `get_all` / `get_all_active`, `create`, `update`, `_to_model`
`DemandManagerRepository` tem `soft_delete()` e `get_by_technician()` para montar `DemandQueue`.

---

## 10. Decisões de Design

| Decisão | Motivo |
|---|---|
| PostgreSQL obrigatório | 2-8 usuários simultâneos |
| Dev local sem Docker | Virtualização desabilitada na máquina de dev; Docker apenas em produção |
| Deploy em nuvem (Railway/Render) | Sem acesso admin na empresa — usuário acessa via navegador |
| Fila como linked-list | Reordenação eficiente |
| `ServiceOrder` eliminado | DemandManager referencia Demand diretamente |
| `DemandQueue`/`SchedulePlanner` como objetos de domínio | Construídos em memória |
| Soft delete (`is_deleted`) | Mantém histórico |
| `SchedulePlanner` recebe `ScheduleInput` resolvido | Planejador não conhece cadeia Demand→Project→Customer→City |
| Planejamento atômico e contínuo | Um ScheduleItem por bloco — permite Gantt e soma de horas pendentes |
| `current_location_city_id` como origem | Permite corrigir localização do técnico manualmente |
| Distância via Haversine + 1.35 | Aproximação suficiente; API externa no futuro |
| `customer_id` e `project_id` como string manual | Avaliar migração para int auto-gerado com prefixo na UI [ TODO ] |

---

## 11. Próximos Passos

1. ✅ Todos os models com TDD
2. ✅ PostgreSQL local + SQLAlchemy + Alembic
3. ✅ ORM models + Repository layer
4. Responder perguntas em aberto da seção 8 ← **próxima sessão começa aqui**
5. Criar tabelas `schedule_item`, `schedule_gantt`, `execution_log` via Alembic migration
6. Implementar `DemandService`
7. Implementar `ScheduleService`
8. Criar rotas FastAPI
9. Criar Schemas Pydantic
10. Criar interface Streamlit
11. Deploy em nuvem (Railway ou Render)

---

*Última atualização: 08/05/2026 — Repository layer concluído; novas funcionalidades identificadas e pendentes de definição*
