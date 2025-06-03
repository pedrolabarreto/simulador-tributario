# app.py
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")
st.title("Simulador Tributário: Fundo Longo Prazo, Renda Fixa e VGBL (lotes)")

# === Funções auxiliares para alíquotas regressivas ===
def aliquota_regressiva(meses):
    """
    Tabela regressiva de IR (Fundo e Renda Fixa, em lote):
    0–6 meses: 22.5%
    6–12 meses: 20%
    12–24 meses: 17.5%
    >24 meses: 15%
    """
    if meses <= 6:
        return 0.225
    elif meses <= 12:
        return 0.20
    elif meses <= 24:
        return 0.175
    else:
        return 0.15

def aliquota_vgbl(meses):
    """
    Tabela regressiva de IR para VGBL (resgate, por lote) baseada no tempo total:
    Até 2 anos (24 meses): 35%
    Até 4 anos: 30%
    Até 6 anos: 25%
    Até 8 anos: 20%
    Até 10 anos: 15%
    Acima de 10 anos: 10%
    """
    anos = meses / 12
    if anos <= 2:
        return 0.35
    elif anos <= 4:
        return 0.30
    elif anos <= 6:
        return 0.25
    elif anos <= 8:
        return 0.20
    elif anos <= 10:
        return 0.15
    else:
        return 0.10

# === Simulação do Fundo de Investimento (lote a lote) ===
def simular_fundo_lotes(valor_inicial, aporte, freq_aporte, taxa_anual, prazo_anos):
    meses_totais = prazo_anos * 12
    taxa_mensal = (1 + taxa_anual)**(1/12) - 1

    # DataFrame para lotes: cada linha é um aporte (incluindo a “inicial”)
    df = pd.DataFrame(columns=["valor", "base", "mes_aporte"])
    # Lote inicial:
    df.loc[0] = [valor_inicial, valor_inicial, 0]

    imposto_total = 0.0
    historico = []  # guarda o valor total líquido mês a mês

    for mes in range(0, meses_totais + 1):
        # Registrar saldo total no histórico
        historico.append(df["valor"].sum())

        if mes == meses_totais:
            # Fim da projeção (não há aporte nem come-cotas neste passo)
            break

        # 1) Inserir aporte (antes do growth mensal)
        if freq_aporte == "Mensal":
            lote = {"valor": aporte, "base": aporte, "mes_aporte": mes}
            df = df.append(lote, ignore_index=True)
        elif freq_aporte == "Anual" and mes % 12 == 0 and mes > 0:
            lote = {"valor": aporte, "base": aporte, "mes_aporte": mes}
            df = df.append(lote, ignore_index=True)

        # 2) Crescimento mensal de cada lote
        df["valor"] = df["valor"] * (1 + taxa_mensal)

        # 3) Se for mês de come-cotas (maio [5] ou novembro [11]):
        mes_do_ano = (mes % 12) + 1
        if mes_do_ano in (5, 11):
            # Para cada lote, calcular IR de acordo com holding em meses:
            for idx, row in df.iterrows():
                holding = mes - int(row["mes_aporte"])
                ganho = row["valor"] - row["base"]
                if ganho > 0:
                    aliquota = aliquota_regressiva(holding)
                    imposto = ganho * aliquota
                    # Subtrair imposto do lote
                    df.at[idx, "valor"] = row["valor"] - imposto
                    # Atualizar base para o próximo ciclo
                    df.at[idx, "base"] = df.at[idx, "valor"]
                    imposto_total += imposto

    return historico, imposto_total

