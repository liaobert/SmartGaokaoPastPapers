#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
题目数据库入库模块
将解析的题目存入数据库
"""

import sqlite3
import os
import json
import hashlib
import re
from typing import List
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from paper_parser.base_parser import Paper, Question


class QuestionBankImporter:
    """题库导入器"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
    
    def connect(self):
        """连接数据库"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def import_paper(self, paper: Paper, subject: str) -> str:
        """
        导入一份试卷
        返回试卷ID
        """
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        
        # 获取学科ID
        subject_map = {
            '语文': 'chinese', '数学': 'math', '英语': 'english',
            '物理': 'physics', '化学': 'chemistry', '生物': 'biology',
            '政治': 'politics', '历史': 'history', '地理': 'geography'
        }
        subject_code = subject_map.get(subject, '')
        cursor.execute("SELECT id FROM subjects WHERE subject_code = ?", (subject_code,))
        subject_row = cursor.fetchone()
        if not subject_row:
            raise ValueError(f"未知学科: {subject}")
        subject_id = subject_row['id']
        
        # 生成试卷ID
        paper_id = self._generate_paper_id(subject, paper.year, paper.region, 
                                          paper.paper_type, paper.paper_name)
        
        # 判断文件类型
        file_type = 'docx' if paper.paper_name.endswith('.docx') else \
                   'pdf' if paper.paper_name.endswith('.pdf') else 'doc'
        
        # 插入试卷记录
        cursor.execute('''
            INSERT OR IGNORE INTO papers 
            (paper_id, subject_id, paper_title, year, region, paper_type, 
             total_score, total_questions, source_file, file_type, parsed_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        ''', (
            paper_id, subject_id, paper.paper_name, paper.year, paper.region,
            paper.paper_type, paper.total_score, len(paper.questions),
            paper.paper_name, file_type
        ))
        
        # 获取试卷的数据库ID
        cursor.execute("SELECT id FROM papers WHERE paper_id = ?", (paper_id,))
        paper_db_id = cursor.fetchone()['id']
        
        # 导入题目
        for i, q in enumerate(paper.questions):
            self._import_question(cursor, paper_id, paper_db_id, subject_id, q, i + 1)
        
        self.conn.commit()
        return paper_id
    
    def _generate_paper_id(self, subject: str, year: int, region: str, paper_type: str, 
                          paper_name: str = "") -> str:
        """生成试卷ID"""
        subject_map = {
            '语文': 'CHN', '数学': 'MATH', '英语': 'ENG',
            '物理': 'PHY', '化学': 'CHEM', '生物': 'BIO',
            '政治': 'POL', '历史': 'HIS', '地理': 'GEO'
        }
        subj_code = subject_map.get(subject, 'UNK')
        
        # 从试卷名称中提取更多信息
        # 卷种
        volume_type = ""
        if '新课标Ⅰ' in paper_name or '新课标I' in paper_name or '新高考I' in paper_name or '新高考Ⅰ' in paper_name:
            volume_type = "X1"
        elif '新课标Ⅱ' in paper_name or '新课标II' in paper_name or '新高考II' in paper_name or '新高考Ⅱ' in paper_name:
            volume_type = "X2"
        elif '新课标Ⅲ' in paper_name or '新课标III' in paper_name:
            volume_type = "X3"
        elif '甲卷' in paper_name:
            volume_type = "J"
        elif '乙卷' in paper_name:
            volume_type = "Y"
        elif '全国卷' in paper_name or '全国' in paper_name:
            volume_type = "Q"
        
        # 文理科
        arts_science = ""
        if '文科' in paper_name or '【文】' in paper_name or '（文）' in paper_name:
            arts_science = "W"
        elif '理科' in paper_name or '【理】' in paper_name or '（理）' in paper_name:
            arts_science = "L"
        
        # 考试类型
        exam_type = ""
        if '春考' in paper_name or '春季' in paper_name:
            exam_type = "S"
        elif '秋考' in paper_name or '秋季' in paper_name:
            exam_type = "A"
        
        # 地区代码
        region_code_map = {
            '全国': 'QGY', '新课标': 'XKB', '北京': 'BJ', '上海': 'SH',
            '天津': 'TJ', '浙江': 'ZJ', '江苏': 'JS', '山东': 'SD',
            '广东': 'GD', '海南': 'HN', '四川': 'SC', '重庆': 'CQ',
            '湖南': 'HN', '湖北': 'HB', '福建': 'FJ', '安徽': 'AH',
            '江西': 'JX', '河南': 'HEN', '河北': 'HEB', '陕西': 'SX',
            '辽宁': 'LN', '吉林': 'JL', '黑龙江': 'HLJ', '广西': 'GX',
            '云南': 'YN', '贵州': 'GZ', '甘肃': 'GS', '青海': 'QH',
            '宁夏': 'NX', '新疆': 'XJ', '西藏': 'XZ', '内蒙古': 'NMG'
        }
        region_code = region_code_map.get(region, region[:2].upper() if region else 'UNK')
        
        # 类型代码
        type_code = 'O' if '原卷' in paper_type else 'A'
        
        # 组合ID
        parts = [subj_code, str(year), region_code]
        if volume_type:
            parts.append(volume_type)
        if arts_science:
            parts.append(arts_science)
        if exam_type:
            parts.append(exam_type)
        parts.append(type_code)
        
        return "P-" + "-".join(parts)
    
    def _import_question(self, cursor, paper_id_str: str, paper_db_id: int, subject_id: int,
                        question: Question, sort_order: int):
        """导入一道题目"""
        question_id = self._generate_question_id(paper_id_str, question.question_number)
        content_hash = self._content_hash(question.content)
        has_image = 1 if question.images else 0
        content = question.content or ""
        has_formula = 1 if ("$" in content or "「公式」" in content or "{{MEDIA:" in content) else 0
        options_json = json.dumps(question.options, ensure_ascii=False) if question.options else None

        cursor.execute("""
            INSERT INTO questions
            (question_id, subject_id, paper_id, question_number, question_type,
             question_text, options_json, answer_text, analysis_text,
             difficulty_level, score_value, has_image, has_formula, content_hash, source_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'parsed')
            ON CONFLICT(question_id) DO UPDATE SET
              question_text=excluded.question_text,
              options_json=excluded.options_json,
              answer_text=excluded.answer_text,
              analysis_text=excluded.analysis_text,
              has_image=excluded.has_image,
              has_formula=excluded.has_formula,
              content_hash=excluded.content_hash,
              updated_at=CURRENT_TIMESTAMP
        """, (
            question_id, subject_id, paper_db_id, question.question_number,
            question.question_type, question.content, options_json,
            question.answer, question.analysis, question.difficulty,
            question.score, has_image, has_formula, content_hash
        ))

        cursor.execute("SELECT id FROM questions WHERE question_id = ?", (question_id,))
        q_db_id = cursor.fetchone()["id"]

        cursor.execute("DELETE FROM question_images WHERE question_id = ?", (q_db_id,))
        for img in question.images:
            fmt = img.image_path.rsplit(".", 1)[-1] if "." in img.image_path else ""
            # image_id 全局唯一：题库内可能复用同一媒体文件
            unique_image_id = f"IMG-{q_db_id}-{img.image_index}-{img.image_id}"
            cursor.execute("""
                INSERT INTO question_images
                (question_id, image_id, image_path, image_type, image_format, description, position_in_question)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                q_db_id,
                unique_image_id,
                img.image_path,
                img.description or "illustration",
                fmt,
                img.description,
                img.image_index,
            ))

    def _generate_question_id(self, paper_id: str, question_number: str) -> str:
        """生成题目ID"""
        return f"{paper_id}-Q{question_number}"
    
    def _content_hash(self, content: str) -> str:
        """计算内容哈希"""
        # 标准化内容
        text = re.sub(r'\s+', '', content)
        text = re.sub(r'[.、，。；：！？,.;:!?()（）【】\[\]]', '', text)
        text = text.lower()
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def import_questions_batch(self, questions: List[Question], paper_id_str: str, 
                               paper_db_id: int, subject_id: int):
        """批量导入题目"""
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        for i, q in enumerate(questions):
            self._import_question(cursor, paper_id_str, paper_db_id, subject_id, q, i + 1)
        self.conn.commit()
    
    def get_question_count(self) -> int:
        """获取题目总数"""
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM questions")
        return cursor.fetchone()[0]
    
    def get_paper_count(self) -> int:
        """获取试卷总数"""
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM papers")
        return cursor.fetchone()[0]
