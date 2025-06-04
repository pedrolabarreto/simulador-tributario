# Simulador Tributário v1.0.1

Este repositório contém um aplicativo em Streamlit que simula investimentos (Fundo, Renda Fixa e VGBL) e calcula a taxa anual necessária para igualar o valor líquido final dos investimentos de Fundo e Renda Fixa ao do VGBL. 

## Atualização

- Versão 1.0.1: adicionado cabeçalho indicando mudança para forçar detecção no GitHub.

## Como usar

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
2. Execute o aplicativo:
   ```bash
   streamlit run app.py
   ```
3. Ajuste os parâmetros na barra lateral:
   - Valor inicial (R$): 500 000  
   - Aporte (R$): 0  
   - Frequência dos aportes: Mensal  
   - Taxa de retorno anual (%): 10.10  
   - Prazo total (anos): 10  
   - Ciclo RF (anos): 5  
4. Clique em **Calcular projeções** e observe que:
   - Renda Fixa (lote a lote) fica R$ 1.163.067,56  
   - VGBL (lote a lote) fica R$ 1.227.846,20  
   - Impostos pagos estarão corretos para cada modalidade.

