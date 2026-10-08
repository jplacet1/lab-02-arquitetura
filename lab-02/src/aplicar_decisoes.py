"""Gera o rotulos.csv final: fotos comuns usam rotulos/decisoes.csv, as demais usam o rótulo de quem rotulou.
Aplica a regra da v2: cena_ocorrencia e nao_medidor ficam sem defeitos.
Uso: python lab-02/src/aplicar_decisoes.py   (rodar depois do kappa.py)"""
import pandas as pd
from config import ROTULOS

DEFEITOS = ["reflexo", "fora_de_foco", "tampa_suja", "enquadramento", "display_apagado"]

a = pd.read_csv(ROTULOS / "rotulos_joao.csv")
b = pd.read_csv(ROTULOS / "rotulos_henrique.csv")
dec = pd.read_csv(ROTULOS / "decisoes.csv")

base = pd.concat([a, b[~b.nome_arquivo.isin(a.nome_arquivo)]]).set_index("nome_arquivo")
dec = dec.set_index("nome_arquivo")
base.loc[dec.index, ["cena", *DEFEITOS]] = dec[["cena", *DEFEITOS]]
base.loc[dec.index, "rotulador"] = "dupla"
base.loc[base.cena.isin(["cena_ocorrencia", "nao_medidor"]), DEFEITOS] = 0
base.reset_index()[["nome_arquivo", "lote", "rotulador", "cena", *DEFEITOS]].to_csv(ROTULOS / "rotulos.csv", index=False)
print(f"rotulos.csv: {len(base)} fotos, {len(dec)} decididas pela dupla")
print(base.cena.value_counts().to_string())
