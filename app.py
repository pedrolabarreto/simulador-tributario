# app.py
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")
st.title("Simulador Tributário: Fundo, Renda Fixa e VGBL com Taxa Necessária")

# === Funções auxiliares para alíquotas regressivas ===
def aliquota_regressiva(meses):
    if meses <= 6:
        return 0.225
    elif meses <= 12:
        return 0.20
    elif meses <= 24:
        return 0.175
    else:
        return 0.15

def aliquota_vgbl(meses):
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

# === Simulações por lote com caching ===
@st.cache_data(show_spinner=False)
def simular_fundo_lotes(valor_inicial, aporte, freq_aporte, taxa_anual, prazo_anos):
    meses_totais = prazo_anos * 12
    taxa_mensal = (1 + taxa_anual)**(1/12) - 1
    df = pd.DataFrame(columns=["valor", "base", "mes_aporte"])
    df.loc[0] = [valor_inicial, valor_inicial, 0]
    imposto_total = 0.0
    historico = []
    for mes in range(meses_totais + 1):
        historico.append(df["valor"].sum())
        if mes == meses_totais:
            break
        if freq_aporte == "Mensal":
            idx = len(df)
            df.loc[idx] = [aporte, aporte, mes]
        elif freq_aporte == "Anual" and mes % 12 == 0 and mes > 0:
            idx = len(df)
            df.loc[idx] = [aporte, aporte, mes]
        df["valor"] = df["valor"] * (1 + taxa_mensal)
        mes_do_ano = (mes % 12) + 1
        if mes_do_ano in (5, 11):
            for idx, row in df.iterrows():
                holding = mes - int(row["mes_aporte"])
                ganho = row["valor"] - row["base"]
                if ganho > 0:
                    aliquota = aliquota_regressiva(holding)
                    imposto = ganho * aliquota
                    df.at[idx, "valor"] = row["valor"] - imposto
                    df.at[idx, "base"] = df.at[idx, "valor"]
                    imposto_total += imposto
    valor_final = historico[-1]
    return historico, valor_final, imposto_total

@st.cache_data(show_spinner=False)
def simular_rf_lotes(valor_inicial, aporte, freq_aporte, taxa_anual, prazo_anos, ciclo_anos):
    meses_totais = prazo_anos * 12
    taxa_mensal = (1 + taxa_anual)**(1/12) - 1
    ciclo_meses = ciclo_anos * 12
    df = pd.DataFrame(columns=["valor", "base", "mes_aporte"])
    df.loc[0] = [valor_inicial, valor_inicial, 0]
    imposto_total = 0.0
    historico = []
    for mes in range(meses_totais + 1):
        historico.append(df["valor"].sum())
        if mes == meses_totais:
            break
        if freq_aporte == "Mensal":
            idx = len(df)
            df.loc[idx] = [aporte, aporte, mes]
        elif freq_aporte == "Anual" and mes % 12 == 0 and mes > 0:
            idx = len(df)
            df.loc[idx] = [aporte, aporte, mes]
        df["valor"] = df["valor"] * (1 + taxa_mensal)
        for idx, row in df.iterrows():
            holding = mes - int(row["mes_aporte"])
            if holding > 0 and (holding % ciclo_meses == 0):
                ganho = row["valor"] - row["base"]
                if ganho > 0:
                    aliquota = aliquota_regressiva(holding)
                    imposto = ganho * aliquota
                    df.at[idx, "valor"] = row["valor"] - imposto
                    df.at[idx, "base"] = df.at[idx, "valor"]
                    imposto_total += imposto
    for idx, row in df.iterrows():
        holding = (prazo_anos * 12) - int(row["mes_aporte"])
        if holding > 0 and (holding % ciclo_meses != 0):
            ganho = row["valor"] - row["base"]
            if ganho > 0:
                aliquota = aliquota_regressiva(holding)
                imposto = ganho * aliquota
                df.at[idx, "valor"] = row["valor"] - imposto
                imposto_total += imposto
    valor_final = historico[-1]
    return historico, valor_final, imposto_total

@st.cache_data(show_spinner=False)
def simular_vgbl_lotes(valor_inicial, aporte, freq_aporte, taxa_anual, prazo_anos):
    meses_totais = prazo_anos * 12
    taxa_mensal = (1 + taxa_anual)**(1/12) - 1
    df = pd.DataFrame(columns=["valor", "mes_aporte"])
    df.loc[0] = [valor_inicial, 0]
    historico = []
    for mes in range(meses_totais + 1):
        historico.append(df["valor"].sum())
        if mes == meses_totais:
            break
        if freq_aporte == "Mensal":
            idx = len(df)
            df.loc[idx] = [aporte, mes]
        elif freq_aporte == "Anual" and mes % 12 == 0 and mes > 0:
            idx = len(df)
            df.loc[idx] = [aporte, mes]
        df["valor"] = df["valor"] * (1 + taxa_mensal)
    imposto_total = 0.0
    valor_final = 0.0
    for idx, row in df.iterrows():
        holding = (prazo_anos * 12) - int(row["mes_aporte"])
        aliquota = aliquota_vgbl(holding)
        original = row["valor"] / ((1 + taxa_mensal) ** holding)
        ganho = row["valor"] - original
        imposto = ganho * aliquota
        imposto_total += imposto
        valor_final += row["valor"] - imposto
    return historico, valor_final, imposto_total

