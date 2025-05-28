
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
