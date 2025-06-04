# Simulador Tributário com Correção Renda Fixa Geral

Este repositório contém um aplicativo em Streamlit que simula investimentos (Fundo, Renda Fixa e VGBL) e calcula a taxa anual necessária para igualar o valor líquido final dos investimentos de Fundo e Renda Fixa ao do VGBL. 

## Correção Importante

A simulação de Renda Fixa agora corrige corretamente tributações nos ciclos completos e residuais, para **qualquer** duração de ciclo (não apenas 5 anos).

## Arquivos

- **app.py**: Código principal do aplicativo Streamlit.  
- **requirements.txt**: Dependências necessárias.  
- **README.md**: Instruções de uso.

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
   - **Valor inicial**: Exemplo R$500.000  
   - **Aporte periódico**: R$0  
   - **Frequência dos aportes**: Mensal ou Anual  
   - **Taxa de retorno anual (%)**: Ex.: 10,10  
   - **Prazo total (anos)**: Ex.: 10  
   - **Ciclo RF (anos)**: Qualquer valor, ex.: 5  
4. Clique em **Calcular projeções**. O aplicativo exibirá:
   1. Valores finais líquidos e impostos pagos.  
   2. Gráfico da evolução mensal.  
   3. Tabela com a **taxa anual necessária** para Fundo e Renda Fixa igualarem o valor líquido do VGBL.

## Observações

- Cada aporte (inclusive o inicial) é tratado como um lote, tributado individualmente.  
- A Renda Fixa corrige tributações em todos os ciclos completos e no residual final.  
