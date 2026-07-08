# Reconstrução do modelo de dados do SmartArt — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reconstruir os nós de conteúdo do modelo de dados (`data*.xml`) das 3 lanes do SmartArt IGOE, para que o `.pptx` gerado permaneça consistente se o usuário editar o SmartArt dentro do PowerPoint — hoje só o desenho em cache é sincronizado corretamente.

**Architecture:** Duas camadas em `templatefill/igoe.py`. Camada 1 (`_sync_data_nodes`, orquestrador) faz todo I/O de `pkg` e garante isolamento transacional (só grava se as 3 lanes forem reconstruídas sem exceção). Camada 2 (`_rebuild_lane_nodes`, mutator puro) só muta uma árvore `lxml` já em memória e pode lançar exceção — nunca toca `pkg`. Descoberta de lane (`_find_lane_roots`) casa esquerda/direita por igualdade exata de texto (rótulos estáveis) e a do meio por eliminação, nunca por ordem de documento.

**Tech Stack:** Python, `lxml.etree`, `uuid` (stdlib) — sem novas dependências.

## Global Constraints

- Spec de referência: `docs/superpowers/specs/2026-07-08-smartart-data-model-editability-design.md` (leia antes de implementar qualquer task — cada task abaixo assume esse documento como verdade sobre os atributos XML exatos).
- Sem `import logging` novo — falhas continuam silenciosas (no-op), mesmo padrão do código já existente.
- Sem dependências novas em `requirements.txt` — só stdlib (`uuid`, já disponível) além do `lxml` já usado.
- Testes seguem o estilo existente de `tests/test_generation.py`: funções `test_*` com `assert` simples, sem `pytest`, executáveis via `python tests/<arquivo>.py` e também via bloco `if __name__ == "__main__"` que chama todas e imprime `"todos os testes passaram"`.
- `templatefill/igoe.py` é o único arquivo de produção modificado. Nenhuma mudança em `opc.py`, `builder.py`, `app.py`.

---

### Task 1: Descoberta de lanes (`_new_guid`, `_shared_pres_id`, `_find_lane_roots`)

**Files:**
- Modify: `templatefill/igoe.py` (imports no topo, linhas 12-29; nova função ao final do arquivo, antes de `set_cover`)
- Test: `tests/test_smartart_data_nodes.py` (novo arquivo)

**Interfaces:**
- Consome: `LANE_LABELS` (já existe, `igoe.py:29`), `_text_of(el) -> str` (já existe, `igoe.py:36-37`), `_q(ns, tag) -> str` (já existe, `igoe.py:32-33`), `DIAGRAM_DATA_REL` e `_diagram_parts(pkg, slide_name)` (já existem, `igoe.py:26-27` e `igoe.py:210-217`).
- Produz: `DGM` (constante de namespace, str), `_new_guid() -> str`, `_shared_pres_id(work, root_id: str) -> str | None`, `_find_lane_roots(work, left_label: str, right_label: str) -> list[tuple[etree._Element, str]] | None` (retorna `[(left_pt, left_shared), (mid_pt, mid_shared), (right_pt, right_shared)]` ou `None`).

- [ ] **Step 1: Escrever os testes que falham**

Criar `tests/test_smartart_data_nodes.py`:

```python
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
```

- [ ] **Step 2: Rodar e confirmar que falha**

Run: `python tests/test_smartart_data_nodes.py`
Expected: `ImportError` — `_new_guid`, `_shared_pres_id`, `_find_lane_roots`, `DGM`, `_rebuild_lane_nodes`, `_sync_data_nodes` ainda não existem em `templatefill/igoe.py`.

- [ ] **Step 3: Implementar**

Em `templatefill/igoe.py`, adicionar `import uuid` logo após `import re` (linha 15):

```python
import copy
import re
import uuid
```

Adicionar a constante de namespace `DGM` junto das outras (após a linha `DSP = "http://schemas.microsoft.com/office/drawing/2008/diagram"`, linha 24):

```python
DGM = "http://schemas.openxmlformats.org/drawingml/2006/diagram"
```

