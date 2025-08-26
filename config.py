# -*- coding: utf-8 -*-
"""
Configurações para a automação de VR/VA
"""

# Configurações do período de referência
PERIODO_REFERENCIA = {
    'inicio': '15/04/2025',  # Início do período de consolidação
    'fim': '15/05/2025',     # Fim do período de consolidação
    'mes_competencia': '05/2025',  # Mês de competência para pagamento
    'ano': 2025,
    'mes': 5
}

# Configurações de execução
EXECUCAO = {
    'periodo_execucao_inicio': 1,    # Dia do mês para início da execução
    'periodo_execucao_fim': 10,      # Dia do mês para fim da execução
    'alerta_execucao_fora_periodo': True,  # Alertar se executando fora do período
    'bloquear_execucao_fora_periodo': False,  # Bloquear execução fora do período (False = apenas alertar)
    'tolerancia_dias': 2,  # Tolerância em dias para execução fora do período
    'mensagem_bloqueio': 'Execução bloqueada: fora do período recomendado. Execute entre os dias 1-10 do mês.'
}

# Configurações de dias úteis
DIAS_UTEIS = {
    'padrao': 22,  # Dias úteis padrão do mês
    'considerar_feriados': True,  # Considerar feriados nacionais
    'considerar_feriados_estaduais': True,  # Considerar feriados estaduais
    'considerar_feriados_municipais': True,  # Considerar feriados municipais
    'prioridade_base_sindicato': True  # Priorizar base do sindicato sobre calendário
}

# Configurações de valores padrão
VALOR_VR_PADRAO = 35.0

# Configurações de proporção de custos
PROPORCAO_EMPRESA = 0.8  # 80%
PROPORCAO_PROFISSIONAL = 0.2  # 20%

# Configurações de validação
DIA_LIMITE_DESLIGAMENTO = 15  # Desligamentos até dia 15 não recebem VR

# Configurações de tratamento de dados
TRATAMENTO_DADOS = {
    'ferias_sem_periodo': 'validar_por_historico',  # Estratégia para férias sem período
    'afastamentos_sem_retorno': 'excluir_automaticamente',  # Como tratar afastamentos sem data de retorno
    'exterior_retornou': 'incluir_se_retornou',  # Como tratar retornos do exterior
    'desligados_sem_comunicado': 'incluir_com_cautela',  # Como tratar desligados sem comunicado
    'validar_consistencia_temporal': True,  # Validar se bases estão alinhadas temporalmente
    'ferias_periodo_padrao': '15/04 a 15/05',  # Período padrão para férias
    'ferias_tolerancia_dias': 5,  # Tolerância em dias para considerar férias no período
    'ferias_estrategia_conservadora': True  # Usar estratégia conservadora para férias
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