# Funções para encontrar taxa necessária via bisseção
def encontrar_taxa_alvo_fundo(valor_inicial, aporte, freq_aporte, prazo_anos, alvo):
    def valor_final_taxa(taxa):
        _, vf, _ = simular_fundo_lotes(valor_inicial, aporte, freq_aporte, taxa, prazo_anos)
        return vf
    low, high = 0.0, 1.0
    for _ in range(20):
        if valor_final_taxa(high) < alvo:
            high *= 2
        else:
            break
    for _ in range(50):
        mid = (low + high) / 2
        if abs(valor_final_taxa(mid) - alvo) < 1e-6:
            return mid
        if valor_final_taxa(mid) < alvo:
            low = mid
        else:
            high = mid
    return mid

def encontrar_taxa_alvo_rf(valor_inicial, aporte, freq_aporte, prazo_anos, ciclo_anos, alvo):
    def valor_final_taxa(taxa):
        _, vf, _ = simular_rf_lotes(valor_inicial, aporte, freq_aporte, taxa, prazo_anos, ciclo_anos)
        return vf
    low, high = 0.0, 1.0
    for _ in range(20):
        if valor_final_taxa(high) < alvo:
            high *= 2
        else:
            break
    for _ in range(50):
        mid = (low + high) / 2
        if abs(valor_final_taxa(mid) - alvo) < 1e-6:
            return mid
        if valor_final_taxa(mid) < alvo:
            low = mid
        else:
            high = mid
    return mid

# === Sidebar ===
st.sidebar.header("Parâmetros Gerais")
valor_inicial = st.sidebar.number_input("Valor inicial (R$):", min_value=0.0, value=10000.0, step=1000.0, format="%.2f")
st.sidebar.subheader("Aportes periódicos")
aporte = st.sidebar.number_input("Valor do aporte (R$):", min_value=0.0, value=1000.0, step=100.0, format="%.2f")
freq_aporte = st.sidebar.selectbox("Frequência dos aportes:", ("Mensal", "Anual"))
taxa_anual = st.sidebar.slider("Taxa de retorno anual (%):", min_value=0.0, max_value=50.0, value=8.0, step=0.1)/100.0
prazo_anos = st.sidebar.number_input("Prazo total (anos):", min_value=1, max_value=100, value=15, step=1)
st.sidebar.subheader("Renda Fixa")
ciclo_anos = st.sidebar.number_input("Ciclo de reinvestimento RF (anos):", min_value=1, max_value=50, value=4, step=1)
btn = st.sidebar.button("Calcular projeções")

if not btn:
    st.write("Ajuste os parâmetros na barra lateral e clique em **Calcular projeções** para ver os resultados.")
else:
    hist_fundo, vf_fundo, imp_fundo = simular_fundo_lotes(valor_inicial, aporte, freq_aporte, taxa_anual, prazo_anos)
    hist_rf, vf_rf, imp_rf = simular_rf_lotes(valor_inicial, aporte, freq_aporte, taxa_anual, prazo_anos, ciclo_anos)
    hist_vgbl, vf_vgbl, imp_vgbl = simular_vgbl_lotes(valor_inicial, aporte, freq_aporte, taxa_anual, prazo_anos)

    st.subheader("Valores Finais (líquidos de IR)")
    c1, c2, c3 = st.columns(3)
    c1.metric("Fundo (lote a lote)", f"R$ {vf_fundo:,.2f}")
    c2.metric("Renda Fixa (lote a lote)", f"R$ {vf_rf:,.2f}")
    c3.metric("VGBL (lote a lote)", f"R$ {vf_vgbl:,.2f}")

    st.subheader("Impostos Pagos")
    c4, c5, c6 = st.columns(3)
    c4.write(f"Fundo: R$ {imp_fundo:,.2f}")
    c5.write(f"Renda Fixa: R$ {imp_rf:,.2f}")
    c6.write(f"VGBL: R$ {imp_vgbl:.,2f}")

    meses = np.arange(0, prazo_anos * 12 + 1)
    df_evolucao = pd.DataFrame({
        "Fundo (líquido lotes)": hist_fundo,
        "Renda Fixa (líquido lotes)": hist_rf,
        "VGBL (bruto lotes)": hist_vgbl
    }, index=meses / 12)
    st.subheader("Gráfico de Evolução Mensal")
    st.line_chart(df_evolucao)

    # Taxas necessárias
    alvo = vf_vgbl
    taxa_fundo_necessaria = encontrar_taxa_alvo_fundo(valor_inicial, aporte, freq_aporte, prazo_anos, alvo)
    taxa_rf_necessaria = encontrar_taxa_alvo_rf(valor_inicial, aporte, freq_aporte, prazo_anos, ciclo_anos, alvo)

    st.subheader("Taxas Necessárias para Igualar ao VGBL")
    df_taxas = pd.DataFrame({
        "Modalidade": ["Fundo", "Renda Fixa"],
        "Taxa Anual Necessária (%)": [round(taxa_fundo_necessaria * 100, 4), round(taxa_rf_necessaria * 100, 4)]
    })
    st.table(df_taxas)

    st.success("Cálculo concluído com sucesso!")
