#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de demonstração da automação de VR/VA
"""

import pandas as pd
from automacao_vr import AutomacaoVR

def demonstrar_carregamento():
    """Demonstra o carregamento das planilhas"""
    print("🔍 DEMONSTRAÇÃO: Carregamento de Dados")
    print("=" * 50)
    
    automacao = AutomacaoVR()
    sucesso = automacao.carregar_dados()
    
    if sucesso:
        print("✓ Planilhas carregadas:")
        print(f"  - ATIVOS: {len(automacao.ativos)} colaboradores")
        print(f"  - FÉRIAS: {len(automacao.ferias)} registros")
        print(f"  - DESLIGADOS: {len(automacao.desligados)} registros")
        print(f"  - ESTÁGIO: {len(automacao.estagio)} registros")
        print(f"  - APRENDIZ: {len(automacao.aprendiz)} registros")
        print(f"  - AFASTAMENTOS: {len(automacao.afastamentos)} registros")
        print(f"  - EXTERIOR: {len(automacao.exterior)} registros")
        print(f"  - ADMISSÃO ABRIL: {len(automacao.admissao_abril)} registros")
        print(f"  - BASE SINDICATO: {len(automacao.base_sindicato)} registros")
        print(f"  - BASE DIAS ÚTEIS: {len(automacao.base_dias_uteis)} registros")
    
    return automacao

def demonstrar_filtros(automacao):
    """Demonstra a aplicação dos filtros de exclusão"""
    print("\n🔍 DEMONSTRAÇÃO: Filtros de Exclusão")
    print("=" * 50)
    
    print("Aplicando filtros de exclusão...")
    automacao.limpar_colunas()
    matriculas_excluidas = automacao.aplicar_filtros_exclusao()
    
    print(f"✓ Colaboradores originais: {len(automacao.ativos)}")
    print(f"✓ Colaboradores após filtros: {len(automacao.ativos_filtrados)}")
    print(f"✓ Matrículas excluídas: {len(set(matriculas_excluidas))}")
    
    # Mostrar alguns exemplos de exclusões
    print("\n📋 Exemplos de exclusões:")
    if len(automacao.estagio) > 0:
        print(f"  - Estagiários: {len(automacao.estagio)}")
    if len(automacao.aprendiz) > 0:
        print(f"  - Aprendizes: {len(automacao.aprendiz)}")
    if len(automacao.exterior) > 0:
        print(f"  - Profissionais no exterior: {len(automacao.exterior)}")
    if len(automacao.afastamentos) > 0:
        print(f"  - Afastados: {len(automacao.afastamentos)}")

def demonstrar_calculo_dias(automacao):
    """Demonstra o cálculo de dias úteis"""
    print("\n🔍 DEMONSTRAÇÃO: Cálculo de Dias Úteis")
    print("=" * 50)
    
    print("Calculando dias úteis por colaborador...")
    automacao.calcular_dias_uteis_colaborador()
    
    dias_uteis = automacao.base_consolidada['DIAS_UTEIS_COLABORADOR']
    
    print(f"✓ Dias úteis do mês: {automacao.dias_uteis_mes}")
    print(f"✓ Dias úteis mínimo: {dias_uteis.min()}")
    print(f"✓ Dias úteis máximo: {dias_uteis.max()}")
    print(f"✓ Total de dias úteis: {dias_uteis.sum():,.0f}")
    
    # Mostrar distribuição de dias úteis
    print("\n📊 Distribuição de dias úteis:")
    for i in range(0, automacao.dias_uteis_mes + 1, 5):
        count = len(dias_uteis[dias_uteis == i])
        if count > 0:
            print(f"  - {i} dias: {count} colaboradores")

def demonstrar_calculo_vr(automacao):
    """Demonstra o cálculo dos valores de VR"""
    print("\n🔍 DEMONSTRAÇÃO: Cálculo de Valores de VR")
    print("=" * 50)
    
    print("Calculando valores de VR...")
    automacao.calcular_valor_vr()
    
    valores_vr = automacao.base_consolidada['VALOR_TOTAL_VR']
    custos_empresa = automacao.base_consolidada['CUSTO_EMPRESA']
    descontos_profissional = automacao.base_consolidada['DESCONTO_PROFISSIONAL']
    
    print(f"✓ Valor total de VR: R$ {valores_vr.sum():,.2f}")
    print(f"✓ Custo total para empresa: R$ {custos_empresa.sum():,.2f}")
    print(f"✓ Desconto total profissional: R$ {descontos_profissional.sum():,.2f}")
    
    # Mostrar valores por faixa
    print("\n📊 Distribuição de valores de VR:")
    faixas = [(0, 500), (500, 1000), (1000, 1500), (1500, 2000), (2000, float('inf'))]
    for inicio, fim in faixas:
        if fim == float('inf'):
            count = len(valores_vr[valores_vr >= inicio])
            print(f"  - R$ {inicio:,.0f}+: {count} colaboradores")
        else:
            count = len(valores_vr[(valores_vr >= inicio) & (valores_vr < fim)])
            print(f"  - R$ {inicio:,.0f} - R$ {fim:,.0f}: {count} colaboradores")

def demonstrar_planilha_final(automacao):
    """Demonstra a geração da planilha final"""
    print("\n🔍 DEMONSTRAÇÃO: Geração da Planilha Final")
    print("=" * 50)
    
    print("Gerando planilha final...")
    arquivo_final = automacao.gerar_planilha_final()
    
    print(f"✓ Planilha gerada: {arquivo_final}")
    
    # Mostrar estrutura da planilha final
    print("\n📋 Estrutura da planilha final:")
    for col in automacao.planilha_final.columns:
        print(f"  - {col}")
    
    # Mostrar algumas linhas de exemplo
    print("\n📊 Exemplos de registros:")
    print(automacao.planilha_final.head(3).to_string(index=False))

def executar_demonstracao_completa():
    """Executa a demonstração completa da automação"""
    print("🎯 DEMONSTRAÇÃO COMPLETA DA AUTOMAÇÃO DE VR/VA")
    print("=" * 60)
    
    try:
        # 1. Carregamento de dados
        automacao = demonstrar_carregamento()
        
        # 2. Filtros de exclusão
        demonstrar_filtros(automacao)
        
        # 3. Cálculo de dias úteis
        demonstrar_calculo_dias(automacao)
        
        # 4. Cálculo de valores de VR
        demonstrar_calculo_vr(automacao)
        
        # 5. Geração da planilha final
        demonstrar_planilha_final(automacao)
        
        print("\n" + "=" * 60)
        print("🎉 DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print("✓ A automação está funcionando perfeitamente")
        print("✓ Todos os cálculos foram realizados")
        print("✓ Planilha final foi gerada")
        print("✓ Sistema pronto para uso em produção")
        
    except Exception as e:
        print(f"\n❌ Erro durante a demonstração: {e}")
        print("Verifique os logs acima para identificar o problema")

if __name__ == "__main__":
    executar_demonstracao_completa() 