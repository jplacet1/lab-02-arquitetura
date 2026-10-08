"""Junta as fotos extras (rotulos_extra_<nome>.csv) ao rotulos.csv. Idempotente.
Aplica a regra da v2 (sem defeitos em cena_ocorrencia e nao_medidor) e confere duplicatas e leituras repetidas.
Uso (depois de aplicar_decisoes.py): python lab-02/src/juntar_extra.py"""
import re
import pandas as pd
from config import ROTULOS, PARTICAO

DEFEITOS = ["reflexo", "fora_de_foco", "tampa_suja", "enquadramento", "display_apagado"]
COLS = ["nome_arquivo", "lote", "rotulador", "cena", *DEFEITOS]
arqs = sorted(ROTULOS.glob("rotulos_extra_*.csv"))
if not arqs:
    raise SystemExit("nenhum rotulos_extra_*.csv encontrado")
extra = pd.concat([pd.read_csv(a) for a in arqs])
extra.loc[extra.cena.isin(["cena_ocorrencia", "nao_medidor"]), DEFEITOS] = 0
base = pd.read_csv(ROTULOS / "rotulos.csv")
base = base[~base.nome_arquivo.isin(extra.nome_arquivo)]  # idempotente
tudo = pd.concat([base[COLS], extra[COLS]], ignore_index=True)
id_leitura = tudo.nome_arquivo.str.replace(r"_\d{3}\.jpg$", "", regex=True)
assert not tudo.nome_arquivo.duplicated().any(), "foto repetida"
assert not id_leitura.duplicated().any(), "duas fotos da mesma leitura"
assert tudo.lote.isin(PARTICAO).all(), "lote desconhecido"
tudo.to_csv(ROTULOS / "rotulos.csv", index=False)
print(f"rotulos.csv: {len(tudo)} fotos ({len(extra)} extras de {[a.stem for a in arqs]})")
print(pd.crosstab(tudo.lote.map(PARTICAO), tudo.cena))
