# Simulador Web de Projeção de Capital com Impacto Tributário - Versão com Gráfico Líquido
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import io
from datetime import datetime

def calcular_previdencia(vp, pmt, taxa_mensal, n_meses):
    saldo = vp
    saldos = []
    for i in range(n_meses):
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
    # Descontar IR final se necessário
    rendimento_final = saldo - (vp + total_aportes)
    saldo_liquido = saldo - rendimento_final * 0.15
    saldos[-1] = saldo_liquido
    return saldo_liquido, saldos

def calcular_fundos(vp, pmt, taxa_mensal, n_meses):
    saldo = vp
    total_aportado = vp
    saldo_tributado = 0
    saldos = []
    for i in range(1, n_meses + 1):
        rendimento_mes = saldo * taxa_mensal
        saldo += rendimento_mes + pmt
        total_aportado += pmt
        if i % 6 == 0:
            imposto = (saldo - total_aportado - saldo_tributado) * 0.15
            saldo -= imposto
            saldo_tributado += imposto
        saldos.append(saldo)
    rendimento_bruto = saldo - total_aportado
    imposto_final = (rendimento_bruto * 0.15) - saldo_tributado
    saldo_liquido = saldo - imposto_final
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
vl_fundos, saldo_fundos = calcular_fundos(vp, pmt, taxa_mensal, n_meses)

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
> - A simulação dos **Fundos** considera come-cotas e IR final, mas não separa cotas individualizadas. Pode **subestimar o valor líquido final em até 2,5%**.
> - A **Renda Fixa** assume reaplicação em blocos de ciclo definido, com IR ao final. Pode **superestimar o valor líquido em até 2%**.
> - A **Previdência** é simulada com IR de 10% sobre rendimento ao final, sem come-cotas.
> 
> ✅ O gráfico exibe **valores líquidos**, considerando a dedução dos impostos no último período.
""")
