"""Testes de fumaça do gerador baseado em template.

Exercita o mesmo caminho que o modo de entrada estruturada do app usa
(ScopeDiagram -> generate_ppt_bytes) sem depender de LLM nem de Streamlit.
Requer apenas lxml + pydantic.
"""

import sys
import zipfile
from io import BytesIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from schema import GlobalElements, Process, ScopeDiagram, Subprocess  # noqa: E402
from templatefill.builder import generate_ppt_bytes  # noqa: E402


def _sample(n_subprocessos: int) -> ScopeDiagram:
    return ScopeDiagram(
        process=Process(
            name="Processo de Teste",
            objective="Objetivo do processo de teste.",
            start_event="Evento inicial",
            end_event="Evento final",
        ),
        global_elements=GlobalElements(
            inputs=["Entrada A", "Entrada B"],
            outputs=["Saída A", "Saída B"],
            regulators=["Norma X", "Norma Y"],
            resources=["Recurso 1"],
        ),
        subprocesses=[
            Subprocess(
                name=f"Subprocesso {i}",
                objective=f"Objetivo {i}",
                inputs=[f"in-{i}-1", f"in-{i}-2"],
                activities=[f"ativ-{i}-1", f"ativ-{i}-2", f"ativ-{i}-3"],
                outputs=[f"out-{i}-1"],
                start_event=f"início {i}",
                end_event=f"fim {i}",
            )
            for i in range(1, n_subprocessos + 1)
        ],
    )


def _slide_count(data: bytes) -> int:
    with zipfile.ZipFile(BytesIO(data)) as zf:
        return sum(1 for n in zf.namelist()
                   if n.startswith("ppt/slides/slide") and n.endswith(".xml")
                   and "_rels" not in n)


def _all_text(data: bytes) -> str:
    import re
    out = []
    with zipfile.ZipFile(BytesIO(data)) as zf:
        for n in zf.namelist():
            if (n.startswith("ppt/slides/slide") or n.startswith("ppt/diagrams/drawing")) and n.endswith(".xml"):
                out.append(re.sub(r"<[^>]+>", "", zf.read(n).decode("utf-8", "ignore")))
    return "\n".join(out)


def test_valid_pptx_and_slide_count():
    for n in (1, 3, 5):
        data = generate_ppt_bytes(_sample(n), today="01/01/2026")
        with zipfile.ZipFile(BytesIO(data)) as zf:
            assert "ppt/presentation.xml" in zf.namelist()
            assert zf.testzip() is None
        # capa + processo + N subprocessos
        assert _slide_count(data) == 2 + n, f"n={n}"


def test_injected_content_present():
    data = generate_ppt_bytes(_sample(3), today="01/01/2026")
    text = _all_text(data)
    assert "Processo de Teste" in text
    assert "Subprocesso 1" in text and "Subprocesso 3" in text
    assert "ativ-2-1" in text          # atividade de subprocesso
    assert "Norma X" in text           # regulador global
    assert "OBJETIVO DO PROCESSO" in text
    assert "SUBPROCESSOS" in text      # rótulo da lane do meio no processo


def test_no_leftover_auditoria_template_content():
    # o conteúdo do template ("Realizar Auditoria") não pode vazar para o deck
    data = generate_ppt_bytes(_sample(2), today="01/01/2026")
    text = _all_text(data)
    assert "Planejar Auditoria" not in text
    assert "Formalizar os trabalhos de auditoria" not in text


if __name__ == "__main__":
    test_valid_pptx_and_slide_count()
    test_injected_content_present()
    test_no_leftover_auditoria_template_content()
    print("todos os testes passaram")
