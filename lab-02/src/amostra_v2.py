"""Sorteia 30 fotos novas (7-8 por lote) para a dupla rotulagem às cegas sob o esquema v2.
Exclui toda leitura já sorteada em amostra.csv. Os dois rotulam as mesmas 30.
Saída: rotulos/lista_v2_joao.csv, rotulos/lista_v2_henrique.csv, rotulos/amostra_v2.csv.
Rotular: python rotular.py joao v2   (ou henrique v2)"""
import csv
import random
import re
from config import DADOS, LOTES, ROTULOS

SEED, TOTAL = 20261009, 30
ROTULADORES = ["joao", "henrique"]
id_leitura = lambda f: re.sub(r"_\d{3}\.jpg$", "", f)
usadas = set()
with open(ROTULOS / "amostra.csv", encoding="utf-8") as fh:
    usadas = {id_leitura(r["nome_arquivo"]) for r in csv.DictReader(fh)}
rng = random.Random(SEED)
cotas = [TOTAL // len(LOTES) + (1 if i < TOTAL % len(LOTES) else 0) for i in range(len(LOTES))]
itens = []
for (pasta, lote), n in zip(LOTES.items(), cotas):
    por_leitura = {}
    for f in sorted(p.name for p in (DADOS / pasta).glob("*.jpg")):
        por_leitura.setdefault(id_leitura(f), []).append(f)
    livres = sorted(set(por_leitura) - usadas)
    itens += [(rng.choice(por_leitura[i]), lote) for i in rng.sample(livres, n)]
rng.shuffle(itens)
with open(ROTULOS / "amostra_v2.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(["nome_arquivo", "lote"]); w.writerows(itens)
for nome in ROTULADORES:
    lst = itens[:]; random.Random(SEED + len(nome)).shuffle(lst)  # ordens diferentes
    with open(ROTULOS / f"lista_v2_{nome}.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["nome_arquivo", "lote"]); w.writerows(lst)
print(len(itens), "fotos novas", dict(zip(LOTES.values(), cotas)))
