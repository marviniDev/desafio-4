# -*- coding: utf-8 -*-
"""
Configurações para a automação de VR/VA
"""

# Configurações do mês de referência
MES_REFERENCIA = "05/2025"
ANO = 2025
MES = 5

# Configurações de dias úteis
DIAS_UTEIS_PADRAO = 22  # Maio 2025

# Configurações de valores padrão
VALOR_VR_PADRAO = 35.0

# Configurações de proporção de custos
PROPORCAO_EMPRESA = 0.8  # 80%
PROPORCAO_PROFISSIONAL = 0.2  # 20%

# Configurações de validação
DIA_LIMITE_DESLIGAMENTO = 15  # Desligamentos até dia 15 não recebem VR

# Configurações de arquivos
ARQUIVOS_ENTRADA = {
    'ativos': 'ATIVOS.xlsx',
    'ferias': 'FÉRIAS.xlsx',
    'desligados': 'DESLIGADOS.xlsx',
    'estagio': 'ESTÁGIO.xlsx',
    'aprendiz': 'APRENDIZ.xlsx',
    'afastamentos': 'AFASTAMENTOS.xlsx',
    'exterior': 'EXTERIOR.xlsx',
    'admissao': 'ADMISSÃO ABRIL.xlsx',
    'sindicato_valor': 'Base sindicato x valor.xlsx',
    'dias_uteis': 'Base dias uteis.xlsx'
}

# Configurações de colunas
COLUNAS_PADRAO = {
    'matricula': 'MATRICULA',
    'cargo': 'TITULO DO CARGO',
    'sindicato': 'Sindicato',
    'situacao': 'DESC. SITUACAO'
}

# Configurações de exclusão
CARGO_EXCLUIR = ['diretor', 'diretor', 'presidente', 'ceo'] 