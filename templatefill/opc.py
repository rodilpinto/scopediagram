"""Camada OPC mínima para manipular um .pptx como pacote de partes XML.

Trabalha diretamente sobre o zip (bytes por parte) + lxml, porque o conteúdo
crítico (diagramas SmartArt) não é acessível via python-pptx. Oferece as
operações de que o gerador precisa: deletar slide, clonar uma unidade de slide
IGOE (com suas partes de diagrama próprias) e reordenar os slides.
"""

from __future__ import annotations

import posixpath
import re
import zipfile
from io import BytesIO

from lxml import etree


CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
PRES_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"

SLIDE_CT = "application/vnd.openxmlformats-officedocument.presentationml.slide+xml"

# Partes "próprias" de um slide (por-slide, seguras para deletar/clonar junto).
_OWNED_DIRS = ("ppt/diagrams/", "ppt/notesSlides/")


def _qn(ns: str, tag: str) -> str:
    return f"{{{ns}}}{tag}"


class Package:
    def __init__(self, data: bytes):
        self._parts: dict[str, bytes] = {}
        with zipfile.ZipFile(BytesIO(data)) as zf:
            for info in zf.infolist():
                self._parts[info.filename] = zf.read(info.filename)

    # ---- construção / serialização -------------------------------------
    @classmethod
    def open(cls, path: str) -> "Package":
        with open(path, "rb") as fh:
            return cls(fh.read())

    def to_bytes(self) -> bytes:
        buf = BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            # [Content_Types].xml precisa vir primeiro por convenção.
            names = sorted(self._parts, key=lambda n: (n != "[Content_Types].xml", n))
            for name in names:
                zf.writestr(name, self._parts[name])
        return buf.getvalue()

    def save(self, path: str) -> None:
        with open(path, "wb") as fh:
            fh.write(self.to_bytes())

    # ---- acesso a partes -----------------------------------------------
    def part(self, name: str) -> bytes:
        return self._parts[name]

    def has_part(self, name: str) -> bool:
        return name in self._parts

    def set_part(self, name: str, data: bytes) -> None:
        self._parts[name] = data

    def remove_part(self, name: str) -> None:
        self._parts.pop(name, None)

    def _xml(self, name: str) -> etree._Element:
        return etree.fromstring(self._parts[name])

    def _write_xml(self, name: str, root: etree._Element) -> None:
        self._parts[name] = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)

    # ---- content types --------------------------------------------------
    def add_override(self, partname: str, content_type: str) -> None:
        root = self._xml("[Content_Types].xml")
        part = "/" + partname
        for ov in root.findall(_qn(CT_NS, "Override")):
            if ov.get("PartName") == part:
                ov.set("ContentType", content_type)
                self._write_xml("[Content_Types].xml", root)
                return
        ov = etree.SubElement(root, _qn(CT_NS, "Override"))
        ov.set("PartName", part)
        ov.set("ContentType", content_type)
        self._write_xml("[Content_Types].xml", root)

    def content_type_of(self, partname: str) -> str | None:
        root = self._xml("[Content_Types].xml")
        part = "/" + partname
        for ov in root.findall(_qn(CT_NS, "Override")):
            if ov.get("PartName") == part:
                return ov.get("ContentType")
        return None

    def remove_override(self, partname: str) -> None:
        root = self._xml("[Content_Types].xml")
        part = "/" + partname
        for ov in root.findall(_qn(CT_NS, "Override")):
            if ov.get("PartName") == part:
                root.remove(ov)
        self._write_xml("[Content_Types].xml", root)

    # ---- relationships --------------------------------------------------
    @staticmethod
    def _rels_name(part_name: str) -> str:
        d = posixpath.dirname(part_name)
        b = posixpath.basename(part_name)
        return posixpath.join(d, "_rels", b + ".rels")

    def rels(self, part_name: str) -> list[dict]:
        rels_name = self._rels_name(part_name)
        if rels_name not in self._parts:
            return []
        root = self._xml(rels_name)
        out = []
        for rel in root.findall(_qn(REL_NS, "Relationship")):
            out.append({
                "Id": rel.get("Id"),
                "Type": rel.get("Type"),
                "Target": rel.get("Target"),
                "TargetMode": rel.get("TargetMode"),
            })
        return out

    def write_rels(self, part_name: str, rels: list[dict]) -> None:
        rels_name = self._rels_name(part_name)
        root = etree.Element(_qn(REL_NS, "Relationships"))
        for r in rels:
            el = etree.SubElement(root, _qn(REL_NS, "Relationship"))
            el.set("Id", r["Id"])
            el.set("Type", r["Type"])
            el.set("Target", r["Target"])
            if r.get("TargetMode"):
                el.set("TargetMode", r["TargetMode"])
        self._write_xml(rels_name, root)

    @staticmethod
    def resolve(part_name: str, target: str) -> str:
        base = posixpath.dirname(part_name)
        return posixpath.normpath(posixpath.join(base, target))

    @staticmethod
    def relpath(from_part: str, to_part: str) -> str:
        base = posixpath.dirname(from_part)
        return posixpath.relpath(to_part, base)

    @staticmethod
    def _next_rid(rels: list[dict]) -> str:
        used = {int(m.group(1)) for r in rels if (m := re.match(r"rId(\d+)$", r["Id"]))}
        n = 1
        while n in used:
            n += 1
        return f"rId{n}"

    # ---- slides ---------------------------------------------------------
    _PRES = "ppt/presentation.xml"

    def slide_names(self) -> list[str]:
        """Slides na ordem de apresentação (sldIdLst)."""
        root = self._xml(self._PRES)
        lst = root.find(_qn(PRES_NS, "sldIdLst"))
        pres_rels = {r["Id"]: r for r in self.rels(self._PRES)}
        names = []
        if lst is None:
            return names
        for sld in lst.findall(_qn(PRES_NS, "sldId")):
            rid = sld.get(_qn(R_NS, "id"))
            rel = pres_rels.get(rid)
            if rel:
                names.append(self.resolve(self._PRES, rel["Target"]))
        return names

    def _owned_targets(self, slide_name: str) -> list[str]:
        owned = []
        for r in self.rels(slide_name):
            if r.get("TargetMode") == "External":
                continue
            tgt = self.resolve(slide_name, r["Target"])
            if any(tgt.startswith(d) for d in _OWNED_DIRS):
                owned.append(tgt)
        return owned

    def delete_slide(self, slide_name: str) -> None:
        # 1) remover sldId + rel na apresentação
        root = self._xml(self._PRES)
        lst = root.find(_qn(PRES_NS, "sldIdLst"))
        pres_rels = self.rels(self._PRES)
        rid_by_target = {self.resolve(self._PRES, r["Target"]): r["Id"] for r in pres_rels}
        rid = rid_by_target.get(slide_name)
        if lst is not None and rid is not None:
            for sld in lst.findall(_qn(PRES_NS, "sldId")):
                if sld.get(_qn(R_NS, "id")) == rid:
                    lst.remove(sld)
        self._write_xml(self._PRES, root)
        if rid is not None:
            self.write_rels(self._PRES, [r for r in pres_rels if r["Id"] != rid])

        # 2) remover partes próprias (diagramas/notas) + rels + overrides
        for tgt in self._owned_targets(slide_name):
            self.remove_part(tgt)
            self.remove_part(self._rels_name(tgt))
            self.remove_override(tgt)

        # 3) remover o slide + rels + override
        self.remove_part(slide_name)
        self.remove_part(self._rels_name(slide_name))
        self.remove_override(slide_name)

    def _max_index(self, prefix: str, suffix: str) -> int:
        rx = re.compile(re.escape(prefix) + r"(\d+)" + re.escape(suffix) + r"$")
        best = 0
        for name in self._parts:
            m = rx.match(name)
            if m:
                best = max(best, int(m.group(1)))
        return best

    def clone_slide(self, src_slide: str) -> str:
        """Duplica um slide e suas partes próprias de diagrama. Retorna o novo nome."""
        new_idx = self._max_index("ppt/slides/slide", ".xml") + 1
        new_slide = f"ppt/slides/slide{new_idx}.xml"
        self.set_part(new_slide, self.part(src_slide))
        self.add_override(new_slide, SLIDE_CT)

        # mapa de partes próprias antigas -> novas (novo sufixo único por parte)
        diag_idx = self._max_index("ppt/diagrams/data", ".xml")
        # também considerar drawing/layout/colors/quickStyle para não colidir
        for base in ("data", "layout", "colors", "quickStyle", "drawing"):
            diag_idx = max(diag_idx, self._max_index(f"ppt/diagrams/{base}", ".xml"))
        new_suffix = diag_idx + 1

        old_rels = self.rels(src_slide)
        new_rels = []
        for r in old_rels:
            if r.get("TargetMode") == "External":
                new_rels.append(dict(r))
                continue
            old_tgt = self.resolve(src_slide, r["Target"])
            if any(old_tgt.startswith(d) for d in _OWNED_DIRS) and old_tgt.startswith("ppt/diagrams/"):
                m = re.match(r"ppt/diagrams/([a-zA-Z]+)\d+\.xml$", old_tgt)
                base = m.group(1)
                new_tgt = f"ppt/diagrams/{base}{new_suffix}.xml"
                self.set_part(new_tgt, self.part(old_tgt))
                ct = self.content_type_of(old_tgt)
                if ct:
                    self.add_override(new_tgt, ct)
                # copiar rels da parte de diagrama, se houver
                old_diag_rels = self.rels(old_tgt)
                if old_diag_rels:
                    self.write_rels(new_tgt, old_diag_rels)
                new_rels.append({
                    "Id": r["Id"], "Type": r["Type"],
                    "Target": self.relpath(new_slide, new_tgt), "TargetMode": None,
                })
            elif old_tgt.startswith("ppt/notesSlides/"):
                # descartar notas nos clones (evita órfãos)
                continue
            else:
                # partes compartilhadas (layout, tema): manter alvo
                new_rels.append({
                    "Id": r["Id"], "Type": r["Type"],
                    "Target": self.relpath(new_slide, old_tgt), "TargetMode": None,
                })
        self.write_rels(new_slide, new_rels)

        # registrar na apresentação (rel + sldId)
        pres_rels = self.rels(self._PRES)
        new_rid = self._next_rid(pres_rels)
        pres_rels.append({
            "Id": new_rid,
            "Type": f"{R_NS}/slide",
            "Target": self.relpath(self._PRES, new_slide),
            "TargetMode": None,
        })
        self.write_rels(self._PRES, pres_rels)

        root = self._xml(self._PRES)
        lst = root.find(_qn(PRES_NS, "sldIdLst"))
        used_ids = {int(s.get("id")) for s in lst.findall(_qn(PRES_NS, "sldId"))}
        new_id = max(used_ids) + 1 if used_ids else 256
        sld = etree.SubElement(lst, _qn(PRES_NS, "sldId"))
        sld.set("id", str(new_id))
        sld.set(_qn(R_NS, "id"), new_rid)
        self._write_xml(self._PRES, root)
        return new_slide

    def reorder(self, ordered_slide_names: list[str]) -> None:
        root = self._xml(self._PRES)
        lst = root.find(_qn(PRES_NS, "sldIdLst"))
        pres_rels = {self.resolve(self._PRES, r["Target"]): r["Id"] for r in self.rels(self._PRES)}
        existing = {s.get(_qn(R_NS, "id")): s for s in lst.findall(_qn(PRES_NS, "sldId"))}
        for s in list(lst):
            lst.remove(s)
        for name in ordered_slide_names:
            rid = pres_rels.get(name)
            if rid and rid in existing:
                lst.append(existing[rid])
        self._write_xml(self._PRES, root)
