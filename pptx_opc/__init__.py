"""pptx_opc: mexer num .pptx como pacote de partes XML (apagar, clonar e reordenar slides, inclusive
com SmartArt) e renderizar slides com o PowerPoint de verdade para QA visual. Comece pelo README.md.

    from pptx_opc import Package
    pkg = Package(dados_pptx); novo = pkg.clone_slide(pkg.slide_names()[0]); pkg.to_bytes()

Pasta copiavel: a ORIGEM vive em github.com/rodilpinto/nuati-framework, pasta pptx_opc/.
Nao edite uma copia: melhore a origem, suba __version__ e recopie.
"""

from .opc import Package

__version__ = "1.0.0"

__all__ = ["Package", "__version__"]
