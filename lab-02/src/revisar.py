"""Revisão conjunta das divergências. Uso: python lab-02/src/revisar.py
Mostra cada foto de rotulos/divergencias.csv com o que cada um marcou e grava a decisão da dupla
em rotulos/decisoes.csv a cada foto.
Teclas: 1-4 cena | q w e r t defeitos (liga/desliga) | Enter salva e avança | Backspace volta.
Em cena_ocorrencia e nao_medidor os defeitos são zerados ao salvar (regra da v2)."""
import csv
import tkinter as tk
import pandas as pd
from PIL import Image, ImageTk
from config import DADOS, LOTES, ROTULOS

CENAS = ["digital", "ciclometrico", "cena_ocorrencia", "nao_medidor"]
DEFEITOS = ["reflexo", "fora_de_foco", "tampa_suja", "enquadramento", "display_apagado"]
TECLAS_DEF = "qwert"
pasta_do_lote = {v: k for k, v in LOTES.items()}

a = pd.read_csv(ROTULOS / "rotulos_joao.csv").set_index("nome_arquivo")
b = pd.read_csv(ROTULOS / "rotulos_henrique.csv").set_index("nome_arquivo")
itens = pd.read_csv(ROTULOS / "divergencias.csv").to_dict("records")
saida = ROTULOS / "decisoes.csv"
feitos = {}
if saida.exists():
    with open(saida, encoding="utf-8") as fh:
        feitos = {r["nome_arquivo"]: r for r in csv.DictReader(fh)}

def salvar():
    with open(saida, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, ["nome_arquivo", "lote", "cena", *DEFEITOS])
        w.writeheader()
        for it in itens:
            if it["nome_arquivo"] in feitos:
                w.writerow(feitos[it["nome_arquivo"]])

def resumo(rot, nome):
    defs = ", ".join(d for d in DEFEITOS if rot[d]) or "-"
    return f"{nome}: {rot['cena']} | defeitos: {defs}"

raiz = tk.Tk(); raiz.title("Revisão das divergências")
rotulo_img = tk.Label(raiz); rotulo_img.pack()
info = tk.Label(raiz, font=("Segoe UI", 11), justify="left"); info.pack()
var_cena = tk.StringVar(value="")
var_def = {d: tk.IntVar() for d in DEFEITOS}
quadro = tk.Frame(raiz); quadro.pack()
for i, c in enumerate(CENAS):
    tk.Radiobutton(quadro, text=f"[{i+1}] {c}", variable=var_cena, value=c).grid(row=0, column=i, padx=6)
for i, d in enumerate(DEFEITOS):
    tk.Checkbutton(quadro, text=f"[{TECLAS_DEF[i]}] {d}", variable=var_def[d]).grid(row=1, column=i, padx=6)
estado = {"i": next((k for k, it in enumerate(itens) if it["nome_arquivo"] not in feitos), 0)}

def mostrar():
    i = estado["i"]
    if i >= len(itens):
        info.config(text="Terminou. Pode fechar."); rotulo_img.config(image=""); return
    it = itens[i]
    img = Image.open(DADOS / pasta_do_lote[it["lote"]] / it["nome_arquivo"])
    img = img.resize((int(img.width * 1.4), int(img.height * 1.4)))
    foto = ImageTk.PhotoImage(img); rotulo_img.image = foto; rotulo_img.config(image=foto)
    ant = feitos.get(it["nome_arquivo"])
    var_cena.set(ant["cena"] if ant else "")
    for d in DEFEITOS:
        var_def[d].set(int(ant[d]) if ant else 0)
    info.config(text=f"{i+1}/{len(itens)}   decididas: {len(feitos)}\n"
                     f"{resumo(a.loc[it['nome_arquivo']], 'João')}\n"
                     f"{resumo(b.loc[it['nome_arquivo']], 'Henrique')}")

def avancar(_=None):
    i = estado["i"]
    if i >= len(itens) or not var_cena.get():
        return  # cena é obrigatória
    it = itens[i]
    sem_defeito = var_cena.get() in ("cena_ocorrencia", "nao_medidor")
    feitos[it["nome_arquivo"]] = {"nome_arquivo": it["nome_arquivo"], "lote": it["lote"],
        "cena": var_cena.get(), **{d: 0 if sem_defeito else var_def[d].get() for d in DEFEITOS}}
    salvar(); estado["i"] += 1; mostrar()

def voltar(_=None):
    estado["i"] = max(0, estado["i"] - 1); mostrar()

for i, c in enumerate(CENAS):
    raiz.bind(str(i + 1), lambda _e, c=c: var_cena.set(c))
for k, d in zip(TECLAS_DEF, DEFEITOS):
    raiz.bind(k, lambda _e, d=d: var_def[d].set(1 - var_def[d].get()))
raiz.bind("<Return>", avancar); raiz.bind("<BackSpace>", voltar)
mostrar(); raiz.mainloop()
