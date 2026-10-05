"""Orquestra a montagem do deck a partir de um ScopeDiagram.

Deck enxuto (decisão do usuário):
- capa (slide1 do template)
- 1 slide IGOE do processo (lane do meio = SUBPROCESSOS)
- 1 slide IGOE por subprocesso (lane do meio = ATIVIDADES)

Todos os slides IGOE derivam da MESMA unidade do template (slide15), clonada
conforme necessário, garantindo consistência visual.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from .igoe import fill_igoe_slide, set_cover
from pptx_opc import Package


TEMPLATE_PATH = Path(__file__).resolve().parent.parent / (
    "Diagramas de Escopo_Realizar Auditoria e subprocessos_2026_GSF.pptx"
)

COVER = "ppt/slides/slide1.xml"
IGOE_TEMPLATE = "ppt/slides/slide15.xml"

_MISSING = "— (não identificado no documento)"


def _or_missing(items: list[str]) -> list[str]:
    return items if items else [_MISSING]


def generate_ppt(scope, *, template_path: str | Path | None = None, today: str | None = None) -> Package:
    pkg = Package.open(str(template_path or TEMPLATE_PATH))
    original_slides = pkg.slide_names()

    ge = scope.global_elements
    inputs = list(ge.inputs) if ge else []
    outputs = list(ge.outputs) if ge else []
    regulators = list(ge.regulators) if ge else []
    resources = list(ge.resources) if ge else []

    # 1 slide de processo (usa a unidade template) + N clones para subprocessos
    process_slide = IGOE_TEMPLATE
    sub_slides = [pkg.clone_slide(IGOE_TEMPLATE) for _ in scope.subprocesses]

    keep = {COVER, process_slide, *sub_slides}
    for s in original_slides:
        if s not in keep:
            pkg.delete_slide(s)
    pkg.reorder([COVER, process_slide, *sub_slides])

    today = today or date.today().strftime("%d/%m/%Y")
    set_cover(
        pkg, COVER,
        title_main="Diagramas de Escopo",
        subtitle=scope.process.name.upper(),
        date=today,
    )

    fill_igoe_slide(
        pkg, process_slide,
        title=f"Diagrama de Escopo do Processo {scope.process.name}",
        objective=scope.process.objective,
        regulators=_or_missing(regulators),
        resources=_or_missing(resources),
        start_event=scope.process.start_event,
        end_event=scope.process.end_event,
        left_label="ENTRADAS", left_items=_or_missing(inputs),
        mid_label="SUBPROCESSOS", mid_items=_or_missing([s.name for s in scope.subprocesses]),
        right_label="SAÍDAS", right_items=_or_missing(outputs),
        objective_scope="PROCESSO",
    )

    for slide, sub in zip(sub_slides, scope.subprocesses):
        fill_igoe_slide(
            pkg, slide,
            title=f"Diagrama de Escopo do Subprocesso {sub.name}",
            objective=sub.objective or scope.process.objective,
            regulators=_or_missing(sub.regulators or regulators),
            resources=_or_missing(sub.resources or resources),
            start_event=sub.start_event or scope.process.start_event,
            end_event=sub.end_event or scope.process.end_event,
            left_label="ENTRADAS", left_items=_or_missing(sub.inputs),
            mid_label="ATIVIDADES", mid_items=_or_missing(sub.activities),
            right_label="SAÍDAS", right_items=_or_missing(sub.outputs),
        )

    return pkg


def generate_ppt_bytes(scope, *, template_path=None, today: str | None = None) -> bytes:
    return generate_ppt(scope, template_path=template_path, today=today).to_bytes()
