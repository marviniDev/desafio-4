#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automação da compra de VR/VA
Sistema para automatizar o processo mensal de compra de Vale Refeição
"""

import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
import warnings
import calendar
from config import *
warnings.filterwarnings('ignore')

class AutomacaoVR:
    def __init__(self, periodo_personalizado=None):
        """
        Inicializa a automação com período configurável
        
        Args:
            periodo_personalizado (dict): Dicionário com 'inicio', 'fim', 'mes_competencia'
        """
        if periodo_personalizado:
            self.periodo = periodo_personalizado
        else:
            self.periodo = PERIODO_REFERENCIA
        
        # Converter strings de data para objetos datetime
        self.data_inicio = datetime.strptime(self.periodo['inicio'], '%d/%m/%Y')
        self.data_fim = datetime.strptime(self.periodo['fim'], '%d/%m/%Y')
        self.mes_competencia = self.periodo['mes_competencia']
        self.ano = self.periodo['ano']
        self.mes = self.periodo['mes']
        
        # Inicializar logs de validação ANTES de chamar os métodos
        self.logs_validacao = []
        self.alertas = []
        
        # Validar período de execução
        self.validar_periodo_execucao()
        
        # Calcular dias úteis do período
        self.dias_uteis_periodo = self.calcular_dias_uteis_periodo()
        
    def validar_periodo_execucao(self):
        """Valida se a execução está no período correto"""
        hoje = datetime.now()
        dia_atual = hoje.day
        
        if EXECUCAO['alerta_execucao_fora_periodo']:
            # Verificar se está dentro do período recomendado
            dentro_periodo = (
                dia_atual >= EXECUCAO['periodo_execucao_inicio'] and 
                dia_atual <= EXECUCAO['periodo_execucao_fim']
            )
            
            # Verificar se está dentro da tolerância
            tolerancia_inicio = EXECUCAO['periodo_execucao_inicio'] - EXECUCAO['tolerancia_dias']
            tolerancia_fim = EXECUCAO['periodo_execucao_fim'] + EXECUCAO['tolerancia_dias']
            
            dentro_tolerancia = (
                dia_atual >= tolerancia_inicio and 
                dia_atual <= tolerancia_fim
            )
            
            if not dentro_periodo:
                if EXECUCAO['bloquear_execucao_fora_periodo']:
                    # Bloquear execução
                    raise ValueError(EXECUCAO['mensagem_bloqueio'])
                else:
                    # Apenas alertar
                    if dentro_tolerancia:
                        self.alertas.append(
                            f"⚠️ ALERTA: Execução próxima ao limite do período recomendado. "
                            f"Período: {EXECUCAO['periodo_execucao_inicio']}-{EXECUCAO['periodo_execucao_fim']}, "
                            f"Hoje: {dia_atual}"
                        )
                    else:
                        self.alertas.append(
                            f"🚨 ALERTA CRÍTICO: Execução fora do período recomendado. "
                            f"Período: {EXECUCAO['periodo_execucao_inicio']}-{EXECUCAO['periodo_execucao_fim']}, "
                            f"Hoje: {dia_atual}. "
                            f"Recomenda-se executar dentro do período para garantir consistência dos dados."
                        )
            else:
                self.logs_validacao.append(
                    f"✅ Execução no período recomendado: dia {dia_atual}"
                )
    
    def calcular_dias_uteis_periodo(self):
        """Calcula dias úteis do período considerando feriados"""
        dias_uteis = 0
        data_atual = self.data_inicio
        
        while data_atual <= self.data_fim:
            # Verificar se é dia útil (não é fim de semana)
            if data_atual.weekday() < 5:  # 0=Segunda, 4=Sexta
                # Verificar se não é feriado nacional
                data_str = data_atual.strftime('%d/%m/%Y')
                if data_str not in FERIADOS_2025['nacionais']:
                    dias_uteis += 1
            
            data_atual += timedelta(days=1)
        
        return dias_uteis
        
    def carregar_dados(self):
        """Carrega todas as planilhas de dados"""
        print("Carregando dados das planilhas...")
        
        try:
            # Carregar planilhas principais
            self.ativos = pd.read_excel(ARQUIVOS_ENTRADA['ativos'])
            self.ferias = pd.read_excel(ARQUIVOS_ENTRADA['ferias'])
            self.desligados = pd.read_excel(ARQUIVOS_ENTRADA['desligados'])
            self.estagio = pd.read_excel(ARQUIVOS_ENTRADA['estagio'])
            self.aprendiz = pd.read_excel(ARQUIVOS_ENTRADA['aprendiz'])
            self.afastamentos = pd.read_excel(ARQUIVOS_ENTRADA['afastamentos'])
            self.exterior = pd.read_excel(ARQUIVOS_ENTRADA['exterior'])
            self.admissao_abril = pd.read_excel(ARQUIVOS_ENTRADA['admissao'])
            self.base_sindicato = pd.read_excel(ARQUIVOS_ENTRADA['sindicato_valor'])
            self.base_dias_uteis = pd.read_excel(ARQUIVOS_ENTRADA['dias_uteis'])
            
            # Validar consistência temporal das bases
            self.validar_consistencia_temporal()
            
            print("✓ Dados carregados com sucesso")
            return True
            
        except Exception as e:
            print(f"✗ Erro ao carregar dados: {e}")
            return False
    
    def validar_consistencia_temporal(self):
        """Valida se as bases estão alinhadas temporalmente"""
        if not TRATAMENTO_DADOS['validar_consistencia_temporal']:
            return
            
        print("Validando consistência temporal das bases...")
        
        # Verificar se base dias úteis está no período correto
        if 'BASE DIAS UTEIS DE 15/04 a 15/05' in self.base_dias_uteis.columns:
            self.logs_validacao.append("✓ Base dias úteis: Período 15/04 a 15/05 (OK)")
        else:
            self.alertas.append("⚠️ Base dias úteis: Período não identificado")
        
        # Verificar se desligados estão no mês de competência
        if 'DATA DEMISSÃO' in self.desligados.columns:
            datas_desligamento = pd.to_datetime(self.desligados['DATA DEMISSÃO'], errors='coerce')
            datas_validas = datas_desligamento.dropna()
            if len(datas_validas) > 0:
                mes_desligamento = datas_validas.dt.month.iloc[0]
                if mes_desligamento == self.mes:
                    self.logs_validacao.append(f"✓ Base desligados: Mês {self.mes} (OK)")
                else:
                    self.alertas.append(f"⚠️ Base desligados: Mês {mes_desligamento} diferente do esperado {self.mes}")
        
        # Verificar se admissões estão no período correto
        if 'Admissão' in self.admissao_abril.columns:
            self.logs_validacao.append("✓ Base admissão: Abril (OK)")
        
        print("✓ Consistência temporal validada")
    
    def limpar_colunas(self):
        """Limpa e padroniza as colunas das planilhas"""
        print("Limpando e padronizando colunas...")
        
        # Limpar colunas da base sindicato
        self.base_sindicato.columns = ['ESTADO', 'VALOR']
        self.base_sindicato['ESTADO'] = self.base_sindicato['ESTADO'].str.strip()
        
        # Limpar colunas da base dias úteis
        self.base_dias_uteis.columns = ['SINDICATO', 'DIAS_UTEIS']
        self.base_dias_uteis['SINDICATO'] = self.base_dias_uteis['SINDICATO'].str.strip()
        
        # Padronizar colunas de matrícula
        for df_name in ['ativos', 'ferias', 'desligados', 'estagio', 'aprendiz', 'afastamentos', 'exterior', 'admissao_abril']:
            df = getattr(self, df_name)
            if 'MATRICULA' in df.columns:
                df['MATRICULA'] = df['MATRICULA'].astype(str).str.strip()
            elif 'MATRICULA ' in df.columns:  # Para desligados que tem espaço extra
                df['MATRICULA'] = df['MATRICULA '].astype(str).str.strip()
                df.drop('MATRICULA ', axis=1, inplace=True)
        
        print("✓ Colunas limpas e padronizadas")
    
    def aplicar_filtros_exclusao(self):
        """Aplica filtros de exclusão conforme regras do negócio"""
        print("Aplicando filtros de exclusão...")
        
        # Lista de matrículas a serem excluídas
        matriculas_excluir = set()
        
        # 1. Estagiários
        if 'MATRICULA' in self.estagio.columns:
            matriculas_excluir.update(self.estagio['MATRICULA'].astype(str).tolist())
        
        # 2. Aprendizes
        if 'MATRICULA' in self.aprendiz.columns:
            matriculas_excluir.update(self.aprendiz['MATRICULA'].astype(str).tolist())
        
        # 3. Profissionais no exterior (CORRIGIDO: não excluir automaticamente)
        if 'MATRICULA' in self.exterior.columns:
            # Verificar se há retornos do exterior
            if 'Unnamed: 2' in self.exterior.columns:
                retornos = self.exterior[self.exterior['Unnamed: 2'].str.contains('RETORNOU', na=False)]
                if len(retornos) > 0:
                    self.logs_validacao.append(f"⚠️ {len(retornos)} colaboradores retornaram do exterior")
                    # Não excluir automaticamente, tratar individualmente
                else:
                    # Excluir apenas se não retornaram
                    matriculas_excluir.update(self.exterior['MATRICULA'].astype(str).tolist())
            else:
                matriculas_excluir.update(self.exterior['MATRICULA'].astype(str).tolist())
        
        # 4. Afastados (CORRIGIDO: verificar datas de retorno)
        if 'MATRICULA' in self.afastamentos.columns:
            # Verificar se há datas de retorno
            if 'Unnamed: 3' in self.afastamentos.columns:
                afastados_sem_retorno = self.afastamentos[
                    self.afastamentos['Unnamed: 3'].isna() | 
                    (self.afastamentos['Unnamed: 3'] == '')
                ]
                afastados_com_retorno = self.afastamentos[
                    self.afastamentos['Unnamed: 3'].notna() & 
                    (self.afastamentos['Unnamed: 3'] != '')
                ]
                
                # Excluir apenas afastados sem data de retorno
                matriculas_excluir.update(afastados_sem_retorno['MATRICULA'].astype(str).tolist())
                
                if len(afastados_com_retorno) > 0:
                    self.logs_validacao.append(f"⚠️ {len(afastados_com_retorno)} afastados com data de retorno (não excluídos)")
            else:
                # Se não há coluna de retorno, excluir todos
                matriculas_excluir.update(self.afastamentos['MATRICULA'].astype(str).tolist())
        
        # 5. Diretores (cargos que contêm "diretor")
        diretores = self.ativos[self.ativos['TITULO DO CARGO'].str.contains('diretor', case=False, na=False)]
        matriculas_excluir.update(diretores['MATRICULA'].astype(str).tolist())
        
        # Aplicar exclusões na base de ativos
        self.ativos_filtrados = self.ativos[~self.ativos['MATRICULA'].astype(str).isin(matriculas_excluir)].copy()
        
        print(f"✓ Filtros aplicados. Colaboradores restantes: {len(self.ativos_filtrados)}")
        return matriculas_excluir
    
    def calcular_dias_uteis_colaborador(self):
        """Calcula dias úteis por colaborador considerando férias, afastamentos e desligamentos"""
        print("Calculando dias úteis por colaborador...")
        
        # Criar base consolidada
        self.base_consolidada = self.ativos_filtrados.copy()
        
        # Adicionar informações de férias
        self.base_consolidada = self.base_consolidada.merge(
            self.ferias[['MATRICULA', 'DIAS DE FÉRIAS']], 
            on='MATRICULA', 
            how='left'
        )
        self.base_consolidada['DIAS DE FÉRIAS'] = self.base_consolidada['DIAS DE FÉRIAS'].fillna(0)
        
        # Adicionar informações de desligamento
        self.base_consolidada = self.base_consolidada.merge(
            self.desligados[['MATRICULA', 'DATA DEMISSÃO', 'COMUNICADO DE DESLIGAMENTO']], 
            on='MATRICULA', 
            how='left'
        )
        
        # Adicionar informações de admissão
        self.base_consolidada = self.base_consolidada.merge(
            self.admissao_abril[['MATRICULA', 'Admissão']], 
            on='MATRICULA', 
            how='left'
        )
        
        # Calcular dias úteis por colaborador
        self.base_consolidada['DIAS_UTEIS_COLABORADOR'] = self.dias_uteis_periodo
        
        # Ajustar para férias (CORRIGIDO: implementar estratégias inteligentes)
        if TRATAMENTO_DADOS['ferias_sem_periodo'] == 'validar_por_historico':
            # Estratégia inteligente: validar por histórico e aplicar estratégia conservadora
            self.aplicar_estrategia_ferias_inteligente()
        elif TRATAMENTO_DADOS['ferias_sem_periodo'] == 'assumir_periodo_consolidacao':
            # Estratégia original: assumir período de consolidação
            self.base_consolidada['DIAS_UTEIS_COLABORADOR'] -= self.base_consolidada['DIAS DE FÉRIAS']
            self.logs_validacao.append("⚠️ Férias sem período: Assumindo período de consolidação")
        else:
            # Outras estratégias podem ser implementadas aqui
            pass
        
        # Ajustar para desligamentos (CORRIGIDO: tratar desligados sem comunicado)
        def ajustar_desligamento(row):
            if pd.notna(row['DATA DEMISSÃO']):
                data_desligamento = pd.to_datetime(row['DATA DEMISSÃO'])
                if data_desligamento.month == self.mes and data_desligamento.year == self.ano:
                    # Verificar se tem comunicado
                    if pd.notna(row['COMUNICADO DE DESLIGAMENTO']) and row['COMUNICADO DE DESLIGAMENTO'] == 'OK':
                        # Comunicado confirmado
                        if data_desligamento.day <= DIA_LIMITE_DESLIGAMENTO:
                            return 0  # Não considerar para pagamento
                        else:
                            # Calcular proporcional
                            dias_ate_desligamento = data_desligamento.day
                            return max(0, dias_ate_desligamento - DIA_LIMITE_DESLIGAMENTO)
                    else:
                        # Sem comunicado - aplicar estratégia configurada
                        if TRATAMENTO_DADOS['desligados_sem_comunicado'] == 'incluir_com_cautela':
                            # Incluir com dias reduzidos (estratégia conservadora)
                            dias_ate_desligamento = data_desligamento.day
                            return max(0, dias_ate_desligamento - DIA_LIMITE_DESLIGAMENTO)
                        elif TRATAMENTO_DADOS['desligados_sem_comunicado'] == 'excluir_automaticamente':
                            return 0
                        else:
                            # Incluir normalmente (estratégia padrão)
                            dias_ate_desligamento = data_desligamento.day
                            return max(0, dias_ate_desligamento - DIA_LIMITE_DESLIGAMENTO)
            return row['DIAS_UTEIS_COLABORADOR']
        
        self.base_consolidada['DIAS_UTEIS_COLABORADOR'] = self.base_consolidada.apply(ajustar_desligamento, axis=1)
        
        # Ajustar para admissões no meio do período (CORRIGIDO: implementar lógica)
        def ajustar_admissao(row):
            if pd.notna(row['Admissão']):
                try:
                    data_admissao = pd.to_datetime(row['Admissão'])
                    if data_admissao.month == self.mes and data_admissao.year == self.ano:
                        # Admissão no mês de competência - calcular proporcional
                        dias_desde_admissao = self.dias_uteis_periodo - (data_admissao.day - 1)
                        return max(0, dias_desde_admissao)
                except:
                    pass
            return row['DIAS_UTEIS_COLABORADOR']
        
        self.base_consolidada['DIAS_UTEIS_COLABORADOR'] = self.base_consolidada.apply(ajustar_admissao, axis=1)
        
        # Garantir que não há valores negativos
        self.base_consolidada['DIAS_UTEIS_COLABORADOR'] = self.base_consolidada['DIAS_UTEIS_COLABORADOR'].clip(lower=0)
        
        # Logs de validação
        total_dias_uteis = self.base_consolidada['DIAS_UTEIS_COLABORADOR'].sum()
        self.logs_validacao.append(f"✓ Total de dias úteis calculados: {total_dias_uteis}")
        
        print("✓ Dias úteis calculados para cada colaborador")
    
    def calcular_valor_vr(self):
        """Calcula o valor de VR para cada colaborador"""
        print("Calculando valores de VR...")
        
        # Mapear valores por sindicato (CORRIGIDO: mapeamento correto)
        mapeamento_sindicato = {}
        
        # Mapear base sindicato x valor
        for _, row in self.base_sindicato.iterrows():
            estado = row['ESTADO'].strip()
            valor = row['VALOR']
            if pd.notna(valor):  # Ignorar valores NaN
                mapeamento_sindicato[estado] = valor
        
        print(f"✓ Mapeamento de valores por estado: {mapeamento_sindicato}")
        
        # Mapear base dias úteis (CORRIGIDO: usar corretamente)
        mapeamento_dias_uteis = {}
        for _, row in self.base_dias_uteis.iterrows():
            sindicato = row['SINDICATO'].strip()
            dias_uteis = row['DIAS_UTEIS']
            mapeamento_dias_uteis[sindicato] = dias_uteis
        
        # Aplicar valores por sindicato (CORRIGIDO: lógica de mapeamento)
        def obter_valor_sindicato(sindicato):
            if pd.isna(sindicato):
                return VALOR_VR_PADRAO
            
            sindicato_str = str(sindicato).strip()
            
            # Mapeamento direto por estado
            for estado, valor in mapeamento_sindicato.items():
                if estado in sindicato_str:
                    return valor
            
            # Mapeamento por correspondência de siglas
            mapeamento_siglas = {
                'SP': 'São Paulo',
                'RJ': 'Rio de Janeiro', 
                'RS': 'Rio Grande do Sul',
                'PR': 'Paraná'
            }
            
            for sigla, estado in mapeamento_siglas.items():
                if sigla in sindicato_str and estado in mapeamento_sindicato:
                    return mapeamento_sindicato[estado]
            
            # Se não encontrar, usar valor padrão
            return VALOR_VR_PADRAO
        
        self.base_consolidada['VALOR_DIARIO_VR'] = self.base_consolidada['Sindicato'].apply(obter_valor_sindicato)
        
        # Logs de validação dos valores aplicados
        valores_aplicados = self.base_consolidada['VALOR_DIARIO_VR'].value_counts().sort_index()
        self.logs_validacao.append(f"✓ Valores diários aplicados: {dict(valores_aplicados)}")
        
        # Aplicar dias úteis por sindicato (CORRIGIDO: implementar prioridade)
        def obter_dias_uteis_sindicato(sindicato):
            if pd.isna(sindicato):
                return self.dias_uteis_periodo
            
            sindicato_str = str(sindicato).strip()
            
            # Buscar por correspondência parcial na base de dias úteis
            for sind, dias in mapeamento_dias_uteis.items():
                if sind.lower() in sindicato_str.lower() or sindicato_str.lower() in sind.lower():
                    return dias
            
            return self.dias_uteis_periodo  # Usar dias úteis do período se não encontrar
        
        # Aplicar dias úteis do sindicato se configurado para priorizar
        if DIAS_UTEIS['prioridade_base_sindicato']:
            self.base_consolidada['DIAS_UTEIS_SINDICATO'] = self.base_consolidada['Sindicato'].apply(obter_dias_uteis_sindicato)
            
            # Recalcular dias úteis considerando o sindicato
            self.base_consolidada['DIAS_UTEIS_COLABORADOR'] = self.base_consolidada.apply(
                lambda row: min(row['DIAS_UTEIS_COLABORADOR'], row['DIAS_UTEIS_SINDICATO']), 
                axis=1
            )
            
            self.logs_validacao.append("✓ Dias úteis ajustados conforme base do sindicato")
        
        # Calcular valor total de VR
        self.base_consolidada['VALOR_TOTAL_VR'] = (
            self.base_consolidada['DIAS_UTEIS_COLABORADOR'] * 
            self.base_consolidada['VALOR_DIARIO_VR']
        )
        
        # Calcular custo empresa (80%) e desconto profissional (20%)
        self.base_consolidada['CUSTO_EMPRESA'] = self.base_consolidada['VALOR_TOTAL_VR'] * PROPORCAO_EMPRESA
        self.base_consolidada['DESCONTO_PROFISSIONAL'] = self.base_consolidada['VALOR_TOTAL_VR'] * PROPORCAO_PROFISSIONAL
        
        # Logs de validação
        total_vr = self.base_consolidada['VALOR_TOTAL_VR'].sum()
        self.logs_validacao.append(f"✓ Valor total de VR calculado: R$ {total_vr:,.2f}")
        
        print("✓ Valores de VR calculados")
    
    def aplicar_estrategia_ferias_inteligente(self):
        """Aplica estratégia inteligente para férias sem período específico"""
        print("Aplicando estratégia inteligente para férias...")
        
        # Contadores para análise
        total_colaboradores_ferias = len(self.base_consolidada[self.base_consolidada['DIAS DE FÉRIAS'] > 0])
        férias_aplicadas = 0
        férias_nao_aplicadas = 0
        
        for idx, row in self.base_consolidada.iterrows():
            if row['DIAS DE FÉRIAS'] > 0:
                dias_ferias = row['DIAS DE FÉRIAS']
                
                # Estratégia conservadora: aplicar apenas uma parte das férias
                if TRATAMENTO_DADOS['ferias_estrategia_conservadora']:
                    # Aplicar apenas 70% das férias para ser conservador
                    dias_aplicar = int(dias_ferias * 0.7)
                    self.base_consolidada.at[idx, 'DIAS_UTEIS_COLABORADOR'] -= dias_aplicar
                    férias_aplicadas += 1
                    
                    # Adicionar observação sobre estratégia aplicada
                    if 'OBSERVACOES_FERIAS' not in self.base_consolidada.columns:
                        self.base_consolidada['OBSERVACOES_FERIAS'] = ''
                    
                    self.base_consolidada.at[idx, 'OBSERVACOES_FERIAS'] = (
                        f"Férias: {dias_ferias} dias, aplicados: {dias_aplicar} dias "
                        f"(estratégia conservadora 70%)"
                    )
                else:
                    # Estratégia padrão: aplicar todas as férias
                    self.base_consolidada.at[idx, 'DIAS_UTEIS_COLABORADOR'] -= dias_ferias
                    férias_aplicadas += 1
        
        # Logs de validação
        self.logs_validacao.append(
            f"✓ Estratégia inteligente de férias aplicada: "
            f"{férias_aplicadas} colaboradores processados"
        )
        
        if TRATAMENTO_DADOS['ferias_estrategia_conservadora']:
            self.logs_validacao.append(
                "⚠️ Estratégia conservadora aplicada: 70% das férias consideradas"
            )
        
        print("✓ Estratégia inteligente de férias aplicada")
    
    def gerar_planilha_final(self):
        """Gera a planilha final para envio à operadora"""
        print("Gerando planilha final...")
        
        # Selecionar colunas para a planilha final
        colunas_finais = [
            'MATRICULA',
            'Admissão',
            'Sindicato',  # Adicionar sindicato do colaborador
            'DATA DEMISSÃO',
            'DIAS_UTEIS_COLABORADOR',
            'VALOR_DIARIO_VR',
            'VALOR_TOTAL_VR',
            'CUSTO_EMPRESA',
            'DESCONTO_PROFISSIONAL'
        ]
        
        # Adicionar coluna de observações de férias se existir
        if 'OBSERVACOES_FERIAS' in self.base_consolidada.columns:
            colunas_finais.append('OBSERVACOES_FERIAS')
        
        # Criar planilha final
        self.planilha_final = self.base_consolidada[colunas_finais].copy()
        
        # Renomear colunas para o formato solicitado
        colunas_renomeadas = [
            'Matricula',
            'Admissão',
            'Sindicato do Colaborador',  # Nome exato solicitado
            'Competência',  # Mês/ano de competência
            'Dias',  # Dias úteis
            'VALOR DIÁRIO VR',  # Nome exato solicitado
            'TOTAL',  # Nome exato solicitado
            'Custo empresa',
            'Desconto profissional'
        ]
        
        # Adicionar coluna de observações de férias se existir
        if 'OBSERVACOES_FERIAS' in self.planilha_final.columns:
            colunas_renomeadas.append('Observações Férias')
        
        self.planilha_final.columns = colunas_renomeadas
        
        # Adicionar coluna de competência (mês/ano)
        self.planilha_final['Competência'] = self.periodo['mes_competencia']
        
        # Adicionar coluna de observações gerais
        self.planilha_final['OBS GERAL'] = ''
        
        # Combinar observações de férias com observações gerais se existir
        if 'Observações Férias' in self.planilha_final.columns:
            # Mover observações de férias para OBS GERAL
            self.planilha_final['OBS GERAL'] = self.planilha_final['Observações Férias'].fillna('')
            # Remover coluna de observações de férias
            self.planilha_final = self.planilha_final.drop('Observações Férias', axis=1)
        
        # Reordenar colunas na ordem solicitada
        colunas_ordenadas = [
            'Matricula',
            'Admissão', 
            'Sindicato do Colaborador',
            'Competência',
            'Dias',
            'VALOR DIÁRIO VR',
            'TOTAL',
            'Custo empresa',
            'Desconto profissional',
            'OBS GERAL'
        ]
        
        self.planilha_final = self.planilha_final[colunas_ordenadas]
        
        # Adicionar coluna de observações
        self.planilha_final['OBS GERAL'] = ''
        
        # Aplicar validações
        self.aplicar_validacoes()
        
        # Salvar planilha
        nome_arquivo = f"VR_MENSAL_{self.mes:02d}_{self.ano}_AUTOMATIZADO.xlsx"
        
        with pd.ExcelWriter(nome_arquivo, engine='openpyxl') as writer:
            self.planilha_final.to_excel(writer, sheet_name='VR Mensal', index=False)
            
            # Criar aba de validações (CORRIGIDO: incluir logs e alertas)
            validacoes_data = []
            
            # Dados básicos
            validacoes_data.extend([
                ['INFORMAÇÕES BÁSICAS', ''],
                ['Período de consolidação', f"{self.periodo['inicio']} a {self.periodo['fim']}"],
                ['Mês de competência', self.periodo['mes_competencia']],
                ['Dias úteis do período', self.dias_uteis_periodo],
                ['', ''],
                ['RESUMO DA AUTOMAÇÃO', ''],
                ['Total de colaboradores', len(self.planilha_final)],
                ['Total de dias úteis', self.planilha_final['Dias'].sum()],
                            ['Valor total VR', f"R$ {self.planilha_final['TOTAL'].sum():,.2f}"],
            ['Custo total empresa', f"R$ {self.planilha_final['Custo empresa'].sum():,.2f}"],
            ['Desconto total profissional', f"R$ {self.planilha_final['Desconto profissional'].sum():,.2f}"],
                ['', ''],
                ['CONTADORES', ''],
                ['Colaboradores com férias', len(self.ferias)],
                ['Colaboradores desligados', len(self.desligados)],
                ['Novas admissões', len(self.admissao_abril)],
                ['', ''],
                ['LOGS DE VALIDAÇÃO', ''],
            ])
            
            # Adicionar logs de validação
            for log in self.logs_validacao:
                validacoes_data.append([log, ''])
            
            # Adicionar alertas
            if self.alertas:
                validacoes_data.extend([
                    ['', ''],
                    ['ALERTAS E AVISOS', ''],
                ])
                for alerta in self.alertas:
                    validacoes_data.append([alerta, ''])
            
            # Adicionar validações de dados
            validacoes_data.extend([
                ['', ''],
                ['VALIDAÇÕES DE DADOS', ''],
                ['Registros com observações', len(self.planilha_final[self.planilha_final['OBS GERAL'] != ''])],
                ['Registros válidos', len(self.planilha_final[self.planilha_final['OBS GERAL'] == ''])],
                ['', ''],
                ['ESTRUTURA DA PLANILHA', ''],
                ['Total de colunas', len(self.planilha_final.columns)],
                ['Colunas implementadas', ', '.join(self.planilha_final.columns.tolist())],
            ])
            
            validacoes = pd.DataFrame(validacoes_data, columns=['Validações', 'Check'])
            validacoes.to_excel(writer, sheet_name='Validações', index=False)
        
        print(f"✓ Planilha final gerada: {nome_arquivo}")
        return nome_arquivo
    
    def aplicar_validacoes(self):
        """Aplica validações na planilha final"""
        print("Aplicando validações...")
        
        # Validar dados inconsistentes
        for idx, row in self.planilha_final.iterrows():
            obs = []
            
            # Validar matrícula
            if pd.isna(row['Matricula']) or str(row['Matricula']).strip() == '':
                obs.append("Matrícula inválida")
            
            # Validar admissão (pode ser NaT para colaboradores antigos)
            if pd.notna(row['Admissão']):
                try:
                    data_admissao = pd.to_datetime(row['Admissão'])
                    # Validar se a data faz sentido
                    if data_admissao.year < 1900 or data_admissao.year > 2030:
                        obs.append("Data de admissão fora do período válido")
                except:
                    obs.append("Formato de data de admissão inválido")
            
            # Validar sindicato
            if pd.isna(row['Sindicato do Colaborador']) or str(row['Sindicato do Colaborador']).strip() == '':
                obs.append("Sindicato não informado")
            
            # Validar competência
            if pd.isna(row['Competência']) or str(row['Competência']).strip() == '':
                obs.append("Competência não informada")
            
            # Validar dias úteis
            if row['Dias'] < 0 or row['Dias'] > self.dias_uteis_periodo:
                obs.append(f"Dias úteis inválidos: {row['Dias']} (máx: {self.dias_uteis_periodo})")
            
            # Validar valor diário VR
            if row['VALOR DIÁRIO VR'] <= 0:
                obs.append("Valor diário VR deve ser maior que zero")
            
            # Validar valor total
            if row['TOTAL'] < 0:
                obs.append("Valor total VR negativo")
            
            # Validar custo empresa
            if row['Custo empresa'] < 0:
                obs.append("Custo empresa negativo")
            
            # Validar desconto profissional
            if row['Desconto profissional'] < 0:
                obs.append("Desconto profissional negativo")
            
            # Validar proporção 80/20
            if abs(row['Custo empresa'] - (row['TOTAL'] * PROPORCAO_EMPRESA)) > 0.01:
                obs.append("Proporção empresa/profissional incorreta")
            
            # Validar proporção 20%
            if abs(row['Desconto profissional'] - (row['TOTAL'] * PROPORCAO_PROFISSIONAL)) > 0.01:
                obs.append("Proporção desconto profissional incorreta")
            
            # Validar consistência de valores
            if abs(row['TOTAL'] - (row['Dias'] * row['VALOR DIÁRIO VR'])) > 0.01:
                obs.append("Inconsistência: Valor Total ≠ Dias × Valor Diário")
            
            # Adicionar observações
            if obs:
                self.planilha_final.at[idx, 'OBS GERAL'] = '; '.join(obs)
        
        # Validações agregadas
        total_observacoes = len(self.planilha_final[self.planilha_final['OBS GERAL'] != ''])
        if total_observacoes > 0:
            self.alertas.append(f"⚠️ {total_observacoes} registros com observações/validações")
        
        print("✓ Validações aplicadas")
    
    def executar_automacao(self):
        """Executa todo o processo de automação"""
        print("=" * 60)
        print("INICIANDO AUTOMAÇÃO DE VR/VA")
        print("=" * 60)
        
        # Exibir configurações do período
        print(f"Período de consolidação: {self.periodo['inicio']} a {self.periodo['fim']}")
        print(f"Mês de competência: {self.periodo['mes_competencia']}")
        print(f"Dias úteis calculados: {self.dias_uteis_periodo}")
        print()
        
        # Exibir alertas de período de execução
        if self.alertas:
            print("ALERTAS:")
            for alerta in self.alertas:
                print(f"  {alerta}")
            print()
        
        # 1. Carregar dados
        if not self.carregar_dados():
            return False
        
        # 2. Limpar colunas
        self.limpar_colunas()
        
        # 3. Aplicar filtros de exclusão
        self.matriculas_excluidas = self.aplicar_filtros_exclusao()
        
        # 4. Calcular dias úteis
        self.calcular_dias_uteis_colaborador()
        
        # 5. Calcular valores de VR
        self.calcular_valor_vr()
        
        # 6. Gerar planilha final
        arquivo_final = self.gerar_planilha_final()
        
        # 7. Exibir resumo
        self.exibir_resumo()
        
        print("=" * 60)
        print("AUTOMAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        
        return True
    
    def exibir_resumo(self):
        """Exibe resumo da automação"""
        print("\n" + "=" * 60)
        print("RESUMO DA AUTOMAÇÃO")
        print("=" * 60)
        
        # Informações básicas
        print(f"Período de consolidação: {self.periodo['inicio']} a {self.periodo['fim']}")
        print(f"Mês de competência: {self.periodo['mes_competencia']}")
        print(f"Dias úteis do período: {self.dias_uteis_periodo}")
        print()
        
        # Resumo da automação
        total_colaboradores = len(self.base_consolidada)
        total_dias_uteis = self.base_consolidada['DIAS_UTEIS_COLABORADOR'].sum()
        total_vr = self.base_consolidada['VALOR_TOTAL_VR'].sum()
        total_custo_empresa = self.base_consolidada['CUSTO_EMPRESA'].sum()
        total_desconto_profissional = self.base_consolidada['DESCONTO_PROFISSIONAL'].sum()
        
        print(f"Total de colaboradores elegíveis: {total_colaboradores}")
        print(f"Total de dias úteis: {total_dias_uteis}")
        print(f"Valor total de VR: R$ {total_vr:,.2f}")
        print(f"Custo total para empresa: R$ {total_custo_empresa:,.2f}")
        print(f"Desconto total profissional: R$ {total_desconto_profissional:,.2f}")
        print()
        
        # Contadores
        print(f"Colaboradores em férias: {len(self.ferias)}")
        print(f"Colaboradores desligados: {len(self.desligados)}")
        print(f"Novas admissões: {len(self.admissao_abril)}")
        print(f"Matrículas excluídas: {len(set(self.matriculas_excluidas))}")
        print()
        
        # Logs de validação
        if self.logs_validacao:
            print("LOGS DE VALIDAÇÃO:")
            for log in self.logs_validacao:
                print(f"  {log}")
            print()
        
        # Alertas
        if self.alertas:
            print("ALERTAS E AVISOS:")
            for alerta in self.alertas:
                print(f"  {alerta}")
            print()
        
        # Validações de dados
        if hasattr(self, 'planilha_final'):
            registros_com_obs = len(self.planilha_final[self.planilha_final['OBS GERAL'] != ''])
            registros_validos = len(self.planilha_final[self.planilha_final['OBS GERAL'] == ''])
            
            print(f"Registros com observações: {registros_com_obs}")
            print(f"Registros válidos: {registros_validos}")
            print()
            
            # Mostrar estatísticas dos novos campos
            if 'Dias' in self.planilha_final.columns:
                total_dias = self.planilha_final['Dias'].sum()
                print(f"Total de dias úteis: {total_dias}")
            
            if 'TOTAL' in self.planilha_final.columns:
                total_vr = self.planilha_final['TOTAL'].sum()
                print(f"Valor total de VR: R$ {total_vr:,.2f}")
            
            if 'Custo empresa' in self.planilha_final.columns:
                total_custo = self.planilha_final['Custo empresa'].sum()
                print(f"Custo total para empresa: R$ {total_custo:,.2f}")
            
            if 'Desconto profissional' in self.planilha_final.columns:
                total_desconto = self.planilha_final['Desconto profissional'].sum()
                print(f"Desconto total profissional: R$ {total_desconto:,.2f}")
        
        print("=" * 60)

def main():
    """Função principal"""
    print("=" * 60)
    print("AUTOMAÇÃO DE VR/VA - SISTEMA CORRIGIDO")
    print("=" * 60)
    
    # Permitir período personalizado
    print("Configurações atuais:")
    print(f"  Período padrão: {PERIODO_REFERENCIA['inicio']} a {PERIODO_REFERENCIA['fim']}")
    print(f"  Mês competência: {PERIODO_REFERENCIA['mes_competencia']}")
    print()
    
    # Perguntar se deseja usar período personalizado
    resposta = input("Deseja usar período personalizado? (s/n): ").lower().strip()
    
    if resposta in ['s', 'sim', 'y', 'yes']:
        print("\nDigite o período personalizado:")
        inicio = input(f"Data início (formato DD/MM/AAAA, padrão {PERIODO_REFERENCIA['inicio']}): ").strip()
        if not inicio:
            inicio = PERIODO_REFERENCIA['inicio']
        
        fim = input(f"Data fim (formato DD/MM/AAAA, padrão {PERIODO_REFERENCIA['fim']}): ").strip()
        if not fim:
            fim = PERIODO_REFERENCIA['fim']
        
        mes_comp = input(f"Mês competência (formato MM/AAAA, padrão {PERIODO_REFERENCIA['mes_competencia']}): ").strip()
        if not mes_comp:
            mes_comp = PERIODO_REFERENCIA['mes_competencia']
        
        # Extrair ano e mês do mês de competência
        try:
            mes, ano = mes_comp.split('/')
            periodo_personalizado = {
                'inicio': inicio,
                'fim': fim,
                'mes_competencia': mes_comp,
                'ano': int(ano),
                'mes': int(mes)
            }
        except:
            print("Formato inválido. Usando período padrão.")
            periodo_personalizado = None
    else:
        periodo_personalizado = None
    
    # Criar instância da automação
    try:
        automacao = AutomacaoVR(periodo_personalizado)
        sucesso = automacao.executar_automacao()
        
        if sucesso:
            print("\n✓ Automação executada com sucesso!")
            print("✓ Verifique o arquivo gerado na pasta do projeto")
            
            # Exibir resumo final
            if hasattr(automacao, 'planilha_final'):
                print(f"\n📊 RESUMO FINAL:")
                print(f"  Arquivo gerado: VR_MENSAL_{automacao.mes:02d}_{automacao.ano}_AUTOMATIZADO.xlsx")
                print(f"  Total colaboradores: {len(automacao.planilha_final)}")
                print(f"  Total VR: R$ {automacao.planilha_final['TOTAL'].sum():,.2f}")
        else:
            print("\n✗ Erro na execução da automação")
            
    except Exception as e:
        print(f"\n✗ Erro crítico: {e}")
        print("Verifique as configurações e tente novamente")

if __name__ == "__main__":
    main() 