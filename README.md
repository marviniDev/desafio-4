# Automação da Compra de VR/VA

## Objetivo
Automatizar o processo mensal de compra de VR (Vale Refeição), garantindo que cada colaborador receba o valor correto, considerando ausências, férias e datas de admissão ou desligamento e calendário de feriados.

## Descrição do Problema
Hoje, o cálculo da quantidade de dias para compra de benefícios é feito manualmente a partir de planilhas. Esse processo envolve:
- Conferência de datas de início e fim do contrato no mês
- Exclusão de colaboradores em férias (parcial ou integral por regra de sindicato)
- Ajustes para datas quebradas (ex.: admissões no meio do mês e desligamentos)
- Cálculo do número exato de dias a serem comprados para cada pessoa
- Geração de um layout de compra a ser enviado para o fornecedor
- Considerar as regras vigentes decorrentes dos acordos coletivos de cada um dos sindicatos

## Funcionalidades Implementadas

### ✅ Base Única Consolidada
- Reunião e consolidação de informações de 5 bases separadas
- Integração de dados de Ativos, Férias, Desligados, Base cadastral (admitidos do mês), Base sindicato x valor e Dias úteis por colaborador

### ✅ Tratamento de Exclusões
- Remoção de profissionais com cargo de diretores, estagiários e aprendizes
- Exclusão de afastados em geral (ex.: licença maternidade)
- Remoção de profissionais que atuam no exterior
- Filtros baseados na matrícula das planilhas

### ✅ Validação e Correção
- Validação de datas inconsistentes ou "quebradas"
- Verificação de campos faltantes
- Validação de férias mal preenchidas
- Aplicação correta de feriados estaduais e municipais

### ✅ Cálculo Automatizado do Benefício
- Quantidade de dias úteis por colaborador
- Consideração dos dias úteis de cada sindicato
- Ajustes para férias, afastamentos e data de desligamento
- Regra de desligamento: OK até dia 15 = não considerar, após dia 15 = proporcional
- Cálculo do valor total de VR conforme valor de cada sindicato

### ✅ Entrega Final
- Geração de planilha para envio à operadora
- Inclusão de valor de VR a ser concedido
- Cálculo de valor a ser pago pela empresa (80%) e profissional (20%)
- Validações conforme aba "validações" da planilha modelo

## Arquivos do Sistema

### 📁 Arquivos Principais
- `automacao_vr.py` - Sistema principal de automação
- `config.py` - Configurações e parâmetros do sistema
- `teste_automacao.py` - Script de testes para validação
- `requirements.txt` - Dependências Python necessárias

### 📊 Planilhas de Entrada
- `ATIVOS.xlsx` - Base de colaboradores ativos
- `FÉRIAS.xlsx` - Informações de férias
- `DESLIGADOS.xlsx` - Colaboradores desligados
- `ESTÁGIO.xlsx` - Estagiários
- `APRENDIZ.xlsx` - Aprendizes
- `AFASTAMENTOS.xlsx` - Afastamentos e licenças
- `EXTERIOR.xlsx` - Profissionais no exterior
- `ADMISSÃO ABRIL.xlsx` - Novas admissões
- `Base sindicato x valor.xlsx` - Valores por sindicato
- `Base dias uteis.xlsx` - Dias úteis por sindicato

### 📋 Planilha Modelo
- `VR MENSAL 05.2025.xlsx` - Modelo de saída com validações

## Instalação e Configuração

### 1. Pré-requisitos
- Python 3.8 ou superior
- Sistema operacional: Linux, Windows ou macOS

### 2. Instalação das Dependências
```bash
# Instalar via apt (Ubuntu/Debian)
sudo apt update
sudo apt install -y python3-pandas python3-openpyxl python3-xlrd

# Ou instalar via pip (se disponível)
pip3 install -r requirements.txt
```

### 3. Verificação da Instalação
```bash
python3 teste_automacao.py
```

## Como Usar

### 1. Execução dos Testes
```bash
python3 teste_automacao.py
```
Este comando executa uma bateria de testes para verificar se todas as funcionalidades estão funcionando corretamente.

