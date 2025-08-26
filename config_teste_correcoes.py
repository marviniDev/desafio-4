# -*- coding: utf-8 -*-
"""
Configuração de teste para as correções implementadas
"""

# Configurações para testar as correções
PERIODO_REFERENCIA = {
    'inicio': '15/04/2025',
    'fim': '15/05/2025',
    'mes_competencia': '05/2025',
    'ano': 2025,
    'mes': 5
}

# Configurações de execução com bloqueio ativo
EXECUCAO = {
    'periodo_execucao_inicio': 1,
    'periodo_execucao_fim': 10,
    'alerta_execucao_fora_periodo': True,
    'bloquear_execucao_fora_periodo': True,  # ATIVADO para teste
    'tolerancia_dias': 2,
    'mensagem_bloqueio': 'Execução bloqueada: fora do período recomendado. Execute entre os dias 1-10 do mês.'
}

# Configurações de dias úteis
DIAS_UTEIS = {
    'padrao': 22,
    'considerar_feriados': True,
    'considerar_feriados_estaduais': True,
    'considerar_feriados_municipais': True,
    'prioridade_base_sindicato': True
}

# Configurações de valores padrão
VALOR_VR_PADRAO = 35.0

# Configurações de proporção de custos
PROPORCAO_EMPRESA = 0.8
PROPORCAO_PROFISSIONAL = 0.2

# Configurações de validação
DIA_LIMITE_DESLIGAMENTO = 15

# Configurações de tratamento de dados com correções
TRATAMENTO_DADOS = {
    'ferias_sem_periodo': 'validar_por_historico',  # Estratégia inteligente
    'afastamentos_sem_retorno': 'excluir_automaticamente',
    'exterior_retornou': 'incluir_se_retornou',
    'desligados_sem_comunicado': 'incluir_com_cautela',
    'validar_consistencia_temporal': True,
    'ferias_periodo_padrao': '15/04 a 15/05',
    'ferias_tolerancia_dias': 5,
    'ferias_estrategia_conservadora': True  # Estratégia conservadora ativada
}

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

# Configurações de feriados (exemplo para 2025)
FERIADOS_2025 = {
    'nacionais': [
        '01/01/2025',  # Ano Novo
        '20/04/2025',  # Tiradentes
        '01/05/2025',  # Dia do Trabalho
        '19/06/2025',  # Corpus Christi
        '07/09/2025',  # Independência
        '12/10/2025',  # Nossa Senhora
        '02/11/2025',  # Finados
        '15/11/2025',  # Proclamação da República
        '25/12/2025'   # Natal
    ],
    'estaduais': {
        'SP': ['25/01/2025'],  # Aniversário de SP
        'RJ': ['23/04/2025'],  # São Jorge
        'MG': ['21/04/2025']   # Tiradentes
    }
}

# Configurações de teste das correções
TESTE_CORRECOES = {
    'testar_valores_sindicato': True,  # Testar correção dos valores por sindicato
    'testar_bloqueio_periodo': True,   # Testar bloqueio fora do período
    'testar_ferias_inteligente': True, # Testar estratégia inteligente de férias
    'modo_teste': True                 # Ativar modo de teste
} 