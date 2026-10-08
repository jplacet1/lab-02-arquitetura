"""Bloco profundo do GridVision (triagem de cena e qualidade): MobileNetV3-Small com duas cabeças, mais carga de dados e baseline V0.
Adaptado de codigo/esqueleto_arquitetura.py. Usado por lab02.ipynb."""
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
from scipy import ndimage
from torchvision.models import MobileNet_V3_Small_Weights, mobilenet_v3_small

from config import DADOS, LOTES, PARTICAO, ROTULOS

CLASSES_CENA = ["digital", "ciclometrico", "cena_ocorrencia", "nao_medidor"]
DEFEITOS = ["reflexo", "fora_de_foco", "tampa_suja", "enquadramento", "display_apagado"]
ALTURA, LARGURA = 480, 360  # resolução nativa das fotos do PDA (retrato, 3:4)
MEDIA = torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1)
DP = torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1)


class ModeloTriagem(nn.Module):
    """Cena é exclusiva (uma foto é de um tipo só): softmax + entropia cruzada.
    Defeitos coexistem (reflexo E fora de foco): uma sigmoide por defeito + BCE.
    A rede devolve logits; softmax e sigmoide ficam dentro das perdas e da decisão."""

    def __init__(self, pretreinado: bool = False, p_dropout: float = 0.2):
        super().__init__()
        pesos = MobileNet_V3_Small_Weights.IMAGENET1K_V1 if pretreinado else None
        base = mobilenet_v3_small(weights=pesos)
        self.extrator = base.features
        self.pool = nn.AdaptiveAvgPool2d(1)
        dim = base.classifier[0].in_features  # 576
        self.cabeca_cena = nn.Sequential(nn.Dropout(p_dropout), nn.Linear(dim, len(CLASSES_CENA)))
        self.cabeca_qualidade = nn.Sequential(nn.Dropout(p_dropout), nn.Linear(dim, len(DEFEITOS)))

    def caracteristicas(self, x):
        return self.pool(self.extrator(x)).flatten(1)

    def forward(self, x):
        z = self.caracteristicas(x)
        return self.cabeca_cena(z), self.cabeca_qualidade(z)


def perda_triagem(logits_cena, logits_qual, y_cena, y_qual, peso_pos=None, lam=1.0):
    return F.cross_entropy(logits_cena, y_cena) + lam * F.binary_cross_entropy_with_logits(
        logits_qual, y_qual, pos_weight=peso_pos)


def contar(modelo):
    total = sum(p.numel() for p in modelo.parameters())
    treino = sum(p.numel() for p in modelo.parameters() if p.requires_grad)
    return total, treino


def tabela_de_formas(modelo, x):
    """Forma de saída de cada bloco do extrator e das cabeças, para uma entrada x."""
    linhas = []

    def gancho(nome):
        def f(_m, _i, o):
            linhas.append((nome, tuple(o.shape)))
        return f

    alvos = [(f"extrator.{n}", m) for n, m in modelo.extrator.named_children()]
    alvos += [("pool", modelo.pool), ("cabeca_cena", modelo.cabeca_cena),
              ("cabeca_qualidade", modelo.cabeca_qualidade)]
    ganchos = [m.register_forward_hook(gancho(n)) for n, m in alvos]
    with torch.no_grad():
        modelo.eval()(x)
    for g in ganchos:
        g.remove()
    return pd.DataFrame(linhas, columns=["camada", "forma_saida"])


def carregar_rotulos():
    """rotulos.csv + coluna 'conjunto' (partição por lote, config.PARTICAO)."""
    r = pd.read_csv(ROTULOS / "rotulos.csv")
    r["conjunto"] = r.lote.map(PARTICAO)
    r["y_cena"] = r.cena.map({c: i for i, c in enumerate(CLASSES_CENA)})
    return r


def carregar_imagens(rotulos, tamanho=(ALTURA, LARGURA)):
    """uint8 (N, 3, H, W). Só lê as fotos do disco (DADOS, fora do Git)."""
    inv = {v: k for k, v in LOTES.items()}
    out = []
    for _, r in rotulos.iterrows():
        im = Image.open(DADOS / inv[r.lote] / r.nome_arquivo).convert("RGB")
        if im.size != (tamanho[1], tamanho[0]):
            im = im.resize((tamanho[1], tamanho[0]), Image.BILINEAR)
        out.append(torch.from_numpy(np.asarray(im).copy()).permute(2, 0, 1))
    return torch.stack(out)


def normalizar(x_uint8):
    return (x_uint8.float() / 255 - MEDIA) / DP


@torch.no_grad()
def extrair(modelo, x_uint8, lote=32):
    """Características de 576-d com o extrator congelado (modo eval), em lotes."""
    modelo.eval()
    return torch.cat([modelo.caracteristicas(normalizar(x_uint8[i:i + lote]))
                      for i in range(0, len(x_uint8), lote)])


def v0_caracteristicas(x_uint8):
    """Baseline V0 (não profunda): Laplaciano, brilho e histograma de cinza, por foto."""
    feats = []
    for im in x_uint8.permute(0, 2, 3, 1).numpy():
        g = im.astype(np.float32) @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
        lap = ndimage.laplace(g)
        h, w = g.shape
        centro = lap[h // 4: 3 * h // 4, w // 4: 3 * w // 4]
        hist = np.histogram(g, bins=16, range=(0, 255))[0] / g.size
        feats.append([np.log1p(lap.var()), np.log1p(centro.var()), g.mean() / 255, g.std() / 255,
                      (g > 250).mean(), (g < 5).mean(), *hist])
    return np.array(feats, dtype=np.float32)
