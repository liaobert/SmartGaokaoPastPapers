"""Convert Office Math Markup Language (OMML) fragments to LaTeX for MathJax."""

from __future__ import annotations

import re
from typing import Any
from xml.etree import ElementTree as ET

M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"m": M_NS, "w": W_NS}


def _local(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", 1)[-1]
    return tag


def _text(el: ET.Element | None) -> str:
    if el is None:
        return ""
    parts: list[str] = []
    for t in el.iter():
        if _local(t.tag) == "t" and t.text:
            parts.append(t.text)
    return "".join(parts)


def _escape_latex_text(s: str) -> str:
    # Keep common math chars; escape latex specials in plain text runs
    repl = {
        "\\": r"\textbackslash{}",
        "{": r"\{",
        "}": r"\}",
        "#": r"\#",
        "$": r"\$",
        "%": r"\%",
        "&": r"\&",
        "_": r"\_",
        "^": r"\^{}",
        "~": r"\textasciitilde{}",
    }
    return "".join(repl.get(ch, ch) for ch in s)


def _chr_latex(el: ET.Element) -> str:
    # Prefer m:t under m:r
    t = _text(el)
    if not t:
        return ""
    # Greek / symbols often already unicode
    mapping = {
        "∞": r"\infty ",
        "≠": r"\neq ",
        "≤": r"\le ",
        "≥": r"\ge ",
        "±": r"\pm ",
        "·": r"\cdot ",
        "×": r"\times ",
        "÷": r"\div ",
        "∈": r"\in ",
        "∉": r"\notin ",
        "⊂": r"\subset ",
        "⊆": r"\subseteq ",
        "∪": r"\cup ",
        "∩": r"\cap ",
        "∅": r"\emptyset ",
        "→": r"\to ",
        "⇒": r"\Rightarrow ",
        "⇔": r"\Leftrightarrow ",
        "∠": r"\angle ",
        "△": r"\triangle ",
        "π": r"\pi ",
        "α": r"\alpha ",
        "β": r"\beta ",
        "θ": r"\theta ",
        "λ": r"\lambda ",
        "μ": r"\mu ",
        "σ": r"\sigma ",
        "Δ": r"\Delta ",
        "∑": r"\sum ",
        "∏": r"\prod ",
        "√": r"\sqrt ",
    }
    out = []
    for ch in t:
        out.append(mapping.get(ch, _escape_latex_text(ch)))
    return "".join(out)


def _children_math(el: ET.Element) -> list[ET.Element]:
    return [c for c in list(el) if _local(c.tag) not in {"ctrlPr", "rPr", "t"}]


def omml_element_to_latex(el: ET.Element) -> str:
    tag = _local(el.tag)

    if tag in {"oMath", "oMathPara", "e", "deg", "num", "den", "sub", "sup", "fName"}:
        return "".join(omml_element_to_latex(c) for c in list(el) if _local(c.tag) != "ctrlPr")

    if tag == "r":
        return _chr_latex(el)

    if tag == "t":
        return _escape_latex_text(el.text or "")

    if tag == "f":  # fraction
        num = den = ""
        for c in list(el):
            loc = _local(c.tag)
            if loc == "num":
                num = omml_element_to_latex(c)
            elif loc == "den":
                den = omml_element_to_latex(c)
        return rf"\frac{{{num}}}{{{den}}}"

    if tag == "sSup":
        base = sup = ""
        for c in list(el):
            loc = _local(c.tag)
            if loc == "e":
                base = omml_element_to_latex(c)
            elif loc == "sup":
                sup = omml_element_to_latex(c)
        return rf"{{{base}}}^{{{sup}}}"

    if tag == "sSub":
        base = sub = ""
        for c in list(el):
            loc = _local(c.tag)
            if loc == "e":
                base = omml_element_to_latex(c)
            elif loc == "sub":
                sub = omml_element_to_latex(c)
        return rf"{{{base}}}_{{{sub}}}"

    if tag == "sSubSup":
        base = sub = sup = ""
        for c in list(el):
            loc = _local(c.tag)
            if loc == "e":
                base = omml_element_to_latex(c)
            elif loc == "sub":
                sub = omml_element_to_latex(c)
            elif loc == "sup":
                sup = omml_element_to_latex(c)
        return rf"{{{base}}}_{{{sub}}}^{{{sup}}}"

    if tag == "rad":
        deg = ""
        body = ""
        for c in list(el):
            loc = _local(c.tag)
            if loc == "deg":
                deg = omml_element_to_latex(c).strip()
            elif loc == "e":
                body = omml_element_to_latex(c)
        if deg:
            return rf"\sqrt[{deg}]{{{body}}}"
        return rf"\sqrt{{{body}}}"

    if tag == "nary":
        # ∑ ∫ ∏
        op = ""
        sub = ""
        sup = ""
        body = ""
        for c in list(el):
            loc = _local(c.tag)
            if loc == "naryPr":
                ch = c.find(f"{{{M_NS}}}chr")
                if ch is not None and ch.get(f"{{{M_NS}}}val"):
                    op = ch.get(f"{{{M_NS}}}val") or ""
            elif loc == "sub":
                sub = omml_element_to_latex(c)
            elif loc == "sup":
                sup = omml_element_to_latex(c)
            elif loc == "e":
                body = omml_element_to_latex(c)
        op_map = {"∑": r"\sum", "∏": r"\prod", "∫": r"\int", "⋃": r"\bigcup", "⋂": r"\bigcap"}
        op_tex = op_map.get(op, r"\sum")
        if sub or sup:
            return rf"{op_tex}_{{{sub}}}^{{{sup}}}{{{body}}}"
        return rf"{op_tex}{{{body}}}"

    if tag == "d":  # delimiter
        body = "".join(
            omml_element_to_latex(c) for c in list(el) if _local(c.tag) in {"e"}
        )
        beg = end = ""
        pr = el.find(f"{{{M_NS}}}dPr")
        if pr is not None:
            b = pr.find(f"{{{M_NS}}}begChr")
            e = pr.find(f"{{{M_NS}}}endChr")
            if b is not None:
                beg = b.get(f"{{{M_NS}}}val") or ""
            if e is not None:
                end = e.get(f"{{{M_NS}}}val") or ""
        left = {"(": "(", "[": "[", "{": r"\{", "|": "|", "": ""}.get(beg, beg)
        right = {")": ")", "]": "]", "}": r"\}", "|": "|", "": ""}.get(end, end)
        if left or right:
            return rf"\left{left}{body}\right{right}"
        return rf"\left({body}\right)"

    if tag == "func":
        name = body = ""
        for c in list(el):
            loc = _local(c.tag)
            if loc == "fName":
                name = omml_element_to_latex(c).strip()
            elif loc == "e":
                body = omml_element_to_latex(c)
        name_map = {
            "sin": r"\sin",
            "cos": r"\cos",
            "tan": r"\tan",
            "cot": r"\cot",
            "sec": r"\sec",
            "csc": r"\csc",
            "ln": r"\ln",
            "log": r"\log",
            "lim": r"\lim",
            "max": r"\max",
            "min": r"\min",
        }
        op = name_map.get(name, rf"\operatorname{{{name}}}" if name else "")
        return rf"{op}\left({body}\right)"

    if tag == "acc":  # accent e.g. vector
        body = ""
        chr_val = ""
        for c in list(el):
            loc = _local(c.tag)
            if loc == "accPr":
                ch = c.find(f"{{{M_NS}}}chr")
                if ch is not None:
                    chr_val = ch.get(f"{{{M_NS}}}val") or ""
            elif loc == "e":
                body = omml_element_to_latex(c)
        if chr_val in {"̂", "^"}:
            return rf"\hat{{{body}}}"
        if chr_val in {"̄", "¯"}:
            return rf"\bar{{{body}}}"
        if chr_val in {"⃗", "→"}:
            return rf"\vec{{{body}}}"
        return rf"\widehat{{{body}}}"

    if tag == "box":
        return "".join(omml_element_to_latex(c) for c in list(el) if _local(c.tag) == "e")

    if tag == "eqArr":
        rows = [omml_element_to_latex(c) for c in list(el) if _local(c.tag) == "e"]
        return r"\begin{aligned}" + r"\\".join(rows) + r"\end{aligned}"

    # fallback: concatenate children / text
    parts = [omml_element_to_latex(c) for c in list(el)]
    if parts:
        return "".join(parts)
    return _escape_latex_text(_text(el))


def omml_to_latex(raw_ooxml: str) -> str:
    """Convert an OMML XML string to LaTeX; empty string on failure."""
    if not raw_ooxml or not raw_ooxml.strip():
        return ""
    xml = raw_ooxml.strip()
    # Ensure a single root for fragments
    if not xml.startswith("<"):
        return ""
    try:
        # Register default namespaces loosely
        root = ET.fromstring(xml)
    except ET.ParseError:
        # wrap if multiple roots
        try:
            root = ET.fromstring(f"<root>{xml}</root>")
        except ET.ParseError:
            # last resort: extract m:t texts
            texts = re.findall(r"<[^>]*:?t[^>]*>([^<]*)</", xml)
            return _escape_latex_text("".join(texts))
    try:
        latex = omml_element_to_latex(root).strip()
        latex = re.sub(r"\s+", " ", latex)
        return latex
    except Exception:
        texts = re.findall(r"<[^>]*:?t[^>]*>([^<]*)</", xml)
        return _escape_latex_text("".join(texts))


def enrich_content_blocks(blocks: list[Any] | None) -> list[dict[str, Any]]:
    """Strip raw_ooxml; add latex for omath runs."""
    if not isinstance(blocks, list):
        return []
    out: list[dict[str, Any]] = []
    for block in blocks:
        if not isinstance(block, dict):
            continue
        b = {k: v for k, v in block.items() if k != "raw_ooxml"}
        if b.get("type") == "paragraph" and isinstance(b.get("runs"), list):
            runs = []
            for r in b["runs"]:
                if not isinstance(r, dict):
                    continue
                rr = {k: v for k, v in r.items() if k != "raw_ooxml"}
                if r.get("type") == "omath":
                    latex = omml_to_latex(r.get("raw_ooxml") or "")
                    if latex:
                        rr["latex"] = latex
                    # keep plain fallback from extracted text
                    if not rr.get("text"):
                        texts = re.findall(
                            r"<[^>]*:?t[^>]*>([^<]*)</", r.get("raw_ooxml") or ""
                        )
                        if texts:
                            rr["text"] = "".join(texts)
                runs.append(rr)
            b["runs"] = runs
        out.append(b)
    return out
