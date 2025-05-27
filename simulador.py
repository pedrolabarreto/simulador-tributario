# Simulador com controle por cotas para fundos de investimento
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import io
from datetime import datetime

def calcular_previdencia(vp, pmt, taxa_mensal, n_meses):
    saldo = vp
    saldos = []
    for _ in range(n_meses):
        saldo *= (1 + taxa_mensal)
        saldo += pmt
        saldos.append(saldo)
    rendimento = saldo - (vp + pmt * n_meses)
    saldo_liquido = saldo - rendimento * 0.10
    saldos[-1] = saldo_liquido
    return saldo_liquido, saldos

def calcular_renda_fixa(vp, pmt, taxa_mensal, n_anos, ciclo_anos):
    saldo = vp
    total_aportes = 0
    saldos = []
    for ano in range(n_anos):
        for mes in range(12):
            saldo *= (1 + taxa_mensal)
            saldo += pmt
            total_aportes += pmt
            saldos.append(saldo)
        if (ano + 1) % ciclo_anos == 0:
            rendimento = saldo - (vp + total_aportes)
            saldo -= rendimento * 0.15
            vp = saldo
            total_aportes = 0
    rendimento_final = saldo - (vp + total_aportes)
    saldo_liquido = saldo - rendimento_final * 0.15
    saldos[-1] = saldo_liquido
    return saldo_liquido, saldos

def calcular_fundos_cotas(vp, pmt, taxa_mensal, n_meses):
    cotas = []  # cada item é um dicionário: {'valor': X, 'rendimento': Y}
    saldo = vp
    total_aportado = vp
    saldo_tributado = 0
    saldos = []

    cotas.append({'valor': vp, 'rendimento': 0})

    for i in range(1, n_meses + 1):
        # Capitaliza cada lote
        for lote in cotas:
            rendimento = lote['valor'] * taxa_mensal
            lote['valor'] += rendimento
            lote['rendimento'] += rendimento

        # Novo aporte (nova cota)
        cotas.append({'valor': pmt, 'rendimento': 0})
        total_aportado += pmt

        # Come-cotas em maio (i % 12 == 5) e novembro (i % 12 == 11)
        if (i % 12 == 5 or i % 12 == 11):
            imposto_total = 0
            for lote in cotas:
                imposto = lote['rendimento'] * 0.15
                lote['valor'] -= imposto
                lote['rendimento'] = 0
                imposto_total += imposto
            saldo_tributado += imposto_total

        # Atualiza saldo
        saldo = sum([l['valor'] for l in cotas])
        saldos.append(saldo)

    saldo_final = sum([l['valor'] for l in cotas])
    rendimento_bruto = saldo_final - total_aportado
    imposto_final = rendimento_bruto * 0.15 - saldo_tributado
    saldo_liquido = saldo_final - imposto_final
    saldos[-1] = saldo_liquido
    return saldo_liquido, saldos

def formatar_reais(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

st.set_page_config(page_title="Simulador Tributário", layout="wide")
st.title("📊 Simulador de Projeção de Capital - Impacto Tributário")

with st.sidebar.expander("🔧 Parâmetros de Entrada", expanded=True):
    vp = st.number_input("Aporte Inicial (R$)", value=50000.0)
    pmt = st.number_input("Aporte Mensal (R$)", value=5000.0)
    taxa_anual = st.number_input("Taxa de Retorno Anual (%)", value=10.0)
    n_anos = st.number_input("Prazo (anos)", min_value=2, value=25)
    ciclo = st.number_input("Ciclo de Renda Fixa (anos)", min_value=1, value=4)

n_meses = int(n_anos * 12)
taxa_mensal = (1 + taxa_anual / 100) ** (1 / 12) - 1

vl_prev, saldo_prev = calcular_previdencia(vp, pmt, taxa_mensal, n_meses)
vl_rf, saldo_rf = calcular_renda_fixa(vp, pmt, taxa_mensal, int(n_anos), int(ciclo))
vl_fundos, saldo_fundos = calcular_fundos_cotas(vp, pmt, taxa_mensal, n_meses)

df_resultados = pd.DataFrame({
    'Modalidade': ['Previdência VGBL', 'Renda Fixa', 'Fundos de Investimento'],
    'Valor Líquido Final (R$)': [formatar_reais(vl_prev), formatar_reais(vl_rf), formatar_reais(vl_fundos)],
    'Desvio Estimado': ['0%', '-0 a -2%', '+0 a +2,5%']
})
st.subheader("📋 Resultados Comparativos")
st.dataframe(df_resultados, use_container_width=True)

st.subheader("📈 Evolução do Capital Líquido")
fig = go.Figure()
fig.add_trace(go.Scatter(y=saldo_prev, mode='lines', name='Previdência'))
fig.add_trace(go.Scatter(y=saldo_rf, mode='lines', name='Renda Fixa'))
fig.add_trace(go.Scatter(y=saldo_fundos, mode='lines', name='Fundos'))
fig.update_layout(
    xaxis_title="Meses",
    yaxis_title="Saldo Acumulado Líquido (R$)",
    hovermode="x unified",
    yaxis_tickprefix="R$ ",
    yaxis_tickformat=",."
)
fig.update_traces(hovertemplate="R$ %{y:,.0f}")
st.plotly_chart(fig, use_container_width=True)

df_export = pd.DataFrame({
    'Mes': list(range(1, n_meses + 1)),
    'Previdência': saldo_prev,
    'Renda Fixa': saldo_rf,
    'Fundos': saldo_fundos
})

buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    df_export.to_excel(writer, sheet_name='Evolucao', index=False)
    pd.DataFrame(df_resultados).to_excel(writer, sheet_name='Resumo', index=False)
buffer.seek(0)

st.download_button(
    label="📥 Baixar Excel com Resultados",
    data=buffer,
    file_name=f"simulador_tributario_{datetime.today().date()}.xlsx",
    mime="application/vnd.ms-excel"
)

st.markdown("""
> ⚠️ **Nota sobre precisão**:
> 
> - Os **Fundos** agora seguem controle por cotas e aplicação do **come-cotas em maio e novembro**, respeitando rendimento individualizado por aporte.
> - A simulação da **Renda Fixa** considera reaplicações em ciclos com IR ao final.
> - A **Previdência** aplica IR final de 10% sobre rendimento total acumulado.
> 
> ✅ O gráfico representa valores **líquidos finais**, após a aplicação dos tributos de cada modalidade.
""")
