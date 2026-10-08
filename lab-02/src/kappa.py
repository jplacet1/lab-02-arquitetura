"""Kappa de Cohen por classe nas fotos rotuladas pelos dois (dupla às cegas) e junta rotulos.csv."""
import sys
import pandas as pd
from sklearn.metrics import cohen_kappa_score
from config import ROTULOS

V2 = len(sys.argv) > 1 and sys.argv[1] == "v2"  # python kappa.py v2: só mede o kappa da rodada v2
PREF = "v2_" if V2 else ""

a = pd.read_csv(ROTULOS / f"rotulos_{PREF}joao.csv")
b = pd.read_csv(ROTULOS / f"rotulos_{PREF}henrique.csv")
dupla = a.merge(b, on="nome_arquivo", suffixes=("_a", "_b"))
print(f"fotos rotuladas pelos dois: {len(dupla)}")
linhas = [("cena (4 classes)", cohen_kappa_score(dupla.cena_a, dupla.cena_b))]
for c in ["digital", "ciclometrico", "cena_ocorrencia", "nao_medidor"]:
    linhas.append((f"cena={c}", cohen_kappa_score(dupla.cena_a == c, dupla.cena_b == c)))
for d in ["reflexo", "fora_de_foco", "tampa_suja", "enquadramento", "display_apagado"]:
    linhas.append((f"defeito={d}", cohen_kappa_score(dupla[d + "_a"], dupla[d + "_b"])))
tab = pd.DataFrame(linhas, columns=["classe", "kappa"]).round(3)
tab["ok(>=0,6)"] = tab.kappa >= 0.6
print(tab.to_string(index=False))
tab.to_csv(ROTULOS / ("kappa_v2.csv" if V2 else "kappa.csv"), index=False)
if V2:
    sys.exit()  # não mexe no rotulos.csv
# rotulos.csv final: fotos comuns ficam com o rótulo de joao (adjudicar divergências antes, se quiserem)
final = pd.concat([a, b[~b.nome_arquivo.isin(a.nome_arquivo)]])
final.to_csv(ROTULOS / "rotulos.csv", index=False)
print("rotulos.csv:", len(final), "fotos")
