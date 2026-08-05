#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Batch sync math rich stems from QuestionBank into SmartGaokaoPastPapers."""

from __future__ import annotations

import os
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from sync_from_questionbank import content_to_rich  # noqa: E402


def norm_region(s: str) -> str:
    s = (s or "").strip()
    for x in ("\u7701", "\u5e02", "\u81ea\u6cbb\u533a", "\u58ee\u65cf", "\u56de\u65cf", "\u7ef4\u543e\u5c14", "\u7279\u522b\u884c\u653f\u533a"):
        s = s.replace(x, "")
    return s


def main():
    qb_db = os.environ.get(
        "QB_DB",
        "/Volumes/yingpan/workspace/AiEdu/QuestionBank/parser_restorer/data/gaokao.db",
    )
    sg_db = os.environ.get("GAOKAO_DB", str(ROOT / "database/gaokao.db"))
    media_dir = Path(os.environ.get("MEDIA_DIR", ROOT / "assets/question_media"))
    media_dir.mkdir(parents=True, exist_ok=True)
    only_embed = "--all" not in sys.argv
    limit = 0
    for a in sys.argv[1:]:
        if a.startswith("--limit="):
            limit = int(a.split("=", 1)[1])

    qb = sqlite3.connect(f"file:{qb_db}?mode=ro", uri=True)
    qb.row_factory = sqlite3.Row
    sg = sqlite3.connect(sg_db)
    sg.row_factory = sqlite3.Row

    by_year = {}
    for p in qb.execute(
        "SELECT paper_id, title, year, region FROM paper WHERE subject LIKE ?",
        ("%\u6570\u5b66%",),
    ):
        by_year.setdefault(str(p["year"]), []).append(p)

    sg_papers = sg.execute(
        """
        SELECT p.id, p.paper_id, p.year, p.region, p.paper_title,
               SUM(CASE WHEN q.question_text LIKE '%EMBED Equation%' THEN 1 ELSE 0 END) AS embed_n
        FROM papers p
        JOIN questions q ON q.paper_id = p.id
        WHERE p.subject_id = 2
        GROUP BY p.id
        ORDER BY embed_n DESC, p.year DESC
        """
    ).fetchall()

    wen = "\u6587\u79d1"
    li = "\u7406\u79d1"
    jiexi = "\u89e3\u6790"
    yuanjuan = "\u539f\u5377"
    quanguo = "\u5168\u56fd"
    xinkebiao = "\u65b0\u8bfe\u6807"
    kebiao = "\u8bfe\u6807"

    pairs = []
    for sp in sg_papers:
        if only_embed and (sp["embed_n"] or 0) <= 0:
            continue
        year = str(sp["year"])
        region = norm_region(sp["region"] or "")
        title_hint = (sp["paper_title"] or "") + (sp["paper_id"] or "")
        want_wen = (wen in title_hint) or ("-W-" in (sp["paper_id"] or ""))
        want_li = (li in title_hint) or ("-L-" in (sp["paper_id"] or ""))
        cands = by_year.get(year) or []
        best = None
        best_score = -1
        for cp in cands:
            title = cp["title"] or ""
            cpreg = norm_region(cp["region"] or "")
            score = 0
            if region and region in title:
                score += 4
            if region and (region == cpreg or region in cpreg or cpreg in region):
                score += 4
            if region in {quanguo} or "QGY" in (sp["paper_id"] or ""):
                if any(k in title for k in (xinkebiao, quanguo, kebiao)):
                    score += 2
            if want_wen:
                if wen in title:
                    score += 3
                elif li in title:
                    score -= 3
            if want_li:
                if li in title:
                    score += 3
                elif wen in title:
                    score -= 3
            if jiexi in title and yuanjuan not in title:
                score -= 1
            if score > best_score:
                best_score = score
                best = cp
        if best and best_score >= 4:
            pairs.append((sp, best, best_score))

    if limit:
        pairs = pairs[:limit]
    print(f"matched papers={len(pairs)} (only_embed={only_embed})")

    total_q = 0
    for sp, qp, score in pairs:
        qrows = qb.execute(
            "SELECT content_json FROM question WHERE paper_id=? ORDER BY sort_order",
            (qp["paper_id"],),
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

        updated = 0
        for num, (rich, medias) in mapped.items():
            row = sg.execute(
                "SELECT id, question_text FROM questions WHERE question_id=?",
                (f"{sp['paper_id']}-Q{num}",),
            ).fetchone()
            if not row:
                row = sg.execute(
                    """
                    SELECT id, question_text FROM questions
                    WHERE paper_id=? AND CAST(question_number AS TEXT)=?
                    """,
                    (sp["id"], num),
                ).fetchone()
            if not row:
                continue
            old = row["question_text"] or ""
            if only_embed and "EMBED Equation" not in old and "{{MEDIA:" in old:
                continue
            sg.execute(
                """
                UPDATE questions
                SET question_text=?, has_image=?, has_formula=?, updated_at=CURRENT_TIMESTAMP
                WHERE id=?
                """,
                (
                    rich,
                    1 if medias else 0,
                    1 if ("{{MEDIA:" in rich or "$" in rich) else 0,
                    row["id"],
                ),
            )
            sg.execute("DELETE FROM question_images WHERE question_id=?", (row["id"],))
            for i, fname in enumerate(medias):
                sg.execute(
                    """
                    INSERT INTO question_images
                    (question_id, image_id, image_path, image_type, image_format,
                     description, position_in_question)
                    VALUES (?,?,?,?,?,?,?)
                    """,
                    (
                        row["id"],
                        f"IMG-{row['id']}-{i}-{fname}"[:100],
                        fname,
                        "formula",
                        fname.rsplit(".", 1)[-1],
                        "formula",
                        i,
                    ),
                )
            updated += 1
        sg.commit()
        total_q += updated
        print(
            f"OK {sp['paper_id']} <- {qp['paper_id']} score={score} "
            f"embed={sp['embed_n']} updated={updated}"
        )

    left = sg.execute(
        """
        SELECT COUNT(*) FROM questions q JOIN papers p ON q.paper_id=p.id
        WHERE p.subject_id=2 AND q.question_text LIKE '%EMBED Equation%'
        """
    ).fetchone()[0]
    print(f"done total_updated={total_q} remaining_embed={left}")
    qb.close()
    sg.close()


if __name__ == "__main__":
    main()
