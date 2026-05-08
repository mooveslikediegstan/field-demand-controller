# Gestão de Agenda Técnica
> Arquivo de contexto para agentes de IA. Última atualização: 07/05/2026.
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
| Banco de dados | PostgreSQL 16 | Obrigatório — multi-usuário |
| ORM | SQLAlchemy 2.x | Padrão Repository |
| Migrações | Alembic | — |
| Validação | Pydantic v2 | — |
| Testes | pytest | TDD |
| Containerização | Docker + Docker Compose | 3 containers |
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
Banco de Dados (PostgreSQL 16)
```

---

## 4. Estrutura de Diretórios

```
field-demand-controller/
├── .gitignore
├── PROJECT_CONTEXT.md
├── backend/
│   ├── requirements.txt
│   ├── Dockerfile                       [ TODO ]
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
│       │   ├── session.py               [ TODO ]
│       │   ├── orm_models.py            [ TODO ]
│       │   └── repository.py            [ TODO ]
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

## 5. Variáveis de Ambiente

### Backend
| Variável | Exemplo | Descrição |
|---|---|---|
| `DATABASE_URL` | `postgresql://admin:senha@banco:5432/agenda_db` | Connection string |
| `SECRET_KEY` | `chave_jwt` | JWT [ TODO ] |

### Banco (container)
| Variável | Exemplo | Descrição |
|---|---|---|
| `POSTGRES_DB` | `agenda_db` | — |
| `POSTGRES_USER` | `admin` | — |
| `POSTGRES_PASSWORD` | `senha_segura` | — |

### Frontend [ TODO ]
| Variável | Exemplo | Descrição |
|---|---|---|
| `API_URL` | `http://backend:8000` | URL do backend |

---

## 6. Models

### `City` ✅ — tabela `CITY`
| Campo | Tipo Python | Obrigatório | Regras |
|---|---|---|---|
| `city_id` | `Optional[int]` | Não | Auto-gerado pelo banco |
| `city_name` | `str` | Sim | Não vazio |
| `state` | `str` | Sim | Siglas válidas + "EX" |
| `country` | `str` | Sim | Não vazio |
| `geolocation_lat` | `float` | Sim | Entre -90 e 90 |
| `geolocation_lon` | `float` | Sim | Entre -180 e 180 |

### `Technician` ✅ — tabela `TECH`
| Campo | Tipo Python | Obrigatório | Regras |
|---|---|---|---|
| `technician_id` | `Optional[int]` | Não | Auto-gerado pelo banco |
| `technician_name` | `str` | Sim | Não vazio |
| `creation_date` | `date` | Sim | — |
| `status` | `str` | Sim | `"ativo"`, `"inativo"` |
| `dismiss_date` | `Optional[date]` | Não | Obrigatório se inativo |
| `position` | `str` | Sim | `"Lider"`, `"Supervisor"`, `"Coordenador"` |
| `base_location_city_id` | `int` | Sim | FK para City |
| `current_location_city_id` | `int` | Sim | FK para City — usado como origem no SchedulePlanner |
| `daily_capacity` | `float` | Sim | Horas/dia > 0 |

### `Demand` ✅ — tabela `DMD`
| Campo | Tipo Python | Obrigatório | Regras |
|---|---|---|---|
| `demand_id` | `Optional[int]` | Não | Auto-gerado pelo banco |
| `demand_title` | `str` | Sim | Não vazio |
| `problem_description` | `str` | Sim | Não vazio |
| `request_date` | `date` | Sim | — |
| `responsible_id` | `int` | Sim | FK para Analyst |
| `project_id` | `str` | Sim | FK para Project |
| `estimated_time` | `float` | Sim | > 0 |
| `actual_time` | `Optional[float]` | Não | Preenchido após execução; validar > 0 na conclusão |
| `technical_visit_reason` | `str` | Sim | Lista fechada |
| `causal_sector` | `str` | Sim | Lista fechada |
| `causal_area` | `str` | Sim | Dependente de causal_sector |
| `root_cause` | `str` | Sim | Dependente de causal_area |
| `equipment` | `str` | Sim | Lista fechada |
| `status` | `str` | Sim | `"Aberta"`, `"Em Andamento"`, `"Concluida"`, `"Cancelada"` |

**Hierarquia de problemas:** dicionário `PROBLEM_HIERARCHY` dentro de `demand.py`.
**Transição de estado pendente:** método `conclude()` deve validar `actual_time > 0`.

