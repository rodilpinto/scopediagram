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


def test_rebuild_lane_nodes_content_and_attrs():
    work = _fresh_work()
    (root_pt, shared), _, _ = _find_lane_roots(work, "ENTRADAS", "SAÍDAS")
    items = ["item-a", "item-b", "item-c"]
    _rebuild_lane_nodes(work, root_pt, shared, "ENTRADAS", items)

    root_id = root_pt.get("modelId")
    hier = [
        c
        for c in work.iter(_q(DGM, "cxn"))
        if c.get("type") is None and c.get("srcId") == root_id
    ]
    assert len(hier) == 3
    content_ids = {c.get("destId") for c in hier}
    content_pts = [
        p for p in work.iter(_q(DGM, "pt")) if p.get("modelId") in content_ids
    ]
    assert len(content_pts) == 3
    assert {_text_of(p) for p in content_pts} == set(items)
    for p in content_pts:
        pr = p.find(_q(DGM, "prSet"))
        assert pr.get("custT") == "1"
        assert pr.get("phldrT") == "[Texto]"

    pres = [
        c
        for c in work.iter(_q(DGM, "cxn"))
        if c.get("type") == "presOf" and c.get("srcId") in content_ids
    ]
    assert len(pres) == 3
    assert {c.get("destId") for c in pres} == {shared}

    hier_by_dest = {c.get("destId"): int(c.get("srcOrd")) for c in hier}
    pres_by_src = {c.get("srcId"): int(c.get("destOrd")) for c in pres}
    assert hier_by_dest == pres_by_src
    assert set(hier_by_dest.values()) == {0, 1, 2}
    assert all(c.get("destOrd") == "0" for c in hier)
    assert all(c.get("srcOrd") == "0" for c in pres)

    trans_by_id = {
        p.get("modelId"): p
        for p in work.iter(_q(DGM, "pt"))
        if p.get("type") in ("parTrans", "sibTrans")
    }
    for c in hier:
        assert trans_by_id[c.get("parTransId")].get("cxnId") == c.get("modelId")
        assert trans_by_id[c.get("sibTransId")].get("cxnId") == c.get("modelId")
        assert c.get("destId") not in {"", None}


def test_rebuild_lane_nodes_relabels_root():
    work = _fresh_work()
    _, (mid_pt, mid_shared), _ = _find_lane_roots(work, "ENTRADAS", "SAÍDAS")
    assert _text_of(mid_pt).strip() == "ATIVIDADES"
    _rebuild_lane_nodes(work, mid_pt, mid_shared, "SUBPROCESSOS", ["Sub 1", "Sub 2"])
    assert _text_of(mid_pt).strip() == "SUBPROCESSOS"


def test_rebuild_lane_nodes_preserves_root_presof_and_presparof():
    work = _fresh_work()
    (root_pt, shared), _, _ = _find_lane_roots(work, "ENTRADAS", "SAÍDAS")
    root_id = root_pt.get("modelId")

    def root_presof_dests():
        return {
            c.get("destId")
            for c in work.iter(_q(DGM, "cxn"))
            if c.get("type") == "presOf" and c.get("srcId") == root_id
        }

    def presparof_count():
        return len(
            [c for c in work.iter(_q(DGM, "cxn")) if c.get("type") == "presParOf"]
        )

    before_root_presof = root_presof_dests()
    before_presparof = presparof_count()
    assert len(before_root_presof) == 2  # confirmado na verificação da spec

    _rebuild_lane_nodes(work, root_pt, shared, "ENTRADAS", ["x", "y", "z", "w"])

    assert root_presof_dests() == before_root_presof
    assert presparof_count() == before_presparof


def test_rebuild_lane_nodes_single_item_fallback():
    work = _fresh_work()
    (root_pt, shared), _, _ = _find_lane_roots(work, "ENTRADAS", "SAÍDAS")
    _rebuild_lane_nodes(work, root_pt, shared, "ENTRADAS", [])
    root_id = root_pt.get("modelId")
    content_ids = {
        c.get("destId")
        for c in work.iter(_q(DGM, "cxn"))
        if c.get("type") is None and c.get("srcId") == root_id
    }
    content_pts = [
        p for p in work.iter(_q(DGM, "pt")) if p.get("modelId") in content_ids
    ]
    assert len(content_pts) == 1
    assert _text_of(content_pts[0]).strip() == "—"


