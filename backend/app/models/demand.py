from dataclasses import dataclass
from typing import Optional
from datetime import date

PROBLEM_HIERARCHY = {
    "Assistência Técnica": {
        "Assistência Técnica": ["Garantia", "Sinistro"]
    },
    "Comercial": {
        "Comercial - Peças": ["Coleta de Dados"],
        "Comercial - Projetos": ["Acordo Comercial", "Coleta de Dados", "Revisão de Escopo"]
    },
    "Compras": {
        "Compras": ["Atraso na compra", "Material comprado divergente da especificação"]
    },
    "Engenharia":{
        "Engenharia de Aplicação": ["Coleta de Dados", "Definição de Layout", "Listagem de Material Projeto"],
        "Engenharia de Produto": ["Atualização de Projeto", "Definição de Produto", "Especificação de Componentes"
                                  "Falha de Performance - Produto","Listagem de Material Estrutura","Melhoria de Produto",
                                  "Projeto Estrutural"],
    },
    "Fornecedor": {
        "Fornecedor": ["Atraso na entrega", "Material entregue divergente da especificação",
                       "Carga Extraviada", "Material fora do padrão de Qualidade"]
    },
    "Logística":{
        "Embarque e Transporte":["Avaria de Transporte","Embarque de material divergente da especificação",
                                 "Sem evidência de envio no embarque"],
        "Preparação": ["Sem evidencias de envio na preparação","Separação de material divergente da especificação"],
        "Recebimento":["Identificação de Peças"]
    },
    "Manufatura":{
        "Corte e Dobra":['Divergência de lado - Dobra invertida','Divergência dimensional ou furação',
                         'Identificação incorreta','Material divergente da especificação','Material fora do padrão de qualidade'],
        "Montagem Final":['Componente faltante','Identificação incorreta','Material divergente da especificação',
                          'Material fora do padrão de qualidade'],
        "Pintura":['Identificação incorreta','Material divergente da especificação','Material fora do padrão de qualidade'],
        "Silo":['Identificação incorreta','Material divergente da especificação','Material fora do padrão de qualidade'],
        "Solda":['Identificação incorreta','Material divergente da especificação','Material fora do padrão de qualidade'],
        "Usinagem":['Divergência dimensional ou furação','Identificação incorreta','Material divergente da especificação',
                    'Material fora do padrão de qualidade']
    },
    "Montagem":{
        "Montagem AGI":['Armazenamento inadequado do material','Listagem de campo errada',
                        'Montagem divergente da especificação','Peças danificadas na montagem','Perda de peça em obra'],
        "Montagem Cliente":['Armazenamento inadequado do material','Listagem de campo errada',
                            'Montagem divergente da especificação','Peças danificadas na montagem','Perda de peça em obra'],
        "Supervisão AGI":['Armazenamento inadequado do material','Listagem de campo errada',
                          'Montagem divergente da especificação','Peças danificadas na montagem','Perda de peça em obra']
    }
}

DEMAND_STATUS = ["Aberta", "Em Andamento", "Concluida", "Cancelada"]

VALID_EQUIPMENTS = ["Secador / Fornalha","Máquina de Limpeza","Elevadores Agrícolas",
                    "Transportadores de Correia","Transportadores Helicoidais","Transportadores de Corrente",
                    "Canalização","Passarela / Torres","Rosca Varredora",
                    "Silos Planos / Elevados / Expedição / Aeração","Tulhas Metálicas","Hi Roller / Hi Life",
                    "Temp Stor","Batco"]

VALID_TECHNICAL_REASONS = ["Instalacao", "Manutencao Corretiva", "Manutencao Preventiva",
                           "Punch-list", "Reforma", "Teste","Verificação", "Visita Tecnica", "Outro"]


@dataclass
class Demand:

    demand_title: str
    problem_description: str
    project_id: str
    status: str
    responsible_id: int
    request_date: date
    estimated_time: float
    technical_visit_reason: str
    causal_sector: str
    causal_area: str
    root_cause: str
    equipment: str
    actual_time: Optional[float] = None
    demand_id: Optional[int] = None

    def __post_init__(self):
        self._normalize()
        self._validate()
    
    def _normalize(self):
        self.demand_title          = self.demand_title.strip()
        self.problem_description   = self.problem_description.strip()
        self.project_id            = self.project_id.strip()
        self.status                = self.status.strip().title()
        self.technical_visit_reason = self.technical_visit_reason.strip()
        self.causal_sector         = self.causal_sector.strip()
        self.causal_area           = self.causal_area.strip()
        self.root_cause           = self.root_cause.strip()
        self.equipment            = self.equipment.strip().title()
    
    def _validate(self):
        if not self.demand_title:
            raise ValueError("Titulo da demanda nao pode ser vazio")
        if not self.project_id:
            raise ValueError("Projeto nao pode ser vazio")
        if not self.problem_description:
            raise ValueError("Descricao do problema nao pode ser vazia")
        if not self.technical_visit_reason:
            raise ValueError("Motivo da visita nao pode ser vazio")
        if self.technical_visit_reason not in VALID_TECHNICAL_REASONS:
            raise ValueError("Motivo da visita invalido")
        if self.causal_sector not in PROBLEM_HIERARCHY:
            raise ValueError("Setor causador invalido")
        if self.causal_area not in PROBLEM_HIERARCHY[self.causal_sector]:
            raise ValueError("Area causadora invalida para o setor informado")
        if self.root_cause not in PROBLEM_HIERARCHY[self.causal_sector][self.causal_area]:
            raise ValueError("Causa raiz invalida para a area informada")
        if self.status not in DEMAND_STATUS:
            raise ValueError("Status invalido")
        if self.estimated_time <= 0:
            raise ValueError("Tempo estimado deve ser maior que zero")
        if self.actual_time is not None and self.actual_time < 0:
            raise ValueError("Tempo real deve ser maior que zero")
        if self.equipment not in VALID_EQUIPMENTS:
            raise ValueError("Equipamento invalido")
        
        