Adicionar as 3 funções novas **logo antes de `def fill_igoe_slide(`** (antes da linha 320 no arquivo atual — ou seja, depois de `_sync_data_text`, que será substituída na Task 4; por ora só adicione estas 3 funções, não mexa em `_sync_data_text` ainda):

```python
def _new_guid() -> str:
    """GUID no mesmo estilo do template (maiúsculo, com chaves)."""
    return "{" + str(uuid.uuid4()).upper() + "}"


def _shared_pres_id(work: etree._Element, root_id: str) -> str | None:
    """ID do objeto de apresentação compartilhado pelos filhos de conteúdo
    atuais de um nó-raiz de lane (via cxn de hierarquia + presOf)."""
    child_ids = {
        cxn.get("destId")
        for cxn in work.iter(_q(DGM, "cxn"))
        if cxn.get("type") is None and cxn.get("srcId") == root_id
    }
    if not child_ids:
        return None
    for cxn in work.iter(_q(DGM, "cxn")):
        if cxn.get("type") == "presOf" and cxn.get("srcId") in child_ids:
            return cxn.get("destId")
    return None


def _find_lane_roots(
    work: etree._Element, left_label: str, right_label: str
) -> list[tuple[etree._Element, str]] | None:
    """Localiza as 3 lanes no modelo de dados por texto (nunca por posição/
    ordem de documento — `data*.xml` não tem coordenadas). Esquerda/direita
    por igualdade exata contra rótulos estáveis; a do meio por eliminação
    (mesmo princípio que o desenho já usa: não casa a lane do meio pelo
    rótulo-alvo, porque esse pode ter sido renomeado só no desenho, ex.
    "SUBPROCESSOS" no slide de processo, enquanto o modelo de dados ainda diz
    "ATIVIDADES"). Retorna `[(left_pt, left_shared), (mid_pt, mid_shared),
    (right_pt, right_shared)]` ou `None` se a estrutura básica não bater."""
    candidates = [
        pt
        for pt in work.iter(_q(DGM, "pt"))
        if not pt.get("type") and _text_of(pt).strip().upper() in LANE_LABELS
    ]
    if len(candidates) != 3:
        return None
    left_pt = next(
        (p for p in candidates if _text_of(p).strip().upper() == left_label.upper()),
        None,
    )
    right_pt = next(
        (p for p in candidates if _text_of(p).strip().upper() == right_label.upper()),
        None,
    )
    if left_pt is None or right_pt is None or left_pt is right_pt:
        return None
    mid_pt = next(p for p in candidates if p is not left_pt and p is not right_pt)

    result = []
    for pt in (left_pt, mid_pt, right_pt):
        shared = _shared_pres_id(work, pt.get("modelId"))
        if shared is None:
            return None
        result.append((pt, shared))
    return result
```

`_rebuild_lane_nodes` e `_sync_data_nodes` ainda não existem — a Task 1 só cobre descoberta. Para o teste rodar sem `ImportError`, adicione por ora **stubs mínimos** (serão substituídos de verdade nas Tasks 2 e 4):

```python
def _rebuild_lane_nodes(work, lane_root_pt, shared_pres_id, label, items):
    raise NotImplementedError  # implementado na Task 2


def _sync_data_nodes(pkg, data_name, lanes):
    raise NotImplementedError  # implementado na Task 4
```

- [ ] **Step 4: Rodar e confirmar que passa**

Run: `python tests/test_smartart_data_nodes.py`
Expected: `todos os testes passaram (task 1)`

- [ ] **Step 5: Commit**

