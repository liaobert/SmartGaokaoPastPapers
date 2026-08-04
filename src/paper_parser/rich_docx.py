#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 DOCX 提取带公式/图片的富文本题干。"""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from xml.etree import ElementTree as ET

from .omml_latex import omml_element_to_latex

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
V_NS = "urn:schemas-microsoft-com:vml"

NS = {"w": W_NS, "m": M_NS, "r": R_NS, "a": A_NS, "v": V_NS}


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def _mime_for(name: str) -> str:
    ext = Path(name).suffix.lower()
    return {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".bmp": "image/bmp",
        ".wmf": "image/x-wmf",
        ".emf": "image/x-emf",
    }.get(ext, "application/octet-stream")


def _convert_vector_to_png(data: bytes, src_ext: str) -> Optional[bytes]:
    """WMF/EMF → PNG（依赖 ImageMagick convert）。"""
    convert = shutil.which("convert")
    if not convert:
        return None
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / f"in{src_ext}"
        dst = Path(td) / "out.png"
        src.write_bytes(data)
        try:
            r = subprocess.run(
                [convert, "-density", "200", str(src), "-trim", "+repage",
                 "-resize", "x48>", "-bordercolor", "white", "-border", "2", str(dst)],
                capture_output=True, timeout=30,
            )
        except Exception:
            return None
        if r.returncode != 0 or not dst.is_file() or dst.stat().st_size < 50:
            return None
        return dst.read_bytes()