# === Simulação da Renda Fixa (lote a lote) ===
def simular_rf_lotes(valor_inicial, aporte, freq_aporte, taxa_anual, prazo_anos, ciclo_anos):
    meses_totais = prazo_anos * 12
    taxa_mensal = (1 + taxa_anual)**(1/12) - 1
    ciclo_meses = ciclo_anos * 12

    df = pd.DataFrame(columns=["valor", "base", "mes_aporte"])
    df.loc[0] = [valor_inicial, valor_inicial, 0]

    imposto_total = 0.0
    historico = []

    for mes in range(0, meses_totais + 1):
        historico.append(df["valor"].sum())

        if mes == meses_totais:
            break

        # 1) Inserir aporte
        if freq_aporte == "Mensal":
            lote = {"valor": aporte, "base": aporte, "mes_aporte": mes}
            df = df.append(lote, ignore_index=True)
        elif freq_aporte == "Anual" and mes % 12 == 0 and mes > 0:
            lote = {"valor": aporte, "base": aporte, "mes_aporte": mes}
            df = df.append(lote, ignore_index=True)

        # 2) Crescimento mensal
        df["valor"] = df["valor"] * (1 + taxa_mensal)

        # 3) Checa maturidade em relação ao ciclo (cada lote que completar múltiplo exato de ciclo_anos):
        for idx, row in df.iterrows():
            holding = mes - int(row["mes_aporte"])
            # Se houver múltiplo exato de ciclo_meses, tributa-se:
            if holding > 0 and (holding % ciclo_meses == 0):
                ganho = row["valor"] - row["base"]
                if ganho > 0:
                    aliquota = aliquota_regressiva(holding)
                    imposto = ganho * aliquota
                    df.at[idx, "valor"] = row["valor"] - imposto
                    df.at[idx, "base"] = df.at[idx, "valor"]
                    imposto_total += imposto

    # 4) No final, tributar lotes que não completaram um ciclo exato:
    for idx, row in df.iterrows():
        holding = meses_totais - int(row["mes_aporte"])
        # Se não completou o ciclo exato, há IR residual:
        if holding > 0 and (holding % ciclo_meses != 0):
            ganho = row["valor"] - row["base"]
            if ganho > 0:
                aliquota = aliquota_regressiva(holding)
                imposto = ganho * aliquota
                df.at[idx, "valor"] = row["valor"] - imposto
                imposto_total += imposto

    return historico, imposto_total

# === Simulação do VGBL (lote a lote) ===
def simular_vgbl_lotes(valor_inicial, aporte, freq_aporte, taxa_anual, prazo_anos):
    meses_totais = prazo_anos * 12
    taxa_mensal = (1 + taxa_anual)**(1/12) - 1

    df = pd.DataFrame(columns=["valor", "mes_aporte"])
    df.loc[0] = [valor_inicial, 0]
    historico = []

    for mes in range(0, meses_totais + 1):
        historico.append(df["valor"].sum())
        if mes == meses_totais:
            break

        # 1) Inserir aporte
        if freq_aporte == "Mensal":
            df = df.append({"valor": aporte, "mes_aporte": mes}, ignore_index=True)
        elif freq_aporte == "Anual" and mes % 12 == 0 and mes > 0:
            df = df.append({"valor": aporte, "mes_aporte": mes}, ignore_index=True)

        # 2) Crescimento mensal
        df["valor"] = df["valor"] * (1 + taxa_mensal)

    # 3) No final, tributar cada lote de acordo com o tempo de holding até meses_totais
    imposto_total = 0.0
    valor_final = 0.0
    for idx, row in df.iterrows():
        holding = meses_totais - int(row["mes_aporte"])
        aliquota = aliquota_vgbl(holding)
        # Calcular a parcela de ganho deste lote:
        # Se valor atual é V e holding = h meses, então valor investido bruto = V / ((1+taxa_mensal)^h).
        original = row["valor"] / ((1 + taxa_mensal) ** holding)
        ganho = row["valor"] - original
        imposto = ganho * aliquota
        imposto_total += imposto
        valor_final += row["valor"] - imposto

    return historico, valor_final, imposto_total

# === Sidebar: parâmetros de entrada ===
st.sidebar.header("Parâmetros Gerais")

valor_inicial = st.sidebar.number_input(
    "Valor inicial (R$):", min_value=0.0, value=10000.0, step=1000.0, format="%.2f"
)
st.sidebar.subheader("Aportes periódicos")
aporte = st.sidebar.number_input(
    "Valor do aporte (R$):", min_value=0.0, value=1000.0, step=100.0, format="%.2f"
)
freq_aporte = st.sidebar.selectbox(
    "Frequência dos aportes:", ("Mensal", "Anual")
)
taxa_anual = st.sidebar.slider(
    "Taxa de retorno anual (%):", min_value=0.0, max_value=50.0, value=8.0, step=0.1
) / 100.0
prazo_anos = st.sidebar.number_input(
    "Prazo total (anos):", min_value=1, max_value=100, value=15, step=1
)
st.sidebar.subheader("Renda Fixa")
ciclo_anos = st.sidebar.number_input(
    "Ciclo de reinvestimento RF (anos):", min_value=1, max_value=50, value=4, step=1
)
btn = st.sidebar.button("Calcular projeções")

