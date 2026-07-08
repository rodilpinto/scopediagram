"""Ponto de entrada da geração de PowerPoint.

A abordagem atual preenche o template real (mantém a forma exata do PowerPoint
de referência) e vive em `templatefill/`. `app.py` importa `generate_ppt_bytes`
daqui, então este módulo apenas reexporta a implementação nova.

O gerador antigo (formas do zero, via python-pptx) permanece em `ppt_legacy.py`
como fallback/comparação e não é carregado a menos que seja necessário.
"""

from __future__ import annotations


try:
    from templatefill.builder import generate_ppt, generate_ppt_bytes  # noqa: F401
except Exception:  # pragma: no cover — fallback se o template não estiver disponível
    from ppt_legacy import generate_ppt, generate_ppt_bytes  # noqa: F401
