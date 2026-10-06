"""Gera o PPTX do exemplo fixo (tests/test_generation._sample(3)), para QA visual antes/depois de uma mudança.

Uso, da raiz do repo:
    py -3.13 tools/qa_gerar_exemplo.py <saida.pptx>
    py -3.13 -m pptx_opc.render_powerpoint <saida.pptx> <pasta_png>      # PowerPoint real (Windows)
    py -3.13 tools/qa_compara_png.py <pasta_png_antes> <pasta_png_depois>

Os bytes do .pptx mudam a cada geração (zip), então "nada mudou" se prova pelos PNGs, não pelo hash do arquivo.
Usado no passe do framework (05/10/2026): 5/5 slides iguais antes e depois do pptx_opc.
"""
import hashlib
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "tests"))

from ppt import generate_ppt_bytes  # noqa: E402
from test_generation import _sample  # noqa: E402

if __name__ == "__main__":
    dados = generate_ppt_bytes(_sample(3))
    Path(sys.argv[1]).write_bytes(dados)
    print(len(dados), hashlib.sha256(dados).hexdigest()[:16])
