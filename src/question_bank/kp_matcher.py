#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
题目-知识点自动关联模块
基于关键词、语义相似度等算法自动匹配题目和知识点
"""

import sqlite3
import re
import json
from typing import List, Dict, Tuple
from difflib import SequenceMatcher


class KnowledgePointMatcher:
    """知识点匹配器"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
        self.knowledge_points = {}  # subject_id -> [kp_dict]
        self.keyword_map = {}  # keyword -> [kp_id]
        
    def connect(self):
        """连接数据库"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def load_knowledge_points(self, subject_id: int):
        """加载指定学科的所有知识点"""
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        
        # 获取知识点
        cursor.execute('''
            SELECT kp.id, kp.kp_id, kp.kp_name, kp.description, 
                   kp.content, kp.chapter_id,
                   c.chapter_name, s.semester_name
            FROM knowledge_points kp
            JOIN chapters c ON kp.chapter_id = c.id
            JOIN semesters s ON c.semester_id = s.id
            WHERE kp.subject_id = ?
            ORDER BY kp.id
        ''', (subject_id,))
        
        kps = []
        for row in cursor.fetchall():
            kp = dict(row)
            
            # 构建匹配关键词集合
            match_keywords = set()
            match_keywords.add(kp['kp_name'])
            
            # 从知识点名称中提取关键词（按常见分隔符拆分）
            name_parts = re.split(r'[、，,（）()\s]+', kp['kp_name'])
            for part in name_parts:
                if len(part) >= 2:
                    match_keywords.add(part)
            
            # 从描述中提取关键词
            if kp.get('description'):
                desc = kp['description']
                # 按常见分隔符拆分
                desc_parts = re.split(r'[、，,；;。\s]+', desc)
                for part in desc_parts:
                    if len(part) >= 2:
                        match_keywords.add(part)
                
                # 提取"的"前面的短语
                desc_phrases = re.findall(r'([\u4e00-\u9fa5]{2,})的', desc)
                for phrase in desc_phrases:
                    if len(phrase) >= 2:
                        match_keywords.add(phrase)
            
            # 添加一些常见的相关词汇（根据知识点名称推断）
            kp_name = kp['kp_name']
            if '运算' in kp_name:
                match_keywords.add('运算')
            if '函数' in kp_name:
                match_keywords.add('函数')
            if '方程' in kp_name:
                match_keywords.add('方程')
            if '不等式' in kp_name:
                match_keywords.add('不等式')
            if '几何' in kp_name:
                match_keywords.add('几何')
            if '概率' in kp_name:
                match_keywords.add('概率')
            if '统计' in kp_name:
                match_keywords.add('统计')
            if '向量' in kp_name:
                match_keywords.add('向量')
            if '数列' in kp_name:
                match_keywords.add('数列')
            if '导数' in kp_name:
                match_keywords.add('导数')
            if '积分' in kp_name:
                match_keywords.add('积分')
            if '三角' in kp_name:
                match_keywords.add('三角')
            if '集合' in kp_name:
                match_keywords.add('集合')
                match_keywords.add('交集')
                match_keywords.add('并集')
                match_keywords.add('补集')
            
            kp['match_keywords'] = match_keywords
            
            kps.append(kp)
            
            # 建立关键词索引
            for kw in match_keywords:
                if len(kw) >= 2:  # 至少2个字
                    kw_lower = kw.lower()
                    if kw_lower not in self.keyword_map:
                        self.keyword_map[kw_lower] = []
                    if kp['kp_id'] not in self.keyword_map[kw_lower]:
                        self.keyword_map[kw_lower].append(kp['kp_id'])
        
        self.knowledge_points[subject_id] = kps
        return kps
    
    def match_question(self, question_text: str, subject_id: int, 
                       top_k: int = 3) -> List[Tuple[str, float]]:
        """
        匹配题目对应的知识点
        返回 [(kp_id, score), ...] 按分数降序排列
        """
        if subject_id not in self.knowledge_points:
            self.load_knowledge_points(subject_id)
        
        kps = self.knowledge_points.get(subject_id, [])
        if not kps:
            return []
        
        # 预处理题目文本
        text = self._preprocess_text(question_text)
        
        # 计算每个知识点的匹配分数
        scores = []
        for kp in kps:
            score = self._calculate_match_score(text, kp)
            if score > 0:
                scores.append((kp['kp_id'], score))
        
        # 按分数排序
        scores.sort(key=lambda x: x[1], reverse=True)
        
        return scores[:top_k]
    
    def _preprocess_text(self, text: str) -> str:
        """预处理文本"""
        # 移除多余空白
        text = re.sub(r'\s+', ' ', text)
        # 转小写
        text = text.lower()
        return text
    
    def _calculate_match_score(self, text: str, kp: dict) -> float:
        """计算匹配分数"""
        score = 0.0
        
        # 1. 精确匹配知识点名称（最高分）
        kp_name = kp['kp_name'].lower()
        if kp_name in text:
            score += 50.0
        
        # 2. 关键词匹配
        for kw in kp['match_keywords']:
            kw_lower = kw.lower()
            if len(kw_lower) >= 2 and kw_lower in text:
                # 关键词越长，权重越高
                score += min(len(kw_lower) * 2, 20)
        
        # 3. 章节名称匹配
        if kp.get('chapter_name'):
            chapter_name = kp['chapter_name'].lower()
            if len(chapter_name) >= 3 and chapter_name in text:
                score += 15.0
        
        # 4. 语义相似度（基于序列匹配）
        if kp.get('description'):
            desc = kp['description'].lower()
            if len(desc) > 10 and len(text) > 10:
                # 取题目文本的前200字进行比较
                similarity = SequenceMatcher(None, text[:200], desc[:200]).ratio()
                score += similarity * 10
        
        return score
    
    def batch_match_questions(self, subject_id: int, limit: int = 100):
        """批量匹配题目"""
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        
        # 获取题目
        cursor.execute('''
            SELECT question_id, question_text, question_type
            FROM questions 
            WHERE subject_id = ?
            ORDER BY id
            LIMIT ?
        ''', (subject_id, limit))
        
        questions = cursor.fetchall()
        print(f'获取到 {len(questions)} 道题目')
        
        # 加载知识点
        self.load_knowledge_points(subject_id)
        
        # 匹配结果
        results = []
        matched_count = 0
        
        for q in questions:
            q_id = q['question_id']
            q_text = q['question_text'] or ''
            
            matches = self.match_question(q_text, subject_id, top_k=3)
            
            if matches:
                matched_count += 1
                results.append({
                    'question_id': q_id,
                    'question_text': q_text[:50] + '...' if len(q_text) > 50 else q_text,
                    'matches': matches
                })
        
        print(f'匹配完成: {matched_count}/{len(questions)} 道题匹配到知识点')
        return results
    
    def save_matches(self, matches: List[dict], subject_id: int):
        """保存匹配结果到数据库"""
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        
        # 先删除该学科已有的关联
        cursor.execute('''
            DELETE FROM question_kp_relations 
            WHERE question_id IN (
                SELECT id FROM questions WHERE subject_id = ?
            )
        ''', (subject_id,))
        
        # 插入新的关联
        count = 0
        for match in matches:
            q_id_str = match['question_id']
            
            # 获取题目的数据库ID
            cursor.execute("SELECT id FROM questions WHERE question_id = ?", (q_id_str,))
            q_row = cursor.fetchone()
            if not q_row:
                continue
            q_db_id = q_row['id']
            
            for i, (kp_id_str, score) in enumerate(match['matches']):
                # 获取知识点的数据库ID
                cursor.execute("SELECT id FROM knowledge_points WHERE kp_id = ?", (kp_id_str,))
                kp_row = cursor.fetchone()
                if kp_row:
                    kp_db_id = kp_row['id']
                    relevance_score = score / 100.0  # 转换为0-1的置信度
                    relation_type = 'auto'
                    
                    cursor.execute('''
                        INSERT OR IGNORE INTO question_kp_relations
                        (question_id, kp_id, relation_type, relevance_score)
                        VALUES (?, ?, ?, ?)
                    ''', (q_db_id, kp_db_id, relation_type, relevance_score))
                    count += 1
        
        self.conn.commit()
        print(f'已保存 {count} 条知识点关联')
        return count


def main():
    """测试"""
    db_path = '../../database/gaokao.db'
    
    matcher = KnowledgePointMatcher(db_path)
    matcher.connect()
    
    # 测试数学学科
    subject_id = 2  # 数学
    
    print('加载知识点...')
    kps = matcher.load_knowledge_points(subject_id)
    print(f'加载了 {len(kps)} 个知识点')
    
    print('\n批量匹配题目...')
    matches = matcher.batch_match_questions(subject_id, limit=50)
    
    print('\n匹配结果示例（前10个）:')
    for i, match in enumerate(matches[:10]):
        print(f'\n{i+1}. {match["question_text"]}')
        for kp_id, score in match['matches']:
            print(f'   - {kp_id}: {score:.1f}分')
    
    # 保存匹配结果
    print('\n保存匹配结果...')
    matcher.save_matches(matches, subject_id)
    
    matcher.close()


if __name__ == '__main__':
    main()
