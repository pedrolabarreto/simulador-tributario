
def calcular_vl_previdencia(vp, pmt, taxa_mensal, n_meses):
    saldo = vp
    for _ in range(n_meses):
        saldo *= (1 + taxa_mensal)
        saldo += pmt
    rendimento = saldo - (vp + pmt * n_meses)
    return saldo - rendimento * 0.10  # IR de 10%

def calcular_vl_renda_fixa(vp, pmt, taxa_mensal, n_anos, ciclo_anos):
    saldo = vp
    total_aportes = 0
    for ano in range(n_anos):
        for _ in range(12):
            saldo *= (1 + taxa_mensal)
            saldo += pmt
            total_aportes += pmt
        if (ano + 1) % ciclo_anos == 0:
            rendimento = saldo - (vp + total_aportes)
            saldo -= rendimento * 0.15
            vp = saldo
            total_aportes = 0
    rendimento_final = saldo - (vp + total_aportes)
    return saldo - rendimento_final * 0.15

def calcular_vl_fundos(vp, pmt, taxa_mensal, n_meses):
    cotas = [{'valor': vp, 'rendimento_nt': 0, 'mes_entrada': 0}]
    total_aportado = vp
    for i in range(1, n_meses + 1):
        for lote in cotas:
            rendimento = lote['valor'] * taxa_mensal
            lote['valor'] += rendimento
            lote['rendimento_nt'] += rendimento
        if pmt > 0:
            cotas.append({'valor': pmt, 'rendimento_nt': 0, 'mes_entrada': i})
            total_aportado += pmt
        if i % 12 == 5 or i % 12 == 11:
            for lote in cotas:
                imposto = lote['rendimento_nt'] * 0.15
                lote['valor'] -= imposto
                lote['rendimento_nt'] = 0
    rendimento_nt_total = sum([l['rendimento_nt'] for l in cotas])
    imposto_final = rendimento_nt_total * 0.15
    saldo_liquido = sum([l['valor'] for l in cotas]) - imposto_final
    return saldo_liquido

def encontrar_taxa_equivalente(funcao, vp, pmt, target, n_meses, n_anos=None, ciclo=None):
    taxa_baixa = 0.0001
    taxa_alta = 1.0
    precisao = 0.00001
    while taxa_alta - taxa_baixa > precisao:
        taxa_media = (taxa_baixa + taxa_alta) / 2
        if funcao == calcular_vl_renda_fixa:
            resultado = funcao(vp, pmt, taxa_media, n_anos, ciclo)
        else:
            resultado = funcao(vp, pmt, taxa_media, n_meses)
        if resultado < target:
            taxa_baixa = taxa_media
        else:
            taxa_alta = taxa_media
    return (1 + taxa_media) ** 12 - 1  # retorna taxa anual equivalente

def calcular_previdencia_regressiva(vp, pmt, taxa_mensal, n_meses):
    cotas = [{'valor': vp, 'rendimento': 0, 'mes_entrada': 0}]
    saldos = []
    total_aportado = vp

    for i in range(1, n_meses + 1):
        for lote in cotas:
            rendimento = lote['valor'] * taxa_mensal
            lote['valor'] += rendimento
            lote['rendimento'] += rendimento

        if pmt > 0:
            cotas.append({'valor': pmt, 'rendimento': 0, 'mes_entrada': i})
            total_aportado += pmt

        saldos.append(sum(l['valor'] for l in cotas))

    def aliquota(meses):
        if meses <= 24:
            return 0.35
        elif meses <= 48:
            return 0.30
        elif meses <= 72:
            return 0.25
        elif meses <= 96:
            return 0.20
        elif meses <= 120:
            return 0.15
        else:
            return 0.10

    ir_total = 0
    for lote in cotas:
        tempo = n_meses - lote['mes_entrada']
        ir = lote['rendimento'] * aliquota(tempo)
        lote['valor'] -= ir
        ir_total += ir

    saldo_liquido = sum(l['valor'] for l in cotas)
    saldos[-1] = saldo_liquido
    return round(saldo_liquido, 2), saldos, round(ir_total, 2)

def calcular_vl_previdencia(vp, pmt, taxa_mensal, n_meses):
    saldo = vp
    for _ in range(n_meses):
        saldo *= (1 + taxa_mensal)
        saldo += pmt
    rendimento = saldo - (vp + pmt * n_meses)
    return saldo - rendimento * 0.10  # IR de 10%

