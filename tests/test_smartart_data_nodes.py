"""Testes da reconstrução do modelo de dados do SmartArt (editabilidade
pós-geração no PowerPoint). Opera direto sobre o `data*.xml` do template de
referência, sem depender de LLM/Streamlit — só lxml.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lxml import etree  # noqa: E402

from templatefill.builder import IGOE_TEMPLATE, TEMPLATE_PATH  # noqa: E402
from templatefill.igoe import (  # noqa: E402
    A,
    DGM,
    _diagram_parts,
    _find_lane_roots,
    _new_guid,
    _q,
    _rebuild_lane_nodes,
    _shared_pres_id,
    _sync_data_nodes,
    _text_of,
)
from templatefill.opc import Package  # noqa: E402


def _fresh_work():
    """Árvore `data*.xml` do template de referência (slide15/data8), fresca a
    cada chamada — cada teste muta sua própria cópia."""
    pkg = Package.open(str(TEMPLATE_PATH))
    _drawing, data = _diagram_parts(pkg, IGOE_TEMPLATE)
    assert data is not None
    return etree.fromstring(pkg.part(data))


def test_new_guid_format():
    g = _new_guid()
    assert re.fullmatch(
        r"\{[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}\}", g
    ), g
    assert _new_guid() != g  # não repete


def test_shared_pres_id_known_lanes():
    work = _fresh_work()
    candidates = {
        _text_of(pt).strip(): pt.get("modelId")
        for pt in work.iter(_q(DGM, "pt"))
        if not pt.get("type") and _text_of(pt).strip().upper() in
        {"ENTRADAS", "ATIVIDADES", "SAÍDAS"}
    }
    assert set(candidates) == {"ENTRADAS", "ATIVIDADES", "SAÍDAS"}
    assert _shared_pres_id(work, candidates["ENTRADAS"]) is not None
    assert _shared_pres_id(work, candidates["ATIVIDADES"]) is not None
    assert _shared_pres_id(work, candidates["SAÍDAS"]) is not None
    # os 3 objetos compartilhados são distintos entre si
    ids = {
        _shared_pres_id(work, candidates[k])
        for k in ("ENTRADAS", "ATIVIDADES", "SAÍDAS")
    }
    assert len(ids) == 3


def test_shared_pres_id_unknown_root_returns_none():
    work = _fresh_work()
    assert _shared_pres_id(work, "{00000000-0000-0000-0000-000000000000}") is None


def test_find_lane_roots_subprocess_labels():
    work = _fresh_work()
    found = _find_lane_roots(work, "ENTRADAS", "SAÍDAS")
    assert found is not None
    assert len(found) == 3
    (left_pt, left_shared), (mid_pt, mid_shared), (right_pt, right_shared) = found
    assert _text_of(left_pt).strip() == "ENTRADAS"
    assert _text_of(right_pt).strip() == "SAÍDAS"
    # lane do meio achada por eliminação — no template é "ATIVIDADES",
    # independente de qual mid_label será usado depois pra renomear
    assert _text_of(mid_pt).strip() == "ATIVIDADES"
    assert len({left_shared, mid_shared, right_shared}) == 3


def test_find_lane_roots_missing_label_returns_none():
    work = _fresh_work()
    assert _find_lane_roots(work, "NAO EXISTE", "SAÍDAS") is None
    assert _find_lane_roots(work, "ENTRADAS", "NAO EXISTE") is None


if __name__ == "__main__":
    test_new_guid_format()
    test_shared_pres_id_known_lanes()
    test_shared_pres_id_unknown_root_returns_none()
    test_find_lane_roots_subprocess_labels()
    test_find_lane_roots_missing_label_returns_none()
    print("todos os testes passaram (task 1)")