### 2. Execução da Automação Completa
```bash
python3 automacao_vr.py
```
Este comando executa todo o processo de automação e gera a planilha final.

### 3. Execução Passo a Passo
```python
from automacao_vr import AutomacaoVR

# Criar instância da automação
automacao = AutomacaoVR()

# Executar passo a passo
automacao.carregar_dados()
automacao.limpar_colunas()
automacao.aplicar_filtros_exclusao()
automacao.calcular_dias_uteis_colaborador()
automacao.calcular_valor_vr()
arquivo_final = automacao.gerar_planilha_final()
```

## Configurações

### Arquivo `config.py`
- **MES_REFERENCIA**: Mês e ano de referência para o cálculo
- **DIAS_UTEIS_PADRAO**: Número padrão de dias úteis no mês
- **VALOR_VR_PADRAO**: Valor padrão do VR quando não especificado
- **PROPORCAO_EMPRESA**: Percentual pago pela empresa (padrão: 80%)
- **PROPORCAO_PROFISSIONAL**: Percentual descontado do profissional (padrão: 20%)
- **DIA_LIMITE_DESLIGAMENTO**: Dia limite para considerar desligamentos (padrão: 15)

## Regras de Negócio Implementadas

### 🏢 Exclusões Automáticas
- Estagiários e aprendizes
- Diretores e cargos executivos
- Profissionais afastados (licença maternidade, etc.)
- Colaboradores no exterior

### 📅 Cálculo de Dias Úteis
- Base: dias úteis do mês por sindicato
- Dedução: dias de férias
- Ajuste: desligamentos (proporcional após dia 15)
- Ajuste: admissões no meio do mês

### 💰 Cálculo de Valores
- Valor diário conforme sindicato
- Total = dias úteis × valor diário
- Empresa: 80% do valor total
- Profissional: 20% do valor total

### ✅ Validações
- Matrículas válidas
- Dias úteis dentro do limite
- Valores não negativos
- Proporções corretas (80/20)
- Consistência de dados

## Saída do Sistema

### 📊 Planilha Final
A automação gera uma planilha Excel com duas abas:

1. **VR Mensal**: Dados principais para envio à operadora
   - Matrícula
   - Data de admissão
   - Data de desligamento
   - Dias úteis
   - Valor diário VR
   - Valor total VR
   - Custo empresa
   - Desconto profissional
   - Observações gerais

2. **Validações**: Resumo e validações do processo
   - Total de colaboradores
   - Total de dias úteis
   - Valores totais
   - Contadores de status

## Tratamento de Erros

### ⚠️ Validações Automáticas
- Verificação de campos obrigatórios
- Validação de formatos de data
- Verificação de valores numéricos
- Consistência entre campos relacionados

### 🔍 Logs de Execução
- Mensagens detalhadas de cada etapa
- Contadores de registros processados
- Identificação de problemas encontrados
- Resumo final da execução

## Manutenção e Atualizações

### 📝 Modificações Frequentes
- Atualização de valores por sindicato
- Alteração de regras de exclusão
- Modificação de proporções de custo
- Ajuste de dias úteis por mês

### 🔧 Personalizações
- Adição de novos filtros de exclusão
- Modificação de regras de cálculo
- Inclusão de novos campos de validação
- Alteração do formato de saída

## Suporte e Troubleshooting

### ❓ Problemas Comuns
1. **Erro ao carregar planilhas**: Verificar se todos os arquivos estão na pasta
2. **Colunas não encontradas**: Verificar nomes das colunas nas planilhas
3. **Valores incorretos**: Verificar formato dos dados nas planilhas
4. **Erro de memória**: Verificar tamanho das planilhas de entrada

### 📞 Contato
Para suporte técnico ou dúvidas sobre a automação, consulte a documentação ou execute os testes para identificar problemas específicos.

## Licença
Este projeto é desenvolvido para uso interno da empresa e não possui licença pública.

---

**Desenvolvido para automatizar o processo de compra de VR/VA e reduzir erros manuais no cálculo de benefícios.**
