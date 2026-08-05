#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""???????????? LaTeX??? media_latex?????????

??:
  python3 scripts/ocr_formula_media.py --subject math --limit 200
  python3 scripts/ocr_formula_media.py --subject chemistry --limit 500
  python3 scripts/ocr_formula_media.py --subject physics --apply-text
"""

from __future__ import annotations

import argparse
import os
import re
import sqlite3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUBJECT_MAP = {
    "chinese": 1,
    "math": 2,
    "english": 3,
    "physics": 4,
    "chemistry": 5,
    "biology": 6,
    "politics": 7,
    "history": 8,
    "geography": 9,
}
SUBJECT_MEDIA_DIR = {
    "chinese": "??",
    "math": "??",
    "english": "??",
    "physics": "??",
    "chemistry": "??",
    "biology": "??",
    "politics": "??",
    "history": "??",
    "geography": "??",
}


def ensure_table(conn: sqlite3.Connection):
    sql = (ROOT / "database/migrations/001_media_latex.sql").read_text(encoding="utf-8")
    conn.executescript(sql)
    conn.commit()


def resolve_image(name: str, subject: str, media_dirs: list[Path]) -> Path | None:
    stem = name.rsplit(".", 1)[0]
    # Prefer raster (OCR-ready) over vector
    ordered = [f"{stem}.png", f"{stem}.jpg", f"{stem}.jpeg", name, f"{stem}.wmf", f"{stem}.emf"]
    for base in media_dirs:
        for nm in ordered:
            p = base / nm
            if p.exists() and p.is_file() and not p.name.startswith("._"):
                return p
    return None


def to_png(path: Path, cache_dir: Path) -> Path | None:
    low = path.suffix.lower()
    if low in {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}:
        return path
    out = cache_dir / f"{path.stem}.png"
    if out.exists() and out.stat().st_size > 50:
        return out
    if not shutil_which("convert"):
        return None
    cache_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        "convert",
        "-density",
        "200",
        str(path),
        "-trim",
        "+repage",
        "-resize",
        "x96>",
        "-bordercolor",
        "white",
        "-border",
        "2",
        str(out),
    ]
    try:
        subprocess.run(cmd, capture_output=True, timeout=30, check=False)
    except Exception:
        return None
    if out.exists() and out.stat().st_size > 50:
        return out
    return None


def shutil_which(cmd: str):
    from shutil import which

    return which(cmd)


def collect_media_names(conn: sqlite3.Connection, subject_id: int) -> list[str]:
    names = set()
    for (t,) in conn.execute(
        """
        SELECT q.question_text FROM questions q
        JOIN papers p ON q.paper_id = p.id
        WHERE p.subject_id=? AND q.question_text LIKE '%MEDIA:%'
        """,
        (subject_id,),
    ):
        names.update(re.findall(r"\{\{MEDIA:([^}]+)\}\}", t or ""))
    for (p, itype) in conn.execute(
        """
        SELECT qi.image_path, qi.image_type FROM question_images qi
        JOIN questions q ON qi.question_id = q.id
        JOIN papers p ON q.paper_id = p.id
        WHERE p.subject_id=?
        """,
        (subject_id,),
    ):
        if (itype or "").lower() in {"formula", "illustration", ""}:
            # ?? formula?illustration ???????????????
            names.add(p)
    return sorted(names)


def looks_like_formula_image(im) -> bool:
    w, h = im.size
    if w < 8 or h < 8:
        return False
    # ??????????????
    if h > 220 and w > 320:
        return False
    if h > 280:
        return False
    return True


def sanitize_latex(latex: str) -> str | None:
    if not latex:
        return None
    s = latex.strip().strip("$").strip()
    if not s or len(s) > 120:
        return None
    if abs(s.count("{") - s.count("}")) > 2:
        return None
    if "begin{array}" in s or "begin{align}" in s or "displaystyle" in s:
        return None
    if s.count("\\") >= 1:
        return None
    if s.count("mathrm") > 4 or "bullet" in s or "oint" in s:
        return None
    if s.count("hat{") > 3 or s.count("overset") + s.count("underset") > 2:
        return None
    if sum(ch.isalnum() for ch in s) < 2:
        return None
    if re.fullmatch(r"[\W_]+", s):
        return None
    return s


def apply_text_replacements(conn: sqlite3.Connection, subject_id: int) -> int:
    """???????? {{MEDIA:x}} ??? $latex$??????????"""
    mapping = {
        r["media_name"]: r["latex"]
        for r in conn.execute("SELECT media_name, latex FROM media_latex")
    }
    if not mapping:
        return 0
    updated = 0
    rows = conn.execute(
        """
        SELECT q.id, q.question_text FROM questions q
        JOIN papers p ON q.paper_id = p.id
        WHERE p.subject_id=? AND q.question_text LIKE '%MEDIA:%'
        """,
        (subject_id,),
    ).fetchall()
    for qid, text in rows:
        if not text:
            continue

        def repl(m):
            name = m.group(1)
            stem = name.rsplit(".", 1)[0]
            latex = mapping.get(name) or mapping.get(stem + ".png") or mapping.get(stem + ".jpg")
            if latex:
                return f"${latex}$"
            return m.group(0)

        new = re.sub(r"\{\{MEDIA:([^}]+)\}\}", repl, text)
        if new != text:
            conn.execute(
                "UPDATE questions SET question_text=?, has_formula=1, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                (new, qid),
            )
            updated += 1
    conn.commit()
    return updated


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject", required=True, choices=sorted(SUBJECT_MAP))
    ap.add_argument("--limit", type=int, default=0, help="???????0=???")
    ap.add_argument("--db", default=str(ROOT / "database/gaokao.db"))
    ap.add_argument("--media-dir", default=str(ROOT / "assets/question_media"))
    ap.add_argument("--apply-text", action="store_true", help="?????????")
    ap.add_argument("--force", action="store_true", help="????????")
    args = ap.parse_args()

    sid = SUBJECT_MAP[args.subject]
    media_dirs = [
        Path(args.media_dir),
        ROOT / "output" / SUBJECT_MEDIA_DIR[args.subject],
    ]
    cache_dir = Path(args.media_dir) / "_ocr_png"
    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row
    ensure_table(conn)

    names = collect_media_names(conn, sid)
    print(f"[{args.subject}] candidates={len(names)}")

    done = {
        r["media_name"]
        for r in conn.execute("SELECT media_name FROM media_latex")
    }
    todo = []
    for name in names:
        stem = name.rsplit(".", 1)[0]
        if not args.force and (name in done or f"{stem}.png" in done):
            continue
        todo.append(name)
    if args.limit:
        todo = todo[: args.limit]
    print(f"[{args.subject}] to_ocr={len(todo)}")

    if not todo:
        if args.apply_text:
            n = apply_text_replacements(conn, sid)
            print(f"apply-text updated={n}")
        return

    from PIL import Image
    from pix2tex.cli import LatexOCR

    model = LatexOCR()
    ok = fail = skip = 0
    for i, name in enumerate(todo, 1):
        src = resolve_image(name, args.subject, media_dirs)
        if not src:
            fail += 1
            print(f"  MISS {name}")
            continue
        png = to_png(src, cache_dir)
        if not png:
            fail += 1
            print(f"  NO_PNG {name}")
            continue
        try:
            im = Image.open(png).convert("RGB")
        except Exception as e:
            fail += 1
            print(f"  OPEN_ERR {name}: {e}")
            continue
        if not looks_like_formula_image(im):
            skip += 1
            continue
        try:
            raw = model(im)
        except Exception as e:
            fail += 1
            print(f"  OCR_ERR {name}: {e}")
            continue
        latex = sanitize_latex(raw)
        if not latex:
            skip += 1
            print(f"  REJECT {name} <- {raw!r}")
            continue
        # ??? png ??? key??????????
        key = f"{src.stem}.png" if src.suffix.lower() in {".wmf", ".emf"} else name
        if key.endswith((".wmf", ".emf")):
            key = key.rsplit(".", 1)[0] + ".png"
        conn.execute(
            """
            INSERT INTO media_latex(media_name, latex, method, updated_at)
            VALUES (?, ?, 'pix2tex', CURRENT_TIMESTAMP)
            ON CONFLICT(media_name) DO UPDATE SET
              latex=excluded.latex, method=excluded.method, updated_at=CURRENT_TIMESTAMP
            """,
            (key, latex),
        )
        # ?????????????
        if key != name:
            conn.execute(
                """
                INSERT INTO media_latex(media_name, latex, method, updated_at)
                VALUES (?, ?, 'pix2tex', CURRENT_TIMESTAMP)
                ON CONFLICT(media_name) DO UPDATE SET
                  latex=excluded.latex, method=excluded.method, updated_at=CURRENT_TIMESTAMP
                """,
                (name, latex),
            )
        conn.commit()
        ok += 1
        if i % 20 == 0 or i <= 10:
            print(f"  [{i}/{len(todo)}] {name} -> ${latex}$")

    print(f"done ok={ok} skip={skip} fail={fail}")
    if args.apply_text:
        n = apply_text_replacements(conn, sid)
        print(f"apply-text updated={n}")
    conn.close()


if __name__ == "__main__":
    main()
