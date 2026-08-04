#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
原卷版与解析版合并模块
将原卷版的题目和解析版的答案、解析合并
"""

import os
import re
from typing import List, Dict, Tuple
from difflib import SequenceMatcher
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from paper_parser.base_parser import Paper, Question


class PaperMerger:
    """试卷合并器"""
    
    def __init__(self):
        pass
    
    def merge_papers(self, original_paper: Paper, answer_paper: Paper) -> Paper:
        """
        合并原卷版和解析版
        original_paper: 原卷版（有题目，无答案）
        answer_paper: 解析版（有答案和解析）
        返回合并后的试卷
        """
        merged_paper = Paper()
        merged_paper.paper_id = original_paper.paper_id
        merged_paper.subject = original_paper.subject
        merged_paper.year = original_paper.year
        merged_paper.region = original_paper.region
        merged_paper.paper_name = original_paper.paper_name
        merged_paper.total_score = original_paper.total_score
        merged_paper.images = original_paper.images
        
        # 匹配题目
        matched_questions = self._match_questions(
            original_paper.questions, 
            answer_paper.questions
        )
        
        # 合并题目
        for orig_q, ans_q in matched_questions:
            merged_q = Question()
            merged_q.question_id = orig_q.question_id
            merged_q.question_number = orig_q.question_number
            merged_q.question_type = orig_q.question_type
            merged_q.content = orig_q.content
            merged_q.options = orig_q.options
            merged_q.images = orig_q.images
            merged_q.source_paper = orig_q.source_paper
            merged_q.year = orig_q.year
            merged_q.region = orig_q.region
            
            if ans_q:
                merged_q.answer = ans_q.answer
                merged_q.analysis = ans_q.analysis
                # 如果原卷没有选项，从解析版提取
                if not merged_q.options and ans_q.options:
                    merged_q.options = ans_q.options
            
            merged_paper.questions.append(merged_q)
        
        return merged_paper
    
    def _match_questions(self, orig_questions: List[Question], 
                        ans_questions: List[Question]) -> List[Tuple[Question, Question]]:
        """
        匹配原卷版和解析版的题目
        返回：[(原卷题目, 解析题目), ...]
        """
        matches = []
        
        # 方法1：按题号匹配
        ans_by_num = {}
        for q in ans_questions:
            ans_by_num[q.question_number] = q
        
        for orig_q in orig_questions:
            ans_q = ans_by_num.get(orig_q.question_number)
            if ans_q:
                matches.append((orig_q, ans_q))
            else:
                # 方法2：按内容相似度匹配
                best_match = None
                best_sim = 0
                
                for ans_q in ans_questions:
                    sim = self._content_similarity(orig_q.content, ans_q.content)
                    if sim > best_sim:
                        best_sim = sim
                        best_match = ans_q
                
                if best_sim > 0.5:  # 相似度阈值
                    matches.append((orig_q, best_match))
                else:
                    matches.append((orig_q, None))
        
        return matches
    
    def _content_similarity(self, text1: str, text2: str) -> float:
        """计算内容相似度"""
        # 标准化文本
        def normalize(text):
            text = re.sub(r'\s+', '', text)
            text = re.sub(r'[.、，。；：！？,.;:!?()（）【】\[\]]', '', text)
            return text.lower()
        
        norm1 = normalize(text1)
        norm2 = normalize(text2)
        
        if not norm1 or not norm2:
            return 0
        
        return SequenceMatcher(None, norm1, norm2).ratio()
    
    def extract_answers_from_text(self, answer_text: str) -> Dict[str, str]:
        """
        从答案文本中提取各题答案
        返回：{题号: 答案}
        """
        answers = {}
        
        # 选择题答案模式
        choice_patterns = [
            r'(\d+)[.、．]\s*([A-D])',  # 1. A
            r'第\s*(\d+)\s*题\s*([A-D])',  # 第1题 A
            r'（\s*(\d+)\s*）\s*([A-D])',  # （1）A
        ]
        
        for pattern in choice_patterns:
            matches = re.findall(pattern, answer_text)
            for q_num, answer in matches:
                answers[q_num] = answer
        
        return answers
