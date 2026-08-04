#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF格式试卷解析器
"""

import os
import re
from typing import List, Dict
import fitz  # PyMuPDF
from .base_parser import BasePaperParser, Paper, Question, QuestionImage


class PdfPaperParser(BasePaperParser):
    """PDF试卷解析器"""
    
    def __init__(self, file_path: str, output_dir: str = ""):
        super().__init__(file_path, output_dir)
        self.doc = None
        self._image_counter = 0
    
    def parse(self) -> Paper:
        """解析PDF试卷"""
        self.doc = fitz.open(self.file_path)
        
        # 提取所有页面文本
        all_text = []
        for page in self.doc:
            text = page.get_text()
            if text.strip():
                # 按行分割
                lines = text.split('\n')
                all_text.extend([line.strip() for line in lines if line.strip()])
        
        # 提取图片
        images = self._extract_images()
        self.paper.images = images
        
        # 提取题目
        self._extract_questions(all_text)
        
        self.doc.close()
        return self.paper
    
    def _extract_images(self) -> Dict[str, str]:
        """从PDF中提取所有图片"""
        images = {}
        if not self.output_dir:
            return images
        
        os.makedirs(self.output_dir, exist_ok=True)
        
        try:
            for page_num in range(len(self.doc)):
                page = self.doc[page_num]
                image_list = page.get_images(full=True)
                
                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    base_image = self.doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    
                    img_name = f"page_{page_num+1}_img_{img_index+1}.{image_ext}"
                    img_path = os.path.join(self.output_dir, img_name)
                    
                    with open(img_path, "wb") as f:
                        f.write(image_bytes)
                    
                    img_id = f"IMG-{self.paper.paper_id}-{self._image_counter}"
                    images[img_id] = img_path
                    self._image_counter += 1
        except Exception as e:
            print(f"提取图片失败: {e}")
        
        return images
    
    def _extract_questions(self, lines: List[str]):
        """从行中提取题目"""
        questions = []
        current_question = None
        current_section = ""
        found_first_question = False
        
        # 题目编号模式（按优先级排序）
        q_num_patterns = [
            r'^（\s*(\d+)\s*）',     # （1）（ 1 ） - 中文括号，支持空格
            r'^\(\s*(\d+)\s*\)',     # (1) ( 1 ) - 英文括号，支持空格
            r'^(\d+)[.、．]',  # 1. 2. 3. - 数字加标点
            r'^第\s*(\d+)\s*题',     # 第1题 第 1 题
        ]
        
        # 大题模式
        section_patterns = [
            r'^[一二三四五六七八九十]+、',  # 一、二、三、
            r'^第[ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ]+卷',  # 第Ⅰ卷
            r'^第[一二三四五六七八九十]+卷',  # 第一卷
            r'^选择题[：:]',  # 选择题：
            r'^填空题[：:]',  # 填空题：
            r'^解答题[：:]',  # 解答题：
        ]
        
        # 试卷说明关键词
        intro_keywords = ['本试卷分', '答题前', '全部答案', '考试结束', '满分', '考试时间', '注意事项']
        
        for line in lines:
            # 跳过太短的行
            if len(line) < 2:
                continue
            
            # 跳过试卷说明
            if not found_first_question:
                is_intro = False
                for kw in intro_keywords:
                    if kw in line:
                        is_intro = True
                        break
                if is_intro:
                    continue
            
            # 检查是否是大题标题
            is_section = False
            for pattern in section_patterns:
                if re.match(pattern, line):
                    current_section = line
                    is_section = True
                    break
            
            if is_section:
                continue
            
            # 检查是否是新题目
            q_num = None
            for pattern in q_num_patterns:
                match = re.match(pattern, line)
                if match:
                    q_num = match.group(1)
                    break
            
            if q_num and (found_first_question or current_section):
                found_first_question = True
                
                # 保存上一题
                if current_question:
                    questions.append(current_question)
                
                # 创建新题目
                current_question = Question()
                current_question.question_number = q_num
                current_question.content = line
                current_question.source_paper = self.paper.paper_name
                current_question.year = self.paper.year
                current_question.region = self.paper.region
                
                # 判断题型
                if '选择' in current_section:
                    current_question.question_type = '选择题'
                elif '填空' in current_section:
                    current_question.question_type = '填空题'
                elif '解答' in current_section or '计算' in current_section or '证明' in current_section:
                    current_question.question_type = '解答题'
                else:
                    current_question.question_type = self._detect_question_type(line, q_num)
            elif current_question:
                # 追加到当前题目
                current_question.content += '\n' + line
                
                # 提取选项（选择题）
                if current_question.question_type == '选择题':
                    self._extract_options(current_question, line)
        
        # 保存最后一题
        if current_question:
            questions.append(current_question)
        
        self.paper.questions = questions
    
    def _extract_options(self, question: Question, text: str):
        """提取选择题选项"""
        # 支持多种选项格式
        option_patterns = [
            r'([A-D])[.、．]\s*(.+?)(?=\s*[A-D][.、．]|$)',  # A. xxx
            r'（([A-D])）\s*(.+?)(?=\s*（[A-D]）|$)',        # （A）xxx
            r'\(([A-D])\)\s*(.+?)(?=\s*\([A-D]\)|$)',        # (A) xxx
        ]
        
        for pattern in option_patterns:
            matches = re.findall(pattern, text)
            if matches:
                for opt_letter, opt_content in matches:
                    option = f"{opt_letter}. {opt_content.strip()}"
                    if option not in question.options:
                        question.options.append(option)
                break  # 找到一种模式就停止
    
    def extract_images_to_dir(self, output_dir: str) -> Dict[str, str]:
        """提取图片到指定目录"""
        self.output_dir = output_dir
        if not self.doc:
            self.doc = fitz.open(self.file_path)
        return self._extract_images()
