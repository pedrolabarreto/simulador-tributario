# Simulador Tributário com Output Corrigido

Este repositório contém um aplicativo em Streamlit que simula investimentos (Fundo, Renda Fixa e VGBL) e calcula a taxa anual necessária para igualar o valor líquido final dos investimentos de Fundo e Renda Fixa ao do VGBL.

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
   - Valor inicial, aporte, frequência, taxa de retorno (para cálculo inicial), prazo e ciclo RF.  
4. Clique em **Calcular projeções** para visualizar:
   - Valores finais líquidos e impostos pagos.  
   - Gráfico da evolução mensal.  
   - Tabela com a **taxa anual necessária** para Fundo e Renda Fixa igualarem o valor líquido do VGBL.

## Observações

- Mensagem inicial instrui a ajustar parâmetros e clicar no botão.  
- Cada aporte (inclusive o inicial) é tratado como um lote, tributado individualmente.  
