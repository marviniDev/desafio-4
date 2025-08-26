#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para a automação de VR/VA - VERSÃO CORRIGIDA
"""

import pandas as pd
import os
from datetime import datetime
from automacao_vr import AutomacaoVR
from config import *

def testar_configuracoes():
    """Testa as configurações do sistema"""
    print("Testando configurações...")
    
    # Verificar se as configurações estão definidas
    assert 'PERIODO_REFERENCIA' in globals(), "PERIODO_REFERENCIA não definido"
    assert 'EXECUCAO' in globals(), "EXECUCAO não definido"
    assert 'DIAS_UTEIS' in globals(), "DIAS_UTEIS não definido"
    assert 'TRATAMENTO_DADOS' in globals(), "TRATAMENTO_DADOS não definido"
    
    print("✓ Configurações: OK")
    return True

def testar_periodo_personalizado():
    """Testa a criação de período personalizado"""
    print("Testando período personalizado...")
    
    periodo_teste = {
        'inicio': '01/04/2025',
        'fim': '30/04/2025',
        'mes_competencia': '04/2025',
        'ano': 2025,
        'mes': 4
    }
    
    automacao = AutomacaoVR(periodo_teste)
    
    assert automacao.periodo == periodo_teste, "Período personalizado não foi aplicado"
    assert automacao.data_inicio.day == 1, "Data início incorreta"
    assert automacao.data_fim.day == 30, "Data fim incorreta"
    
    print("✓ Período personalizado: OK")
    return True

def testar_calculo_dias_uteis_periodo():
    """Testa o cálculo de dias úteis do período"""
    print("Testando cálculo de dias úteis do período...")
    
    automacao = AutomacaoVR()
    
    # Verificar se o cálculo considera feriados
    dias_uteis = automacao.calcular_dias_uteis_periodo()
    assert dias_uteis > 0, "Dias úteis deve ser maior que zero"
    assert dias_uteis <= 31, "Dias úteis não pode ser maior que 31"
    
    print(f"✓ Cálculo dias úteis: {dias_uteis} dias")
    return True

def testar_validacao_periodo_execucao():
    """Testa a validação do período de execução"""
    print("Testando validação do período de execução...")
    
    automacao = AutomacaoVR()
    
    # Verificar se os alertas são criados quando necessário
    hoje = datetime.now()
    dia_atual = hoje.day
    
    if dia_atual < EXECUCAO['periodo_execucao_inicio'] or dia_atual > EXECUCAO['periodo_execucao_fim']:
        assert len(automacao.alertas) > 0, "Alerta de período deve ser criado"
        print("✓ Alerta de período fora do recomendado: OK")
    else:
        print("✓ Execução no período recomendado: OK")
    
    return True

def testar_carregamento_dados():
    """Testa o carregamento das planilhas"""
    print("Testando carregamento de dados...")
    
    automacao = AutomacaoVR()
    sucesso = automacao.carregar_dados()
    
    if sucesso:
        print("✓ Carregamento de dados: OK")
        
        # Verificar se as bases foram carregadas
        assert hasattr(automacao, 'ativos'), "Base ativos não carregada"
        assert hasattr(automacao, 'ferias'), "Base férias não carregada"
        assert hasattr(automacao, 'desligados'), "Base desligados não carregada"
        assert hasattr(automacao, 'base_sindicato'), "Base sindicato não carregada"
        assert hasattr(automacao, 'base_dias_uteis'), "Base dias úteis não carregada"
        
        return True
    else:
        print("✗ Carregamento de dados: FALHOU")
        return False

def testar_estrutura_planilhas():
    """Testa a estrutura das planilhas carregadas"""
    print("Testando estrutura das planilhas...")
    
    automacao = AutomacaoVR()
    automacao.carregar_dados()
    
    # Verificar se as planilhas foram carregadas
    planilhas_essenciais = ['ativos', 'ferias', 'desligados', 'base_sindicato', 'base_dias_uteis']
    
    for planilha in planilhas_essenciais:
        if hasattr(automacao, planilha):
            df = getattr(automacao, planilha)
            if len(df.columns) >= 2:  # Pelo menos 2 colunas
                print(f"✓ {planilha}: OK ({len(df.columns)} colunas)")
            else:
                print(f"✗ {planilha}: Poucas colunas ({len(df.columns)})")
                return False
        else:
            print(f"✗ {planilha}: Planilha não encontrada")
            return False
    
    print("✓ Estrutura das planilhas: OK")
    return True

def testar_filtros_exclusao():
    """Testa os filtros de exclusão"""
    print("Testando filtros de exclusão...")
    
    automacao = AutomacaoVR()
    automacao.carregar_dados()
    automacao.limpar_colunas()
    
    # Aplicar filtros
    matriculas_excluidas = automacao.aplicar_filtros_exclusao()
    
    if len(automacao.ativos_filtrados) < len(automacao.ativos):
        print("✓ Filtros de exclusão: OK")
        print(f"  - Colaboradores originais: {len(automacao.ativos)}")
        print(f"  - Colaboradores após filtros: {len(automacao.ativos_filtrados)}")
        print(f"  - Matrículas excluídas: {len(set(matriculas_excluidas))}")
        return True
    else:
        print("✗ Filtros de exclusão: Nenhuma exclusão aplicada")
        return False

def testar_calculo_dias_uteis():
    """Testa o cálculo de dias úteis"""
    print("Testando cálculo de dias úteis...")
    
    automacao = AutomacaoVR()
    automacao.carregar_dados()
    automacao.limpar_colunas()
    automacao.aplicar_filtros_exclusao()
    automacao.calcular_dias_uteis_colaborador()
    
    # Verificar se os cálculos fazem sentido
    dias_uteis = automacao.base_consolidada['DIAS_UTEIS_COLABORADOR']
    
    if dias_uteis.min() >= 0 and dias_uteis.max() <= automacao.dias_uteis_periodo:
        print("✓ Cálculo de dias úteis: OK")
        print(f"  - Dias úteis mínimo: {dias_uteis.min()}")
        print(f"  - Dias úteis máximo: {dias_uteis.max()}")
        print(f"  - Total de dias úteis: {dias_uteis.sum()}")
        return True
    else:
        print("✗ Cálculo de dias úteis: Valores fora do esperado")
        return False

def testar_calculo_valores():
    """Testa o cálculo de valores de VR"""
    print("Testando cálculo de valores...")
    
    automacao = AutomacaoVR()
    automacao.carregar_dados()
    automacao.limpar_colunas()
    automacao.aplicar_filtros_exclusao()
    automacao.calcular_dias_uteis_colaborador()
    automacao.calcular_valor_vr()
    
    # Verificar se os valores foram calculados
    if 'VALOR_TOTAL_VR' in automacao.base_consolidada.columns:
        valores = automacao.base_consolidada['VALOR_TOTAL_VR']
        if valores.sum() > 0:
            print("✓ Cálculo de valores: OK")
            print(f"  - Total VR: R$ {valores.sum():,.2f}")
            print(f"  - Média por colaborador: R$ {valores.mean():,.2f}")
            return True
        else:
            print("✗ Cálculo de valores: Total zero")
            return False
    else:
        print("✗ Cálculo de valores: Coluna não encontrada")
        return False

def testar_validacoes():
    """Testa as validações do sistema"""
    print("Testando validações...")
    
    automacao = AutomacaoVR()
    automacao.carregar_dados()
    automacao.limpar_colunas()
    automacao.aplicar_filtros_exclusao()
    automacao.calcular_dias_uteis_colaborador()
    automacao.calcular_valor_vr()
    automacao.gerar_planilha_final()
    
    # Verificar se as validações foram aplicadas
    if hasattr(automacao, 'planilha_final'):
        planilha = automacao.planilha_final
        
        # Verificar se há coluna de observações
        if 'OBS GERAL' in planilha.columns:
            obs_nao_vazias = planilha[planilha['OBS GERAL'] != '']
            print(f"✓ Validações aplicadas: {len(obs_nao_vazias)} registros com observações")
            return True
        else:
            print("✗ Validações: Coluna de observações não encontrada")
            return False
    else:
        print("✗ Validações: Planilha final não gerada")
        return False

def testar_logs_e_alertas():
    """Testa os logs e alertas do sistema"""
    print("Testando logs e alertas...")
    
    automacao = AutomacaoVR()
    
    # Verificar se os logs são criados
    assert hasattr(automacao, 'logs_validacao'), "Logs de validação não criados"
    assert hasattr(automacao, 'alertas'), "Alertas não criados"
    
    # Verificar se os logs são preenchidos durante a execução
    automacao.carregar_dados()
    automacao.validar_consistencia_temporal()
    
    if len(automacao.logs_validacao) > 0:
        print("✓ Logs de validação: OK")
        print(f"  - Total de logs: {len(automacao.logs_validacao)}")
    else:
        print("⚠️ Logs de validação: Nenhum log criado")
    
    if len(automacao.alertas) > 0:
        print("✓ Alertas: OK")
        print(f"  - Total de alertas: {len(automacao.alertas)}")
    else:
        print("✓ Alertas: Nenhum alerta (OK)")
    
    return True

def executar_todos_testes():
    """Executa todos os testes"""
    print("=" * 60)
    print("EXECUTANDO TESTES DA AUTOMAÇÃO CORRIGIDA")
    print("=" * 60)
    
    testes = [
        testar_configuracoes,
        testar_periodo_personalizado,
        testar_calculo_dias_uteis_periodo,
        testar_validacao_periodo_execucao,
        testar_carregamento_dados,
        testar_estrutura_planilhas,
        testar_filtros_exclusao,
        testar_calculo_dias_uteis,
        testar_calculo_valores,
        testar_validacoes,
        testar_logs_e_alertas
    ]
    
    resultados = []
    
    for teste in testes:
        try:
            resultado = teste()
            resultados.append(resultado)
        except Exception as e:
            print(f"✗ Erro no teste {teste.__name__}: {e}")
            resultados.append(False)
    
    # Resumo dos testes
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)
    
    total_testes = len(testes)
    testes_ok = sum(resultados)
    testes_falharam = total_testes - testes_ok
    
    print(f"Total de testes: {total_testes}")
    print(f"Testes OK: {testes_ok}")
    print(f"Testes falharam: {testes_falharam}")
    
    if testes_ok == total_testes:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Sistema corrigido e funcionando perfeitamente")
    else:
        print(f"\n⚠️ {testes_falharam} TESTE(S) FALHARAM")
        print("🔧 Verifique os erros acima")
    
    return testes_ok == total_testes

if __name__ == "__main__":
    executar_todos_testes() 