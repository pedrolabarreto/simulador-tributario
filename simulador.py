
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ------------------------
# Funções de cálculo
# ------------------------

def calcular_previdencia(vp, pmt, taxa_anual, n_meses):
    taxa_mensal = (1 + taxa_anual / 100) ** (1/12) - 1
    saldo = vp
    saldos = [saldo]
    for i in range(1, n_meses + 1):
        saldo *= (1 + taxa_mensal)
        saldo += pmt
        saldos.append(saldo)
    return saldo, saldos

def calcular_renda_fixa(vp, pmt, taxa_anual, anos, ciclo):
    taxa_mensal = (1 + taxa_anual / 100) ** (1/12) - 1
    meses = anos * 12
    ciclo_meses = ciclo * 12
    saldos = []
    total = 0

    for i in range(meses):
        if i == 0:
            blocos = [{'valor': vp, 'meses': 0}]
        else:
            blocos = [{'valor': b['valor'] * (1 + taxa_mensal), 'meses': b['meses'] + 1} for b in blocos]
        if pmt > 0:
            blocos.append({'valor': pmt, 'meses': 0})
        novos_blocos = []
        for b in blocos:
            if b['meses'] >= ciclo_meses:
                total += b['valor'] * 0.85
            else:
                novos_blocos.append(b)
        blocos = novos_blocos
        saldos.append(total + sum([b['valor'] for b in blocos]))
    return saldos[-1], saldos

def calcular_fundos(vp, pmt, taxa_anual, n_meses):
    taxa_mensal = (1 + taxa_anual / 100) ** (1/12) - 1
    cotas = [{'valor': vp, 'rendimento_nt': 0, 'mes_entrada': 0}]
    saldos = []

    for i in range(1, n_meses + 1):
        for lote in cotas:
            rendimento = lote['valor'] * taxa_mensal
            lote['valor'] += rendimento
            lote['rendimento_nt'] += rendimento
        if pmt > 0:
            cotas.append({'valor': pmt, 'rendimento_nt': 0, 'mes_entrada': i})
        if i % 12 == 5 or i % 12 == 11:
            for lote in cotas:
                ultimo_comecotas = i - 6
                if lote['mes_entrada'] <= ultimo_comecotas:
                    imposto = lote['rendimento_nt'] * 0.15
                    lote['valor'] -= imposto
                    lote['rendimento_nt'] = 0
        saldos.append(sum([l['valor'] for l in cotas]))
    rendimento_nt_total = sum([l['rendimento_nt'] for l in cotas])
    imposto_final = rendimento_nt_total * 0.15
    saldo_liquido = sum([l['valor'] for l in cotas]) - imposto_final
    saldos[-1] = saldo_liquido
    return saldo_liquido, saldos

# ------------------------
# Interface
# ------------------------

st.title("Simulador de Projeção de Capital - Impacto Tributário")

vp = st.number_input("Aporte Inicial (R$)", value=100000.0, step=1000.0)
pmt = st.number_input("Aporte Mensal (R$)", value=5000.0, step=500.0)
taxa = st.number_input("Taxa de Retorno Anual (%)", value=10.0, step=0.5)
anos = st.number_input("Prazo (anos)", value=20, step=1, min_value=2)
ciclo = st.number_input("Ciclo de Renda Fixa (anos)", value=4, step=1, min_value=1)

n_meses = int(anos * 12)

vl_prev, prev_saldos = calcular_previdencia(vp, pmt, taxa, n_meses)
vl_rf, rf_saldos = calcular_renda_fixa(vp, pmt, taxa, anos, ciclo)
vl_fundos, fundos_saldos = calcular_fundos(vp, pmt, taxa, n_meses)

df_resultados = pd.DataFrame({
    'Modalidade': ['Previdência VGBL', 'Renda Fixa', 'Fundos de Investimento'],
    'Valor Líquido Final (R$)': [vl_prev, vl_rf, vl_fundos],
    'Desvio Estimado': ['0%', '-0 a -2%', '+0 a +2,5%']
})
st.subheader("📋 Resultados Comparativos")
st.dataframe(df_resultados, use_container_width=True)

# ------------------------
# Gráfico
# ------------------------

fig = go.Figure()
fig.add_trace(go.Scatter(y=prev_saldos, name="Previdência", line=dict(color="blue")))
fig.add_trace(go.Scatter(y=rf_saldos, name="Renda Fixa", line=dict(color="lightblue")))
fig.add_trace(go.Scatter(y=fundos_saldos, name="Fundos", line=dict(color="red")))
fig.update_layout(title="Evolução do Capital Acumulado",
                  xaxis_title="Meses",
                  yaxis_title="Saldo Acumulado (R$)",
                  hovermode="x unified")

st.plotly_chart(fig, use_container_width=True)
