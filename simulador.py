# Simulador Web de Projeção de Capital com Impacto Tributário
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def calcular_previdencia(vp, pmt, taxa_mensal, n_meses):
    saldo = vp
    saldos = []
    for _ in range(n_meses):
        saldo *= (1 + taxa_mensal)
        saldo += pmt
        saldos.append(saldo)
    rendimento = saldo - (vp + pmt * n_meses)
    return saldo - rendimento * 0.10, saldos

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
    return saldo, saldos

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
    saldo -= imposto_final
    return saldo, saldos

st.title("Simulador de Projeção de Capital - Impacto Tributário")

st.sidebar.header("Parâmetros de Entrada")
vp = st.sidebar.number_input("Aporte Inicial (R$)", value=50000.0)
pmt = st.sidebar.number_input("Aporte Mensal (R$)", value=5000.0)
taxa_anual = st.sidebar.number_input("Taxa de Retorno Anual (%)", value=10.0)
n_anos = st.sidebar.number_input("Prazo (anos)", min_value=2, value=25)
ciclo = st.sidebar.number_input("Ciclo de Renda Fixa (anos)", min_value=1, value=4)

n_meses = int(n_anos * 12)
taxa_mensal = (1 + taxa_anual / 100) ** (1 / 12) - 1

vl_previdencia, saldo_prev = calcular_previdencia(vp, pmt, taxa_mensal, n_meses)
vl_renda_fixa, saldo_rf = calcular_renda_fixa(vp, pmt, taxa_mensal, n_anos, ciclo)
vl_fundos, saldo_fundos = calcular_fundos(vp, pmt, taxa_mensal, n_meses)

st.subheader("Resultados - Valor Líquido Final")
df = pd.DataFrame({
    'Modalidade': ['Previdência VGBL', 'Renda Fixa', 'Fundos de Investimento'],
    'Valor Líquido Final (R$)': [vl_previdencia, vl_renda_fixa, vl_fundos],
    'Desvio Estimado': ['0%', '-0 a -2%', '+0 a +2,5%']
})
st.dataframe(df, use_container_width=True)

st.subheader("Evolução do Capital Acumulado")
plt.figure(figsize=(10, 5))
plt.plot(saldo_prev, label="Previdência")
plt.plot(saldo_rf, label="Renda Fixa")
plt.plot(saldo_fundos, label="Fundos")
plt.xlabel("Meses")
plt.ylabel("Saldo Acumulado (R$)")
plt.legend()
plt.grid(True)
st.pyplot(plt)

st.markdown("""
> ⚠️ **Nota sobre precisão**:
> 
> - A simulação dos **Fundos** considera come-cotas e IR final, mas não separa cotas individualizadas. Pode **subestimar o valor líquido final em até 2,5%**.
> - A **Renda Fixa** assume reaplicação em blocos de ciclo definido, com IR ao final. Pode **superestimar o valor líquido em até 2%**.
> - A **Previdência** é simulada com IR de 10% sobre rendimento ao final, sem come-cotas.
""")
