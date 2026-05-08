# Gestão de Agenda Técnica
> Arquivo de contexto para agentes de IA. Gerado em 06/05/2026.
> Itens marcados com `[ TODO ]` ainda não foram definidos e devem ser preenchidos nas próximas sessões.
> Convenção: nomes de código em inglês, mensagens de erro em português.

---

## 1. Visão Geral

Sistema de **gestão de demandas técnicas e agendamento de técnicos de campo**, desenvolvido para substituir uma solução legada em Excel/VBA + Access (`.xlsm` + `.accdb`).

O sistema gerencia o ciclo completo de uma demanda técnica:
```
Demanda (DMD) → Fila do Técnico (DMD_MGMT) → Agenda Planejada
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
│       │   ├── city.py                  
│       │   ├── customer.py              [ TODO ]
│       │   ├── project.py               [ TODO ]
│       │   ├── analyst.py               [ TODO ]
│       │   ├── technician.py            
│       │   ├── demand.py                
│       │   ├── demand_manager.py        
│       │   ├── demand_queue.py          
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
    ├── test_city.py                     
    ├── test_customer.py                 [ TODO ]
    ├── test_project.py                  [ TODO ]
    ├── test_analyst.py                  [ TODO ]
    ├── test_technician.py               
    ├── test_demand.py                   
    ├── test_demand_manager.py           
    ├── test_demand_queue.py             
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

### `City` — tabela `CITY`
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

### `Analyst` [ TODO ] — tabela `ANL`
| Campo | Tipo Python | Obrigatório | Regras |
|---|---|---|---|
Definição de campos pendentes

### `Technician` — tabela `TECH`
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

### `Demand` — tabela `DMD`
Ponto de entrada do fluxo principal.

| Campo | Tipo Python | Obrigatório | Regras |
|---|---|---|---|
| `demand_id` | `int` | Sim | Auto-gerado |
| `request_date` | `date` | Sim | — |
| `responsible_id` | `int` | Sim | FK para Analyst |
| `project_id` | `str` | Sim | FK para Project |
| `estimated_time` | `float` | Sim | Horas estimadas |
| `actual_time` | `Optional[float]` | Não | Preenchido após execução |
| `problem_description` | `str` | Sim | Não vazio |
| `demand_title` | `str` | Sim | Não vazio |
| `technical_visit_reason` | `str` | Sim | Lista fechada (ver abaixo) |
| `causal_sector` | `str` | Sim | Lista fechada |
| `causal_area` | `str` | Sim | Lista fechada |
| `root_cause` | `str` | Sim | Lista fechada |
| `equipment` | `str` | Sim | Lista fechada |
| `status` | `str` | Sim | Lista fechada |

**Valores válidos — `status`:**
`"Aberta"`, `"Em Andamento"`, `"Concluída"`, `"Cancelada"`

**Valores válidos — `equipment`:**
`"Secador / Fornalha"`,`"Máquina de Limpeza"`,`"Elevadores Agrícolas"`,
`"Transportadores de Correia"`,`"Transportadores Helicoidais"`,
`"Transportadores de Corrente"`,`"Canalização"`,`"Passarela / Torres"`,
`"Rosca Varredora"`,`"Silos Planos / Elevados / Expedição / Aeração"`,
`"Tulhas Metálicas"`,`"Hi Roller / Hi Life"`,`"Temp Stor"`,`"Batco"`

**Valores válidos — `technical_visit_reason`:**
`"Instalação"`, `"Manutenção Corretiva"`, `"Manutenção Preventiva"`,
`"Punch-list"`, `"Reforma"`, `"Teste"`,`"Verificação"`, `"Visita Técnica"`, `"Outro"`

**Valores válidos — `causal_sector`:**
`"Assistência Técnica"`, `"Comercial"`,`"Compras"` `"Engenharia"`, `"Fornecedor"`, `"Logística"`,`"Manufatura"`,`"Montagem"`

**Valores válidos — `causal_area`:**
`"Assistência Técnica"`, `"Comercial - Peças"`,`"Comercial - Projetos"` `"Engenharia de Aplicação"`, `"Engenharia de Produto"`, `"Fornecedor"`,`"Embarque e Transporte"`,`"Preparação"`,`"Recebimento"`, `"Corte e Dobra"`,`"Montagem Final"` `"Pintura"`, `"Silo"`, `"Solda"`,`"Usinagem"`,`"Montagem AGI"`,`"Montagem Cliente"`,`"Supervisão AGI"`

**Valores válidos — `root_cause`:**
Conforme hierarquia criada com dicionário dentro da classe Demand.


### `DemandManager` — tabela `DMD_MGMT`
Referencia `Demand` diretamente — `ServiceOrder` eliminado por simplicidade.
Implementa linked-list para ordenação da fila por técnico.

| Campo | Tipo Python | Obrigatório | Regras |
|---|---|---|---|
| `demand_id` | `int` | Sim | FK para Demand |
| `technician_id` | `int` | Sim | FK para Technician |
| `next_demand_manager_id` | `Optional[int]` | Não | None = último da fila |
| `start_date` | `Optional[date]` | Não | Após execução |
| `finish_date` | `Optional[date]` | Não | Após execução |
| `travel_time` | `Optional[float]` | Não | Calculado pelo planejador |
| `travel_distance` | `Optional[float]` | Não | Calculado pelo planejador |
| `status` | `str` | Sim | valores válidos |
| `is_deleted` | `bool` | Sim | Soft delete, default False |
| `demand_manager_id` | `Optional[int]` | Não | Auto-gerado pelo banco |

**Arquitetura linked-list:**
- `next_demand_manager_id = None` → último da fila (tail)
- Reordenação: `sort()` reconstrói ordem a partir dos links
- `rebuild_links()` recalcula `next_demand_manager_id` após reordenação

### `DemandQueue` — objeto de domínio (não é tabela)
| Campo | Tipo Python | Descrição |
|---|---|---|
| `technician_id` | `int` | Técnico dono da fila |
| `head_id` | `int` |  ← ID do primeiro a executar
| `demands` | `list[DemandManager]` | Lista ordenada (head = próxima execução) |

Métodos:
- `sort()` — reconstrói ordem correta via links (≈ `SortDemandSequence()` VBA)
- `rebuild_links()` — recalcula `next_demand_id` após reordenação (≈ `RebuildLinks()` VBA)

### `ScheduleItem` [ TODO ] — objeto de domínio (não é tabela)
| Campo | Tipo Python | Descrição |
|---|---|---|
| `demand_id` | `int` | FK para DemandManager |
| `technician_id` | `int` | FK para Technician |
| `scheduled_date` | `date` | Data planejada |
| `action` | `str` | Tipo de ação |
| `distance` | `int` | Distância em km |
| `work_time` | `float` | Tempo de trabalho em horas |
| `sequence_position` | `int` | Posição na sequência do dia |

`ScheduleInput` — objeto de domínio (não é tabela)
Dados já resolvidos pelo Service antes de entregar ao SchedulePlanner.

| Campo | Tipo Python | Descrição |
|---|---|---|
| `demand_manager_id` | `int` | ID do registro na fila |
| `demand_id` | `int` | FK para Demand |
| `estimated_time` | `float` | Horas de trabalho |
| `city_lat` | `float` | Latitude do local — resolvida via Demand → Project → Customer → City |
| `city_lon` | `float` | Longitude do local — resolvida via Demand → Project → Customer → City |

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
| `ANL` | `Analyst` | Analistas |
| `DMD` | `Demand` | Demandas técnicas |
| `SERVORD` | `ServiceOrder` | Ordens de serviço | (Excluído por decisão de design)
| `DMD_MGMT` | `DemandManager` | Fila de execução (linked-list) |

---

## 8. Fluxo Principal

```
1. Analista cadastra Demand
2. Analista atribui Demand a técnicos
3. Para cada técnico: cria DemandManager → demanda vai ao final da fila
4. Analista reordena fila via AgendaManager → RebuildLinks recalcula links
5. Sistema gera planejamento dia-a-dia via SchedulePlanner
```

---

## 9. Decisões de Design

| Decisão | Motivo |
|---|---|
| PostgreSQL obrigatório | 2-8 usuários simultâneos — SQLite não suporta concorrência de escrita |
| Fila como linked-list | Mantém arquitetura do VBA — permite reordenação eficiente |
| `DemandQueue` e `SchedulePlanner` como objetos de domínio | Construídos em memória — não persistidos diretamente |
| Soft delete (`is_deleted`) | Mantém histórico — padrão do sistema legado |
| Nomes de código em inglês, mensagens em português | Consistência com projeto anterior |
| `ServiceOrder` eliminado | Não agregava valor — `DemandManager` referencia `Demand` diretamente; múltiplos técnicos = múltiplos registros no `DMD_MGMT` |
| `SchedulePlanner` recebe `ScheduleInput` resolvido | Planejador não conhece a cadeia Demand → Project → Customer → City — responsabilidade do Service |
---

## 10. Próximos Passos

1. Criar repositório Git e estrutura de pastas [OK]
2. Criar model `City` com TDD ← **começar aqui** [OK]
3. Criar model `Technician` com TDD [OK]
4. Criar model `Demand` com TDD (usar `Enum` Python para listas fechadas) [OK]
5. Criar model `DemandManager` com TDD [OK]
6. Implementar `DemandQueue.sort()` com TDD — algoritmo linked-list [OK]
7. Implementar `SchedulePlanner` com TDD — algoritmo mais complexo
8. Criar model `Project` com TDD
9. Criar model `Customer` com TDD
10. Criar model `Analyst` com TDD
11. Criar ORM models + SQLAlchemy + PostgreSQL
12. Implementar Repositories e Services
13. Criar rotas FastAPI
14. Configurar Docker Compose
15. Criar interface Streamlit