def test_rebuild_lane_nodes_idempotent():
    work = _fresh_work()
    (root_pt, shared), _, _ = _find_lane_roots(work, "ENTRADAS", "SAÍDAS")
    _rebuild_lane_nodes(work, root_pt, shared, "ENTRADAS", ["a", "b", "c", "d"])
    _rebuild_lane_nodes(work, root_pt, shared, "ENTRADAS", ["x", "y"])

    root_id = root_pt.get("modelId")
    hier = [
        c
        for c in work.iter(_q(DGM, "cxn"))
        if c.get("type") is None and c.get("srcId") == root_id
    ]
    assert len(hier) == 2
    content_ids = {c.get("destId") for c in hier}
    content_pts = [
        p for p in work.iter(_q(DGM, "pt")) if p.get("modelId") in content_ids
    ]
    assert {_text_of(p) for p in content_pts} == {"x", "y"}

    all_content_texts = {
        _text_of(p).strip()
        for p in work.iter(_q(DGM, "pt"))
        if not p.get("type") and _text_of(p).strip() not in ("", "ENTRADAS")
    }
    assert "a" not in all_content_texts
    assert "b" not in all_content_texts
    assert "c" not in all_content_texts
    assert "d" not in all_content_texts

    # nenhum cxn/pt órfão referenciando modelIds que não existem mais
    all_pt_ids = {p.get("modelId") for p in work.iter(_q(DGM, "pt"))}
    for c in work.iter(_q(DGM, "cxn")):
        for attr in ("srcId", "destId", "parTransId", "sibTransId"):
            ref = c.get(attr)
            if ref is not None:
                assert ref in all_pt_ids, f"{attr}={ref} órfão após 2a chamada"


def test_rebuild_lane_nodes_propagates_exception_and_leaves_partial_state_to_caller():
    work = _fresh_work()
    (root_pt, shared), _, _ = _find_lane_roots(work, "ENTRADAS", "SAÍDAS")

    import templatefill.igoe as igoe_mod

    calls = {"n": 0}
    real_guid = igoe_mod._new_guid

    def flaky_guid():
        calls["n"] += 1
        if calls["n"] > 7:  # falha no meio do 2o item (5 guids por item)
            raise RuntimeError("boom")
        return real_guid()

    igoe_mod._new_guid = flaky_guid
    try:
        raised = False
        try:
            _rebuild_lane_nodes(work, root_pt, shared, "ENTRADAS", ["a", "b", "c"])
        except RuntimeError:
            raised = True
        assert raised, "exceção esperada não foi levantada"
    finally:
        igoe_mod._new_guid = real_guid


def _package_with_data():
    pkg = Package.open(str(TEMPLATE_PATH))
    _drawing, data_name = _diagram_parts(pkg, IGOE_TEMPLATE)
    return pkg, data_name


def test_sync_data_nodes_happy_path_rewrites_all_lanes():
    pkg, data_name = _package_with_data()
    before = pkg.part(data_name)
    lanes = [
        ("ENTRADAS", ["in-1", "in-2"]),
        ("SUBPROCESSOS", ["Sub 1", "Sub 2", "Sub 3"]),
        ("SAÍDAS", ["out-1"]),
    ]
    _sync_data_nodes(pkg, data_name, lanes)
    after = pkg.part(data_name)
    assert after != before

    root = etree.fromstring(after)
    all_texts = {_text_of(p).strip() for p in root.iter(_q(DGM, "pt")) if not p.get("type")}
    for label, items in lanes:
        assert label in all_texts
        for item in items:
            assert item in all_texts


def test_sync_data_nodes_precheck_failure_is_noop():
    pkg, data_name = _package_with_data()
    before = pkg.part(data_name)
    lanes = [("NAO EXISTE", ["x"]), ("ATIVIDADES", ["y"]), ("SAÍDAS", ["z"])]
    _sync_data_nodes(pkg, data_name, lanes)
    assert pkg.part(data_name) == before


def test_sync_data_nodes_missing_part_is_noop():
    pkg, _data_name = _package_with_data()
    lanes = [("ENTRADAS", ["x"]), ("ATIVIDADES", ["y"]), ("SAÍDAS", ["z"])]
    _sync_data_nodes(pkg, "ppt/diagrams/data999.xml", lanes)  # não existe no pacote


def test_sync_data_nodes_mid_lane_failure_aborts_whole_write():
    pkg, data_name = _package_with_data()
    before = pkg.part(data_name)

    import templatefill.igoe as igoe_mod

    real_rebuild = igoe_mod._rebuild_lane_nodes
    calls = {"n": 0}

    def flaky_rebuild(work, lane_root_pt, shared_pres_id, label, items):
        calls["n"] += 1
        if calls["n"] == 2:  # explode na 2a lane (do meio)
            raise RuntimeError("boom no meio")
        return real_rebuild(work, lane_root_pt, shared_pres_id, label, items)

    igoe_mod._rebuild_lane_nodes = flaky_rebuild
    try:
        lanes = [
            ("ENTRADAS", ["in-1"]),
            ("ATIVIDADES", ["ativ-1"]),
            ("SAÍDAS", ["out-1"]),
        ]
        _sync_data_nodes(pkg, data_name, lanes)
    finally:
        igoe_mod._rebuild_lane_nodes = real_rebuild

    # 1a lane já tinha sido mutada em `work` (cópia) quando a 2a explodiu —
    # mas `work` nunca foi gravado: `pkg.part(data_name)` deve continuar
    # bit-a-bit idêntico ao estado anterior à chamada.
    assert pkg.part(data_name) == before