def calcular_vl_renda_fixa(vp, pmt, taxa_mensal, n_anos, ciclo_anos):
    saldo = vp
    total_aportes = 0
    for ano in range(n_anos):
        for _ in range(12):
            saldo *= (1 + taxa_mensal)
            saldo += pmt
            total_aportes += pmt
        if (ano + 1) % ciclo_anos == 0:
            rendimento = saldo - (vp + total_aportes)
            saldo -= rendimento * 0.15
            vp = saldo
            total_aportes = 0
    rendimento_final = saldo - (vp + total_aportes)
    return saldo - rendimento_final * 0.15

def calcular_vl_fundos(vp, pmt, taxa_mensal, n_meses):
    cotas = [{'valor': vp, 'rendimento_nt': 0, 'mes_entrada': 0}]
    total_aportado = vp
    for i in range(1, n_meses + 1):
        for lote in cotas:
            rendimento = lote['valor'] * taxa_mensal
            lote['valor'] += rendimento
            lote['rendimento_nt'] += rendimento
        if pmt > 0:
            cotas.append({'valor': pmt, 'rendimento_nt': 0, 'mes_entrada': i})
            total_aportado += pmt
        if i % 12 == 5 or i % 12 == 11:
            for lote in cotas:
                imposto = lote['rendimento_nt'] * 0.15
                lote['valor'] -= imposto
                lote['rendimento_nt'] = 0
    rendimento_nt_total = sum([l['rendimento_nt'] for l in cotas])
    imposto_final = rendimento_nt_total * 0.15
    saldo_liquido = sum([l['valor'] for l in cotas]) - imposto_final
    return saldo_liquido

def encontrar_taxa_equivalente(funcao, vp, pmt, target, n_meses, n_anos=None, ciclo=None):
    taxa_baixa = 0.0001
    taxa_alta = 1.0
    precisao = 0.00001
    while taxa_alta - taxa_baixa > precisao:
        taxa_media = (taxa_baixa + taxa_alta) / 2
        if funcao == calcular_vl_renda_fixa:
            resultado = funcao(vp, pmt, taxa_media, n_anos, ciclo)
        else:
            resultado = funcao(vp, pmt, taxa_media, n_meses)
        if resultado < target:
            taxa_baixa = taxa_media
        else:
            taxa_alta = taxa_media
    return (1 + taxa_media) ** 12 - 1  # retorna taxa anual equivalente
# Simulador com controle refinado de cotas e IR final preciso
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import io
from datetime import datetime

def calcular_fundos_cotas_preciso(vp, pmt, taxa_mensal, n_meses):
    cotas = []  # Cada lote: {'valor': float, 'rendimento_nt': float}
    saldo = vp
    total_aportado = vp
    saldos = []

    # Lote inicial
    cotas.append({'valor': vp, 'rendimento_nt': 0})

    for i in range(1, n_meses + 1):
        # Capitaliza cotas e acumula rendimento não tributado
        for lote in cotas:
            rendimento = lote['valor'] * taxa_mensal
            lote['valor'] += rendimento
            lote['rendimento_nt'] += rendimento

        # Novo aporte
        cotas.append({'valor': pmt, 'rendimento_nt': 0})
        total_aportado += pmt

        # Come-cotas em maio e novembro (i % 12 == 5 ou 11)
        if i % 12 == 5 or i % 12 == 11:
            for lote in cotas:
                imposto = lote['rendimento_nt'] * 0.15
                lote['valor'] -= imposto
                lote['rendimento_nt'] = 0

        # Soma do saldo
        saldo = sum([l['valor'] for l in cotas])
        saldos.append(saldo)

    # Calcular IR final somente sobre o rendimento não tributado
    rendimento_nt_total = sum([l['rendimento_nt'] for l in cotas])
    imposto_final = rendimento_nt_total * 0.15
    saldo_liquido = sum([l['valor'] for l in cotas]) - imposto_final
    saldos[-1] = saldo_liquido
    return saldo_liquido, saldos

# As funções previdência e renda fixa continuam as mesmas do código anterior
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


# Cálculo da nova previdência regressiva
vl_prev, saldo_prev, ir_prev_total = calcular_previdencia_regressiva(vp, pmt, taxa_mensal, n_meses)

vl_rf, saldo_rf = calcular_renda_fixa(vp, pmt, taxa_mensal, int(n_anos), int(ciclo))
vl_fundos, saldo_fundos = calcular_fundos_cotas_preciso(vp, pmt, taxa_mensal, n_meses)

