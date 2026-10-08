"""C4: partição por lote e prova numérica de que nenhum id de leitura nem número de medidor está em dois conjuntos.
Confere (a) as 300 fotos rotuladas e (b) a base inteira (12.340 fotos).
Saída: rotulos/particao.csv (resumo) e rotulos/particao_vazamento.csv (medidores repetidos entre conjuntos).
Uso: python lab-02/src/particao.py"""
import re
import pandas as pd
from config import DADOS, LOTES, PARTICAO, ROTULOS

def id_leitura(foto):
    return re.sub(r"_\d{3}\.jpg$", "", foto)

linhas = []
for pasta, lote in LOTES.items():
    csv = next((DADOS / pasta).glob("BaseExtracao_*.csv"))
    d = pd.read_csv(csv, sep=";", encoding="latin1", dtype=str)
    d = d[d["Foto do medidor"].notna() & (d["Foto do medidor"] != "NA")]
    for _, r in d.iterrows():
        for m in r["Numero do medidor"].split("/"):  # "A/B" = dois medidores na mesma foto
            linhas.append((r["Foto do medidor"], id_leitura(r["Foto do medidor"]), m.strip(), lote))
base = pd.DataFrame(linhas, columns=["foto", "id_leitura", "medidor", "lote"])
base["conjunto"] = base.lote.map(PARTICAO)

rot = pd.read_csv(ROTULOS / "rotulos.csv")
rotulada = base[base.foto.isin(rot.nome_arquivo)]
print(f"fotos rotuladas encontradas no CSV da base: {rotulada.foto.nunique()} de {len(rot)}")

def vazamento(df, chave):
    n = df.groupby(chave).conjunto.nunique()
    return n[n > 1].index

res = []
for nome, df in [("rotuladas (300)", rotulada), ("base inteira", base)]:
    for chave in ["id_leitura", "medidor"]:
        res.append((nome, chave, df[chave].nunique(), len(vazamento(df, chave))))
    print(nome, df.groupby("conjunto").foto.nunique().to_dict())
tab = pd.DataFrame(res, columns=["universo", "chave", "valores_distintos", "em_2_ou_mais_conjuntos"])
print(tab.to_string(index=False))
tab.to_csv(ROTULOS / "particao.csv", index=False)

vaz = base[base.medidor.isin(vazamento(base, "medidor"))].sort_values(["medidor", "lote"])
vaz.to_csv(ROTULOS / "particao_vazamento.csv", index=False)
print("rotuladas com medidor presente em outro conjunto:",
      rotulada.medidor.isin(vazamento(base, "medidor")).sum(), "de", len(rotulada))