```bash
git add templatefill/igoe.py tests/test_smartart_data_nodes.py
git commit -m "$(cat <<'EOF'
Adiciona descoberta de lanes no modelo de dados do SmartArt (D3, task 1/6)

_find_lane_roots casa esquerda/direita por igualdade exata de texto e a
do meio por eliminação (nunca por ordem de documento, que não existe no
data*.xml) — pré-requisito para reconstruir os nós de conteúdo.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 2: Mutator puro — reconstrução da lane (`_rebuild_lane_nodes`, caminho feliz)

**Files:**
- Modify: `templatefill/igoe.py` (substitui o stub de `_rebuild_lane_nodes` da Task 1)
- Test: `tests/test_smartart_data_nodes.py` (adiciona testes)

**Interfaces:**
- Consome: `_q`, `_text_of`, `_set_run_text` (já existe, `igoe.py:48-52`), `_new_guid`, `DGM`, `A` (Task 1).
- Produz: `_rebuild_lane_nodes(work: etree._Element, lane_root_pt: etree._Element, shared_pres_id: str, label: str, items: list[str]) -> None` — muta `work` in-place; levanta exceção em estrutura inesperada; nunca toca `pkg`.

- [ ] **Step 1: Escrever os testes que falham**

Adicionar a `tests/test_smartart_data_nodes.py`:

```python
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
```

- [ ] **Step 2: Rodar e confirmar que falha**

Run: `python tests/test_smartart_data_nodes.py`
Expected: `NotImplementedError` (stub da Task 1) nos 4 testes novos.

- [ ] **Step 3: Implementar**

Substituir o stub `_rebuild_lane_nodes` (adicionado na Task 1) por:

```python
def _rebuild_lane_nodes(
    work: etree._Element,
    lane_root_pt: etree._Element,
    shared_pres_id: str,
    label: str,
    items: list[str],
) -> None:
    """Reconstrói os nós de conteúdo de uma lane no modelo de dados do
    SmartArt, replicando o padrão nativo (dgm:pt de conteúdo + parTrans +
    sibTrans + cxn de hierarquia + cxn presOf). Mutator puro: só opera sobre
    `work` (já em memória), nunca toca `pkg`. Levanta exceção em estrutura
    inesperada — quem chama decide o que fazer (ver `_sync_data_nodes`).
    `label` é o rótulo-alvo: para a lane do meio pode diferir do texto atual
    de `lane_root_pt` (ex. "ATIVIDADES" -> "SUBPROCESSOS"); para
    esquerda/direita já bate por construção (nenhum efeito)."""
    items = [i for i in items if i and i.strip()] or ["—"]
    root_id = lane_root_pt.get("modelId")

    pt_lst = work.find(_q(DGM, "ptLst"))
    cxn_lst = work.find(_q(DGM, "cxnLst"))

    hier_cxns = [
        c
        for c in cxn_lst.findall(_q(DGM, "cxn"))
        if c.get("type") is None and c.get("srcId") == root_id
    ]
    child_ids = {c.get("destId") for c in hier_cxns}
    content_pts = [
        p for p in pt_lst.findall(_q(DGM, "pt")) if p.get("modelId") in child_ids
    ]
    if not content_pts:
        raise ValueError(f"lane {label!r}: nenhum filho de conteúdo para usar de molde")

    template_run = None
    for p in content_pts:
        template_run = p.find(f".//{_q(A, 'r')}")
        if template_run is not None:
            break
    if template_run is None:
        raise ValueError(f"lane {label!r}: nenhum run de formatação para clonar")

    trans_ids = set()
    for c in hier_cxns:
        trans_ids.add(c.get("parTransId"))
        trans_ids.add(c.get("sibTransId"))
    pres_of_cxns = [
        c
        for c in cxn_lst.findall(_q(DGM, "cxn"))
        if c.get("type") == "presOf" and c.get("srcId") in child_ids
    ]

    for c in hier_cxns:
        cxn_lst.remove(c)
    for c in pres_of_cxns:
        cxn_lst.remove(c)
    for p in list(pt_lst.findall(_q(DGM, "pt"))):
        mid = p.get("modelId")
        if mid in child_ids or mid in trans_ids:
            pt_lst.remove(p)

    for k, text in enumerate(items):
        content_id, par_id, sib_id, hier_id, pres_id = (
            _new_guid(), _new_guid(), _new_guid(), _new_guid(), _new_guid()
        )

        content_pt = etree.SubElement(pt_lst, _q(DGM, "pt"))
        content_pt.set("modelId", content_id)
        pr = etree.SubElement(content_pt, _q(DGM, "prSet"))
        pr.set("phldrT", "[Texto]")
        pr.set("custT", "1")
        t = etree.SubElement(content_pt, _q(DGM, "t"))
        etree.SubElement(t, _q(A, "bodyPr"))
        etree.SubElement(t, _q(A, "lstStyle"))
        p_el = etree.SubElement(t, _q(A, "p"))
        r_el = copy.deepcopy(template_run)
        _set_run_text(r_el, text)
        p_el.append(r_el)

        for trans_type, trans_id in (("parTrans", par_id), ("sibTrans", sib_id)):
            trans_pt = etree.SubElement(pt_lst, _q(DGM, "pt"))
            trans_pt.set("modelId", trans_id)
            trans_pt.set("type", trans_type)
            trans_pt.set("cxnId", hier_id)
            etree.SubElement(trans_pt, _q(DGM, "prSet"))
            tt = etree.SubElement(trans_pt, _q(DGM, "t"))
            etree.SubElement(tt, _q(A, "bodyPr"))
            etree.SubElement(tt, _q(A, "lstStyle"))
            pp = etree.SubElement(tt, _q(A, "p"))
            etree.SubElement(pp, _q(A, "endParaRPr"))

        hier_cxn = etree.SubElement(cxn_lst, _q(DGM, "cxn"))
        hier_cxn.set("modelId", hier_id)
        hier_cxn.set("srcId", root_id)
        hier_cxn.set("destId", content_id)
        hier_cxn.set("srcOrd", str(k))
        hier_cxn.set("destOrd", "0")
        hier_cxn.set("parTransId", par_id)
        hier_cxn.set("sibTransId", sib_id)

        pres_cxn = etree.SubElement(cxn_lst, _q(DGM, "cxn"))
        pres_cxn.set("modelId", pres_id)
        pres_cxn.set("type", "presOf")
        pres_cxn.set("srcId", content_id)
        pres_cxn.set("destId", shared_pres_id)
        pres_cxn.set("srcOrd", "0")
        pres_cxn.set("destOrd", str(k))
        pres_cxn.set(
            "presId", "urn:microsoft.com/office/officeart/2005/8/layout/hProcess7"
        )

    for p in lane_root_pt.iter(_q(A, "p")):
        rs = p.findall(_q(A, "r"))
        if rs:
            _set_run_text(rs[0], label)
            for extra in rs[1:]:
                p.remove(extra)
            break
