"""Preenche uma unidade de slide IGOE (título, bandas, eventos e as três lanes
SmartArt) preservando a forma exata do template.

Endereçamento:
- Bandas/título/eventos são caixas de texto comuns do slide, em ordem estável de
  shape (idêntica nos slides 15/18/21 do template e nos clones).
- As lanes ficam no desenho SmartArt em cache (`drawingN.xml`): rótulos e listas
  de itens são identificados por texto/geometria (não por índice), tolerando
  pequenas variações de layout.
"""

from __future__ import annotations

import copy
import re

from lxml import etree

from .opc import Package, R_NS


A = "http://schemas.openxmlformats.org/drawingml/2006/main"
P = "http://schemas.openxmlformats.org/presentationml/2006/main"
DSP = "http://schemas.microsoft.com/office/drawing/2008/diagram"

DIAGRAM_DRAWING_REL = "http://schemas.microsoft.com/office/2007/relationships/diagramDrawing"
DIAGRAM_DATA_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/diagramData"

LANE_LABELS = {"ENTRADAS", "ATIVIDADES", "SAÍDAS", "SAIDAS", "SUBPROCESSOS"}


def _q(ns: str, tag: str) -> str:
    return f"{{{ns}}}{tag}"


def _text_of(el: etree._Element) -> str:
    return "".join(t.text or "" for t in el.iter(_q(A, "t")))


def _paras(txbody: etree._Element) -> list[etree._Element]:
    return txbody.findall(_q(A, "p"))


def _runs(para: etree._Element) -> list[etree._Element]:
    return para.findall(_q(A, "r"))


def _set_run_text(run: etree._Element, text: str) -> None:
    t = run.find(_q(A, "t"))
    if t is None:
        t = etree.SubElement(run, _q(A, "t"))
    t.text = text


def _set_run_size(run: etree._Element, sz: int) -> None:
    """Define o tamanho da fonte do run (sz em centésimos de ponto: 1000 = 10pt)."""
    rpr = run.find(_q(A, "rPr"))
    if rpr is None:
        rpr = etree.Element(_q(A, "rPr"))
        run.insert(0, rpr)
    rpr.set("sz", str(sz))


def _shift_shape(shape: etree._Element, dy: int = 0, dcy: int = 0) -> None:
    """Ajusta a posição/altura de um shape (EMU) editando o a:xfrm."""
    xfrm = shape.find(f"{_q(P, 'spPr')}/{_q(A, 'xfrm')}")
    if xfrm is None:
        return
    off = xfrm.find(_q(A, "off"))
    ext = xfrm.find(_q(A, "ext"))
    if off is not None and dy:
        off.set("y", str(int(off.get("y")) + dy))
    if ext is not None and dcy:
        ext.set("cy", str(int(ext.get("cy")) + dcy))


def _strip_empty_paras(shape: etree._Element) -> None:
    """Remove parágrafos vazios (sem texto) do txBody — evita linhas em branco
    que empurram o conteúdo para fora da caixa quando ancorado no topo."""
    body = shape.find(_q(P, "txBody"))
    if body is None:
        return
    ps = body.findall(_q(A, "p"))
    for p in ps:
        if not any((t.text or "").strip() for t in p.iter(_q(A, "t"))):
            if len(ps) > 1:  # nunca remover o último
                body.remove(p)
                ps.remove(p)


def _set_anchor(shape: etree._Element, anchor: str) -> None:
    """Define a ancoragem vertical do texto (t/ctr/b) no bodyPr."""
    body = shape.find(_q(P, "txBody"))
    if body is None:
        return
    bpr = body.find(_q(A, "bodyPr"))
    if bpr is None:
        bpr = etree.SubElement(body, _q(A, "bodyPr"))
    bpr.set("anchor", anchor)


def _template_para(txbody: etree._Element) -> etree._Element | None:
    """Primeiro parágrafo com run de texto — usado como molde de formatação."""
    for p in _paras(txbody):
        if _runs(p):
            return p
    return None


