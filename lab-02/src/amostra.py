"""Sorteia 300 fotos estratificadas pelos 4 lotes (75 por lote), seed fixa.
Uma foto por leitura (id sem o sufixo _NNN). 50 fotos (12-13 por lote) são comuns aos dois
rotuladores (dupla rotulagem às cegas); as outras 250 são divididas entre eles.
Saída: rotulos/lista_<rotulador>.csv e rotulos/amostra.csv (só nomes de arquivo)."""
import csv
import random
import re
from config import DADOS, LOTES, ROTULOS

SEED, POR_LOTE, COMUNS = 20261008, 75, 50
ROTULADORES = ["joao", "henrique"]
rng = random.Random(SEED)
amostra = []  # (arquivo, lote)
for pasta, lote in LOTES.items():
    fotos = sorted(p.name for p in (DADOS / pasta).glob("*.jpg"))
    por_leitura = {}
    for f in fotos:  # PSP_..._<id>_<NNN>.jpg
        por_leitura.setdefault(re.sub(r"_\d{3}\.jpg$", "", f), []).append(f)
    ids = sorted(por_leitura)
    for i in rng.sample(ids, POR_LOTE):
        amostra.append((rng.choice(por_leitura[i]), lote))
rng.shuffle(amostra)
comuns, resto = amostra[:COMUNS], amostra[COMUNS:]
metade = len(resto) // 2
listas = {ROTULADORES[0]: comuns + resto[:metade], ROTULADORES[1]: comuns + resto[metade:]}
ROTULOS.mkdir(exist_ok=True)
with open(ROTULOS / "amostra.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["nome_arquivo", "lote", "grupo"])
    for a in comuns: w.writerow([*a, "dupla"])
    for a in resto[:metade]: w.writerow([*a, ROTULADORES[0]])
    for a in resto[metade:]: w.writerow([*a, ROTULADORES[1]])
for nome, lst in listas.items():
    lst = lst[:]; random.Random(SEED + len(nome)).shuffle(lst)  # ordem embaralhada: dupla não se destaca
    with open(ROTULOS / f"lista_{nome}.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["nome_arquivo", "lote"]); w.writerows(lst)
    print(nome, len(lst), "fotos")
print("total distinto:", len(amostra))