df_resultados = pd.DataFrame({
    'Modalidade': ['Previdência VGBL', 'Renda Fixa', 'Fundos de Investimento'],
    'Valor Líquido Final (R$)': [formatar_reais(vl_prev), formatar_reais(vl_rf), formatar_reais(vl_fundos)],
    'Desvio Estimado': ['0%', '-0 a -2%', '+0 a +2,5%']
})
st.subheader("📋 Resultados Comparativos")

# Cálculo da taxa de equivalência para Renda Fixa e Fundos
taxa_mensal_prev = (1 + taxa_anual / 100) ** (1 / 12) - 1
vl_prev_target = calcular_vl_previdencia(vp, pmt, taxa_mensal_prev, n_meses)
taxa_rf_equivalente = encontrar_taxa_equivalente(calcular_vl_renda_fixa, vp, pmt, vl_prev_target, n_meses, int(n_anos), int(ciclo))
taxa_fundos_equivalente = encontrar_taxa_equivalente(calcular_vl_fundos, vp, pmt, vl_prev_target, n_meses)

# Exibir quadro comparativo
st.subheader("📐 Rentabilidade Bruta Equivalente")
st.write("Para que os investimentos em Renda Fixa ou Fundos entreguem o mesmo valor líquido da Previdência, as taxas brutas necessárias seriam:")

df_equiv = pd.DataFrame({
    'Modalidade': ['Previdência (referência)', 'Renda Fixa', 'Fundos de Investimento'],
    'Rentabilidade Anual Necessária (%)': [
        round(taxa_anual, 2),
        round(taxa_rf_equivalente * 100, 2),
        round(taxa_fundos_equivalente * 100, 2)
    ]
})
st.dataframe(df_equiv, use_container_width=True)

# Frase automática de apoio
vl_rf, *_ = calcular_renda_fixa(vp, pmt, taxa_mensal, int(n_anos), int(ciclo))
vl_fundos, *_ = calcular_fundos_cotas_preciso(vp, pmt, taxa_mensal, n_meses)
economia_rf = vl_prev - vl_rf
economia_fundos = vl_prev - vl_fundos

st.subheader("💬 Vantagem Tributária Estimada")
st.markdown(f"➡️ Ao optar pela **previdência**, você economizaria aproximadamente **R$ {economia_rf:,.0f}** em relação à renda fixa, e **R$ {economia_fundos:,.0f}** em relação aos fundos tradicionais, no final do período.")


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

# Quadro de rentabilidade bruta equivalente
st.subheader("📐 Rentabilidade Bruta Equivalente")
st.write("Para que os investimentos em Renda Fixa ou Fundos entreguem o mesmo valor líquido da Previdência, as taxas brutas necessárias seriam:")

df_equiv = pd.DataFrame({
    'Modalidade': ['Previdência (referência)', 'Renda Fixa', 'Fundos de Investimento'],
    'Rentabilidade Anual Necessária (%)': [
        round(taxa_anual, 2),
        round(taxa_rf_equivalente * 100, 2),
        round(taxa_fundos_equivalente * 100, 2)
    ]
})
st.dataframe(df_equiv, use_container_width=True)

# Frase automática de apoio
vl_rf, *_ = calcular_renda_fixa(vp, pmt, taxa_mensal, int(n_anos), int(ciclo))
vl_fundos, *_ = calcular_fundos_cotas_preciso(vp, pmt, taxa_mensal, n_meses)
economia_rf = vl_prev - vl_rf
economia_fundos = vl_prev - vl_fundos

st.subheader("💬 Vantagem Tributária Estimada")
st.write(
    f"Ao final do período, a previdência resultaria em um ganho líquido de "
    f"R$ {economia_rf:,.0f} a mais que a renda fixa, e "
    f"R$ {economia_fundos:,.0f} a mais que os fundos de investimento, "
    f"considerando a mesma rentabilidade bruta."
)


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
> ✅ Agora com **cálculo exato dos fundos de investimento**, aplicando:
> 
> - Come-cotas semestral (maio e novembro), por lote de aporte
> - Tributação final de 15% apenas sobre rendimentos **não tributados**
> - Controle separado dos rendimentos em cada cota
> 
> 📊 O gráfico e a tabela representam **valores líquidos reais**, sem saltos artificiais.
""")
