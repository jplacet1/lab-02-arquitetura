"""Caminho dos dados (fora do Git). Sobrescreva com a variável DADOS_NEOENERGIA."""
import os
from pathlib import Path

DADOS = Path(os.environ.get(
    "DADOS_NEOENERGIA",
    r"C:\Users\joaop\Downloads\Base de Dados Neoenergia PE\Base de Dados Neoenergia PE",
))
LOTES = {  # pasta -> rótulo do lote
    "PSP_EXTRATLEITIMPL_200526_0352": "2026-05-20",
    "PSP_EXTRATLEITIMPL_210526_0335": "2026-05-21",
    "PSP_EXTRATLEITIMPL_220526_0408": "2026-05-22",
    "PSP_EXTRATLEITIMPL_030726_0121": "2026-07-03",
}
PARTICAO = {"2026-05-20": "treino", "2026-05-21": "treino",
            "2026-05-22": "validacao", "2026-07-03": "teste"}
RAIZ_LAB = Path(__file__).resolve().parents[1]
ROTULOS = RAIZ_LAB / "rotulos"
