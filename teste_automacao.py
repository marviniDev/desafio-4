#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para a automação de VR/VA
"""

import pandas as pd
import os
from automacao_vr import AutomacaoVR

def testar_carregamento_dados():
    """Testa o carregamento das planilhas"""
    print("Testando carregamento de dados...")
    
    automacao = AutomacaoVR()
    sucesso = automacao.carregar_dados()
    
    if sucesso:
        print("✓ Carregamento de dados: OK")
        return True
    else:
        print("✗ Carregamento de dados: FALHOU")
        return False

def testar_estrutura_planilhas():
    """Testa a estrutura das planilhas carregadas"""
    print("Testando estrutura das planilhas...")
    
    automacao = AutomacaoVR()
    automacao.carregar_dados()
    
    # Verificar se as colunas esperadas estão presentes
    colunas_esperadas = {
        'ativos': ['MATRICULA', 'EMPRESA', 'TITULO DO CARGO', 'DESC. SITUACAO', 'Sindicato'],
        'ferias': ['MATRICULA', 'DESC. SITUACAO', 'DIAS DE FÉRIAS'],
        'desligados': ['MATRICULA ', 'DATA DEMISSÃO', 'COMUNICADO DE DESLIGAMENTO'],
        'base_sindicato': ['ESTADO\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0', 'VALOR'],
        'base_dias_uteis': ['BASE DIAS UTEIS DE 15/04 a 15/05', 'Unnamed: 1']
    }
    
    for planilha, colunas in colunas_esperadas.items():
        if hasattr(automacao, planilha):
            df = getattr(automacao, planilha)
            colunas_presentes = [col for col in colunas if col in df.columns]
            if len(colunas_presentes) == len(colunas):
                print(f"✓ {planilha}: OK")
            else:
                print(f"✗ {planilha}: Colunas faltando")
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
    
    if dias_uteis.min() >= 0 and dias_uteis.max() <= automacao.dias_uteis_mes:
        print("✓ Cálculo de dias úteis: OK")
        print(f"  - Dias úteis mínimo: {dias_uteis.min()}")
        print(f"  - Dias úteis máximo: {dias_uteis.max()}")
        print(f"  - Total de dias úteis: {dias_uteis.sum()}")
        return True
    else:
        print("✗ Cálculo de dias úteis: Valores fora do esperado")
        return False

def testar_calculo_valor_vr():
    """Testa o cálculo dos valores de VR"""
    print("Testando cálculo de valores de VR...")
    
    automacao = AutomacaoVR()
    automacao.carregar_dados()
    automacao.limpar_colunas()
    automacao.aplicar_filtros_exclusao()
    automacao.calcular_dias_uteis_colaborador()
    automacao.calcular_valor_vr()
    
    # Verificar se os cálculos fazem sentido
    valores_vr = automacao.base_consolidada['VALOR_TOTAL_VR']
    custos_empresa = automacao.base_consolidada['CUSTO_EMPRESA']
    descontos_profissional = automacao.base_consolidada['DESCONTO_PROFISSIONAL']
    
    if valores_vr.min() >= 0 and custos_empresa.min() >= 0 and descontos_profissional.min() >= 0:
        print("✓ Cálculo de valores de VR: OK")
        print(f"  - Valor total VR: R$ {valores_vr.sum():,.2f}")
        print(f"  - Custo empresa: R$ {custos_empresa.sum():,.2f}")
        print(f"  - Desconto profissional: R$ {descontos_profissional.sum():,.2f}")
        return True
    else:
        print("✗ Cálculo de valores de VR: Valores negativos encontrados")
        return False

def executar_todos_testes():
    """Executa todos os testes"""
    print("=" * 60)
    print("EXECUTANDO TESTES DA AUTOMAÇÃO")
    print("=" * 60)
    
    testes = [
        testar_carregamento_dados,
        testar_estrutura_planilhas,
        testar_filtros_exclusao,
        testar_calculo_dias_uteis,
        testar_calculo_valor_vr
    ]
    
    resultados = []
    for teste in testes:
        try:
            resultado = teste()
            resultados.append(resultado)
        except Exception as e:
            print(f"✗ Erro no teste: {e}")
            resultados.append(False)
    
    # Resumo dos testes
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)
    
    testes_ok = sum(resultados)
    total_testes = len(resultados)
    
    print(f"Testes executados: {total_testes}")
    print(f"Testes aprovados: {testes_ok}")
    print(f"Testes reprovados: {total_testes - testes_ok}")
    
    if testes_ok == total_testes:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✓ A automação está funcionando corretamente")
    else:
        print(f"\n⚠️  {total_testes - testes_ok} TESTE(S) FALHARAM")
        print("✗ Verifique os erros acima antes de executar a automação completa")
    
    return testes_ok == total_testes

if __name__ == "__main__":
    executar_todos_testes() 