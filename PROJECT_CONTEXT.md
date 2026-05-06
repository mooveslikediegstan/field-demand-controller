# AgGrowth — Gestão de Agenda Técnica
> Arquivo de contexto para agentes de IA. Gerado em 06/05/2026.
> Itens marcados com `[ TODO ]` ainda não foram definidos e devem ser preenchidos nas próximas sessões.
> Convenção: nomes de código em inglês, mensagens de erro em português.

---

## 1. Visão Geral

Sistema de **gestão de demandas técnicas e agendamento de técnicos de campo**, desenvolvido para substituir uma solução legada em Excel/VBA + Access (`.xlsm` + `.accdb`).

O sistema gerencia o ciclo completo de uma demanda técnica:
```
Demanda (DMD) → Ordem de Serviço (SERVORD) → Fila do Técnico (ORD_MGMT) → Agenda Planejada
```

Principais funcionalidades:
- Cadastro e gestão de Demandas (visitas técnicas solicitadas por clientes)
- Criação de Ordens de Serviço vinculadas a demandas, com atribuição de técnicos
- Gerenciamento de Fila de Execução por técnico (linked-list: order_id → next_order_id)
- Planejamento automático de agenda considerando: data de início, capacidade diária, tempo de trabalho estimado, tempo de deslocamento entre cidades e dias úteis (seg-sex)
- Cadastro de Técnicos, Clientes, Projetos e Cidades

**Uso simultâneo:** 2 a 8 usuários — requer PostgreSQL (não SQLite).

---

## 2. Stack Tecnológico

| Camada | Tecnologia | Observação |
|---|---|---|
| Backend / API | FastAPI | Framework principal |
| Servidor ASGI | Uvicorn | Roda o FastAPI |
| Frontend | Streamlit | Fase inicial |
| Banco de dados | PostgreSQL 16 | Obrigatório — multi-usuário |
| ORM | SQLAlchemy 2.x | Com padrão Repository |
| Migrações | Alembic | Controle de versão do schema |
| Validação | Pydantic v2 | Schemas de entrada/saída da API |
| Testes | pytest | TDD — testes escritos antes do código |
| Containerização | Docker + Docker Compose | 3 containers: frontend, backend, banco |
| Linguagem | Python 3.13 | |
| Controle de versão | Git + GitHub | Repositório: [ TODO ] |
| SO (dev) | Windows 11 | Terminal: PowerShell no VS Code |

### Comando padrão para rodar testes (Windows)
```powershell
python -m pytest tests/ -v
```

### Padrão de testes consolidado
- Fixture `valid_*` compartilhada por módulo
- Helper `make_*(valid_fixture, **overrides)` para criar objetos com campos substituídos
- Testes de validação criam objeto novo via `make_*()` — nunca mutam a fixture nem chamam `_validate()` diretamente
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
agenda-tecnica/
├── .gitignore
├── PROJECT_CONTEXT.md
├── backend/
│   ├── requirements.txt
│   ├── Dockerfile                       [ TODO ]
│   └── app/
│       ├── main.py                      [ TODO ]
│       ├── models/
│       │   ├── city.py                  [ TODO ]
│       │   ├── customer.py              [ TODO ]
│       │   ├── project.py               [ TODO ]
│       │   ├── technician.py            [ TODO ]
│       │   ├── demand.py                [ TODO ]
│       │   ├── order_manager.py         [ TODO ]
│       │   ├── order_queue.py           [ TODO ]
│       │   └── schedule_planner.py      [ TODO ]
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
    ├── test_city.py                     [ TODO ]
    ├── test_customer.py                 [ TODO ]
    ├── test_project.py                  [ TODO ]
    ├── test_technician.py               [ TODO ]
    ├── test_demand.py                   [ TODO ]
    ├── test_service_order.py            [ TODO ]
    ├── test_order_manager.py            [ TODO ]
    ├── test_order_queue.py              [ TODO ]
    └── test_schedule_planner.py         [ TODO ]
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
| `POSTGRES_DB` | `agenda_db` | Nome do banco |
| `POSTGRES_USER` | `admin` | Usuário |
| `POSTGRES_PASSWORD` | `senha_segura` | Senha |

### Frontend [ TODO ]
| Variável | Exemplo | Descrição |
|---|---|---|
| `API_URL` | `http://backend:8000` | URL do backend |

---

## 6. Models — Mapeamento VBA → Python

### `City` [ TODO ] — tabela `CITY`
| Campo | Tipo Python | Obrigatório | Regras |
|---|---|---|---|
| `city_id` | `int` | Sim | Auto-gerado |
| `city_name` | `str` | Sim | Não vazio |
| `state` | `str` | Sim | Siglas válidas + "EX" |
| `country` | `str` | Sim | Não vazio |
| `geolocation_lat` | `float` | Sim | Entre -90 e 90 |
| `geolocation_lon` | `float` | Sim | Entre -180 e 180 |