```

- [ ] **Step 4: Rodar e confirmar que passa**

Run: `python tests/test_smartart_data_nodes.py`
Expected: `todos os testes passaram (task 1)` (adicione as chamadas dos 4 testes novos ao bloco `if __name__ == "__main__":` antes de rodar — ver Step 5).

- [ ] **Step 5: Atualizar o bloco de execução e commitar**

No final de `tests/test_smartart_data_nodes.py`, atualizar o bloco `__main__`:

```python
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
    print("todos os testes passaram (task 2)")
```

Rodar de novo (`python tests/test_smartart_data_nodes.py`), confirmar `todos os testes passaram (task 2)`, depois:

```bash
git add templatefill/igoe.py tests/test_smartart_data_nodes.py
git commit -m "$(cat <<'EOF'
Implementa reconstrução dos nós de conteúdo de uma lane (D3, task 2/6)

_rebuild_lane_nodes replica o padrão nativo hProcess7 (conteúdo + parTrans
+ sibTrans + cxn de hierarquia + presOf compartilhado), incluindo o
atributo cxnId de retorno e custT="1", confirmados byte-a-byte contra o
template real durante a verificação da spec.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 3: Robustez do mutator — idempotência e propagação de falha

**Files:**
- Modify: `templatefill/igoe.py` (nenhuma mudança de produção nesta task — só testes; se algum teste achar um bug real na Task 2, corrija aqui antes de prosseguir)
- Test: `tests/test_smartart_data_nodes.py`

**Interfaces:**
- Consome: tudo de Task 1/2, mais `templatefill.igoe` como módulo (para monkeypatch manual de `_new_guid`).

- [ ] **Step 1: Escrever os testes que falham (podem já passar — é uma verificação, não uma feature nova)**

```python
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
```

- [ ] **Step 2: Rodar e confirmar o resultado**

