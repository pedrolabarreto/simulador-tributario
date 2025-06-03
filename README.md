# Simulador Tributário Versão Final

Este repositório contém um aplicativo em Streamlit que simula investimentos (Fundo, Renda Fixa e VGBL) e calcula a taxa anual necessária para igualar o valor líquido final dos investimentos de Fundo e Renda Fixa ao do VGBL. Esta versão inclui caching para otimizar desempenho e uma mensagem de sucesso ao final.

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
4. Clique em **Calcular projeções** e aguarde a mensagem de sucesso. O aplicativo exibirá:
   - Valores finais líquidos e impostos pagos.  
   - Gráfico da evolução mensal.  
   - Tabela com a **taxa anual necessária** para Fundo e Renda Fixa igualarem o valor líquido do VGBL.

## Observações

- Funções de simulação são memorizadas (cached) para acelerar bisseção e evitar tempo de espera indefinido.  
- Mensagem de sucesso aparecerá quando o cálculo terminar.  
- Cada aporte (inclusive o inicial) é tratado como um lote, tributado individualmente.  
