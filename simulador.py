import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import io
from datetime import datetime

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
    return saldo_liquido, saldos, ir_total

def calcular_fundos_cotas_preciso(vp, pmt, taxa_mensal, n_meses):
    cotas = []
    total_aportado = vp
    saldos = []

    cotas.append({'valor': vp, 'rendimento_nt': 0, 'mes_entrada': 0})

    for i in range(1, n_meses + 1):
        for lote in cotas:
            rendimento = lote['valor'] * taxa_mensal
            lote['valor'] += rendimento
            lote['rendimento_nt'] += rendimento

        cotas.append({'valor': pmt, 'rendimento_nt': 0, 'mes_entrada': i})
        total_aportado += pmt

        if i % 12 == 5 or i % 12 == 11:
            for lote in cotas:
                imposto = lote['rendimento_nt'] * 0.15
                lote['valor'] -= imposto
                lote['rendimento_nt'] = 0

        saldos.append(sum(l['valor'] for l in cotas))

    rendimento_nt_total = sum(l['rendimento_nt'] for l in cotas)
    imposto_final = rendimento_nt_total * 0.15
    saldo_liquido = sum(l['valor'] for l in cotas) - imposto_final
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


def encontrar_taxa_equivalente(func, vp, pmt, target, *args):
    baixo = 0.0001
    alto = 1.0
    for _ in range(100):
        meio = (baixo + alto) / 2
        valor, *_ = func(vp, pmt, meio * 100, *args)
        if valor < target:
            baixo = meio
        else:
            alto = meio
    return meio * 100

def main():
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

    vl_prev, saldo_prev, ir_prev = calcular_previdencia_regressiva(vp, pmt, taxa_mensal, n_meses)
    vl_rf, saldo_rf = calcular_renda_fixa(vp, pmt, taxa_mensal, int(n_anos), int(ciclo))
    vl_fundos, saldo_fundos = calcular_fundos_cotas_preciso(vp, pmt, taxa_mensal, n_meses)

    df_resultados = pd.DataFrame({
        'Modalidade': ['Previdência VGBL', 'Renda Fixa', 'Fundos de Investimento'],
        'Valor Líquido Final (R$)': [formatar_reais(vl_prev), formatar_reais(vl_rf), formatar_reais(vl_fundos)],
        'IR Total (R$)': [formatar_reais(ir_prev), formatar_reais((vl_rf - (vp + pmt * n_meses)) * 0.15), formatar_reais((vl_fundos - (vp + pmt * n_meses)) * 0.15)]
    })

    st.subheader("📋 Resultados Comparativos")
    st.dataframe(df_resultados, use_container_width=True)

    df_evolucao = pd.DataFrame({
        'Mês': list(range(1, n_meses + 1)),
        'Previdência': saldo_prev,
        'Renda Fixa': saldo_rf,
        'Fundos': saldo_fundos
    })

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_evolucao['Mês'], y=df_evolucao['Previdência'], name='Previdência'))
    fig.add_trace(go.Scatter(x=df_evolucao['Mês'], y=df_evolucao['Renda Fixa'], name='Renda Fixa'))
    fig.add_trace(go.Scatter(x=df_evolucao['Mês'], y=df_evolucao['Fundos'], name='Fundos'))
    fig.update_layout(title="Evolução dos Investimentos", xaxis_title="Meses", yaxis_title="Valor (R$)")
    st.plotly_chart(fig, use_container_width=True)
    # Calcular taxas equivalentes

    taxa_eq_rf = encontrar_taxa_equivalente(calcular_renda_fixa, vp, pmt, vl_prev, int(n_anos), ciclo)

    taxa_eq_fundos = encontrar_taxa_equivalente(calcular_fundos_cotas_preciso, vp, pmt, vl_prev, int(n_anos))

    st.subheader('📊 Rentabilidade Bruta Necessária para Igualar à Previdência')
    df_eq = pd.DataFrame({
        'Modalidade': ['Renda Fixa', 'Fundos de Investimento'],
    'Taxa Bruta Anual Equivalente (%)': [f"{taxa_eq_rf:.2f}%", f"{taxa_eq_fundos:.2f}%"]
    }, index=[1, 2])
    st.dataframe(df_eq, use_container_width=True)

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df_evolucao.to_excel(writer, sheet_name='Evolução', index=False)
        df_resultados.to_excel(writer, sheet_name='Resumo', index=False)
    buffer.seek(0)

    st.download_button(
        label="📥 Baixar Excel com Resultados",
        data=buffer,
        file_name=f"simulador_tributario_{datetime.today().date()}.xlsx",
        mime="application/vnd.ms-excel"
    )

    st.markdown("""
    > ✅ **Melhorias implementadas:**
    > - Cálculo preciso do IR regressivo para Previdência
    > - Come-cotas semestral para Fundos de Investimento
    > - Tabela comparativa com IR total por modalidade
    > - Gráfico interativo com a evolução dos investimentos
    """)

if __name__ == "__main__":
    main()