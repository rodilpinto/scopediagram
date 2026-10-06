"""Compara pixel a pixel duas pastas de PNG (ex.: renders do PowerPoint antes e depois de uma mudança).

Uso: py -3.13 tools/qa_compara_png.py <pasta_a> <pasta_b>
Imprime, por arquivo, IGUAL ou a caixa onde difere. Antes de confiar numa comparação, rode uma dupla de controle
(duas gerações do mesmo estado) para saber se o render tem ruído; em 05/10/2026 o controle deu 5/5 iguais.
"""
import sys
from pathlib import Path

from PIL import Image, ImageChops

if __name__ == "__main__":
    a, b = Path(sys.argv[1]), Path(sys.argv[2])
    nomes_a = sorted(p.name for p in a.glob("*.png"))
    nomes_b = sorted(p.name for p in b.glob("*.png"))
    print("mesmos arquivos:", nomes_a == nomes_b, len(nomes_a))
    for nome in nomes_a:
        ia, ib = Image.open(a / nome).convert("RGB"), Image.open(b / nome).convert("RGB")
        if ia.size != ib.size:
            print(nome, "TAMANHO DIFERENTE", ia.size, ib.size)
            continue
        caixa = ImageChops.difference(ia, ib).getbbox()
        print(nome, ia.size, "IGUAL" if caixa is None else f"DIFERE em {caixa}")