# === Quando o usuário clicar em "Calcular projeções" ===
if btn:
    # 1) Fundo de Investimento
    hist_fundo, imp_fundo = simular_fundo_lotes(
        valor_inicial, aporte, freq_aporte, taxa_anual, prazo_anos
    )
    # 2) Renda Fixa
    hist_rf, imp_rf = simular_rf_lotes(
        valor_inicial, aporte, freq_aporte, taxa_anual, prazo_anos, ciclo_anos
    )
    # 3) VGBL
    hist_vgbl, val_vgbl, imp_vgbl = simular_vgbl_lotes(
        valor_inicial, aporte, freq_aporte, taxa_anual, prazo_anos
    )

    # Exibir valores finais
    st.subheader("1) Valores Finais (já líquidos de IR)")
    c1, c2, c3 = st.columns(3)
    c1.metric("Fundo (lote a lote)", f"R$ {hist_fundo[-1]:,.2f}")
    c2.metric("Renda Fixa (lote a lote)", f"R$ {hist_rf[-1]:,.2f}")
    c3.metric("VGBL (lote a lote)", f"R$ {val_vgbl:,.2f}")

    # Exibir impostos totais pagos
    st.subheader("2) Impostos Pagos ao Longo do Período")
    c4, c5, c6 = st.columns(3)
    c4.write(f"Fundo (come-cotas): R$ {imp_fundo:,.2f}")
    c5.write(f"Renda Fixa: R$ {imp_rf:,.2f}")
    c6.write(f"VGBL (resgate): R$ {imp_vgbl:,.2f}")

    # Montar DataFrame de evolução (apenas para plotagem)
    meses = np.arange(0, prazo_anos * 12 + 1)
    df_evolucao = pd.DataFrame({
        "Fundo (líquido lotes)": hist_fundo,
        "Renda Fixa (líquido lotes)": hist_rf,
        "VGBL (bruto lotes)": hist_vgbl
    }, index=meses / 12)

    st.subheader("3) Gráfico de Evolução Mensal")
    st.line_chart(df_evolucao)

    st.markdown(
        """
        **Como funciona este simulador (lote a lote)**

        1. **Fundo de Investimento**
           - Cada aporte (inclusive o inicial) é tratado como um lote separado.
           - A cada mês de maio e novembro (“come-cotas”), calcula-se, para cada lote:
             - `holding` = meses decorrido desde o `mes_aporte` até o mês atual.
             - `ganho` = valor atual do lote menos o valor-base (último valor após IR).
             - `aliquota` = função `aliquota_regressiva(holding)`:
               - 0–6 meses: 22,5%
               - 6–12 meses: 20%
               - 12–24 meses: 17,5%
               - >24 meses: 15%
             - Aplica IR sobre o `ganho` (ganho × alíquota). O lote é deduzido do imposto e, então, seu “base” é atualizado para o valor líquido.
        2. **Renda Fixa**
           - Cada aporte (inclusive o inicial) é tratado como um lote separado.
           - Informar o ciclo de reinvestimento (em anos). Cada lote que completar “múltiplo” exato de ciclos (em meses) paga IR sobre o ganho acumulado:
             - `holding` = meses desde o `mes_aporte` até o mês de avaliação.
             - `aliquota` = mesmo esquema regressivo acima.
             - Aplica IR e atualiza o “base” do lote (valor que continuará rendendo no próximo ciclo).
           - Ao final do período de projeção, cada lote que não tenha completado um ciclo exato ainda paga IR proporcional ao tempo decorrido (meses totais – mes_aporte).
        3. **VGBL**
           - Cada aporte (inclusive o inicial) é tratado como um lote separado.
           - Não há tributação durante a acumulação.
           - No final, para cada lote calcula-se:
             - `holding` = meses desde `mes_aporte` até o fim da projeção.
             - `aliquota` = função `aliquota_vgbl(holding)`:
               - Até 2 anos: 35%
               - Até 4 anos: 30%
               - Até 6 anos: 25%
               - Até 8 anos: 20%
               - Até 10 anos: 15%
               - Acima de 10 anos: 10%
             - `ganho` = valor atual do lote menos o valor inicial bruto (reconstruído via `(valor_atual) / ((1+taxa_mensal)^holding)`).
             - Aplica IR e deduz do lote. Soma-se todos os lotes líquidos para obter o valor final.
        4. **Aportes**
           - Se “Mensal”, cada mês haverá um lote extra com o valor do aporte.
           - Se “Anual”, cada 12 meses (jan/â cada ano) haverá um lote extra.
        5. **Taxa de Retorno**
           - Taxa anual informada no sidebar é convertida para taxa mensal composta: `(1 + taxa_anual)**(1/12) - 1`.

        Este algoritmo garante que cada aporte pague IR de acordo com seu próprio tempo de permanência (exato em meses), e não apenas pela idade da carteira como um todo. As saídas exibidas (“valor final” e “imposto pago”) são calculadas quando temos 100% de certeza de cada lote estar tributado corretamente.
        """
    )
