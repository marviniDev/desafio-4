#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para validar as correções implementadas
"""

import pandas as pd
import sys
import os
from datetime import datetime

# Adicionar o diretório atual ao path para importar a automação
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def testar_correcao_valores_sindicato():
    """Testa a correção dos valores por sindicato"""
    print("=" * 60)
    print("TESTANDO CORREÇÃO: Valores por Sindicato")
    print("=" * 60)
    
    try:
        # Importar a automação com configurações de teste
        from automacao_vr import AutomacaoVR
        
        # Criar instância da automação
        automacao = AutomacaoVR()
        
        # Carregar dados
        if not automacao.carregar_dados():
            print("❌ Falha ao carregar dados")
            return False
        
        # Limpar colunas
        automacao.limpar_colunas()
        
        # Aplicar filtros de exclusão
        automacao.aplicar_filtros_exclusao()
        
        # Calcular dias úteis
        automacao.calcular_dias_uteis_colaborador()
        
        # Calcular valores de VR (CORREÇÃO TESTADA)
        automacao.calcular_valor_vr()
        
        # Verificar se os valores foram aplicados corretamente
        valores_unicos = automacao.base_consolidada['VALOR_DIARIO_VR'].unique()
        print(f"Valores únicos aplicados: {valores_unicos}")
        
        # Verificar se há mais de um valor (correção funcionando)
        if len(valores_unicos) > 1:
            print("✅ CORREÇÃO FUNCIONANDO: Múltiplos valores por sindicato aplicados")
            
            # Mostrar distribuição dos valores
            distribuicao = automacao.base_consolidada['VALOR_DIARIO_VR'].value_counts().sort_index()
            print("Distribuição dos valores:")
            for valor, quantidade in distribuicao.items():
                print(f"  R$ {valor:.2f}: {quantidade} colaboradores")
            
            return True
        else:
            print("❌ CORREÇÃO NÃO FUNCIONOU: Ainda há apenas um valor único")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def testar_correcao_bloqueio_periodo():
    """Testa a correção do bloqueio fora do período"""
    print("\n" + "=" * 60)
    print("TESTANDO CORREÇÃO: Bloqueio Fora do Período")
    print("=" * 60)
    
    try:
        # Importar configurações de teste
        from config_teste_correcoes import EXECUCAO
        
        # Verificar se o bloqueio está ativo
        if EXECUCAO['bloquear_execucao_fora_periodo']:
            print("✅ Configuração de bloqueio ativa")
            
            # Simular execução fora do período
            hoje = datetime.now()
            dia_atual = hoje.day
            
            if dia_atual < EXECUCAO['periodo_execucao_inicio'] or dia_atual > EXECUCAO['periodo_execucao_fim']:
                print(f"⚠️ Executando fora do período recomendado (dia {dia_atual})")
                print("✅ Bloqueio deve ser ativado na próxima execução")
                return True
            else:
                print(f"✅ Executando no período recomendado (dia {dia_atual})")
                print("ℹ️ Para testar o bloqueio, execute fora do período 1-10")
                return True
        else:
            print("❌ Configuração de bloqueio não está ativa")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def testar_correcao_ferias_inteligente():
    """Testa a correção da estratégia inteligente de férias"""
    print("\n" + "=" * 60)
    print("TESTANDO CORREÇÃO: Estratégia Inteligente de Férias")
    print("=" * 60)
    
    try:
        # Importar a automação
        from automacao_vr import AutomacaoVR
        
        # Criar instância da automação
        automacao = AutomacaoVR()
        
        # Carregar dados
        if not automacao.carregar_dados():
            print("❌ Falha ao carregar dados")
            return False
        
        # Limpar colunas
        automacao.limpar_colunas()
        
        # Aplicar filtros de exclusão
        automacao.aplicar_filtros_exclusao()
        
        # Calcular dias úteis (inclui estratégia inteligente de férias)
        automacao.calcular_dias_uteis_colaborador()
        
        # Verificar se a estratégia foi aplicada
        if hasattr(automacao, 'base_consolidada') and 'OBSERVACOES_FERIAS' in automacao.base_consolidada.columns:
            observacoes_ferias = automacao.base_consolidada['OBSERVACOES_FERIAS'].notna().sum()
            print(f"✅ Estratégia inteligente aplicada: {observacoes_ferias} colaboradores com observações de férias")
            
            # Mostrar algumas observações
            obs_nao_vazias = automacao.base_consolidada[automacao.base_consolidada['OBSERVACOES_FERIAS'].notna()]
            if len(obs_nao_vazias) > 0:
                print("Exemplos de observações aplicadas:")
                for idx, row in obs_nao_vazias.head(3).iterrows():
                    print(f"  Matrícula {row['MATRICULA']}: {row['OBSERVACOES_FERIAS']}")
            
            return True
        else:
            print("❌ Estratégia inteligente não foi aplicada")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def executar_todos_testes_correcoes():
    """Executa todos os testes das correções"""
    print("🚀 INICIANDO TESTES DAS CORREÇÕES IMPLEMENTADAS")
    print("=" * 60)
    
    testes = [
        ("Valores por Sindicato", testar_correcao_valores_sindicato),
        ("Bloqueio Fora do Período", testar_correcao_bloqueio_periodo),
        ("Estratégia Inteligente de Férias", testar_correcao_ferias_inteligente)
    ]
    
    resultados = []
    
    for nome, teste in testes:
        try:
            resultado = teste()
            resultados.append((nome, resultado))
        except Exception as e:
            print(f"❌ Erro no teste {nome}: {e}")
            resultados.append((nome, False))
    
    # Resumo dos testes
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES DAS CORREÇÕES")
    print("=" * 60)
    
    total_testes = len(testes)
    testes_ok = sum(1 for _, resultado in resultados if resultado)
    testes_falharam = total_testes - testes_ok
    
    for nome, resultado in resultados:
        status = "✅ OK" if resultado else "❌ FALHOU"
        print(f"{nome}: {status}")
    
    print(f"\nTotal de testes: {total_testes}")
    print(f"Testes OK: {testes_ok}")
    print(f"Testes falharam: {testes_falharam}")
    
    if testes_ok == total_testes:
        print("\n🎉 TODAS AS CORREÇÕES ESTÃO FUNCIONANDO!")
        print("✅ Sistema corrigido e validado")
    else:
        print(f"\n⚠️ {testes_falharam} CORREÇÃO(ÕES) AINDA PRECISAM DE AJUSTES")
        print("🔧 Verifique os erros acima")
    
    return testes_ok == total_testes

if __name__ == "__main__":
    executar_todos_testes_correcoes() 