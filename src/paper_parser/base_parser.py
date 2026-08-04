#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
试卷解析器基础类
"""

import os
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class QuestionImage:
    """题目图片"""
    image_id: str
    image_path: str
    image_index: int  # 在题目中的序号
    description: str = ""


@dataclass
class Question:
    """题目数据结构"""
    question_id: str = ""
    question_number: str = ""  # 题号，如 "1", "2(1)"
    question_type: str = ""  # 题型：选择题、填空题、解答题
    content: str = ""  # 题目内容（含图片占位符）
    options: List[str] = field(default_factory=list)  # 选项（选择题）
    answer: str = ""  # 答案
    analysis: str = ""  # 解析
    images: List[QuestionImage] = field(default_factory=list)
    difficulty: int = 0  # 难度 1-5
    score: float = 0  # 分值
    source_paper: str = ""  # 来源试卷
    year: int = 0  # 年份
    region: str = ""  # 地区


@dataclass
class Paper:
    """试卷数据结构"""
    paper_id: str = ""
    subject: str = ""  # 学科
    year: int = 0  # 年份
    region: str = ""  # 地区
    paper_type: str = ""  # 试卷类型：原卷版、解析版
    paper_name: str = ""  # 试卷名称
    total_score: float = 0  # 总分
    questions: List[Question] = field(default_factory=list)
    images: Dict[str, str] = field(default_factory=dict)  # 所有图片 id -> path


class BasePaperParser(ABC):
    """试卷解析器基类"""
    
    def __init__(self, file_path: str, output_dir: str = ""):
        self.file_path = file_path
        self.filename = os.path.basename(file_path)
        self.output_dir = output_dir
        self.paper = Paper()
        self._parse_filename()
    
    def _parse_filename(self):
        """从文件名解析试卷信息"""
        filename = self.filename
        
        # 提取年份
        year_match = re.search(r'(\d{4})年', filename)
        if year_match:
            self.paper.year = int(year_match.group(1))
        
        # 提取地区
        regions = ['全国', '新课标', '北京', '上海', '天津', '浙江', '江苏', '山东', 
                   '广东', '海南', '四川', '重庆', '湖南', '湖北', '福建', '安徽',
                   '江西', '河南', '河北', '陕西', '辽宁', '吉林', '黑龙江', '广西',
                   '云南', '贵州', '甘肃', '青海', '宁夏', '新疆', '西藏', '内蒙古']
        for region in regions:
            if region in filename:
                self.paper.region = region
                break
        
        # 提取文理科
        if '文' in filename:
            self.paper.paper_type = '文科'
        elif '理' in filename:
            self.paper.paper_type = '理科'
        
        # 原卷版/解析版
        if '原卷版' in filename:
            self.paper.paper_type = '原卷版'
        elif '解析版' in filename:
            self.paper.paper_type = '解析版'
        
        self.paper.paper_name = filename.replace('.docx', '').replace('.pdf', '').replace('.doc', '')
    
    @abstractmethod
    def parse(self) -> Paper:
        """解析试卷，返回Paper对象"""
        pass
    
    def extract_images(self, output_dir: str) -> Dict[str, str]:
        """提取图片到指定目录，返回图片ID到路径的映射"""
        pass
    
    def _generate_question_id(self, subject: str, year: int, region: str, q_num: str) -> str:
        """生成题目ID"""
        subject_map = {
            '语文': 'CHN', '数学': 'MATH', '英语': 'ENG',
            '物理': 'PHY', '化学': 'CHEM', '生物': 'BIO',
            '政治': 'POL', '历史': 'HIS', '地理': 'GEO'
        }
        subj_code = subject_map.get(subject, 'UNK')
        region_code = region[:2] if region else 'UNK'
        return f"Q-{subj_code}-{year}-{region_code}-{q_num}"
    
    def _detect_question_type(self, content: str, q_num: str) -> str:
        """判断题型"""
        # 选择题特征：有A、B、C、D选项
        if re.search(r'[A-D][.、．]', content) or re.search(r'\n\s*[A-D]\s', content):
            return '选择题'
        # 填空题特征：有横线或"____"
        if '____' in content or '＿＿' in content:
            return '填空题'
        # 解答题特征：题号较大或有"解答"字样
        if '解答' in content or '证明' in content or '计算' in content:
            return '解答题'
        # 默认
        return '其他'
