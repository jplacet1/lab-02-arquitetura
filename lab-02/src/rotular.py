"""Ferramenta de rotulagem local. Uso: python rotular.py joao   (ou henrique); "python rotular.py joao v2" ou "... extra" para as rodadas extras
Lê rotulos/lista_<nome>.csv, mostra a foto e grava rotulos/rotulos_<nome>.csv a cada foto.
Teclas: 1-4 cena | q w e r t defeitos (liga/desliga) | Enter salva e avança | Backspace volta.
Rotule os dois sem conversar até terminar (as 50 fotos comuns são a dupla rotulagem às cegas)."""
import csv
import sys
import tkinter as tk
from PIL import Image, ImageTk
from config import DADOS, LOTES, ROTULOS

CENAS = ["digital", "ciclometrico", "cena_ocorrencia", "nao_medidor"]
DEFEITOS = ["reflexo", "fora_de_foco", "tampa_suja", "enquadramento", "display_apagado"]
TECLAS_DEF = "qwert"
pasta_do_lote = {v: k for k, v in LOTES.items()}

nome = sys.argv[1]
sufixo = f"{sys.argv[2]}_" if len(sys.argv) > 2 else ""  # rodada: "v2" (30 comuns) ou "extra" (fotos extras)
with open(ROTULOS / f"lista_{sufixo}{nome}.csv", encoding="utf-8") as fh:
    itens = list(csv.DictReader(fh))
saida = ROTULOS / f"rotulos_{sufixo}{nome}.csv"
feitos = {}
if saida.exists():
    with open(saida, encoding="utf-8") as fh:
        feitos = {r["nome_arquivo"]: r for r in csv.DictReader(fh)}

def salvar():
    with open(saida, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, ["nome_arquivo", "lote", "rotulador", "cena", *DEFEITOS])
        w.writeheader()
        for it in itens:
            if it["nome_arquivo"] in feitos:
                w.writerow(feitos[it["nome_arquivo"]])

raiz = tk.Tk(); raiz.title(f"Rotulagem - {nome}")
rotulo_img = tk.Label(raiz); rotulo_img.pack()
info = tk.Label(raiz, font=("Segoe UI", 11)); info.pack()
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
    img = img.resize((int(img.width * 1.6), int(img.height * 1.6)))
    foto = ImageTk.PhotoImage(img); rotulo_img.image = foto; rotulo_img.config(image=foto)
    ant = feitos.get(it["nome_arquivo"])
    var_cena.set(ant["cena"] if ant else "")
    for d in DEFEITOS:
        var_def[d].set(int(ant[d]) if ant else 0)
    info.config(text=f"{i+1}/{len(itens)}   rotulados: {len(feitos)}")

def avancar(_=None):
    i = estado["i"]
    if i >= len(itens) or not var_cena.get():
        return  # cena é obrigatória
    it = itens[i]
    feitos[it["nome_arquivo"]] = {"nome_arquivo": it["nome_arquivo"], "lote": it["lote"],
        "rotulador": nome, "cena": var_cena.get(), **{d: var_def[d].get() for d in DEFEITOS}}
    salvar(); estado["i"] += 1; mostrar()

def voltar(_=None):
    estado["i"] = max(0, estado["i"] - 1); mostrar()

for i, c in enumerate(CENAS):
    raiz.bind(str(i + 1), lambda _e, c=c: var_cena.set(c))
for k, d in zip(TECLAS_DEF, DEFEITOS):
    raiz.bind(k, lambda _e, d=d: var_def[d].set(1 - var_def[d].get()))
raiz.bind("<Return>", avancar); raiz.bind("<BackSpace>", voltar)
mostrar(); raiz.mainloop()