class RichDocxExtractor:
    """按文档顺序提取段落纯文本/富文本，并落盘媒体文件。"""

    def __init__(self, docx_path: str, media_dir: str):
        self.docx_path = docx_path
        self.media_dir = Path(media_dir)
        self.media_dir.mkdir(parents=True, exist_ok=True)
        self.rels: Dict[str, str] = {}
        self.saved: Dict[str, str] = {}  # media_id -> relative filename
        self.images: List[dict] = []

    def extract_paragraphs(self) -> List[str]:
        """返回富文本段落列表（含 $latex$ 与 {{MEDIA:file}}）。"""
        with zipfile.ZipFile(self.docx_path, "r") as zf:
            self._load_rels(zf)
            root = ET.fromstring(zf.read("word/document.xml"))
            body = root.find(f"{{{W_NS}}}body")
            if body is None:
                return []
            paragraphs: List[str] = []
            for child in body:
                tag = _local(child.tag)
                if tag == "p":
                    text = self._parse_paragraph(zf, child).strip()
                    if text:
                        paragraphs.append(text)
                elif tag == "tbl":
                    # 简单表格：逐单元格拼成段落
                    for p in child.iter(f"{{{W_NS}}}p"):
                        text = self._parse_paragraph(zf, p).strip()
                        if text:
                            paragraphs.append(text)
            return paragraphs

    def _load_rels(self, zf: zipfile.ZipFile):
        try:
            rel_root = ET.fromstring(zf.read("word/_rels/document.xml.rels"))
        except KeyError:
            return
        for rel in rel_root:
            rid = rel.attrib.get("Id")
            target = rel.attrib.get("Target", "")
            if rid and target:
                self.rels[rid] = target

    def _parse_paragraph(self, zf: zipfile.ZipFile, p_el: ET.Element) -> str:
        parts: List[str] = []
        for child in p_el:
            tag = _local(child.tag)
            if tag == "r":
                parts.append(self._parse_run(zf, child))
            elif tag == "hyperlink":
                for r in child.findall(f"{{{W_NS}}}r"):
                    parts.append(self._parse_run(zf, r))
            elif tag in {"oMath", "oMathPara"}:
                latex = omml_element_to_latex(child) or ""
                if latex:
                    parts.append(f"${latex}$")
                else:
                    parts.append("「公式」")
        return "".join(parts)

    def _parse_run(self, zf: zipfile.ZipFile, r_el: ET.Element) -> str:
        chunks: List[str] = []
        for obj in r_el.findall(f"{{{W_NS}}}object"):
            mid = self._save_object_preview(zf, obj)
            if mid:
                chunks.append("{{" + "MEDIA:" + mid + "}}")
            else:
                chunks.append("「公式」")
        for drawing in r_el.findall(f"{{{W_NS}}}drawing"):
            mid = self._save_drawing(zf, drawing)
            if mid:
                chunks.append("{{" + "MEDIA:" + mid + "}}")
        for pict in r_el.findall(f"{{{W_NS}}}pict"):
            mid = self._save_pict(zf, pict)
            if mid:
                chunks.append("{{" + "MEDIA:" + mid + "}}")
        texts = [t.text or "" for t in r_el.findall(f".//{{{W_NS}}}t")]
        text = "".join(texts)
        rPr = r_el.find(f"{{{W_NS}}}rPr")
        has_underline = rPr is not None and rPr.find(f"{{{W_NS}}}u") is not None
        if has_underline and not chunks:
            blank_chars = {"\u3000", " ", "\t", "\xa0"}
            if not text.strip() or all(ch in blank_chars for ch in text):
                width = max(6, min(16, len(text) if text else 8))
                chunks.append("_" * width)
            else:
                chunks.append(text)
        elif text:
            chunks.insert(0, text)
        elif not chunks and r_el.find(f"{{{W_NS}}}br") is not None:
            chunks.append("\n")
        return "".join(chunks)

    def _rid_from(self, el: ET.Element) -> Optional[str]:
        for attr, val in el.attrib.items():
            if _local(attr) in {"embed", "id", "href"} and val.startswith("rId"):
                return val
        return None

    def _save_by_rid(self, zf: zipfile.ZipFile, rid: str, role: str = "illustration") -> Optional[str]:
        target = self.rels.get(rid)
        if not target:
            return None
        part = target.lstrip("/")
        if not part.startswith("word/"):
            part = "word/" + part
        try:
            data = zf.read(part)
        except KeyError:
            return None
        return self._store_bytes(data, Path(part).name, role)

    def _store_bytes(self, data: bytes, filename: str, role: str) -> Optional[str]:
        digest = hashlib.md5(data).hexdigest()[:16]
        ext = Path(filename).suffix.lower() or ".bin"
        media_id = f"{digest}{ext}"

        # vector → png
        if ext in {".wmf", ".emf"}:
            png = _convert_vector_to_png(data, ext)
            if png:
                media_id = f"{digest}.png"
                data = png
                ext = ".png"
            # 若无法转换，仍保存原文件（浏览器可能无法显示）

        out_name = media_id
        out_path = self.media_dir / out_name
        if not out_path.exists():
            out_path.write_bytes(data)

        if out_name not in self.saved:
            self.saved[out_name] = out_name
            self.images.append({
                "image_id": f"IMG-{digest}",
                "image_path": out_name,
                "image_index": len(self.images),
                "description": role,
                "mime": _mime_for(out_name),
            })
        return out_name

    def _save_object_preview(self, zf: zipfile.ZipFile, obj: ET.Element) -> Optional[str]:
        # Prefer VML imagedata
        for el in obj.iter():
            if _local(el.tag) in {"imagedata", "blip"}:
                rid = self._rid_from(el)
                if rid:
                    mid = self._save_by_rid(zf, rid, role="formula")
                    if mid:
                        return mid
        # any rId in object
        for el in obj.iter():
            rid = self._rid_from(el)
            if rid:
                mid = self._save_by_rid(zf, rid, role="formula")
                if mid:
                    return mid
        return None

    def _save_drawing(self, zf: zipfile.ZipFile, drawing: ET.Element) -> Optional[str]:
        for el in drawing.iter():
            if _local(el.tag) == "blip":
                rid = self._rid_from(el)
                if rid:
                    return self._save_by_rid(zf, rid, role="illustration")
        return None

    def _save_pict(self, zf: zipfile.ZipFile, pict: ET.Element) -> Optional[str]:
        for el in pict.iter():
            if _local(el.tag) == "imagedata":
                rid = self._rid_from(el)
                if rid:
                    return self._save_by_rid(zf, rid, role="illustration")
        return None


def clean_legacy_placeholders(text: str) -> str:
    """清理历史 EMBED / INCLUDEPICTURE 占位。"""
    if not text:
        return text
    text = re.sub(r'EMBED\s+Equation\.[A-Za-z0-9.]+', '「公式」', text)
    text = re.sub(r'INCLUDEPICTURE\s+"[^"]*"\s*\\\*\s*MERGEFORMAT', '「图片」', text)
    text = re.sub(r'INCLUDEPICTURE\s+"[^"]*"', '「图片」', text)
    return text