### `Customer` [ TODO ] — tabela `CUSTOMER`
| Campo | Tipo Python | Obrigatório | Regras |
|---|---|---|---|
| `customer_id` | `str` | Sim | Não vazio |
| `customer_name` | `str` | Sim | Não vazio |
| `short_name` | `str` | Sim | Não vazio |
| `city_id` | `int` | Sim | FK para City |
| `address` | `str` | [ TODO ] | — |
| `segment` | `str` | [ TODO ] | — |
| `sub_segment` | `str` | [ TODO ] | — |
| `responsible` | `str` | [ TODO ] | Analista responsável |
| `region` | `str` | [ TODO ] | — |

### `Project` [ TODO ] — tabela `PROJECT`
| Campo | Tipo Python | Obrigatório | Regras |
|---|---|---|---|
| `project_id` | `str` | Sim | Não vazio |
| `project_name` | `str` | Sim | Não vazio |
| `customer_id` | `str` | Sim | FK para Customer |
| `city_id` | `int` | Sim | FK para City |
| `site_location_lat` | `float` | [ TODO ] | Entre -90 e 90 |
| `site_location_lon` | `float` | [ TODO ] | Entre -180 e 180 |
| `address` | `str` | [ TODO ] | — |

### `Technician` [ TODO ] — tabela `TECH`
| Campo | Tipo Python | Obrigatório | Regras |
|---|---|---|---|
| `technician_id` | `int` | Sim | Auto-gerado |
| `technician_name` | `str` | Sim | Não vazio |
| `creation_date` | `date` | Sim | — |
| `status` | `str` | Sim | [ TODO ] valores válidos |
| `dismiss_date` | `Optional[date]` | Não | Só quando inativo |
| `position` | `str` | Sim | Lista fechada: "Lider", "Supervisor", "Coordenador" |
| `base_location_city_id` | `int` | Sim | FK para City |
| `current_location_city_id` | `int` | Sim | FK para City |
| `daily_capacity` | `float` | Sim | Horas disponíveis/dia |

### `Demand` [ TODO ] — tabela `DMD`
Ponto de entrada do fluxo principal.

| Campo | Tipo Python | Obrigatório | Regras |
|---|---|---|---|
| `demand_id` | `int` | Sim | Auto-gerado |
| `request_date` | `date` | Sim | — |
| `responsible` | `str` | Sim | Analista |
| `project_id` | `str` | Sim | FK para Project |
| `classification` | `str` | Sim | Lista fechada (ver abaixo) |
| `estimated_time` | `float` | Sim | Horas estimadas |
| `actual_time` | `Optional[float]` | Não | Preenchido após execução |
| `problem_description` | `str` | Sim | Não vazio |
| `technical_visit_reason` | `str` | Sim | Lista fechada (ver abaixo) |
| `root_cause_area` | `str` | [ TODO ] | Lista fechada |
| `equipment` | `str` | [ TODO ] | — |
| `status` | `str` | Sim | [ TODO ] valores válidos |

**Valores válidos — `classification`:**
`"Assistência Técnica"`, `"Folga de Campo"`, `"Visita Comercial"`, `"Visita Preventiva"`, `"Entrega Técnica"`

**Valores válidos — `technical_visit_reason`:**
`"Acompanhamento Atividade"`, `"Administrativo"`, `"Atestado Médico"`, `"Comercial"`, `"Falha Operacional"`, `"Garantia"`, `"Inspeção / Verificação"`, `"Instalação / Ajuste"`, `"Manutenção Corretiva"`, `"Manutenção Preventiva"`, `"Orientação / Treinamento"`, `"Punchlist / Entrega Técnica"`, `"Quebra de Componente"`, `"Start-up Equipamento"`

**Valores válidos — `root_cause_area`:**
`"Assistência Técnica"`, `"Cliente"`, `"Comercial"`, `"Engenharia"`, `"Fornecedor"`, `"Logística"`


### `OrderManager` [ TODO ] — tabela `ORD_MGMT`
Referencia `Demand` diretamente — `ServiceOrder` eliminado por simplicidade.
Implementa linked-list para ordenação da fila por técnico.

| Campo | Tipo Python | Obrigatório | Regras |
|---|---|---|---|
| `demand_id` | `int` | Sim | FK para Demand |
| `technician_id` | `int` | Sim | FK para Technician |
| `next_order_id` | `Optional[int]` | Não | None = último da fila |
| `start_date` | `Optional[date]` | Não | Após execução |
| `finish_date` | `Optional[date]` | Não | Após execução |
| `travel_time` | `Optional[float]` | Não | Calculado pelo planejador |
| `travel_distance` | `Optional[float]` | Não | Calculado pelo planejador |
| `status` | `str` | Sim | [ TODO ] valores válidos |
| `is_deleted` | `bool` | Sim | Soft delete, default False |
| `order_manager_id` | `Optional[int]` | Não | Auto-gerado pelo banco |

