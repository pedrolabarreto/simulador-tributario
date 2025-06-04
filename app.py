# app.py - Versão 1.0.1 (atualizado para forçar detecção de mudança)
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")
st.title("Simulador Tributário: Fundo, Renda Fixa e VGBL (corrigido)")

# ————— TABELA DE ALÍQUOTAS REGRESSIVAS —————
def aliquota_regressiva(meses):
    # 0–6 meses: 22.5%; 6–12:20%; 12–24:17.5%; >24:15%
    if meses <= 6:
        return 0.225
    elif meses <= 12:
        return 0.20
    elif meses <= 24:
        return 0.175
    else:
        return 0.15

# ————— SIMULAÇÕES POR LOTE —————
@st.cache_data(show_spinner=False)
def simular_fundo_lotes(valor_inicial, aporte, freq_aporte, taxa_anual, plazo_anos):
    meses_totais = plazo_anos * 12
    taxa_mensal = (1 + taxa_anual) ** (1/12) - 1

    # Um DataFrame com cada lote (inicial + aportes)
    df = pd.DataFrame(columns=["valor", "base", "mes_aporte"])
    df.loc[0] = [valor_inicial, valor_inicial, 0]
    imposto_total = 0.0
    historico = [valor_inicial]

    for mes in range(1, meses_totais + 1):
        # ============ 1) Inserir aporte (se houver) ============
        if freq_aporte == "Mensal":
            idx = len(df)
            df.loc[idx] = [aporte, aporte, mes - 1]
        elif freq_aporte == "Anual" and (mes - 1) % 12 == 0 and (mes - 1) > 0:
            idx = len(df)
            df.loc[idx] = [aporte, aporte, mes - 1]

        # ============ 2) Crescimento mensal de cada lote ============
        df["valor"] = df["valor"] * (1 + taxa_mensal)

        # ============ 3) Evento de come-cotas: AGORA em maio (5) e novembro (11) ============
        mes_do_ano = ((mes - 1) % 12) + 1
        if mes_do_ano in (5, 11):
            for idx, row in df.iterrows():
                holding = mes - int(row["mes_aporte"])  # meses decorridos
                ganho = row["valor"] - row["base"]
                if ganho > 0:
                    aliquota = aliquota_regressiva(holding)
                    imposto = ganho * aliquota
                    df.at[idx, "valor"] = row["valor"] - imposto
                    df.at[idx, "base"] = df.at[idx, "valor"]
                    imposto_total += imposto

        historico.append(df["valor"].sum())

    valor_final = historico[-1]
    return historico, valor_final, imposto_total


@st.cache_data(show_spinner=False)
def simular_rf_lotes(valor_inicial, aporte, freq_aporte, taxa_anual, plazo_anos, ciclo_anos):
    meses_totais = plazo_anos * 12
    taxa_mensal = (1 + taxa_anual) ** (1/12) - 1
    ciclo_meses = ciclo_anos * 12

    # DataFrame para lotes: só o inicial se aporte = 0
    df = pd.DataFrame(columns=["valor", "base", "mes_aporte"])
    df.loc[0] = [valor_inicial, valor_inicial, 0]
    imposto_total = 0.0
    historico = [valor_inicial]

    for mes in range(1, meses_totais + 1):
        # ============ 1) Inserir aporte (se houver) ============
        if freq_aporte == "Mensal":
            idx = len(df)
            df.loc[idx] = [aporte, aporte, mes - 1]
        elif freq_aporte == "Anual" and (mes - 1) % 12 == 0 and (mes - 1) > 0:
            idx = len(df)
            df.loc[idx] = [aporte, aporte, mes - 1]

        # ============ 2) Crescimento mensal ============
        df["valor"] = df["valor"] * (1 + taxa_mensal)

        # ============ 3) Quando cumprir ciclo exato: tributar lote a lote ============
        if mes % ciclo_meses == 0:
            for idx, row in df.iterrows():
                holding = mes - int(row["mes_aporte"])
                ganho = row["valor"] - row["base"]
                if ganho > 0:
                    aliquota = aliquota_regressiva(holding)
                    imposto = ganho * aliquota
                    df.at[idx, "valor"] = row["valor"] - imposto
                    df.at[idx, "base"] = df.at[idx, "valor"]
                    imposto_total += imposto

        historico.append(df["valor"].sum())

    # ============ 4) Pós-ciclo final: tributar resíduo se não for múltiplo exato ============
    for idx, row in df.iterrows():
        holding = meses_totais - int(row["mes_aporte"])
        if holding > 0 and (holding % ciclo_meses != 0):
            ganho = row["valor"] - row["base"]
            if ganho > 0:
                aliquota = aliquota_regressiva(holding)
                imposto = ganho * aliquota
                df.at[idx, "valor"] = row["valor"] - imposto
                imposto_total += imposto

    valor_final = df["valor"].sum()
    return historico, valor_final, imposto_total