Run: `python tests/test_smartart_data_nodes.py` (com estes 2 testes chamados manualmente antes de mexer no `__main__` — pode rodar via `python -c "import tests.test_smartart_data_nodes as t; t.test_rebuild_lane_nodes_idempotent(); t.test_rebuild_lane_nodes_propagates_exception_and_leaves_partial_state_to_caller(); print('ok')"` a partir da raiz do repo).
Expected: `ok` — estes testes validam comportamento que a implementação da Task 2 já deveria satisfazer (remoção por conjunto de IDs, não por índice). Se algum `assert` falhar, é um bug real na Task 2: volte lá e corrija antes de prosseguir (não pule esta task).

- [ ] **Step 3: (se necessário) corrigir Task 2**

Só aplicável se o Step 2 falhar. Given a implementação do Step 3 da Task 2 já usa remoção por conjunto de IDs coletados primeiro (não `.find()`), o esperado é que passe sem mudança de código de produção.

- [ ] **Step 4: Atualizar o bloco de execução e rodar tudo**

Adicionar ao `__main__`:

```python
    test_rebuild_lane_nodes_idempotent()
    test_rebuild_lane_nodes_propagates_exception_and_leaves_partial_state_to_caller()
    print("todos os testes passaram (task 3)")
```

Run: `python tests/test_smartart_data_nodes.py`
Expected: `todos os testes passaram (task 3)`

- [ ] **Step 5: Commit**

```bash
git add tests/test_smartart_data_nodes.py
git commit -m "$(cat <<'EOF'
Testa idempotência e propagação de falha do mutator (D3, task 3/6)

Confirma que _rebuild_lane_nodes remove por conjunto de IDs (sem órfãos
numa 2a chamada) e propaga exceção em vez de engolir erro no meio da
reconstrução — pré-requisito para o isolamento transacional da task 4.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 4: Orquestrador transacional (`_sync_data_nodes`)

**Files:**
- Modify: `templatefill/igoe.py` (substitui o stub de `_sync_data_nodes` da Task 1)
- Test: `tests/test_smartart_data_nodes.py`

**Interfaces:**
- Consome: `_find_lane_roots`, `_rebuild_lane_nodes` (Tasks 1-2), `Package.has_part`/`.part`/`.set_part` (já existem em `templatefill/opc.py`).
- Produz: `_sync_data_nodes(pkg: Package, data_name: str, lanes: list[tuple[str, list[str]]]) -> None` — mesma assinatura de 3 argumentos que `_sync_data_text` tem hoje (será usada como substituta direta na Task 5).

- [ ] **Step 1: Escrever os testes que falham**

```python
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
```

- [ ] **Step 2: Rodar e confirmar que falha**

Run: `python -c "import tests.test_smartart_data_nodes as t; t.test_sync_data_nodes_happy_path_rewrites_all_lanes()"` a partir da raiz do repo.
Expected: `NotImplementedError` (stub da Task 1).

- [ ] **Step 3: Implementar**

Substituir o stub `_sync_data_nodes` (adicionado na Task 1) por:

```python
def _sync_data_nodes(
    pkg: Package, data_name: str, lanes: list[tuple[str, list[str]]]
) -> None:
    """Reconstrói os nós de conteúdo das 3 lanes no modelo de dados do
    SmartArt (editabilidade pós-geração no PowerPoint). Isolamento
    transacional: só grava (`pkg.set_part`) se as 3 lanes forem
    reconstruídas sem exceção; qualquer falha (pré-checagem ou no meio da
    reconstrução) deixa `data_name` 100% intocado."""
    if not pkg.has_part(data_name):
        return
    root = etree.fromstring(pkg.part(data_name))
    work = copy.deepcopy(root)

    left_label, right_label = lanes[0][0], lanes[2][0]
    found = _find_lane_roots(work, left_label, right_label)
    if found is None:
        return

    try:
        for (lane_root_pt, shared_pres_id), (label, items) in zip(found, lanes):
            _rebuild_lane_nodes(work, lane_root_pt, shared_pres_id, label, items)
    except Exception:
        return

    pkg.set_part(
        data_name,
        etree.tostring(work, xml_declaration=True, encoding="UTF-8", standalone=True),
    )