def _replace_paragraph_list(txbody: etree._Element, lines: list[str]) -> None:
    """Substitui todos os parágrafos do txBody por um por linha, preservando a
    formatação (pPr/rPr) do primeiro parágrafo-molde."""
    lines = [ln for ln in lines if ln and ln.strip()] or ["—"]
    tmpl = _template_para(txbody)
    if tmpl is None:  # sem molde: cria parágrafos simples
        for p in _paras(txbody):
            txbody.remove(p)
        for ln in lines:
            p = etree.SubElement(txbody, _q(A, "p"))
            r = etree.SubElement(p, _q(A, "r"))
            etree.SubElement(r, _q(A, "t")).text = ln
        return

    tmpl_copy = copy.deepcopy(tmpl)
    # posição de inserção = antes do primeiro parágrafo; depois removemos os antigos
    anchor_index = list(txbody).index(_paras(txbody)[0])
    for p in _paras(txbody):
        txbody.remove(p)

    for offset, ln in enumerate(lines):
        p = copy.deepcopy(tmpl_copy)
        rs = _runs(p)
        # manter só o primeiro run; ajustar texto
        for extra in rs[1:]:
            p.remove(extra)
        if rs:
            _set_run_text(rs[0], ln)
        else:
            r = etree.SubElement(p, _q(A, "r"))
            etree.SubElement(r, _q(A, "t")).text = ln
        txbody.insert(anchor_index + offset, p)


def _set_label_plus_body(shape_txbody: etree._Element, body: str, *, label_token: str, body_sz: int | None = None) -> None:
    """Caixas onde rótulo (negrito) e corpo convivem no mesmo parágrafo em runs
    consecutivos (ex.: OBJETIVO, EVENTO DE FIM). Mantém os runs do rótulo e
    substitui os runs seguintes pelo novo corpo."""
    for p in _paras(shape_txbody):
        rs = _runs(p)
        # localizar o último run que faz parte do rótulo
        label_end = None
        acc = ""
        for i, r in enumerate(rs):
            acc += _text_of(r)
            if label_token in acc.upper().replace("  ", " "):
                label_end = i
                break
        if label_end is None:
            continue
        # corpo = runs após label_end
        if label_end + 1 < len(rs):
            body_run = rs[label_end + 1]
            _set_run_text(body_run, " " + body)
            for extra in rs[label_end + 2:]:
                p.remove(extra)
        else:  # não havia run de corpo: clonar o run do rótulo para o corpo
            body_run = copy.deepcopy(rs[label_end])
            _set_run_text(body_run, " " + body)
            rs[label_end].addnext(body_run)
        if body_sz is not None:
            _set_run_size(body_run, body_sz)
        return


def _relabel_prefix(shape_txbody: etree._Element, new_label: str, *, token: str) -> None:
    """Substitui o run do rótulo (que contém `token`) por `new_label`, preservando
    o espaçamento à direita do run original."""
    for p in _paras(shape_txbody):
        for r in _runs(p):
            txt = _text_of(r)
            if token in txt.upper():
                trailing = txt[len(txt.rstrip()):]
                _set_run_text(r, new_label + (trailing or "     "))
                return


def _set_body_only(shape_txbody: etree._Element, body: str, *, body_sz: int | None = None) -> None:
    """Caixas de corpo puro (ex.: EVENTO DE INÍCIO body)."""
    for p in _paras(shape_txbody):
        rs = _runs(p)
        if rs:
            _set_run_text(rs[0], body)
            for extra in rs[1:]:
                p.remove(extra)
            if body_sz is not None:
                _set_run_size(rs[0], body_sz)
            return


# ---------------------------------------------------------------------------
def _slide_shapes(slide_root: etree._Element) -> list[etree._Element]:
    tree = slide_root.find(f".//{_q(P, 'spTree')}")
    return tree.findall(_q(P, "sp"))


def _shape_txbody(shape: etree._Element) -> etree._Element | None:
    return shape.find(_q(P, "txBody"))


def _diagram_parts(pkg: Package, slide_name: str) -> tuple[str | None, str | None]:
    drawing = data = None
    for r in pkg.rels(slide_name):
        if r["Type"] == DIAGRAM_DRAWING_REL:
            drawing = pkg.resolve(slide_name, r["Target"])
        elif r["Type"] == DIAGRAM_DATA_REL:
            data = pkg.resolve(slide_name, r["Target"])
    return drawing, data


