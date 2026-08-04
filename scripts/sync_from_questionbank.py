#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 QuestionBank 同步试卷题干/公式媒体到 SmartGaokaoPastPapers。

示例（服务器）:
  PYTHONPATH=src \
  QB_DB=/opt/gaokao/QuestionBank/parser_restorer/data/gaokao.db \
  GAOKAO_DB=/opt/smart-gaokao-pastpapers/database/gaokao.db \
  MEDIA_DIR=/opt/smart-gaokao-pastpapers/assets/question_media \
  python3 scripts/sync_from_questionbank.py P2023.北京.D9F96092B5E6 P-MATH-2023-BJ-O
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path


def export_media(qb: sqlite3.Connection, media_id: str, media_dir: Path) -> str | None:
    row = qb.execute(
        "SELECT media_id, mime_type, kind, data FROM media_asset WHERE media_id=?",
        (media_id,),
    ).fetchone()
    if not row:
        return None
    data = row["data"]
    kind = (row["kind"] or "").lower()
    mime = (row["mime_type"] or "").lower()
    digest = hashlib.md5(data).hexdigest()[:16]
    if "png" in mime or kind == "png":
        ext = ".png"
    elif "jpeg" in mime or "jpg" in mime or kind in {"jpeg", "jpg"}:
        ext = ".jpg"
    elif kind in {"wmf", "emf"} or "wmf" in mime or "emf" in mime:
        ext = ".emf" if (kind == "emf" or data[:4] == b"\x01\x00\x00\x00") else ".wmf"
    else:
        ext = ".bin"
    out = media_dir / f"{digest}{ext}"
    if not out.exists():
        out.write_bytes(data)
    if ext in {".wmf", ".emf"}:
        png = media_dir / f"{digest}.png"
        if (not png.exists() or png.stat().st_size < 50) and shutil.which("convert"):
            subprocess.run(
                [
                    "convert", "-density", "200", str(out),
                    "-trim", "+repage", "-resize", "x48>", "-bordercolor", "white", "-border", "2", str(png),
                ],
                capture_output=True, timeout=30,
            )
        if png.exists() and png.stat().st_size > 50:
            return png.name
        return out.name
    return out.name


def content_to_rich(qb: sqlite3.Connection, content_json: str, media_dir: Path):
    blocks = json.loads(content_json)
    parts, media_files = [], []
    for para in blocks:
        if not isinstance(para, dict):
            continue
        line = []
        for run in para.get("runs") or []:
            t = run.get("type")
            if t == "text":
                line.append(run.get("text") or "")
            elif t in {"image", "omath"}:
                mid, latex = run.get("media_id"), run.get("latex")
                if mid:
                    fname = export_media(qb, mid, media_dir)
                    if fname:
                        line.append("{{MEDIA:%s}}" % fname)
                        media_files.append(fname)
                    elif latex:
                        line.append("$%s$" % latex)
                    else:
                        line.append("「公式」")
                elif latex:
                    line.append("$%s$" % latex)
                else:
                    line.append("「公式」")
        text = "".join(line).rstrip()
        if text:
            parts.append(text)
    rich = "\n".join(parts)
    lines = rich.split("\n")
    while lines and re.match(r"^[一二三四五六七八九十]+[、.]", lines[0]):
        lines.pop(0)
    rich = "\n".join(lines).strip()
    return rich, media_files


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    qb_paper, sg_paper = sys.argv[1], sys.argv[2]
    qb_db = os.environ.get("QB_DB", "/opt/gaokao/QuestionBank/parser_restorer/data/gaokao.db")
    sg_db = os.environ.get("GAOKAO_DB", "database/gaokao.db")
    media_dir = Path(os.environ.get("MEDIA_DIR", "assets/question_media"))
    media_dir.mkdir(parents=True, exist_ok=True)

    qb = sqlite3.connect(qb_db)
    qb.row_factory = sqlite3.Row
    sg = sqlite3.connect(sg_db)
    sg.row_factory = sqlite3.Row

    qrows = qb.execute(
        "SELECT question_id, question_no, sort_order, content_json, plain_text "
        "FROM question WHERE paper_id=? ORDER BY sort_order",
        (qb_paper,),
    ).fetchall()
    mapped = {}
    for r in qrows:
        rich, medias = content_to_rich(qb, r["content_json"], media_dir)
        m = re.match(r"^(\d+)[.、．]", rich)
        if not m:
            for line in rich.split("\n"):
                m = re.match(r"^(\d+)[.、．]", line.strip())
                if m:
                    idx = rich.find(line.strip()[:20])
                    if idx >= 0:
                        rich = rich[idx:]
                    break
            m = re.match(r"^(\d+)[.、．]", rich)
        if m:
            mapped[m.group(1)] = (rich, medias)

    paper = sg.execute("SELECT id FROM papers WHERE paper_id=?", (sg_paper,)).fetchone()
    if not paper:
        raise SystemExit(f"missing paper {sg_paper}")

    updated = 0
    for num, (rich, medias) in mapped.items():
        qid = f"{sg_paper}-Q{num}"
        row = sg.execute("SELECT id FROM questions WHERE question_id=?", (qid,)).fetchone()
        if not row:
            print("skip missing", qid)
            continue
        q_db_id = row["id"]
        sg.execute(
            "UPDATE questions SET question_text=?, has_image=?, has_formula=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (rich, 1 if medias else 0, 1 if ("{{MEDIA:" in rich or "$" in rich) else 0, q_db_id),
        )
        sg.execute("DELETE FROM question_images WHERE question_id=?", (q_db_id,))
        for i, fname in enumerate(medias):
            sg.execute(
                "INSERT INTO question_images "
                "(question_id, image_id, image_path, image_type, image_format, description, position_in_question) "
                "VALUES (?,?,?,?,?,?,?)",
                (q_db_id, f"IMG-{q_db_id}-{i}-{fname}", fname, "formula",
                 fname.rsplit(".", 1)[-1], "formula", i),
            )
        updated += 1
        print(f"updated {qid} media={len(medias)}")
    sg.commit()
    print(f"done updated={updated}")
    qb.close()
    sg.close()


if __name__ == "__main__":
    main()
