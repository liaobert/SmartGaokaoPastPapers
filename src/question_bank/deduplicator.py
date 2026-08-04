#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
题目去重模块
支持基于内容哈希和文本相似度的去重
"""

import hashlib
import re
from typing import List, Dict, Tuple
from difflib import SequenceMatcher


class QuestionDeduplicator:
    """题目去重器"""
    
    def __init__(self):
        self.content_hash_map = {}  # 内容哈希 -> 题目ID
        self.question_cache = []  # 已处理题目列表
    
    def normalize_content(self, content: str) -> str:
        """标准化题目内容，用于去重比较"""
        # 移除多余空白
        text = re.sub(r'\s+', '', content)
        # 移除标点符号
        text = re.sub(r'[.、，。；：！？,.;:!?()（）【】\[\]""''《》<>]', '', text)
        # 转小写
        text = text.lower()
        return text
    
    def content_hash(self, content: str) -> str:
        """计算题目内容的哈希值"""
        normalized = self.normalize_content(content)
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()
    
    def similarity(self, text1: str, text2: str) -> float:
        """计算两个文本的相似度"""
        norm1 = self.normalize_content(text1)
        norm2 = self.normalize_content(text2)
        return SequenceMatcher(None, norm1, norm2).ratio()
    
    def is_duplicate(self, question_content: str, threshold: float = 0.9) -> Tuple[bool, str]:
        """
        判断题目是否重复
        返回：(是否重复, 重复的题目ID或空字符串)
        """
        content_hash = self.content_hash(question_content)
        
        # 一级去重：精确哈希匹配
        if content_hash in self.content_hash_map:
            return True, self.content_hash_map[content_hash]
        
        # 二级去重：相似度匹配
        for cached_q in self.question_cache:
            sim = self.similarity(question_content, cached_q['content'])
            if sim >= threshold:
                return True, cached_q['id']
        
        return False, ""
    
    def add_question(self, question_id: str, question_content: str):
        """添加题目到去重器"""
        content_hash = self.content_hash(question_content)
        self.content_hash_map[content_hash] = question_id
        self.question_cache.append({
            'id': question_id,
            'content': question_content
        })
    
    def deduplicate_questions(self, questions: List, threshold: float = 0.9) -> List:
        """
        对题目列表进行去重
        返回去重后的题目列表
        """
        unique_questions = []
        
        for q in questions:
            is_dup, dup_id = self.is_duplicate(q.content, threshold)
            if not is_dup:
                self.add_question(q.question_id, q.content)
                unique_questions.append(q)
        
        return unique_questions