**Valores válidos — `technical_visit_reason`:**
`"Instalação"`, `"Manutenção Corretiva"`, `"Manutenção Preventiva"`, `"Punch-list"`, `"Reforma"`, `"Teste"`, `"Verificação"`, `"Visita Técnica"`, `"Outro"`

**Valores válidos — `equipment`:**
`"Secador / Fornalha"`, `"Máquina de Limpeza"`, `"Elevadores Agrícolas"`, `"Transportadores de Correia"`, `"Transportadores Helicoidais"`, `"Transportadores de Corrente"`, `"Canalização"`, `"Passarela / Torres"`, `"Rosca Varredora"`, `"Silos Planos / Elevados / Expedição / Aeração"`, `"Tulhas Metálicas"`, `"Hi Roller / Hi Life"`, `"Temp Stor"`, `"Batco"`

### `DemandManager` ✅ — tabela `DMD_MGMT`
Linked-list por técnico. `ServiceOrder` eliminado — referencia `Demand` diretamente.

| Campo | Tipo Python | Obrigatório | Regras |
|---|---|---|---|
| `demand_manager_id` | `Optional[int]` | Não | Auto-gerado pelo banco |
| `demand_id` | `int` | Sim | FK para Demand |
| `technician_id` | `int` | Sim | FK para Technician |
| `next_demand_manager_id` | `Optional[int]` | Não | None = tail da fila |
| `status` | `str` | Sim | `"Pendente"`, `"Em Execucao"`, `"Concluido"` |
| `start_date` | `Optional[date]` | Não | Após execução |
| `finish_date` | `Optional[date]` | Não | Requer start_date; não pode ser anterior |
| `travel_time` | `Optional[float]` | Não | >= 0 |
| `travel_distance` | `Optional[float]` | Não | >= 0 |
| `is_deleted` | `bool` | Sim | Soft delete, default False |

### `DemandQueue` ✅ — objeto de domínio (não é tabela)
| Campo | Tipo Python | Descrição |
|---|---|---|
| `technician_id` | `int` | Técnico dono da fila |
| `head_id` | `Optional[int]` | ID do primeiro DemandManager a executar |
| `demands` | `list[DemandManager]` | Lista ordenada |

Métodos:
- `sort()` — reconstrói ordem via links a partir do `head_id`
- `rebuild_links()` — recalcula `next_demand_manager_id` e atualiza `head_id`
- `append(dm)` — adiciona ao final e chama `rebuild_links()`

### `ScheduleInput` ✅ — objeto de domínio (não é tabela)
Dados resolvidos pelo `ScheduleService` antes de entregar ao `SchedulePlanner`.

| Campo | Tipo Python | Descrição |
|---|---|---|
| `demand_manager_id` | `int` | ID do registro na fila |
| `demand_id` | `int` | FK para Demand |
| `estimated_time` | `float` | Horas de trabalho |
| `city_lat` | `float` | Resolvida via Demand → Project → Customer → City |
| `city_lon` | `float` | Resolvida via Demand → Project → Customer → City |

### `ScheduleItem` ✅ — objeto de domínio (não é tabela)
| Campo | Tipo Python | Descrição |
|---|---|---|
| `demand_manager_id` | `int` | FK para DemandManager |
| `technician_id` | `int` | FK para Technician |
| `scheduled_date` | `date` | Data do bloco |
| `action` | `str` | `"Deslocamento"` ou `"Prestacao de Servico"` |
| `work_time` | `float` | Horas do bloco |
| `sequence_position` | `int` | Posição global na sequência |
| `distance` | `int` | Km — só no primeiro item de deslocamento |

### `SchedulePlanner` ✅ — objeto de domínio (não é tabela)
Planejamento **atômico e contínuo** — gera um `ScheduleItem` por bloco de horas.

| Campo | Tipo Python | Descrição |
|---|---|---|
| `technician_id` | `int` | — |
| `initial_start_date` | `date` | — |
| `daily_capacity_hours` | `float` | > 0 |
| `travel_speed_kmh` | `float` | > 0 |
| `origin_lat` | `float` | current_location do técnico |
| `origin_lon` | `float` | current_location do técnico |
| `scheduled_items` | `list[ScheduleItem]` | Resultado do plan() |