def _data_parts_by_slide(pkg_bytes: bytes) -> dict[str, bytes]:
    """slide_name -> bytes do data*.xml correspondente, para todo slide que
    tenha um diagrama SmartArt."""
    out = {}
    pkg = Package(pkg_bytes)
    for slide_name in pkg.slide_names():
        _drawing, data_name = _diagram_parts(pkg, slide_name)
        if data_name:
            out[slide_name] = pkg.part(data_name)
    return out


def test_full_pipeline_data_model_matches_content_process_and_subprocess():
    from schema import GlobalElements, Process, ScopeDiagram, Subprocess
    from templatefill.builder import generate_ppt_bytes

    scope = ScopeDiagram(
        process=Process(
            name="Processo X",
            objective="Objetivo do processo X.",
            start_event="Início X",
            end_event="Fim X",
        ),
        global_elements=GlobalElements(
            inputs=["ENTRADA-MARCADOR-1", "ENTRADA-MARCADOR-2"],
            outputs=["SAIDA-MARCADOR-1"],
            regulators=["Norma Z"],
            resources=["Recurso Z"],
        ),
        subprocesses=[
            Subprocess(
                name="Sub A",
                objective="Objetivo A",
                inputs=["ATIV-ENTRADA-A"],
                activities=["ATIVIDADE-MARCADOR-A1", "ATIVIDADE-MARCADOR-A2"],
                outputs=["ATIV-SAIDA-A"],
                start_event="Início A",
                end_event="Fim A",
            )
        ],
    )
    data = generate_ppt_bytes(scope, today="01/01/2026")
    parts = _data_parts_by_slide(data)
    assert len(parts) == 2  # slide de processo + 1 de subprocesso

    all_texts_by_slide = {
        slide: {
            _text_of(p).strip()
            for p in etree.fromstring(xml).iter(_q(DGM, "pt"))
            if not p.get("type")
        }
        for slide, xml in parts.items()
    }

    # slide de processo: lane do meio SUBPROCESSOS com o nome do subprocesso;
    # marcadores de entrada/saída globais nas lanes corretas
    process_texts = next(
        texts for texts in all_texts_by_slide.values()
        if "SUBPROCESSOS" in texts
    )
    assert "Sub A" in process_texts
    assert "ENTRADA-MARCADOR-1" in process_texts
    assert "SAIDA-MARCADOR-1" in process_texts

    # slide de subprocesso: lane do meio ATIVIDADES com as atividades do sub
    sub_texts = next(
        texts for texts in all_texts_by_slide.values()
        if "ATIVIDADES" in texts
    )
    assert "ATIVIDADE-MARCADOR-A1" in sub_texts
    assert "ATIVIDADE-MARCADOR-A2" in sub_texts
    assert "ATIV-ENTRADA-A" in sub_texts
    assert "ATIV-SAIDA-A" in sub_texts

    # nenhum texto de exemplo do template original vazou
    for texts in all_texts_by_slide.values():
        assert "Objetivo geral da auditoria" not in texts
        assert "Formalizar os trabalhos de auditoria" not in texts


if __name__ == "__main__":
    test_new_guid_format()
    test_shared_pres_id_known_lanes()
    test_shared_pres_id_unknown_root_returns_none()
    test_find_lane_roots_subprocess_labels()
    test_find_lane_roots_missing_label_returns_none()
    test_rebuild_lane_nodes_content_and_attrs()
    test_rebuild_lane_nodes_relabels_root()
    test_rebuild_lane_nodes_preserves_root_presof_and_presparof()
    test_rebuild_lane_nodes_single_item_fallback()
    test_rebuild_lane_nodes_idempotent()
    test_rebuild_lane_nodes_propagates_exception_and_leaves_partial_state_to_caller()
    test_sync_data_nodes_happy_path_rewrites_all_lanes()
    test_sync_data_nodes_precheck_failure_is_noop()
    test_sync_data_nodes_missing_part_is_noop()
    test_sync_data_nodes_mid_lane_failure_aborts_whole_write()
    test_full_pipeline_data_model_matches_content_process_and_subprocess()
    print("todos os testes passaram (task 5)")
