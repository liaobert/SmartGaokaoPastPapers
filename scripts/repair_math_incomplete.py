#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Repair incomplete math stems by syncing rich content from QuestionBank.

Only updates a question when the QB stem is richer (more MEDIA / fewer EMBED),
and uses stricter paper matching to avoid cross-paper contamination.
"""

from __future__ import annotations

import os
import re
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from sync_from_questionbank import content_to_rich  # noqa: E402


def norm_region(s: str) -> str:
    s = (s or "").strip()
    for x in (
        "省",
        "市",
        "自治区",
        "壮族",
        "回族",
        "维吾尔",
        "特别行政区",
        "卷",
    ):
        s = s.replace(x, "")
    return s


def strip_noise(text: str) -> str:
    t = text or ""
    t = re.sub(r"\{\{MEDIA:[^}]+\}\}", "", t)
    t = re.sub(r"EMBED\s+Equation[^\s]*", "", t, flags=re.I)
    t = re.sub(r"\[FORMULA\]|「公式」|\$[^$]*\$", "", t)
    t = re.sub(r"\s+", "", t)
    return t


def is_incomplete(text: str) -> bool:
    t = text or ""
    if "EMBED Equation" in t or re.search(r"\bEMBED\b", t):
        return True
    if "「公式」" in t or "[FORMULA]" in t:
        return True
    if "{{MEDIA:" in t or "$" in t:
        return False
    if re.search(r"A[\.、．]\s*\t?\s*B[\.、．]\s*\t?\s*C", t):
        return True
    if re.search(r"A[\.、．]\s*$", t, re.M) and "（" in t:
        return True
    # formula likely stripped between Chinese connectors
    head = re.split(r"\nA[\.、．]", t)[0]
    body = re.sub(r"^\d+[\.、．]\s*", "", head)
    body = re.sub(r"[（(]\s*[)）]", "", body)
    body = re.sub(r"_+", "", body)
    compact = re.sub(r"\s+", "", body)
    if len(compact) <= 28 and re.search(r"[，。；]", compact) and (
        "则" in compact or "集合" in compact or "已知" in compact or "设" in compact
    ):
        return True
    if re.search(r"集合，则|全集，集合|不等式的解集为|设集合，|若复数，则|已知，则", t):
        return True
    return False


def _has_vol1(s: str) -> bool:
    if re.search(r"Ⅱ|III|Ⅲ|II卷|二卷|新Ⅱ|新课标\s*II|新高考\s*II", s):
        # II/Ⅲ present: only count as I if explicit Ⅰ / 新Ⅰ without II
        return bool(re.search(r"Ⅰ|新课标\s*Ⅰ|新高考\s*Ⅰ|新Ⅰ", s)) and not re.search(
            r"Ⅱ|II", s
        )
    return bool(
        re.search(
            r"X1|-X1-|Ⅰ|新课标\s*Ⅰ|新高考\s*Ⅰ|新Ⅰ|新课标\s*I(?!I)|全国\s*Ⅰ|全国一卷|I卷",
            s,
        )
    )


def _has_vol2(s: str) -> bool:
    return bool(
        re.search(
            r"X2|-X2-|-Q-O|Ⅱ|II卷|二卷|新Ⅱ|新课标\s*Ⅱ|新课标\s*II|新高考\s*Ⅱ|新高考\s*II|全国\s*Ⅱ|全国二卷",
            s,
        )
    )


def _has_vol3(s: str) -> bool:
    return bool(re.search(r"X3|-X3-|Ⅲ|III|三卷|新课标\s*Ⅲ|全国\s*Ⅲ", s))


def paper_flags(paper_id: str, title: str) -> dict:
    hint = (paper_id or "") + (title or "")
    return {
        "wen": ("文科" in hint) or ("-W-" in (paper_id or "")),
        "li": ("理科" in hint) or ("-L-" in (paper_id or "")),
        "jia": ("甲" in hint) or ("-J-" in (paper_id or "")),
        "yi": ("乙" in hint) or ("-Y-" in (paper_id or "")),
        "x1": _has_vol1(hint),
        "x2": _has_vol2(hint),
        "x3": _has_vol3(hint),
        "spring": ("春" in hint) or ("-S-" in (paper_id or "")),
        "autumn": ("秋" in hint) or ("-A-" in (paper_id or "")),
    }


def score_pair(sp, qp) -> int:
    pid = sp["paper_id"] or ""
    stitle = sp["paper_title"] or ""
    region = norm_region(sp["region"] or "")
    qtitle = qp["title"] or ""
    qreg = norm_region(qp["region"] or "")
    qblob = qtitle + " " + qreg + " " + (qp["paper_id"] or "")
    sf = paper_flags(pid, stitle)
    qf = paper_flags(qp["paper_id"] or "", qblob)

    score = 0
    # region / title locality
    if region and region in qblob:
        score += 5
    if region and (region == qreg or region in qreg or qreg in region):
        score += 4
    # national / xinkebiao buckets
    if "QGY" in pid or "XKB" in pid or region in {"全国", "新课标"}:
        if any(k in qblob for k in ("全国", "新课标", "新高考", "课标")):
            score += 2
    # 甲乙
    if sf["jia"]:
        score += 4 if ("甲" in qblob) else -5
    if sf["yi"]:
        score += 4 if ("乙" in qblob) else -5
    # I/II/III — strong penalties for cross-volume
    q1, q2, q3 = _has_vol1(qblob), _has_vol2(qblob), _has_vol3(qblob)
    if sf["x1"]:
        score += 5 if q1 else 0
        if q2 or q3:
            score -= 8
        if ("乙" in qblob or "甲" in qblob) and not q1:
            score -= 3
    if sf["x2"]:
        score += 5 if q2 else 0
        if q1 or q3:
            score -= 8
    if sf["x3"]:
        score += 5 if q3 else 0
        if not q3:
            score -= 6
        if "甲" in qblob or "乙" in qblob:
            score -= 4
    # 文理
    if sf["wen"]:
        score += 3 if ("文科" in qblob) else (-3 if "理科" in qblob else 0)
    if sf["li"]:
        score += 3 if ("理科" in qblob) else (-3 if "文科" in qblob else 0)
    # 上海春秋
    if "上海" in (region + stitle + pid):
        if sf["spring"]:
            score += 4 if "春" in qblob else -4
        elif sf["autumn"] or (not sf["spring"] and "SH-O" in pid):
            # summer/autumn: prefer non-spring
            score += 3 if ("春" not in qblob) else -4
            if "秋" in qblob or "夏" in qblob or "上海" in qblob:
                score += 1
    # prefer 原卷 / avoid 解析-only when both exist
    if "解析" in qtitle and "原卷" not in qtitle and "真题" not in qtitle:
        score -= 1
    if "[IMG]" in qtitle:
        score += 1  # often richer scanned/original
    if any(k in qtitle for k in ("解析", "详解", "答案汇编")) and "原卷" not in qtitle:
        score -= 8
    if "【高考真题】" in qtitle:
        score -= 3  # often answer-key style dumps
    return score


def qb_media_count(qb, paper_id: str) -> int:
    n = 0
    for (cj,) in qb.execute(
        "SELECT content_json FROM question WHERE paper_id=?", (paper_id,)
    ):
        if not cj:
            continue
        n += cj.count('"type": "image"') + cj.count('"type":"image"')
        n += cj.count('"type": "omath"') + cj.count('"type":"omath"')
    return n


def qb_q1_plain(qb, paper_id: str) -> str:
    row = qb.execute(
        "SELECT plain_text, content_json FROM question WHERE paper_id=? ORDER BY sort_order LIMIT 1",
        (paper_id,),
    ).fetchone()
    if not row:
        return ""
    plain = row[0] or ""
    plain = re.sub(r"\[FORMULA\]|「公式」", "", plain)
    # drop section headers
    lines = [ln.strip() for ln in plain.splitlines() if ln.strip()]
    for ln in lines:
        if re.match(r"^\d+[\.、．]", ln):
            return strip_noise(ln)[:40]
    return strip_noise(plain)[:40]


def local_q1_plain(sg, paper_db_id: int) -> str:
    row = sg.execute(
        """
        SELECT question_text FROM questions
        WHERE paper_id=? ORDER BY CAST(question_number AS INTEGER), question_id
        LIMIT 1
        """,
        (paper_db_id,),
    ).fetchone()
    if not row:
        return ""
    lines = [ln.strip() for ln in (row[0] or "").splitlines() if ln.strip()]
    for ln in lines:
        if re.match(r"^\d+[\.、．]", ln) or re.match(r"^（\d+）", ln):
            return strip_noise(ln)[:40]
    return strip_noise(row[0] or "")[:40]


# Hard overrides: local paper_id -> QB paper_id (when auto-match is ambiguous)
MANUAL_MAP = {
    "P-MATH-2024-XKB-X1-O": "P2024.新课标I.26093C2D1790",
    "P-MATH-2024-XKB-X2-O": "P2024.新课标I.1F06466CA028",
    "P-MATH-2024-TJ-O": "P2024.天津.95A1FB54E9ED",
    "P-MATH-2023-XKB-X2-O": "P2023.新高考Ⅱ.5400E399EC9C",
    "P-MATH-2022-QGY-X1-O": "P2022.新高考Ⅰ.7764A47302B4",
    "P-MATH-2022-QGY-J-L-O": "P2022.全国甲卷.5827D9F3C4D1",
    "P-MATH-2021-QGY-Q-O": "P2021.新高考Ⅰ.4D430DBB260E",
    "P-MATH-2021-QGY-Y-L-O": "P2021.全国乙卷.967C7D16636E",
    "P-MATH-2020-GD-L-O": "P2020.广东.354F7213788F",
    "P-MATH-2020-XKB-X1-O": "P2020.新课标Ⅰ.C16B56AF3517",
}


def main():
    qb_db = os.environ.get(
        "QB_DB",
        "/Volumes/yingpan/workspace/AiEdu/QuestionBank/parser_restorer/data/gaokao.db",
    )
    sg_db = os.environ.get("GAOKAO_DB", str(ROOT / "database/gaokao.db"))
    media_dir = Path(os.environ.get("MEDIA_DIR", ROOT / "assets/question_media"))
    media_dir.mkdir(parents=True, exist_ok=True)
    dry = "--dry-run" in sys.argv

    qb = sqlite3.connect(f"file:{qb_db}?mode=ro", uri=True)
    qb.row_factory = sqlite3.Row
    sg = sqlite3.connect(sg_db)
    sg.row_factory = sqlite3.Row

    by_year = defaultdict(list)
    qb_by_id = {}
    for p in qb.execute(
        "SELECT paper_id, title, year, region FROM paper WHERE subject LIKE ?",
        ("%数学%",),
    ):
        by_year[str(p["year"])].append(p)
        qb_by_id[p["paper_id"]] = p

    sg_papers = sg.execute(
        """
        SELECT p.id, p.paper_id, p.year, p.region, p.paper_title,
               SUM(CASE WHEN q.question_text LIKE '%MEDIA:%' THEN 1 ELSE 0 END) AS med,
               SUM(CASE WHEN q.question_text LIKE '%EMBED Equation%' THEN 1 ELSE 0 END) AS emb,
               COUNT(q.id) AS qn
        FROM papers p
        JOIN questions q ON q.paper_id = p.id
        WHERE p.subject_id = 2
        GROUP BY p.id
        ORDER BY p.year DESC, p.paper_id
        """
    ).fetchall()

    # papers that need repair: any incomplete question, or zero media with incomplete heuristics
    need_papers = []
    for sp in sg_papers:
        qs = sg.execute(
            "SELECT question_id, question_text FROM questions WHERE paper_id=?",
            (sp["id"],),
        ).fetchall()
        inc = [q for q in qs if is_incomplete(q["question_text"] or "")]
        if inc or (sp["med"] or 0) == 0 and (sp["emb"] or 0) > 0:
            need_papers.append((sp, inc))

    print(f"papers needing check={len(need_papers)}")

    pairs = []
    skipped = []
    for sp, inc in need_papers:
        if sp["paper_id"] in MANUAL_MAP:
            qp = qb_by_id.get(MANUAL_MAP[sp["paper_id"]])
            if qp:
                media_n = qb_media_count(qb, qp["paper_id"])
                ov = 1.0
                pairs.append((sp, qp, 99, media_n, ov, len(inc)))
                continue
        cands = by_year.get(str(sp["year"])) or []
        ranked = []
        for cp in cands:
            sc = score_pair(sp, cp)
            if sc < 6:
                continue
            media_n = qb_media_count(qb, cp["paper_id"])
            ranked.append((sc, media_n, cp))
        ranked.sort(key=lambda x: (x[0], x[1]), reverse=True)
        if not ranked:
            skipped.append((sp["paper_id"], "no_cand", len(inc)))
            continue
        # among top score band, prefer text similarity + media
        top_score = ranked[0][0]
        band = [r for r in ranked if r[0] >= top_score - 1]
        lq1 = local_q1_plain(sg, sp["id"])
        best = None
        best_key = None
        for sc, media_n, cp in band:
            qq1 = qb_q1_plain(qb, cp["paper_id"])
            # character overlap ratio on prefixes
            overlap = 0
            if lq1 and qq1:
                a, b = set(lq1[:20]), set(qq1[:20])
                overlap = len(a & b) / max(1, len(a | b))
            # require some overlap unless local is nearly empty shell
            shared = any(k in lq1 and k in qq1 for k in ("集合", "已知", "设", "若", "样本", "函数"))
            if lq1 and len(lq1) >= 8 and overlap < 0.2 and not shared:
                continue
            key = (sc, overlap, media_n)
            if best is None or key > best_key:
                best = (cp, sc, media_n, overlap, len(inc))
                best_key = key
        if not best or best[2] <= 0:
            skipped.append((sp["paper_id"], "no_rich_qb", len(inc)))
            continue
        # reject dangerous low-confidence cross matches
        if best[1] < 8 and best[3] < 0.35:
            skipped.append((sp["paper_id"], "low_confidence", len(inc)))
            continue
        pairs.append((sp, best[0], best[1], best[2], best[3], len(inc)))

    print(f"matched for sync={len(pairs)} skipped={len(skipped)}")
    for sp, qp, sc, media_n, ov, inc_n in pairs:
        print(
            f"  {sp['paper_id']} <- {qp['paper_id']} score={sc} qb_media_nodes~{media_n} "
            f"overlap={ov:.2f} incomplete_qs={inc_n} | {(qp['title'] or '')[:40]}"
        )
    if skipped:
        print("skipped:")
        for s in skipped:
            print(" ", s)

    if dry:
        print("dry-run, stop")
        return

    total_updated = 0
    total_skipped_q = 0
    for sp, qp, sc, media_n, ov, _ in pairs:
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
            new_media = rich.count("{{MEDIA:")
            old_media = old.count("{{MEDIA:")
            old_embed = old.count("EMBED")
            # update if incomplete, or new has more media, or replaces embeds
            if not (
                is_incomplete(old)
                or (new_media > old_media)
                or (old_embed and new_media > 0)
            ):
                total_skipped_q += 1
                continue
            if new_media == 0 and not is_incomplete(old):
                total_skipped_q += 1
                continue
            # avoid replacing good rich text with emptyish
            if new_media == 0 and old_media > 0:
                total_skipped_q += 1
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
        total_updated += updated
        print(f"OK {sp['paper_id']} updated={updated}")

    left_inc = 0
    for sp in sg_papers:
        for q in sg.execute(
            "SELECT question_text FROM questions WHERE paper_id=?", (sp["id"],)
        ):
            if is_incomplete(q["question_text"] or ""):
                left_inc += 1
    print(
        f"done updated_questions={total_updated} skipped_ok_questions={total_skipped_q} "
        f"remaining_incomplete~={left_inc}"
    )
    qb.close()
    sg.close()


if __name__ == "__main__":
    main()
