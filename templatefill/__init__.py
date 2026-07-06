"""Geração de PPT por preenchimento do template real.

Substitui a geração de slides "do zero": abre o PowerPoint de referência como
pacote OPC, seleciona/clona a unidade de diagrama IGOE e preenche o conteúdo,
preservando a forma exata do template.
"""

try:  # builder é adicionado depois; evita quebrar imports parciais durante o build
    from .builder import generate_ppt_bytes  # noqa: F401
except ImportError:  # pragma: no cover
    pass
