#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DOCX格式试卷解析器（支持公式图 / OMML / 插图）
"""

import os
import re
from typing import List, Dict
from docx import Document
from .base_parser import BasePaperParser, Paper, Question, QuestionImage
from .rich_docx import RichDocxExtractor, clean_legacy_placeholders


class DocxPaperParser(BasePaperParser):
    """DOCX试卷解析器"""

    def __init__(self, file_path: str, output_dir: str = ""):
        super().__init__(file_path, output_dir)
        self.doc = None
        self._image_counter = 0
        self._rich_images: List[dict] = []

    def parse(self) -> Paper:
        """解析docx试卷"""
        paragraphs: List[str] = []

        # 优先富文本提取（保留公式图/OMML）
        if self.output_dir:
            try:
                extractor = RichDocxExtractor(self.file_path, self.output_dir)
                paragraphs = extractor.extract_paragraphs()
                self._rich_images = extractor.images
                self.paper.images = {img["image_id"]: img["image_path"] for img in extractor.images}
            except Exception as e:
                print(f"富文本提取失败，回退 python-docx: {e}")
                paragraphs = []

        if not paragraphs:
            self.doc = Document(self.file_path)
            for para in self.doc.paragraphs:
                text = clean_legacy_placeholders(para.text.strip())
                if text:
                    paragraphs.append(text)
            images = self._extract_images()
            self.paper.images = images

        self._extract_questions(paragraphs)
        self._attach_inline_images()
        return self.paper

    def _attach_inline_images(self):
        """把题干中的 MEDIA 标记关联到 Question.images"""
        path_map = {img["image_path"]: img for img in self._rich_images}
        for q in self.paper.questions:
            media_ids = re.findall(r"\{\{MEDIA:([^}]+)\}\}", q.content)
            for i, mid in enumerate(media_ids):
                meta = path_map.get(mid, {
                    "image_id": f"IMG-{mid}",
                    "image_path": mid,
                    "description": "",
                })
                q.images.append(QuestionImage(
                    image_id=meta.get("image_id", f"IMG-{mid}"),
                    image_path=meta.get("image_path", mid),
                    image_index=i,
                    description=meta.get("description", ""),
                ))
            if media_ids or "「公式」" in q.content or "$" in q.content:
                # 标记含公式（借用 difficulty 以外字段：importer 用 has_image）
                pass

    def _extract_images(self) -> Dict[str, str]:
        """从docx中提取所有图片（回退路径）"""
        import zipfile
        images = {}
        if not self.output_dir:
            return images

        os.makedirs(self.output_dir, exist_ok=True)

        try:
            with zipfile.ZipFile(self.file_path, "r") as zf:
                for name in zf.namelist():
                    if name.startswith("word/media/") and name.lower().endswith(
                        (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".wmf", ".emf")
                    ):
                        img_name = os.path.basename(name)
                        img_path = os.path.join(self.output_dir, img_name)
                        with zf.open(name) as src, open(img_path, "wb") as dst:
                            dst.write(src.read())
                        img_id = f"IMG-{self.paper.paper_id}-{self._image_counter}"
                        images[img_id] = img_path
                        self._image_counter += 1
        except Exception as e:
            print(f"提取图片失败: {e}")

        return images

    def _extract_questions(self, paragraphs: List[str]):
        """从段落中提取题目。

        主客观大题用「1.」「2.」编号；「（1）」多为解答题小问，不可覆盖大题号。
        若整卷仅用「（1）（2）」编号（如部分广东卷），则仍按主客观题处理。
        """
        questions = []
        current_question = None
        current_section = ""
        found_first_question = False
        seen_dotted_numbering = False  # 是否出现过 1. 2. 这种主编号

        dotted_patterns = [
            r'^(\d+)[.、．]',
            r'^第\s*(\d+)\s*题',
        ]
        paren_patterns = [
            r'^（\s*(\d+)\s*）',
            r'^\(\s*(\d+)\s*\)',
        ]

        section_patterns = [
            r'^[一二三四五六七八九十]+[、.．]',
            r'^第[ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ]+卷',
            r'^第[一二三四五六七八九十]+卷',
            r'^选择题[：:]',
            r'^填空题[：:]',
            r'^解答题[：:]',
            r'^[一二三四五六七八九十]+[、.．][选择填空解答]',
        ]

        intro_keywords = ['本试卷分', '答题前', '全部答案', '考试结束', '满分', '考试时间', '注意事项']

        def match_num(patterns, para):
            for pattern in patterns:
                m = re.match(pattern, para)
                if m:
                    return m.group(1)
            return None

        for para in paragraphs:
            is_section = False
            for pattern in section_patterns:
                if re.match(pattern, para):
                    current_section = para
                    is_section = True
                    break
            if is_section:
                continue

            if not found_first_question and not current_section:
                if any(kw in para for kw in intro_keywords):
                    continue

            dotted_num = match_num(dotted_patterns, para)
            paren_num = match_num(paren_patterns, para)

            start_new = False
            q_num = None

            if dotted_num:
                start_new = True
                q_num = dotted_num
                seen_dotted_numbering = True
            elif paren_num:
                # 已有 1.2. 主编号后，将（1）视为小问，并入当前大题
                if seen_dotted_numbering and current_question is not None:
                    start_new = False
                else:
                    start_new = True
                    q_num = paren_num

            if start_new:
                if not found_first_question and any(kw in para for kw in intro_keywords):
                    continue
                found_first_question = True

                if current_question:
                    questions.append(current_question)

                current_question = Question()
                current_question.question_number = q_num
                current_question.content = para
                current_question.source_paper = self.paper.paper_name
                current_question.year = self.paper.year
                current_question.region = self.paper.region

                if '选择' in current_section:
                    current_question.question_type = '选择题'
                elif '填空' in current_section:
                    current_question.question_type = '填空题'
                elif '解答' in current_section or '计算' in current_section or '证明' in current_section:
                    current_question.question_type = '解答题'
                else:
                    current_question.question_type = self._detect_question_type(para, q_num)
            elif current_question:
                current_question.content += '\n' + para
                if current_question.question_type == '选择题':
                    self._extract_options(current_question, para)

        if current_question:
            questions.append(current_question)

        self.paper.questions = questions

    def _extract_options(self, question: Question, text: str):
        option_patterns = [
            r"([A-D])[.、．]\s*(.+?)(?=\s*[A-D][.、．]|$)",
            r"（([A-D])）\s*(.+?)(?=\s*（[A-D]）|$)",
            r"\(([A-D])\)\s*(.+?)(?=\s*\([A-D]\)|$)",
        ]
        for pattern in option_patterns:
            matches = re.findall(pattern, text)
            if matches:
                for opt_letter, opt_content in matches:
                    option = f"{opt_letter}. {opt_content.strip()}"
                    if option not in question.options:
                        question.options.append(option)
                break

    def extract_images_to_dir(self, output_dir: str) -> Dict[str, str]:
        self.output_dir = output_dir
        return self._extract_images()
