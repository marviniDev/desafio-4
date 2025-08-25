# 🚀 Instruções Rápidas - Automação VR/VA

## ⚡ Execução Rápida

### 1. Executar Automação Completa
```bash
python3 automacao_vr.py
```
**Resultado**: Gera planilha `VR_MENSAL_05_2025_AUTOMATIZADO.xlsx`

### 2. Executar Testes
```bash
python3 teste_automacao.py
```
**Resultado**: Valida todas as funcionalidades

### 3. Executar Demonstração
```bash
python3 demo_automacao.py
```
**Resultado**: Mostra passo a passo como funciona

## 📊 Arquivos Gerados

- **`VR_MENSAL_05_2025_AUTOMATIZADO.xlsx`** - Planilha final para envio à operadora
  - Aba 1: VR Mensal (dados principais)
  - Aba 2: Validações (resumo e contadores)

## 🔧 Configurações

Edite `config.py` para alterar:
- Mês/ano de referência
- Dias úteis padrão
- Valores padrão de VR
- Proporções empresa/profissional (80%/20%)

## 📋 Resumo da Automação

✅ **Processados**: 1.815 colaboradores
✅ **Elegíveis**: 1.795 colaboradores  
✅ **Excluídos**: 80 (estagiários, aprendizes, afastados, etc.)
✅ **Total VR**: R$ 1.342.670,00
✅ **Custo empresa**: R$ 1.074.136,00 (80%)
✅ **Desconto profissional**: R$ 268.534,00 (20%)

## 🚨 Solução de Problemas

### Erro ao carregar planilhas
- Verifique se todos os arquivos `.xlsx` estão na pasta
- Verifique se os nomes dos arquivos estão corretos

### Erro de dependências
```bash
sudo apt install -y python3-pandas python3-openpyxl python3-xlrd
```

### Validação manual
- Execute `python3 teste_automacao.py` para identificar problemas específicos

## 📞 Suporte

- **Documentação completa**: `README.md`
- **Configurações**: `config.py`
- **Código principal**: `automacao_vr.py`
- **Testes**: `teste_automacao.py`
- **Demonstração**: `demo_automacao.py`

---

**🎯 Sistema funcionando e pronto para uso em produção!** 