**Arquitetura linked-list:**
- `next_demand_id = None` → último da fila (tail)
- Reordenação: `sort()` reconstrói ordem a partir dos links
- `rebuild_links()` recalcula `next_order_id` após reordenação

### `OrderQueue` [ TODO ] — objeto de domínio (não é tabela)
| Campo | Tipo Python | Descrição |
|---|---|---|
| `technician_id` | `int` | Técnico dono da fila |
| `orders` | `list[OrderManager]` | Lista ordenada (head = próxima execução) |

Métodos a implementar:
- `sort()` — reconstrói ordem correta via links (≈ `SortOrderSequence()` VBA)
- `rebuild_links()` — recalcula `next_order_id` após reordenação (≈ `RebuildLinks()` VBA)

### `ScheduleItem` [ TODO ] — objeto de domínio (não é tabela)
| Campo | Tipo Python | Descrição |
|---|---|---|
| `order_id` | `int` | FK para OrderManager |
| `technician_id` | `int` | FK para Technician |
| `scheduled_date` | `date` | Data planejada |
| `action` | `str` | Tipo de ação |
| `distance` | `int` | Distância em km |
| `work_time` | `float` | Tempo de trabalho em horas |
| `sequence_position` | `int` | Posição na sequência do dia |

### `SchedulePlanner` [ TODO ] — objeto de domínio mais complexo
Gera o planejamento dia-a-dia da agenda de um técnico.

| Campo | Tipo Python | Descrição |
|---|---|---|
| `technician_id` | `int` | Técnico sendo planejado |
| `initial_start_date` | `date` | Data de início |
| `daily_capacity_hours` | `float` | Capacidade diária em horas |
| `travel_speed_kmh` | `float` | Velocidade média (km/h) |
| `scheduled_orders` | `list[ScheduleItem]` | Resultado do planejamento |

**Lógica do planejamento:**
1. Recebe fila de ordens pendentes em ordem de execução
2. Para cada ordem: calcula tempo de deslocamento = distância / velocidade
3. Aloca em dias úteis (seg-sex), respeitando capacidade diária
4. Quando capacidade do dia é atingida, avança para próximo dia útil
5. Gera lista de `ScheduleItem` com data e posição de cada ordem

---

## 7. Tabelas Access Identificadas

| Tabela | Model Python | Observação |
|---|---|---|
| `CITY` | `City` | Catálogo com geolocalização |
| `CUSTOMER` | `Customer` | Clientes |
| `PROJECT` | `Project` | Projetos por cliente/cidade |
| `TECH` | `Technician` | Técnicos de campo |
| `ANL` | `[ TODO ]` | Analistas — ainda não mapeado |
| `DMD` | `Demand` | Demandas técnicas |
| `SERVORD` | `ServiceOrder` | Ordens de serviço |
| `ORD_MGMT` | `OrderManager` | Fila de execução (linked-list) |

---

## 8. Fluxo Principal

```
1. Analista cadastra Demand
2. Analista cria ServiceOrder → atribui técnicos
3. Para cada técnico: cria OrderManager → ordem vai ao final da fila
4. Analista reordena fila via AgendaManager → RebuildLinks recalcula links
5. Sistema gera planejamento dia-a-dia via SchedulePlanner
```

---

## 9. Decisões de Design

| Decisão | Motivo |
|---|---|
| PostgreSQL obrigatório | 2-8 usuários simultâneos — SQLite não suporta concorrência de escrita |
| Fila como linked-list | Mantém arquitetura do VBA — permite reordenação eficiente |
| `OrderQueue` e `SchedulePlanner` como objetos de domínio | Construídos em memória — não persistidos diretamente |
| Soft delete (`is_deleted`) | Mantém histórico — padrão do sistema legado |
| Nomes de código em inglês, mensagens em português | Consistência com projeto anterior |
| `ServiceOrder` eliminado | Não agregava valor — `OrderManager` referencia `Demand` diretamente; múltiplos técnicos = múltiplos registros no `ORD_MGMT` |
---

## 10. Próximos Passos

1. Criar repositório Git e estrutura de pastas
2. Criar model `City` com TDD ← **começar aqui**
3. Criar model `Technician` com TDD
4. Criar model `Demand` com TDD (usar `Enum` Python para listas fechadas)
5. Criar model `ServiceOrder` com TDD
6. Criar model `OrderManager` com TDD
7. Implementar `OrderQueue.sort()` com TDD — algoritmo linked-list
8. Implementar `SchedulePlanner` com TDD — algoritmo mais complexo
9. Criar ORM models + SQLAlchemy + PostgreSQL
10. Implementar Repositories e Services
11. Criar rotas FastAPI
12. Configurar Docker Compose
13. Criar interface Streamlit

---

*Gerado em: 06/05/2026 — análise inicial do VBA, nenhum código Python escrito ainda*
