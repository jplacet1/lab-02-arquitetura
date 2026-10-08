"""Sorteia fotos EXTRAS para rotular (mais dados de treino, validação e teste), divididas entre 2 rotuladores.
50 por lote (200 no total), uma foto por leitura, sem repetir nenhuma leitura de amostra.csv nem de amostra_v2.csv.
Cada foto vai para um rotulador só (sem dupla): o esquema já passou do kappa 0,6 na v2.
Saída: rotulos/lista_extra_<nome>.csv e rotulos/amostra_extra.csv.
Rotular: python rotular.py <nome> extra"""
import csv
import random
import re
from config import DADOS, LOTES, ROTULOS

SEED, POR_LOTE = 20261010, 50
ROTULADORES = ["joao", "henrique"]
id_leitura = lambda f: re.sub(r"_\d{3}\.jpg$", "", f)
usadas = set()
for arq in ["amostra.csv", "amostra_v2.csv"]:
    with open(ROTULOS / arq, encoding="utf-8") as fh:
        usadas |= {id_leitura(r["nome_arquivo"]) for r in csv.DictReader(fh)}
rng = random.Random(SEED)
itens = []
for pasta, lote in LOTES.items():
    por_leitura = {}
    for f in sorted(p.name for p in (DADOS / pasta).glob("*.jpg")):
        por_leitura.setdefault(id_leitura(f), []).append(f)
    livres = sorted(set(por_leitura) - usadas)
    itens += [(rng.choice(por_leitura[i]), lote) for i in rng.sample(livres, POR_LOTE)]
rng.shuffle(itens)
partes = {n: itens[i::len(ROTULADORES)] for i, n in enumerate(ROTULADORES)}
with open(ROTULOS / "amostra_extra.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(["nome_arquivo", "lote", "rotulador"])
    for n, p in partes.items():
        for a in p: w.writerow([*a, n])
for n, p in partes.items():
    with open(ROTULOS / f"lista_extra_{n}.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["nome_arquivo", "lote"]); w.writerows(p)
    print(n, len(p), "fotos")
print("total:", len(itens))