```

- [ ] **Step 4: Rodar e confirmar que passa**

Adicionar ao `__main__` de `tests/test_smartart_data_nodes.py`:

```python
    test_sync_data_nodes_happy_path_rewrites_all_lanes()
    test_sync_data_nodes_precheck_failure_is_noop()
    test_sync_data_nodes_missing_part_is_noop()
    test_sync_data_nodes_mid_lane_failure_aborts_whole_write()
    print("todos os testes passaram (task 4)")
```

Run: `python tests/test_smartart_data_nodes.py`
Expected: `todos os testes passaram (task 4)`

- [ ] **Step 5: Commit**

```bash
git add templatefill/igoe.py tests/test_smartart_data_nodes.py
git commit -m "$(cat <<'EOF'
Implementa orquestrador transacional _sync_data_nodes (D3, task 4/6)

Só grava a parte data*.xml se as 3 lanes forem reconstruídas sem
exceção — uma falha no meio (ex. lane do meio) descarta a cópia mutada
inteira, nunca escreve um XML pela metade. Achado grave da verificação
da spec, agora coberto por teste explícito.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 5: Ligar ao pipeline real (`_fill_lanes`) e remover `_sync_data_text`

**Files:**
- Modify: `templatefill/igoe.py:271-277` (call site dentro de `_fill_lanes`), `templatefill/igoe.py:301-317` (remover `_sync_data_text`)
- Test: `tests/test_generation.py` (regressão, já existe — sem mudança), `tests/test_smartart_data_nodes.py` (novo teste de integração ponta-a-ponta)

**Interfaces:**
- Consome: `_sync_data_nodes` (Task 4), `generate_ppt_bytes` (já existe em `templatefill/builder.py`).
- Produz: nada novo — só troca o miolo de `_fill_lanes`.

- [ ] **Step 1: Escrever o teste de integração que falha**

Adicionar a `tests/test_smartart_data_nodes.py`:

```python
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
```

- [ ] **Step 2: Rodar e confirmar que falha (ou passa por acidente)**

Run: `python -c "import tests.test_smartart_data_nodes as t; t.test_full_pipeline_data_model_matches_content_process_and_subprocess()"`
Expected: falha — hoje `_fill_lanes` ainda chama `_sync_data_text` (best-effort, contagem raramente bate), então os marcadores de "SUBPROCESSOS"/atividades muito provavelmente **não** aparecerão no modelo de dados reconstruído (o teste vai falhar no `assert "Sub A" in process_texts` ou similar).

- [ ] **Step 3: Implementar — trocar o call site e remover a função antiga**

Em `templatefill/igoe.py`, dentro de `_fill_lanes` (por volta da linha 275-277), trocar:

```python
    # sincronização best-effort do texto no modelo de dados (para editabilidade)
    if data and pkg.has_part(data):
        _sync_data_text(pkg, data, lanes)
```

por:

```python
    # reconstrução do modelo de dados (para editabilidade pós-geração no PowerPoint)
    if data and pkg.has_part(data):
        _sync_data_nodes(pkg, data, lanes)
```

Remover a função `_sync_data_text` inteira (linhas ~301-317, o bloco que começa com `def _sync_data_text(pkg: Package, data_name: str, lanes: ...)` e termina antes de `def fill_igoe_slide(`).

- [ ] **Step 4: Rodar tudo e confirmar que passa**

Adicionar ao `__main__` de `tests/test_smartart_data_nodes.py`:

```python
    test_full_pipeline_data_model_matches_content_process_and_subprocess()
    print("todos os testes passaram (task 5)")
```

Run: `python tests/test_smartart_data_nodes.py`
Expected: `todos os testes passaram (task 5)`

Run (regressão): `python tests/test_generation.py`
Expected: `todos os testes passaram`

- [ ] **Step 5: Commit**

