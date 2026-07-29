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

DEMAND_STATUS = ["Aberta", "Em Andamento", "Concluída", "Cancelada"]

VALID_EQUIPMENTS = ["Secador / Fornalha","Máquina de Limpeza","Elevadores Agrícolas",
                    "Transportadores de Correia","Transportadores Helicoidais","Transportadores de Corrente",
                    "Canalização","Passarela / Torres","Rosca Varredora",
                    "Silos Planos / Elevados / Expedição / Aeração","Tulhas Metálicas","Hi Roller / Hi Life",
                    "Temp Stor","Batco"]

VALID_TECHNICAL_REASONS = ["Instalação", "Manutenção Corretiva", "Manutenção Preventiva",
                           "Punch-list", "Reforma", "Teste","Verificação", "Visita Técnica", "Outro"]