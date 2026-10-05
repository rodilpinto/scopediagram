"""Renderiza slides de um .pptx para PNG usando o PowerPoint REAL via COM
(pywin32), não uma aproximação (LibreOffice/Graphviz). Existe porque o
render do LibreOffice já divergiu do PowerPoint de verdade em casos reais —
este script é a fonte de verdade para QA visual de SmartArt.

Uso: python tools/render_pptx_powerpoint.py <caminho.pptx> [dir_saida]

Sem dir_saida, usa uma pasta "<nome-do-pptx>_render" ao lado do próprio .pptx.
Imprime, um por linha, o caminho de cada PNG gerado (um por slide, em ordem).
"""
import sys
from pathlib import Path

import win32com.client


def render(pptx_path: str, out_dir: str | None = None) -> list[str]:
    pptx_path = str(Path(pptx_path).resolve())
    base = Path(pptx_path)
    out = Path(out_dir).resolve() if out_dir else base.with_name(base.stem + "_render")
    out.mkdir(parents=True, exist_ok=True)

    app = win32com.client.Dispatch("PowerPoint.Application")
    app.DisplayAlerts = 0  # ppAlertsNone
    app.Visible = True  # PowerPoint COM não roda totalmente headless

    pres = app.Presentations.Open(pptx_path, WithWindow=True, ReadOnly=True)
    paths = []
    try:
        for slide in pres.Slides:
            png_path = out / f"slide{slide.SlideIndex:02d}.png"
            # 1920 largura mantém proporção 16:9 -> altura calculada por PowerPoint
            slide.Export(str(png_path), "PNG", 1920, 1080)
            paths.append(str(png_path))
    finally:
        pres.Close()
        app.Quit()
    return paths


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("uso: python tools/render_pptx_powerpoint.py <caminho.pptx> [dir_saida]", file=sys.stderr)
        raise SystemExit(2)
    result = render(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    for p in result:
        print(p)