Método `plan(demand_inputs)`:
1. Para cada `ScheduleInput`: calcula deslocamento via `geo_utils.distance_between_coordinates()`
2. Consome deslocamento em fatias diárias (dias úteis seg-sex) → gera itens `"Deslocamento"`
3. Consome trabalho em fatias diárias → gera itens `"Prestacao de Servico"`
4. Avança dia só quando `remaining_hours <= 0`
5. Primeira demanda do dia sempre é alocada mesmo se exceder capacidade

### `geo_utils` ✅ — utilitário
- `distance_between_coordinates(lat_o, lon_o, lat_d, lon_d, apply_correction=True)`
- Fórmula Haversine + fator de correção 1.35 (aproximação rota/linha reta)
- Futuramente: substituir por API Google Maps / similar

### `Customer` [ TODO ] — tabela `CUSTOMER`
| Campo | Tipo Python | Obrigatório | Regras |
|---|---|---|---|
| `customer_id` | `str` | Sim | Não vazio |
| `customer_name` | `str` | Sim | Não vazio |
| `short_name` | `str` | Sim | Não vazio |
| `city_id` | `int` | Sim | FK para City — cidade do cliente |
| `address` | `str` | [ TODO ] | — |
| `segment` | `str` | [ TODO ] | — |
| `sub_segment` | `str` | [ TODO ] | — |
| `region` | `str` | [ TODO ] | — |

### `Project` [ TODO ] — tabela `PROJECT`
City herdada do Customer (Project não tem city_id próprio).

| Campo | Tipo Python | Obrigatório | Regras |
|---|---|---|---|
| `project_id` | `str` | Sim | Não vazio |
| `project_name` | `str` | Sim | Não vazio |
| `customer_id` | `str` | Sim | FK para Customer |

### `Analyst` [ TODO ] — tabela `ANL`
Campos a definir na próxima sessão.

---

## 7. Tabelas

| Tabela | Model | Status |
|---|---|---|
| `CITY` | `City` | ✅ |
| `TECH` | `Technician` | ✅ |
| `DMD` | `Demand` | ✅ |
| `DMD_MGMT` | `DemandManager` | ✅ |
| `CUSTOMER` | `Customer` | [ TODO ] |
| `PROJECT` | `Project` | [ TODO ] |
| `ANL` | `Analyst` | [ TODO ] |

---

## 8. Fluxo Principal

```
1. Analista cadastra Demand
2. Analista atribui Demand a técnicos → cria DemandManager por técnico
3. DemandManager vai ao final da fila (append)
4. Analista reordena fila → rebuild_links recalcula links
5. ScheduleService resolve coordenadas → monta lista de ScheduleInput
6. SchedulePlanner.plan() gera agenda atômica dia-a-dia
```

---

## 9. Decisões de Design

| Decisão | Motivo |
|---|---|
| PostgreSQL obrigatório | 2-8 usuários simultâneos |
| Fila como linked-list | Reordenação eficiente; mantém histórico |
| `ServiceOrder` eliminado | Sem valor — DemandManager referencia Demand diretamente |
| `DemandQueue`/`SchedulePlanner` como objetos de domínio | Construídos em memória — não persistidos |
| Soft delete (`is_deleted`) | Mantém histórico |
| `SchedulePlanner` recebe `ScheduleInput` resolvido | Planejador não conhece cadeia Demand→Project→Customer→City |
| Planejamento atômico e contínuo | Um ScheduleItem por bloco de horas — permite Gantt e persistência granular |
| `current_location_city_id` do Technician como origem | Permite "teletransporte" para corrigir localização sem histórico |
| Distância via Haversine + fator 1.35 | Aproximação suficiente; API externa planejada para versão futura |

---

## 10. Próximos Passos

1. ✅ Repositório Git + estrutura de pastas
2. ✅ `City` com TDD
3. ✅ `Technician` com TDD
4. ✅ `Demand` com TDD
5. ✅ `DemandManager` com TDD
6. ✅ `DemandQueue` com TDD
7. ✅ `geo_utils` com TDD
8. ✅ `SchedulePlanner` com TDD
9. ✅ `Customer` com TDD
10. ✅ `Project` com TDD
11. ✅ `Analyst` com TDD
12. Criar ORM models + SQLAlchemy + PostgreSQL
13. Implementar Repositories e Services (incluindo `ScheduleService`)
14. Criar rotas FastAPI
15. Configurar Docker Compose
16. Criar interface Streamlit

---

*Última atualização: 07/05/2026 — SchedulePlanner concluído com planejamento atômico*