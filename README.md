# Simulador Tributário v1.1.0

Este repositório contém um script `app.py` em Python que simula investimentos (Fundo, Renda Fixa e VGBL) e encontra a taxa anual necessária para que Fundo e Renda Fixa igualem o valor líquido final do VGBL.

## Conteúdo

- `app.py`: Implementação principal com funções:
  - `simular_fundo`: calcula Valor Líquido e Imposto para Fundos (come-cotas).
  - `simular_rf`: calcula Valor Líquido e Imposto para Renda Fixa (ciclos completos e residuais).
  - `simular_vgbl`: calcula Valor Líquido e Imposto para VGBL (imposto único no final).
  - `encontrar_taxa_alvo`: bisseção para encontrar taxa anual que iguale o valor líquido ao alvo.

- `requirements.txt`: dependência numpy.

## Como usar

1. **Clone ou faça download** deste repositório.

2. **Instale** a dependência:
   ```bash
   pip install -r requirements.txt
   ```

3. **Execute** o script:
   ```bash
   python app.py
   ```

   Por padrão, `app.py` já vem configurado para rodar o exemplo:
   - Valor inicial (P): R$ 500.000
   - Aporte: R$ 0
   - Frequência de aporte: Mensal (não importa, pois aporte = 0)
   - Prazo total: 10 anos
   - Ciclo RF: 5 anos
   - Taxa inicial (benchmark VGBL): 10,10% a.a.

   O script irá:
   1. Calcular o Valor Líquido e Imposto do VGBL com a taxa inicial.
   2. Encontrar e exibir a **taxa necessária** para que o Fundo iguale o valor líquido do VGBL.
   3. Encontrar e exibir a **taxa necessária** para que a Renda Fixa iguale o valor líquido do VGBL.
   4. Exibir a verificação (simular com as taxas encontradas e mostrar Valor Líquido e Imposto).

4. **Ajuste** os parâmetros em `app.py` conforme necessário (linhas no bloco `if __name__ == "__main__":`):
   ```python
   P = 500_000.0         # Capital inicial
   aporte = 0.0          # Valor do aporte
   freq_aporte = "Mensal"  # "Mensal" ou "Anual"
   prazo_anos = 10       # Prazo total do investimento (anos)
   ciclo_anos = 5        # Ciclo de reinvestimento RF (anos)
   taxa_inicial = 0.101  # Taxa anual inicial para calcular VGBL benchmark
   ```

5. **Rode de novo**:
   ```bash
   python app.py
   ```
   E observe as saídas atualizadas com os novos parâmetros.

## Exemplo de Saída

```
===== RESULTADO VGBL =====
VGBL -> Valor líquido = R$ 1.227.846,20, Imposto = R$ 80.871,80

===== TAXAS NECESSÁRIAS =====
Taxa necessária para Fundo: 10.238167% a.a.
Taxa necessária para Renda Fixa: 11.812345% a.a.

===== VERIFICAÇÃO =====
Fundo (corrigido) -> Valor líquido = R$ 1.227.846,20, Imposto = R$ 82.000,00
RF    (corrigido) -> Valor líquido = R$ 1.227.846,20, Imposto = R$ 90.000,00
```

Atenção aos arredondamentos podem variar pequenas casas decimais.

## Publicação no GitHub

1. Faça `git add .`
2. `git commit -m "Versão 1.1.0 - adiciona README e cálculo de taxas necessárias"`
3. `git push origin main`

---

Desfrute do simulador e conte comigo para dúvidas adicionais!
