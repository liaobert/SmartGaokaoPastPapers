#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语文学科知识点体系构建
基于《普通高中语文课程标准》和人教版教材
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '../../database/gaokao.db')


def build_chinese_knowledge_graph():
    """构建语文学科知识图谱"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM subjects WHERE subject_code = 'chinese'")
    subject_id = cursor.fetchone()[0]
    
    # 学期/模块
    semesters = [
        {'code': 'compulsory_1', 'name': '必修上册', 'grade': '高一', 'sort': 1},
        {'code': 'compulsory_2', 'name': '必修下册', 'grade': '高一', 'sort': 2},
        {'code': 'selective_1', 'name': '选择性必修上册', 'grade': '高二', 'sort': 3},
        {'code': 'selective_2', 'name': '选择性必修中册', 'grade': '高二', 'sort': 4},
        {'code': 'selective_3', 'name': '选择性必修下册', 'grade': '高二', 'sort': 5},
    ]
    
    semester_ids = {}
    for sem in semesters:
        cursor.execute('''
            INSERT OR IGNORE INTO semesters 
            (subject_id, semester_code, semester_name, grade_level, sort_order)
            VALUES (?, ?, ?, ?, ?)
        ''', (subject_id, sem['code'], sem['name'], sem['grade'], sem['sort']))
        cursor.execute("SELECT id FROM semesters WHERE subject_id = ? AND semester_code = ?", 
                       (subject_id, sem['code']))
        semester_ids[sem['code']] = cursor.fetchone()[0]
    
    # 知识点体系（按高考考点组织）
    chapters = [
        {
            'semester': 'compulsory_1', 'code': 'CH-READ-MODERN', 'name': '现代文阅读', 
            'number': '专题一', 'sort': 1,
            'kps': [
                {'id': 'CHN-MR-001', 'name': '论述类文本阅读', 'level': 1, 'parent': None,
                 'desc': '论述类文本的阅读理解与分析', 'importance': 4, 'difficulty': 3},
                {'id': 'CHN-MR-002', 'name': '实用类文本阅读', 'level': 1, 'parent': None,
                 'desc': '新闻、传记、科普文等实用类文本阅读', 'importance': 4, 'difficulty': 2},
                {'id': 'CHN-MR-003', 'name': '文学类文本阅读', 'level': 1, 'parent': None,
                 'desc': '小说、散文等文学类文本阅读', 'importance': 4, 'difficulty': 3},
                # 二级知识点
                {'id': 'CHN-MR-101', 'name': '理解文中重要概念', 'level': 2, 'parent': 'CHN-MR-001',
                 'desc': '理解文中重要概念的含义', 'importance': 3, 'difficulty': 2},
                {'id': 'CHN-MR-102', 'name': '理解文中重要句子', 'level': 2, 'parent': 'CHN-MR-001',
                 'desc': '理解文中重要句子的含意', 'importance': 3, 'difficulty': 2},
                {'id': 'CHN-MR-103', 'name': '筛选并整合文中信息', 'level': 2, 'parent': 'CHN-MR-001',
                 'desc': '筛选并整合文中的信息', 'importance': 4, 'difficulty': 2},
                {'id': 'CHN-MR-104', 'name': '分析文章结构', 'level': 2, 'parent': 'CHN-MR-001',
                 'desc': '分析文章结构，把握文章思路', 'importance': 3, 'difficulty': 3},
                {'id': 'CHN-MR-105', 'name': '归纳内容要点', 'level': 2, 'parent': 'CHN-MR-001',
                 'desc': '归纳内容要点，概括中心意思', 'importance': 4, 'difficulty': 3},
                {'id': 'CHN-MR-106', 'name': '分析概括作者观点', 'level': 2, 'parent': 'CHN-MR-001',
                 'desc': '分析概括作者在文中的观点态度', 'importance': 3, 'difficulty': 3},
                {'id': 'CHN-MR-107', 'name': '小说阅读', 'level': 2, 'parent': 'CHN-MR-003',
                 'desc': '小说的人物、情节、环境、主题分析', 'importance': 4, 'difficulty': 3},
                {'id': 'CHN-MR-108', 'name': '散文阅读', 'level': 2, 'parent': 'CHN-MR-003',
                 'desc': '散文的形象、语言、表达技巧分析', 'importance': 4, 'difficulty': 3},
            ]
        },
        {
            'semester': 'compulsory_2', 'code': 'CH-READ-CLASSIC', 'name': '古代诗文阅读', 
            'number': '专题二', 'sort': 2,
            'kps': [
                {'id': 'CHN-CR-001', 'name': '文言文阅读', 'level': 1, 'parent': None,
                 'desc': '文言文的阅读理解与翻译', 'importance': 4, 'difficulty': 3},
                {'id': 'CHN-CR-002', 'name': '古代诗歌鉴赏', 'level': 1, 'parent': None,
                 'desc': '古代诗歌的形象、语言、表达技巧鉴赏', 'importance': 4, 'difficulty': 3},
                {'id': 'CHN-CR-003', 'name': '名句名篇默写', 'level': 1, 'parent': None,
                 'desc': '常见的名句名篇默写', 'importance': 3, 'difficulty': 1},
                # 二级知识点
                {'id': 'CHN-CR-101', 'name': '文言实词', 'level': 2, 'parent': 'CHN-CR-001',
                 'desc': '常见文言实词在文中的含义', 'importance': 4, 'difficulty': 3},
                {'id': 'CHN-CR-102', 'name': '文言虚词', 'level': 2, 'parent': 'CHN-CR-001',
                 'desc': '常见文言虚词在文中的意义和用法', 'importance': 4, 'difficulty': 3},
                {'id': 'CHN-CR-103', 'name': '文言句式', 'level': 2, 'parent': 'CHN-CR-001',
                 'desc': '判断句、被动句、宾语前置、成分省略等', 'importance': 3, 'difficulty': 3},
                {'id': 'CHN-CR-104', 'name': '文言文翻译', 'level': 2, 'parent': 'CHN-CR-001',
                 'desc': '理解并翻译文中的句子', 'importance': 4, 'difficulty': 3},
                {'id': 'CHN-CR-105', 'name': '文言文内容分析', 'level': 2, 'parent': 'CHN-CR-001',
                 'desc': '归纳内容要点，概括中心意思', 'importance': 3, 'difficulty': 3},
                {'id': 'CHN-CR-106', 'name': '诗歌形象', 'level': 2, 'parent': 'CHN-CR-002',
                 'desc': '鉴赏诗歌的形象', 'importance': 3, 'difficulty': 3},
                {'id': 'CHN-CR-107', 'name': '诗歌语言', 'level': 2, 'parent': 'CHN-CR-002',
                 'desc': '鉴赏诗歌的语言', 'importance': 3, 'difficulty': 3},
                {'id': 'CHN-CR-108', 'name': '诗歌表达技巧', 'level': 2, 'parent': 'CHN-CR-002',
                 'desc': '鉴赏诗歌的表达技巧', 'importance': 4, 'difficulty': 3},
                {'id': 'CHN-CR-109', 'name': '诗歌思想内容', 'level': 2, 'parent': 'CHN-CR-002',
                 'desc': '评价诗歌的思想内容和作者的观点态度', 'importance': 4, 'difficulty': 3},
            ]
        },
        {
            'semester': 'selective_1', 'code': 'CH-LANG', 'name': '语言文字运用', 
            'number': '专题三', 'sort': 3,
            'kps': [
                {'id': 'CHN-LANG-001', 'name': '识记现代汉语普通话常用字的字音', 'level': 1, 'parent': None,
                 'desc': '字音识记', 'importance': 2, 'difficulty': 1},
                {'id': 'CHN-LANG-002', 'name': '识记并正确书写现代常用规范汉字', 'level': 1, 'parent': None,
                 'desc': '字形识记', 'importance': 2, 'difficulty': 1},
                {'id': 'CHN-LANG-003', 'name': '正确使用标点符号', 'level': 1, 'parent': None,
                 'desc': '标点符号的正确使用', 'importance': 2, 'difficulty': 2},
                {'id': 'CHN-LANG-004', 'name': '正确使用词语', 'level': 1, 'parent': None,
                 'desc': '正确使用词语（包括熟语）', 'importance': 3, 'difficulty': 2},
                {'id': 'CHN-LANG-005', 'name': '辨析并修改病句', 'level': 1, 'parent': None,
                 'desc': '病句的辨析与修改', 'importance': 3, 'difficulty': 2},
                {'id': 'CHN-LANG-006', 'name': '扩展语句压缩语段', 'level': 1, 'parent': None,
                 'desc': '扩展语句，压缩语段', 'importance': 3, 'difficulty': 2},
                {'id': 'CHN-LANG-007', 'name': '选用仿用变换句式', 'level': 1, 'parent': None,
                 'desc': '选用、仿用、变换句式', 'importance': 3, 'difficulty': 3},
                {'id': 'CHN-LANG-008', 'name': '语言表达简明连贯得体', 'level': 1, 'parent': None,
                 'desc': '语言表达简明、连贯、得体、准确、鲜明、生动', 'importance': 4, 'difficulty': 3},
                {'id': 'CHN-LANG-009', 'name': '正确使用常见的修辞手法', 'level': 1, 'parent': None,
                 'desc': '常见修辞手法的运用', 'importance': 3, 'difficulty': 2},
                # 二级知识点
                {'id': 'CHN-LANG-101', 'name': '成语运用', 'level': 2, 'parent': 'CHN-LANG-004',
                 'desc': '成语的正确使用', 'importance': 3, 'difficulty': 2},
                {'id': 'CHN-LANG-102', 'name': '病句类型', 'level': 2, 'parent': 'CHN-LANG-005',
                 'desc': '语序不当、搭配不当、成分残缺或赘余、结构混乱、表意不明、不合逻辑', 'importance': 3, 'difficulty': 2},
                {'id': 'CHN-LANG-103', 'name': '语句衔接', 'level': 2, 'parent': 'CHN-LANG-008',
                 'desc': '语句的衔接与排序', 'importance': 4, 'difficulty': 2},
            ]
        },
        {
            'semester': 'selective_2', 'code': 'CH-WRITING', 'name': '写作', 
            'number': '专题四', 'sort': 4,
            'kps': [
                {'id': 'CHN-WR-001', 'name': '议论文写作', 'level': 1, 'parent': None,
                 'desc': '议论文的写作方法与技巧', 'importance': 4, 'difficulty': 3},
                {'id': 'CHN-WR-002', 'name': '记叙文写作', 'level': 1, 'parent': None,
                 'desc': '记叙文的写作方法与技巧', 'importance': 3, 'difficulty': 3},
                {'id': 'CHN-WR-003', 'name': '材料作文', 'level': 1, 'parent': None,
                 'desc': '材料作文的审题立意与写作', 'importance': 4, 'difficulty': 3},
                {'id': 'CHN-WR-004', 'name': '任务驱动型作文', 'level': 1, 'parent': None,
                 'desc': '任务驱动型作文的写作', 'importance': 4, 'difficulty': 3},
                # 二级知识点
                {'id': 'CHN-WR-101', 'name': '审题立意', 'level': 2, 'parent': 'CHN-WR-003',
                 'desc': '准确审题，正确立意', 'importance': 4, 'difficulty': 3},
                {'id': 'CHN-WR-102', 'name': '文章结构', 'level': 2, 'parent': 'CHN-WR-001',
                 'desc': '合理安排文章结构', 'importance': 3, 'difficulty': 2},
                {'id': 'CHN-WR-103', 'name': '论据使用', 'level': 2, 'parent': 'CHN-WR-001',
                 'desc': '论据的选择与运用', 'importance': 3, 'difficulty': 2},
                {'id': 'CHN-WR-104', 'name': '论证方法', 'level': 2, 'parent': 'CHN-WR-001',
                 'desc': '多种论证方法的运用', 'importance': 3, 'difficulty': 3},
            ]
        },
        {
            'semester': 'selective_3', 'code': 'CH-CULTURE', 'name': '文学文化常识', 
            'number': '专题五', 'sort': 5,
            'kps': [
                {'id': 'CHN-CULT-001', 'name': '中国古代文学常识', 'level': 1, 'parent': None,
                 'desc': '中国古代重要作家作品及文学体裁', 'importance': 2, 'difficulty': 1},
                {'id': 'CHN-CULT-002', 'name': '中国现代文学常识', 'level': 1, 'parent': None,
                 'desc': '中国现代重要作家作品', 'importance': 2, 'difficulty': 1},
                {'id': 'CHN-CULT-003', 'name': '外国文学常识', 'level': 1, 'parent': None,
                 'desc': '外国重要作家作品', 'importance': 1, 'difficulty': 1},
                {'id': 'CHN-CULT-004', 'name': '古代文化常识', 'level': 1, 'parent': None,
                 'desc': '古代天文、地理、官职、科举、礼仪等常识', 'importance': 3, 'difficulty': 2},
            ]
        },
    ]
    
    kp_id_map = {}
    total_kp = 0
    
    for ch in chapters:
        sem_id = semester_ids[ch['semester']]
        cursor.execute('''
            INSERT OR IGNORE INTO chapters 
            (semester_id, chapter_code, chapter_name, chapter_number, sort_order)
            VALUES (?, ?, ?, ?, ?)
        ''', (sem_id, ch['code'], ch['name'], ch['number'], ch['sort']))
        cursor.execute("SELECT id FROM chapters WHERE semester_id = ? AND chapter_code = ?",
                       (sem_id, ch['code']))
        chapter_id = cursor.fetchone()[0]
        
        for kp in ch['kps']:
            cursor.execute('''
                INSERT OR IGNORE INTO knowledge_points 
                (kp_id, subject_id, chapter_id, kp_name, kp_level, description, 
                 difficulty_level, importance_level, sort_order)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (kp['id'], subject_id, chapter_id, kp['name'], kp['level'], kp['desc'],
                  kp['difficulty'], kp['importance'], total_kp + 1))
            
            cursor.execute("SELECT id FROM knowledge_points WHERE kp_id = ?", (kp['id'],))
            kp_id_map[kp['id']] = cursor.fetchone()[0]
            total_kp += 1
    
    # 更新父知识点
    for ch in chapters:
        for kp in ch['kps']:
            if kp['parent'] and kp['parent'] in kp_id_map:
                cursor.execute('''
                    UPDATE knowledge_points SET parent_kp_id = ? WHERE kp_id = ?
                ''', (kp_id_map[kp['parent']], kp['id']))
    
    print(f"✅ 语文：{total_kp} 个知识点")
    
    # 考点
    exam_points = [
        ('CHN-MR-001', '论述类文本阅读', '理解、分析综合论述类文本', '选择题', 3),
        ('CHN-MR-003', '文学类文本阅读', '小说、散文的阅读鉴赏', '选择题/简答题', 3),
        ('CHN-CR-001', '文言文阅读', '文言文阅读理解与翻译', '选择题/翻译题', 3),
        ('CHN-CR-002', '古代诗歌鉴赏', '诗歌形象、语言、表达技巧鉴赏', '简答题', 3),
        ('CHN-CR-003', '名句名篇默写', '常见名句名篇默写', '填空题', 1),
        ('CHN-LANG-005', '病句辨析', '辨析并修改病句', '选择题', 2),
        ('CHN-LANG-008', '语言表达连贯', '语言表达简明连贯得体', '选择题/简答题', 2),
        ('CHN-WR-003', '材料作文', '材料作文的写作', '作文题', 3),
    ]
    
    ep_count = 0
    for kp_id, ep_name, desc, exam_type, difficulty in exam_points:
        if kp_id in kp_id_map:
            ep_id = f"EP-CHN-{ep_count+1:03d}"
            cursor.execute('''
                INSERT OR IGNORE INTO exam_points 
                (ep_id, kp_id, ep_name, description, exam_type, difficulty_level)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (ep_id, kp_id_map[kp_id], ep_name, desc, exam_type, difficulty))
            ep_count += 1
    
    conn.commit()
    conn.close()
    print(f"✅ 语文：{ep_count} 个考点")


if __name__ == '__main__':
    build_chinese_knowledge_graph()