```bash
git add templatefill/igoe.py tests/test_smartart_data_nodes.py
git commit -m "$(cat <<'EOF'
Liga _sync_data_nodes ao pipeline real, remove _sync_data_text (D3, task 5/6)

_fill_lanes agora reconstrói o modelo de dados de verdade em vez do
best-effort anterior (que quase nunca sincronizava, pois exigia contagem
exata de nós). Teste de integração ponta-a-ponta confirma slide de
processo (lane SUBPROCESSOS) e de subprocesso (lane ATIVIDADES) com o
conteúdo certo no modelo de dados, sem vazamento de texto do template.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 6: Verificação final — QA visual, regressão completa, revisão por subagentes

**Files:** nenhuma mudança de código esperada — task de verificação. Se algo for encontrado, corrigir no arquivo relevante (`templatefill/igoe.py` ou os testes) e commitar como parte desta task.

**Interfaces:** N/A (task de verificação, não de código novo).

- [ ] **Step 1: Rodar toda a suíte de testes**

```bash
python tests/test_generation.py
python tests/test_smartart_data_nodes.py
```

Expected: ambos terminam com `todos os testes passaram`.

- [ ] **Step 2: QA visual (render) — confirma que o desenho não mudou**

Se o pipeline de QA existir no repo (`tools/qa_render.py` ou similar, conforme `docs/SESSION-ONBOARD-pptx.md`), gerar um deck de teste e renderizar (LibreOffice → PDF → PyMuPDF → PNG); comparar visualmente com uma geração anterior à Task 5 (checkout do commit anterior num worktree separado, ou simplesmente confirmar ausência de overflow/sobreposição nas lanes) — esta mudança só toca o modelo de dados, o desenho (fonte de verdade do render) não deveria mudar 1 byte. Se não houver script pronto, gerar manualmente:

```bash
python -c "
from schema import GlobalElements, Process, ScopeDiagram, Subprocess
from templatefill.builder import generate_ppt_bytes
scope = ScopeDiagram(
    process=Process(name='QA Final', objective='Objetivo QA', start_event='Início', end_event='Fim'),
    global_elements=GlobalElements(inputs=['in1'], outputs=['out1'], regulators=['reg1'], resources=['res1']),
    subprocesses=[Subprocess(name='Sub QA', objective='Obj sub', inputs=['ins1'], activities=['a1','a2'], outputs=['outs1'], start_event='ini', end_event='fim')],
)
data = generate_ppt_bytes(scope, today='08/07/2026')
open('/tmp/qa_final.pptx', 'wb').write(data)
print(len(data), 'bytes')
"
```

Confirmar que o arquivo abre sem erro (`zf.testzip() is None`, já coberto pelos testes de fumaça) e, se possível, abrir visualmente (LibreOffice ou similar) para checar ausência de regressão visual.

- [ ] **Step 3: Revisão de código por subagente independente**

Disparar um subagente fresco (sem contexto desta conversa) para revisar o diff final de `templatefill/igoe.py` contra a spec (`docs/superpowers/specs/2026-07-08-smartart-data-model-editability-design.md`) — confirmar que a implementação bate com o que a spec (já verificada 2x) descreve, e que não introduziu nenhum desvio silencioso. Aplicar qualquer correção encontrada e rodar os testes de novo até ficar limpo.

- [ ] **Step 4: Atualizar durables do projeto**

- `docs/_DECISOES-PENDENTES.md`: marcar D3 como 🟢 DECIDIDA (opção B, implementada).
- `docs/_TODO.md`: mover o item de D3/editabilidade de pendente para concluído.
- `docs/SESSION-ONBOARD-pptx.md`: atualizar §2 (feito) e §5 (próximo movimento) — a editabilidade pós-geração agora está implementada; próximo passo real é o usuário abrir o `.pptx` gerado no PowerPoint de verdade e confirmar manualmente (limite conhecido, não testável nesta máquina).

- [ ] **Step 5: Commit final**

```bash
git add docs/_DECISOES-PENDENTES.md docs/_TODO.md docs/SESSION-ONBOARD-pptx.md
git commit -m "$(cat <<'EOF'
Marca D3 (editabilidade do SmartArt) como implementada e verificada

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

**Nota final para quem executar este plano:** a validação real de "abrir no PowerPoint de verdade, editar um item, e o resultado continuar consistente" **não pode ser feita nesta máquina** (sem PowerPoint instalado; LibreOffice não recalcula SmartArt a partir do modelo de dados). Isso é do usuário — comunicar isso claramente ao final, não afirmar que a editabilidade "funciona no PowerPoint" sem essa confirmação manual.
