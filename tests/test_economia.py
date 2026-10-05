"""As etapas do tempo_economizado dão o mesmo número da conta antiga do app.py (horas por componente)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from economia import etapas_manuais  # noqa: E402
from schema import GlobalElements, Process, ScopeDiagram, Subprocess  # noqa: E402
from tempo_economizado import estimar  # noqa: E402


def _conta_antiga_horas(scope: ScopeDiagram) -> float:
    """Cópia literal de app.py::_estimate_time_saved_hours até 05/10/2026."""
    g = scope.global_elements or GlobalElements()
    i, o, r, rec = len(g.inputs), len(g.outputs), len(g.regulators), len(g.resources)
    sub = len(scope.subprocesses)
    ativ = sum(len(s.activities) for s in scope.subprocesses)
    extraction_time = 0.6 + (i + o + r + rec) * 0.06
    structuring_time = 0.8 + sub * 0.35 + ativ * 0.08
    diagramming_time = 0.9 + sub * 0.3 + (i + o) * 0.05
    formatting_time = 0.7 + sub * 0.2
    review_time = 0.4 + r * 0.03 + rec * 0.03
    return round(extraction_time + structuring_time + diagramming_time + formatting_time + review_time, 1)


def _scope(i, o, r, rec, sub, ativ_por_sub) -> ScopeDiagram:
    return ScopeDiagram(
        process=Process(name="P", objective="O", start_event="i", end_event="f"),
        global_elements=GlobalElements(
            inputs=[f"e{k}" for k in range(i)], outputs=[f"s{k}" for k in range(o)],
            regulators=[f"r{k}" for k in range(r)], resources=[f"rec{k}" for k in range(rec)],
        ),
        subprocesses=[
            Subprocess(name=f"S{n}", objective="o", inputs=[], outputs=[], start_event="a", end_event="b",
                       activities=[f"a{n}-{k}" for k in range(ativ_por_sub)])
            for n in range(sub)
        ],
    )


@pytest.mark.parametrize("dims", [
    (0, 0, 0, 0, 0, 0), (2, 2, 2, 1, 3, 3), (3, 3, 2, 2, 4, 5), (10, 8, 6, 5, 12, 7), (1, 0, 0, 3, 1, 0),
])
def test_mesmo_numero_da_conta_antiga(dims):
    scope = _scope(*dims)
    est = estimar(etapas_manuais(scope))  # sem tempo da ferramenta, como a conta antiga
    assert round(est.economia_horas, 1) == _conta_antiga_horas(scope)