def _fill_lanes(pkg: Package, slide_name: str, lanes: list[tuple[str, list[str]]]) -> None:
    """lanes = [(label_esquerda, itens), (label_meio, itens), (label_dir, itens)]."""
    drawing, data = _diagram_parts(pkg, slide_name)
    if not drawing:
        return
    root = etree.fromstring(pkg.part(drawing))
    sps = root.findall(f".//{_q(DSP, 'sp')}")

    def off_x(sp):
        off = sp.find(f".//{_q(A, 'off')}")
        return int(off.get("x")) if off is not None else 0

    label_shapes, content_shapes = [], []
    for sp in sps:
        tb = sp.find(_q(DSP, "txBody"))
        if tb is None:
            continue
        txt = _text_of(tb).strip()
        if not txt:
            continue
        norm = txt.upper()
        if norm in LANE_LABELS:
            label_shapes.append((off_x(sp), sp, tb))
        else:
            content_shapes.append((off_x(sp), sp, tb))

    label_shapes.sort(key=lambda t: t[0])
    content_shapes.sort(key=lambda t: t[0])

    # rótulos: mapear por posição (esq/meio/dir)
    for idx, (_, sp, tb) in enumerate(label_shapes[:3]):
        new_label = lanes[idx][0]
        for p in _paras(tb):
            rs = _runs(p)
            if rs:
                _set_run_text(rs[0], new_label)
                for extra in rs[1:]:
                    p.remove(extra)
                # rótulos longos (ex.: SUBPROCESSOS) na caixa girada e estreita
                # precisam de fonte menor para não quebrar em duas linhas.
                if len(new_label) > 10:
                    _set_run_size(rs[0], 1200)
                break

    # conteúdos: mapear por posição (esq/meio/dir)
    content_tbs = []
    for idx, (_, sp, tb) in enumerate(content_shapes[:3]):
        items = lanes[idx][1]
        _replace_paragraph_list(tb, items)
        content_tbs.append((tb, items))

    _lane_font_fit(content_tbs)

    pkg.set_part(drawing, etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True))

    # sincronização best-effort do texto no modelo de dados (para editabilidade)
    if data and pkg.has_part(data):
        _sync_data_text(pkg, data, lanes)


