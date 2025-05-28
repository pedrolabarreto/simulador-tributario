
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Funções de cálculo
def calcular_previdencia(vp, pmt, taxa, n_meses):
    taxa_mensal = (1 + taxa / 100) ** (1/12) - 1
    saldo = vp
    for _ in range(n_meses):
        saldo *= (1 + taxa_mensal)
        saldo += pmt
    return saldo, []

def calcular_rf_corrigido(vp, pmt, taxa, anos, ciclo):
    taxa_anual = taxa / 100
    meses = anos * 12
    ciclo_meses = ciclo * 12
    aportes = [(0, vp)]
    for m in range(1, meses + 1):
        if pmt > 0:
            aportes.append((m, pmt))

    saldos = []
    for m in range(meses + 1):
        saldo = 0
        for mes_aporte, valor in aportes:
            idade = m - mes_aporte
            if idade < 0:
                continue
            ciclos_completos = idade // ciclo_meses
            meses_restantes = idade % ciclo_meses
            if ciclos_completos == 0:
                taxa_efetiva = (1 + taxa_anual) ** (idade / 12)
                saldo += valor * taxa_efetiva
            else:
                valor_liquido = valor
                for _ in range(ciclos_completos):
                    bruto = valor_liquido * ((1 + taxa_anual) ** ciclo)
                    lucro = bruto - valor_liquido
                    valor_liquido = bruto - lucro * 0.15
                saldo += valor_liquido * ((1 + taxa_anual) ** (meses_restantes / 12))
        saldos.append(saldo)
    return saldos[-1], saldos

def calcular_fundos_preciso(vp, pmt, taxa, anos):
    taxa_mensal = (1 + taxa / 100) ** (1 / 12) - 1
    cotas = [{'valor': vp, 'rendimento_nt': 0, 'mes_entrada': 0}]
    n_meses = anos * 12

    for i in range(1, n_meses + 1):
        for lote in cotas:
            rendimento = lote['valor'] * taxa_mensal
            lote['valor'] += rendimento
            lote['rendimento_nt'] += rendimento
        if pmt > 0:
            cotas.append({'valor': pmt, 'rendimento_nt': 0, 'mes_entrada': i})
        if i % 12 == 5 or i % 12 == 11:
            for lote in cotas:
                if lote['mes_entrada'] <= i - 6:
                    imposto = lote['rendimento_nt'] * 0.15
                    lote['valor'] -= imposto
                    lote['rendimento_nt'] = 0

    rendimento_nt_total = sum([l['rendimento_nt'] for l in cotas])
    imposto_final = rendimento_nt_total * 0.15
    saldo_liquido = sum([l['valor'] for l in cotas]) - imposto_final
    return saldo_liquido, []

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

# Interface
st.title("Simulador Tributário – Previdência x Fundos x Renda Fixa")

vp = st.number_input("Aporte Inicial (R$)", value=500000)
pmt = st.number_input("Aporte Mensal (R$)", value=5000)
anos = st.slider("Prazo (anos)", min_value=2, max_value=50, value=25)
taxa_prev = st.number_input("Retorno Anual Previdência (%)", value=10.0)
ciclo = st.number_input("Ciclo Renda Fixa (anos)", value=4)

n_meses = anos * 12
vl_prev, _ = calcular_previdencia(vp, pmt, taxa_prev, n_meses)
vl_rf, _ = calcular_rf_corrigido(vp, pmt, taxa_prev, anos, ciclo)
vl_fundos, _ = calcular_fundos_preciso(vp, pmt, taxa_prev, anos)

st.markdown("### Valor Futuro Líquido ao Final do Período")
df_vf = pd.DataFrame({
    "Modalidade": ["Previdência", "Renda Fixa", "Fundos"],
    "Valor Líquido Final (R$)": [round(vl_prev, 2), round(vl_rf, 2), round(vl_fundos, 2)]
})
st.dataframe(df_vf.set_index("Modalidade"))

# Taxas equivalentes
taxa_eq_rf = encontrar_taxa_equivalente(calcular_rf_corrigido, vp, pmt, vl_prev, anos, ciclo)
taxa_eq_fundos = encontrar_taxa_equivalente(calcular_fundos_preciso, vp, pmt, vl_prev, anos)

st.markdown("### Rentabilidade Bruta Necessária para Igualar à Previdência")
df_taxas = pd.DataFrame({
    "Modalidade": ["Renda Fixa", "Fundos"],
    "Taxa Bruta Anual Equivalente (%)": [f"{taxa_eq_rf:.2f}%", f"{taxa_eq_fundos:.2f}%"]
})
st.dataframe(df_taxas.set_index("Modalidade"))