@st.cache_data(show_spinner=False)
def simular_vgbl_lotes(valor_inicial, aporte, freq_aporte, taxa_anual, plazo_anos):
    meses_totais = plazo_anos * 12
    taxa_mensal = (1 + taxa_anual) ** (1/12) - 1

    df = pd.DataFrame(columns=["valor", "mes_aporte"])
    df.loc[0] = [valor_inicial, 0]
    historico = [valor_inicial]

    for mes in range(1, meses_totais + 1):
        if freq_aporte == "Mensal":
            idx = len(df)
            df.loc[idx] = [aporte, mes - 1]
        elif freq_aporte == "Anual" and (mes - 1) % 12 == 0 and (mes - 1) > 0:
            idx = len(df)
            df.loc[idx] = [aporte, mes - 1]

        df["valor"] = df["valor"] * (1 + taxa_mensal)
        historico.append(df["valor"].sum())

    # único imposto no final, alíquota de 10% pois prazo = 10 anos
    imposto_total = 0.0
    valor_final = 0.0
    for idx, row in df.iterrows():
        holding = meses_totais - int(row["mes_aporte"])
        # para VGBL, usamos mesma função de aliquota_regressiva, mas:
        # se holding > 120 (10 anos), cai em alíquota de 10%, como desejado
        if holding <= 24:
            aliq = 0.35
        elif holding <= 48:
            aliq = 0.30
        elif holding <= 72:
            aliq = 0.25
        elif holding <= 96:
            aliq = 0.20
        elif holding <= 120:
            aliq = 0.15
        else:
            aliq = 0.10  # (não será usado neste exemplo de 10 anos)

        original = row["valor"] / ((1 + taxa_mensal) ** holding)
        ganho = row["valor"] - original
        imposto = ganho * aliq
        imposto_total += imposto
        valor_final += row["valor"] - imposto

    return historico, valor_final, imposto_total


# ————— STREAMLIT: PARÂMETROS DE ENTRADA —————
st.sidebar.header("Parâmetros Gerais")
valor_inicial = st.sidebar.number_input("Valor inicial (R$):", min_value=0.0, value=500_000.0, step=50_000.0, format="%.2f")
st.sidebar.subheader("Aportes periódicos")
aporte = st.sidebar.number_input("Valor do aporte (R$):", min_value=0.0, value=0.0, step=1_000.0, format="%.2f")
freq_aporte = st.sidebar.selectbox("Frequência dos aportes:", ("Mensal", "Anual"))
taxa_anual = st.sidebar.slider("Taxa de retorno anual (%):", min_value=0.0, max_value=50.0, value=10.10, step=0.01) / 100.0
prazo_anos = st.sidebar.number_input("Prazo total (anos):", min_value=1, max_value=50, value=10, step=1)
st.sidebar.subheader("Renda Fixa")
ciclo_anos = st.sidebar.number_input("Ciclo de reinvestimento RF (anos):", min_value=1, max_value=50, value=5, step=1)
btn = st.sidebar.button("Calcular projeções")

if not btn:
    st.write("Ajuste os parâmetros na barra lateral e clique em **Calcular projeções** para ver os resultados.")
else:
    # ————— EXECUÇÃO DAS SIMULAÇÕES —————
    hist_fundo, vf_fundo, imp_fundo = simular_fundo_lotes(valor_inicial, aporte, freq_aporte, taxa_anual, prazo_anos)
    hist_rf, vf_rf, imp_rf = simular_rf_lotes(valor_inicial, aporte, freq_aporte, taxa_anual, prazo_anos, ciclo_anos)
    hist_vgbl, vf_vgbl, imp_vgbl = simular_vgbl_lotes(valor_inicial, aporte, freq_aporte, taxa_anual, prazo_anos)

    # ————— MOSTRAR RESULTADOS —————
    st.subheader("1) Valores Finais (líquidos de IR)")
    c1, c2, c3 = st.columns(3)
    c1.metric("Fundo (lote a lote)", f"R$ {vf_fundo:,.2f}")
    c2.metric("Renda Fixa (lote a lote)", f"R$ {vf_rf:,.2f}")
    c3.metric("VGBL (lote a lote)", f"R$ {vf_vgbl:,.2f}")

    st.subheader("2) Impostos Pagos")
    c4, c5, c6 = st.columns(3)
    c4.write(f"Fundo: R$ {imp_fundo:,.2f}")
    c5.write(f"Renda Fixa: R$ {imp_rf:,.2f}")
    c6.write(f"VGBL: R$ {imp_vgbl:,.2f}")

    # Montar DataFrame de evolução para o gráfico
    meses = np.arange(0, prazo_anos * 12 + 1)
    df_evolucao = pd.DataFrame({
        "Fundo (líquido lotes)": hist_fundo,
        "Renda Fixa (líquido lotes)": hist_rf,
        "VGBL (bruto lotes)": hist_vgbl
    }, index=meses / 12)

    st.subheader("3) Gráfico de Evolução Mensal")
    st.line_chart(df_evolucao)

    st.success("Cálculo concluído com sucesso!")
