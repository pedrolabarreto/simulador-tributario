# Simulador Tributário de Investimentos (Fundo, Renda Fixa e VGBL)

Este repositório contém um aplicativo em [Streamlit](https://streamlit.io/) que simula, lote a lote, a evolução do patrimônio líquido em três modalidades de investimento, levando em conta:

- Fundo de investimento com tributação (come-cotas) semestral e alíquota regressiva por lote.  
- Títulos de Renda Fixa com tributação regressiva ao final de cada ciclo (parâmetro “Ciclo RF”) e tributação parcial ao final se estiver fora de um ciclo exato.  
- VGBL com tributação regressiva única no resgate, por lote, de acordo com o tempo total de permanência.

## Como instalar

1. Clone este repositório:
   ```bash
   git clone https://github.com/SEU_USUARIO_GITHUB/simulador-tributario.git
   cd simulador-tributario
   ```

2. Crie e ative um ambiente virtual (opcional, mas recomendado):
   ```bash
   python -m venv venv
   # No Windows:
   venv\Scripts\activate
   # No macOS/Linux:
   source venv/bin/activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

## Como usar

1. Execute o Streamlit:
   ```bash
   streamlit run app.py
   ```
2. O navegador abrirá automaticamente (ou copie a URL sugerida no terminal).

3. Ajuste os parâmetros na barra lateral:
   - **Valor inicial**: valor de “seed” do investimento.  
   - **Aporte**: valor do aporte periódico.  
   - **Frequência dos aportes**: Mensal ou Anual.  
   - **Taxa de retorno anual** (em %).  
   - **Prazo total** (em anos).  
   - **Ciclo RF (anos)**: período em anos para reinvestimento tributado da Renda Fixa (pode ser > 10).  
4. Clique em **“Calcular projeções”**.

5. A página exibirá:
   1. **Valores finais líquidos** em cada modalidade.  
   2. **Total de imposto pago** em cada modalidade.  
   3. **Gráfico de evolução mensal** dos saldos (líquido no Fundo e RF, bruto no VGBL).

## Como funciona internamente

- Cada **aporte** (e o valor inicial) é tratado como um “lote” com data de entrada (`mes_aporte`).  
- A cada mês, todos os lotes rendem a mesma **taxa mensal** (derivada da taxa anual).  
- No **Fundo**: nos meses de maio e novembro, cada lote é tributado de acordo com seu `holding` (meses desde o mes_aporte). A alíquota segue a tabela regressiva (0–6m=22.5%, 6–12m=20%, 12–24m=17.5%, >24m=15%). Após pagar IR, o “base” do lote é atualizado para o valor líquido.  
- Na **Renda Fixa**: cada lote é tributado ao completar “múltiplo” exato de ciclo (Ciclo RF em meses). Se, ao fim da projeção, um lote não completar o ciclo, ele paga IR proporcional ao seu tempo total de permanência. A alíquota segue a mesma tabela regressiva.  
- No **VGBL**: não há tributação até o resgate final. Ao final, cada lote paga IR de acordo com a tabela regressiva de VGBL (prazos totais: ≤2a=35%, ≤4a=30%, ≤6a=25%, ≤8a=20%, ≤10a=15%, >10a=10%). O ganho de cada lote é calculado a partir da sua “origem” (reconstruída via `(valor_atual) / ((1+taxa_mensal)^holding)`).

Dessa forma, garantimos que aportes mais recentes paguem alíquotas maiores e aportes mais antigos tenham direito a alíquota mínima.

## Licença

Este projeto é fornecido “no estado em que se encontra” (MIT License, sem garantias). Use à vontade e faça forks.  

---

Feito com ❤️ para quem não quer imprecisões.  
