#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automação da compra de VR/VA
Sistema para automatizar o processo mensal de compra de Vale Refeição
"""

import pandas as pd
import numpy as np
from datetime import datetime, date
import warnings
warnings.filterwarnings('ignore')

class AutomacaoVR:
    def __init__(self):
        self.mes_referencia = "05/2025"
        self.ano = 2025
        self.mes = 5
        self.dias_uteis_mes = 22  # Maio 2025 tem 22 dias úteis
        
    def carregar_dados(self):
        """Carrega todas as planilhas de dados"""
        print("Carregando dados das planilhas...")
        
        try:
            # Carregar planilhas principais
            self.ativos = pd.read_excel('ATIVOS.xlsx')
            self.ferias = pd.read_excel('FÉRIAS.xlsx')
            self.desligados = pd.read_excel('DESLIGADOS.xlsx')
            self.estagio = pd.read_excel('ESTÁGIO.xlsx')
            self.aprendiz = pd.read_excel('APRENDIZ.xlsx')
            self.afastamentos = pd.read_excel('AFASTAMENTOS.xlsx')
            self.exterior = pd.read_excel('EXTERIOR.xlsx')
            self.admissao_abril = pd.read_excel('ADMISSÃO ABRIL.xlsx')
            self.base_sindicato = pd.read_excel('Base sindicato x valor.xlsx')
            self.base_dias_uteis = pd.read_excel('Base dias uteis.xlsx')
            
            print("✓ Dados carregados com sucesso")
            return True
            
        except Exception as e:
            print(f"✗ Erro ao carregar dados: {e}")
            return False
    
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
        
        # 3. Profissionais no exterior
        if 'MATRICULA' in self.exterior.columns:
            matriculas_excluir.update(self.exterior['MATRICULA'].astype(str).tolist())
        
        # 4. Afastados (licença maternidade, etc.)
        if 'MATRICULA' in self.afastamentos.columns:
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
        self.base_consolidada['DIAS_UTEIS_COLABORADOR'] = self.dias_uteis_mes
        
        # Ajustar para férias
        self.base_consolidada['DIAS_UTEIS_COLABORADOR'] -= self.base_consolidada['DIAS DE FÉRIAS']
        
        # Ajustar para desligamentos
        def ajustar_desligamento(row):
            if pd.notna(row['DATA DEMISSÃO']):
                data_desligamento = pd.to_datetime(row['DATA DEMISSÃO'])
                if data_desligamento.month == self.mes and data_desligamento.year == self.ano:
                    if pd.notna(row['COMUNICADO DE DESLIGAMENTO']) and row['COMUNICADO DE DESLIGAMENTO'] == 'OK':
                        if data_desligamento.day <= 15:
                            return 0  # Não considerar para pagamento
                        else:
                            # Calcular proporcional
                            dias_ate_desligamento = data_desligamento.day
                            return max(0, dias_ate_desligamento - 15)
            return row['DIAS_UTEIS_COLABORADOR']
        
        self.base_consolidada['DIAS_UTEIS_COLABORADOR'] = self.base_consolidada.apply(ajustar_desligamento, axis=1)
        
        # Garantir que não há valores negativos
        self.base_consolidada['DIAS_UTEIS_COLABORADOR'] = self.base_consolidada['DIAS_UTEIS_COLABORADOR'].clip(lower=0)
        
        print("✓ Dias úteis calculados para cada colaborador")
    
    def calcular_valor_vr(self):
        """Calcula o valor de VR para cada colaborador"""
        print("Calculando valores de VR...")
        
        # Mapear valores por sindicato
        # Criar dicionário de mapeamento
        mapeamento_sindicato = {}
        
        # Mapear base sindicato x valor
        for _, row in self.base_sindicato.iterrows():
            estado = row['ESTADO'].strip()
            valor = row['VALOR']
            mapeamento_sindicato[estado] = valor
        
        # Mapear base dias úteis
        for _, row in self.base_dias_uteis.iterrows():
            sindicato = row['SINDICATO'].strip()
            dias_uteis = row['DIAS_UTEIS']
            # Encontrar estado correspondente
            for estado, valor in mapeamento_sindicato.items():
                if estado.lower() in sindicato.lower():
                    mapeamento_sindicato[sindicato] = valor
                    break
        
        # Aplicar valores por sindicato
        def obter_valor_sindicato(sindicato):
            if pd.isna(sindicato):
                return 35.0  # Valor padrão
            
            sindicato_str = str(sindicato).strip()
            
            # Buscar por correspondência parcial
            for sind, valor in mapeamento_sindicato.items():
                if sind.lower() in sindicato_str.lower() or sindicato_str.lower() in sind.lower():
                    return valor
            
            return 35.0  # Valor padrão se não encontrar
        
        self.base_consolidada['VALOR_DIARIO_VR'] = self.base_consolidada['Sindicato'].apply(obter_valor_sindicato)
        
        # Calcular valor total de VR
        self.base_consolidada['VALOR_TOTAL_VR'] = (
            self.base_consolidada['DIAS_UTEIS_COLABORADOR'] * 
            self.base_consolidada['VALOR_DIARIO_VR']
        )
        
        # Calcular custo empresa (80%) e desconto profissional (20%)
        self.base_consolidada['CUSTO_EMPRESA'] = self.base_consolidada['VALOR_TOTAL_VR'] * 0.8
        self.base_consolidada['DESCONTO_PROFISSIONAL'] = self.base_consolidada['VALOR_TOTAL_VR'] * 0.2
        
        print("✓ Valores de VR calculados")
    
    def gerar_planilha_final(self):
        """Gera a planilha final para envio à operadora"""
        print("Gerando planilha final...")
        
        # Selecionar colunas para a planilha final
        colunas_finais = [
            'MATRICULA',
            'Admissão',
            'DATA DEMISSÃO',
            'DIAS_UTEIS_COLABORADOR',
            'VALOR_DIARIO_VR',
            'VALOR_TOTAL_VR',
            'CUSTO_EMPRESA',
            'DESCONTO_PROFISSIONAL'
        ]
        
        # Criar planilha final
        self.planilha_final = self.base_consolidada[colunas_finais].copy()
        
        # Renomear colunas para o formato esperado
        self.planilha_final.columns = [
            'Matricula',
            'Admissão',
            'Data Desligamento',
            'Dias Úteis',
            'Valor Diário VR',
            'Valor Total VR',
            'Custo Empresa',
            'Desconto Profissional'
        ]
        
        # Adicionar coluna de observações
        self.planilha_final['OBS GERAL'] = ''
        
        # Aplicar validações
        self.aplicar_validacoes()
        
        # Salvar planilha
        nome_arquivo = f"VR_MENSAL_{self.mes:02d}_{self.ano}_AUTOMATIZADO.xlsx"
        
        with pd.ExcelWriter(nome_arquivo, engine='openpyxl') as writer:
            self.planilha_final.to_excel(writer, sheet_name='VR Mensal', index=False)
            
            # Criar aba de validações
            validacoes = pd.DataFrame({
                'Validações': [
                    'Total de colaboradores',
                    'Total de dias úteis',
                    'Valor total VR',
                    'Custo total empresa',
                    'Desconto total profissional',
                    'Colaboradores com férias',
                    'Colaboradores desligados',
                    'Colaboradores admitidos no mês'
                ],
                'Check': [
                    len(self.planilha_final),
                    self.planilha_final['Dias Úteis'].sum(),
                    self.planilha_final['Valor Total VR'].sum(),
                    self.planilha_final['Custo Empresa'].sum(),
                    self.planilha_final['Desconto Profissional'].sum(),
                    len(self.ferias),
                    len(self.desligados),
                    len(self.admissao_abril)
                ]
            })
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
            
            # Validar dias úteis
            if row['Dias Úteis'] < 0 or row['Dias Úteis'] > self.dias_uteis_mes:
                obs.append(f"Dias úteis inválidos: {row['Dias Úteis']}")
            
            # Validar valores
            if row['Valor Total VR'] < 0:
                obs.append("Valor total VR negativo")
            
            if row['Custo Empresa'] < 0:
                obs.append("Custo empresa negativo")
            
            if row['Desconto Profissional'] < 0:
                obs.append("Desconto profissional negativo")
            
            # Validar proporção 80/20
            if abs(row['Custo Empresa'] - (row['Valor Total VR'] * 0.8)) > 0.01:
                obs.append("Proporção empresa/profissional incorreta")
            
            # Adicionar observações
            if obs:
                self.planilha_final.at[idx, 'OBS GERAL'] = '; '.join(obs)
        
        print("✓ Validações aplicadas")
    
    def executar_automacao(self):
        """Executa todo o processo de automação"""
        print("=" * 60)
        print("INICIANDO AUTOMAÇÃO DE VR/VA")
        print("=" * 60)
        
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
        print(f"Colaboradores em férias: {len(self.ferias)}")
        print(f"Colaboradores desligados: {len(self.desligados)}")
        print(f"Novas admissões: {len(self.admissao_abril)}")
        print(f"Matrículas excluídas: {len(set(self.matriculas_excluidas))}")

def main():
    """Função principal"""
    automacao = AutomacaoVR()
    sucesso = automacao.executar_automacao()
    
    if sucesso:
        print("\n✓ Automação executada com sucesso!")
        print("✓ Verifique o arquivo gerado na pasta do projeto")
    else:
        print("\n✗ Erro na execução da automação")

if __name__ == "__main__":
    main() 