def _lane_font_fit(content_tbs: list[tuple[etree._Element, list[str]]]) -> None:
    """Auto-fit por fonte: se a lane mais cheia exceder a capacidade da caixa,
    reduz a fonte de TODAS as lanes uniformemente (mantém consistência)."""
    CHARS_PER_LINE = 30   # ~30 chars por linha na largura da lane a 11pt
    CAPACITY_LINES = 11   # ~11 linhas envolvidas cabem na altura da lane
    BASE_SZ, MIN_SZ = 1100, 700

    def lines_for(items: list[str]) -> int:
        return sum(max(1, -(-len(it) // CHARS_PER_LINE)) for it in items) or 1

    max_lines = max((lines_for(items) for _, items in content_tbs), default=1)
    if max_lines <= CAPACITY_LINES:
        return  # cabe na fonte padrão do template

    sz = max(MIN_SZ, int(BASE_SZ * CAPACITY_LINES / max_lines))
    for tb, _ in content_tbs:
        for p in _paras(tb):
            for r in _runs(p):
                _set_run_size(r, sz)


def _sync_data_text(pkg: Package, data_name: str, lanes: list[tuple[str, list[str]]]) -> None:
    """Best-effort: substitui os textos de nós do modelo de dados pelos novos
    itens, na ordem em que aparecem. Não recria a topologia de nós."""
    root = etree.fromstring(pkg.part(data_name))
    # Coletar todos os <a:t> em ordem de documento e os novos valores esperados
    new_values = []
    for label, items in lanes:
        new_values.append(label)
        new_values.extend(items)
    ts = list(root.iter(_q(A, "t")))
    # Só sincroniza se as contagens baterem razoavelmente; caso contrário, deixa
    # o modelo como está (o render usa o desenho, que já foi corrigido).
    text_ts = [t for t in ts if (t.text or "").strip()]
    if len(text_ts) == len(new_values):
        for t, val in zip(text_ts, new_values):
            t.text = val
        pkg.set_part(data_name, etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True))


def fill_igoe_slide(
    pkg: Package,
    slide_name: str,
    *,
    title: str,
    objective: str,
    regulators: list[str],
    resources: list[str],
    start_event: str,
    end_event: str,
    left_label: str,
    left_items: list[str],
    mid_label: str,
    mid_items: list[str],
    right_label: str,
    right_items: list[str],
    objective_scope: str = "SUBPROCESSO",
) -> None:
    root = etree.fromstring(pkg.part(slide_name))
    shapes = _slide_shapes(root)

    # ordem estável de shapes (slides 15/18/21 do template):
    # 0=título 1=REG-body 2=REG-label 3=RECURSOS-body 4=RECURSOS-label
    # 5=INÍCIO-body 6=FIM(label+body) 7=OBJETIVO(label+body) 8=INÍCIO-label
    def tb(i):
        return _shape_txbody(shapes[i])

    EVENT_SZ = 1000  # 10pt: mantém 2 linhas dentro da caixa, longe da borda inferior

    _set_body_only(tb(0), title)
    _replace_paragraph_list(tb(1), regulators)
    _replace_paragraph_list(tb(3), resources)
    _set_body_only(tb(5), start_event, body_sz=EVENT_SZ)
    _set_label_plus_body(tb(6), end_event, label_token="FIM", body_sz=EVENT_SZ)
    _set_label_plus_body(tb(7), objective, label_token="OBJETIVO")
    # rótulo da banda OBJETIVO: "DO PROCESSO" vs "DO SUBPROCESSO"
    _relabel_prefix(tb(7), f"OBJETIVO DO {objective_scope}", token="OBJETIVO")

    # --- reflow da faixa inferior (eventos) ---------------------------------
    # As caixas EVENTO são centradas e coladas na borda inferior; um corpo de 2
    # linhas transborda. Ancoramos no topo, crescemos as caixas para cima e
    # subimos a banda RECURSOS para manter folga (o layout é apertado).
    for i in (5, 6, 8):
        _strip_empty_paras(shapes[i])
        _set_anchor(shapes[i], "t")
        _shift_shape(shapes[i], dy=-190000, dcy=+190000)
    _shift_shape(shapes[3], dy=-80000)  # RECURSOS sobe um pouco
    # rótulos EVENTO (negrito, fonte grande) reduzidos p/ diminuir a altura da linha
    for i in (6, 8):
        for p in _paras(tb(i)):
            for r in _runs(p):
                if "EVENTO" in _text_of(r).upper() or _text_of(r).strip() in {"DE", "FIM", "INÍCIO"}:
                    _set_run_size(r, 1200)
    # z-order: trazer as caixas EVENTO para a frente (evita que o cant_o inferior
    # do contêiner verde cubra o topo das caixas laranja após o reflow).
    sp_tree = root.find(f".//{_q(P, 'spTree')}")
    for i in (5, 6, 8):
        sp_tree.remove(shapes[i])
        sp_tree.append(shapes[i])

    pkg.set_part(slide_name, etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True))

    _fill_lanes(pkg, slide_name, [
        (left_label, left_items),
        (mid_label, mid_items),
        (right_label, right_items),
    ])


def set_cover(pkg: Package, slide_name: str, *, title_main: str, subtitle: str, date: str) -> None:
    """Capa (slide1): shape com 'Diagramas de Escopo' + subtítulo; shape da data."""
    root = etree.fromstring(pkg.part(slide_name))
    shapes = _slide_shapes(root)
    for sp in shapes:
        tbx = _shape_txbody(sp)
        if tbx is None:
            continue
        txt = _text_of(tbx).strip()
        if txt == date or re.match(r"^\d{2}/\d{2}/\d{4}$", txt):
            _set_body_only(tbx, date)
        elif "Diagramas de Escopo" in txt or "SUBPROCESSOS" in txt.upper():
            ps = _paras(tbx)
            # 1º parágrafo = título fixo "Diagramas de Escopo"; 2º = subtítulo
            if len(ps) >= 2:
                rs = _runs(ps[0])
                if rs:
                    _set_run_text(rs[0], title_main)
                    for e in rs[1:]:
                        ps[0].remove(e)
                rs2 = _runs(ps[1])
                if rs2:
                    _set_run_text(rs2[0], subtitle)
                    for e in rs2[1:]:
                        ps[1].remove(e)
    pkg.set_part(slide_name, etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True))
