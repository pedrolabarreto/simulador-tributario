# app.py - Versão 1.2.0

import numpy as np

def aliquota_regressiva(meses):
    """
    Retorna a alíquota de IR para cada fundo/renda fixa (lote a lote),
    segundo esquema regressivo:
      - 0–6 meses   : 22,5%
      - 7–12 meses  : 20%
      - 13–24 meses : 17,5%
      - >24 meses   : 15%
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
    Retorna a alíquota de IR para VGBL no momento do resgate, por lote:
      - até  24 meses (2 anos) : 35%
      - até  48 meses (4 anos) : 30%
      - até  72 meses (6 anos) : 25%
      - até  96 meses (8 anos) : 20%
      - até 120 meses (10 anos): 15%
      - > 120 meses           : 10%
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

def simular_fundo(valor_inicial, aporte, freq_aporte, taxa_anual, prazo_anos):
    """
    Simula fundo de investimento lote a lote, com come-cotas semestrais (maio e novembro)
    e alíquotas regressivas por lote, aplicando aporte (Mensal ou Anual).
    Retorna: (valor_final_líquido, imposto_total_pago)
    """
    meses_totais = int(prazo_anos * 12)
    taxa_mensal = (1 + taxa_anual) ** (1 / 12) - 1

    lotes = [[valor_inicial, valor_inicial, 0]]
    imposto_total = 0.0

    for mes in range(1, meses_totais + 1):
        # Inserir aporte
        if freq_aporte == "Mensal":
            lotes.append([aporte, aporte, mes - 1])
        elif freq_aporte == "Anual" and (mes - 1) % 12 == 0 and (mes - 1) > 0:
            lotes.append([aporte, aporte, mes - 1])

        # Crescimento mensal
        for lote in lotes:
            lote[0] *= (1 + taxa_mensal)

        # Come-cotas em maio (5) e novembro (11)
        mes_do_ano = ((mes - 1) % 12) + 1
        if mes_do_ano in (5, 11):
            for i, (valor, base, mes_ap) in enumerate(lotes):
                holding = mes - mes_ap
                ganho = valor - base
                if ganho > 0:
                    alq = aliquota_regressiva(holding)
                    imposto = ganho * alq
                    valor_liquido = valor - imposto
                    lotes[i][0] = valor_liquido
                    lotes[i][1] = valor_liquido
                    imposto_total += imposto

    valor_final = sum(lote[0] for lote in lotes)
    return valor_final, imposto_total

def simular_rf(valor_inicial, aporte, freq_aporte, taxa_anual, prazo_anos, ciclo_anos):
    """
    Simula títulos de renda fixa lote a lote, com tributação regressiva ao final de cada ciclo.
    Se ciclo_anos <= 0, não tributa periodicamente, apenas tributa no fim.
    Retorna: (valor_final_líquido, imposto_total_pago)
    """
    meses_totais = int(prazo_anos * 12)
    taxa_mensal = (1 + taxa_anual) ** (1 / 12) - 1
    ciclo_meses = int(ciclo_anos * 12) if ciclo_anos > 0 else None

    lotes = [[valor_inicial, valor_inicial, 0]]
    imposto_total = 0.0

    for mes in range(1, meses_totais + 1):
        # Inserir aporte
        if freq_aporte == "Mensal":
            lotes.append([aporte, aporte, mes - 1])
        elif freq_aporte == "Anual" and (mes - 1) % 12 == 0 and (mes - 1) > 0:
            lotes.append([aporte, aporte, mes - 1])

        # Crescimento mensal
        for lote in lotes:
            lote[0] *= (1 + taxa_mensal)

        # Tributar a cada ciclo completo, se aplicável
        if ciclo_meses and mes % ciclo_meses == 0:
            for i, (valor, base, mes_ap) in enumerate(lotes):
                holding = mes - mes_ap
                ganho = valor - base
                if ganho > 0:
                    alq = aliquota_regressiva(holding)
                    imposto = ganho * alq
                    valor_liquido = valor - imposto
                    lotes[i][0] = valor_liquido
                    lotes[i][1] = valor_liquido
                    imposto_total += imposto

    # Tributar resíduo final se houver e ciclo aplicável
    if ciclo_meses:
        for i, (valor, base, mes_ap) in enumerate(lotes):
            holding = meses_totais - mes_ap
            if holding > 0 and (holding % ciclo_meses != 0):
                ganho = valor - base
                if ganho > 0:
                    alq = aliquota_regressiva(holding)
                    imposto = ganho * alq
                    valor_liquido = valor - imposto
                    lotes[i][0] = valor_liquido
                    imposto_total += imposto
    else:
        # se sem ciclo, tributa tudo no fim
        for i, (valor, base, mes_ap) in enumerate(lotes):
            holding = meses_totais - mes_ap
            ganho = valor - base
            if ganho > 0:
                alq = aliquota_regressiva(holding)
                imposto = ganho * alq
                valor_liquido = valor - imposto
                lotes[i][0] = valor_liquido
                imposto_total += imposto

    valor_final = sum(lote[0] for lote in lotes)
    return valor_final, imposto_total

def simular_vgbl(valor_inicial, aporte, freq_aporte, taxa_anual, prazo_anos):
    """
    Simula VGBL lote a lote, tributado apenas no final.
    Retorna: (valor_final_líquido, imposto_total_pago)
    """
    meses_totais = int(prazo_anos * 12)
    taxa_mensal = (1 + taxa_anual) ** (1 / 12) - 1

    lotes = [[valor_inicial, 0]]
    imposto_total = 0.0

    for mes in range(1, meses_totais + 1):
        # Inserir aporte
        if freq_aporte == "Mensal":
            lotes.append([aporte, mes - 1])
        elif freq_aporte == "Anual" and (mes - 1) % 12 == 0 and (mes - 1) > 0:
            lotes.append([aporte, mes - 1])

        # Crescimento mensal
        for lote in lotes:
            lote[0] *= (1 + taxa_mensal)

    valor_final = 0.0
    for valor, mes_ap in lotes:
        holding = meses_totais - mes_ap
        alq = aliquota_vgbl(holding)
        original = valor / ((1 + taxa_mensal) ** holding)
        ganho = valor - original
        imposto = ganho * alq
        imposto_total += imposto
        valor_final += valor - imposto

    return valor_final, imposto_total

def encontrar_taxa_alvo(func, args, alvo, low=0.0, high=1.0, tol=1e-6, max_iter=100):
    """
    Encontra taxa anual para que func(*args, taxa_anual)[0] seja igual a alvo,
    usando bisseção no intervalo [low, high].
    func deve retornar (valor_final, imposto).
    """
    def valor_final_taxa(taxa):
        val, _ = func(*args, taxa)
        return val

    # Ajustar high caso insuficiente
    for _ in range(20):
        if valor_final_taxa(high) < alvo:
            high *= 2
        else:
            break

    for _ in range(max_iter):
        mid = (low + high) / 2
        val_mid = valor_final_taxa(mid)
        if abs(val_mid - alvo) < tol:
            return mid
        if val_mid < alvo:
            low = mid
        else:
            high = mid
    return (low + high) / 2

if __name__ == "__main__":
    # Parâmetros exemplo
    P = 500_000.0
    aporte = 0.0
    freq_aporte = "Mensal"
    prazo_anos = 10
    ciclo_anos = 5  # se definir como 0, tributa só no fim
    taxa_inicial = 0.101  # utilizado apenas para calcular VGBL benchmark

    # 1) Calcular VGBL benchmark
    vf_vgbl, imp_vgbl = simular_vgbl(P, aporte, freq_aporte, taxa_inicial, prazo_anos)
    print(f"VGBL -> Valor líquido = R$ {vf_vgbl:,.2f}, Imposto = R$ {imp_vgbl:,.2f}")

    # 2) Encontrar taxa necessária para Fundo
    args_fundo = (P, aporte, freq_aporte, prazo_anos)
    taxa_fundo_necessaria = encontrar_taxa_alvo(simular_fundo, args_fundo, vf_vgbl)
    print(f"Taxa necessária para Fundo: {taxa_fundo_necessaria*100:.6f}% a.a.")

    # 3) Encontrar taxa necessária para RF
    args_rf = (P, aporte, freq_aporte, prazo_anos, ciclo_anos)
    taxa_rf_necessaria = encontrar_taxa_alvo(simular_rf, args_rf, vf_vgbl)
    print(f"Taxa necessária para Renda Fixa: {taxa_rf_necessaria*100:.6f}% a.a.")

    # 4) Verificação
    vf_fundo_corr, imp_fundo_corr = simular_fundo(P, aporte, freq_aporte, taxa_fundo_necessaria, prazo_anos)
    vf_rf_corr, imp_rf_corr = simular_rf(P, aporte, freq_aporte, taxa_rf_necessaria, prazo_anos, ciclo_anos)
    print(f"Fundo (corrigido) -> Valor líquido = R$ {vf_fundo_corr:,.2f}, Imposto = R$ {imp_fundo_corr:,.2f}")
    print(f"RF    (corrigido) -> Valor líquido = R$ {vf_rf_corr:,.2f}, Imposto = R$ {imp_rf_corr:,.2f}")
