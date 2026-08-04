#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用富文本解析器重解析数学原卷，刷新题干公式/图片。"""

from __future__ import annotations

import glob
import os
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from paper_parser import parse_paper
from question_bank.importer import QuestionBankImporter

DATA_DIR = Path(os.environ.get(
    "PAPER_DATA_DIR",
    ROOT / "data" / "10年高考" / "数学" / "原卷版",
))
DB_PATH = Path(os.environ.get("GAOKAO_DB", ROOT / "database" / "gaokao.db"))
MEDIA_DIR = Path(os.environ.get("MEDIA_DIR", ROOT / "assets" / "question_media"))


def prefer_source_files() -> list[Path]:
    """同一试卷优先选择 .docx（含 _1.docx）。"""
    files = [Path(p) for p in glob.glob(str(DATA_DIR / "*"))
             if Path(p).is_file() and not Path(p).name.startswith("._")]
    by_stem: dict[str, list[Path]] = {}
    for p in files:
        stem = p.stem
        if stem.endswith("_1"):
            stem = stem[:-2]
        by_stem.setdefault(stem, []).append(p)

    chosen: list[Path] = []
    for stem, cands in sorted(by_stem.items()):
        docxs = [c for c in cands if c.suffix.lower() == ".docx"]
        if docxs:
            # 优先非 _1，其次任意 docx
            primary = [c for c in docxs if not c.stem.endswith("_1")]
            chosen.append(primary[0] if primary else docxs[0])
        else:
            docs = [c for c in cands if c.suffix.lower() == ".doc"]
            if docs:
                chosen.append(docs[0])
    return chosen


def main():
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    files = prefer_source_files()
    print(f"待处理试卷: {len(files)}")
    print(f"媒体目录: {MEDIA_DIR}")
    print(f"数据库: {DB_PATH}")

    importer = QuestionBankImporter(str(DB_PATH))
    importer.connect()

    ok = fail = 0
    for i, fp in enumerate(files, 1):
        print(f"\n[{i}/{len(files)}] {fp.name}")
        paper_media = MEDIA_DIR / fp.stem.replace(" ", "_")
        paper_media.mkdir(parents=True, exist_ok=True)
        try:
            paper = parse_paper(str(fp), str(paper_media))
            # 媒体路径改为相对：paper_stem/filename，便于 /media 查找时扁平化
            # 将文件拷到 MEDIA_DIR 根下用唯一名（extractor 已用 md5 名）
            for q in paper.questions:
                for img in q.images:
                    src = Path(paper_media) / img.image_path
                    if src.exists():
                        dest = MEDIA_DIR / img.image_path
                        if not dest.exists():
                            dest.write_bytes(src.read_bytes())
            paper_id = importer.import_paper(paper, "数学")
            n_media = sum(len(q.images) for q in paper.questions)
            print(f"  OK questions={len(paper.questions)} media_refs={n_media} paper_id={paper_id}")
            ok += 1
        except Exception as e:
            print(f"  FAIL: {e}")
            fail += 1

    importer.close()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM questions")
    qn = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM question_images")
    img = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM questions WHERE question_text LIKE '%{{MEDIA:%'")
    rich = cur.fetchone()[0]
    conn.close()
    print(f"\n完成 success={ok} fail={fail}")
    print(f"DB questions={qn} question_images={img} rich_text={rich}")


if __name__ == "__main__":
    main()
