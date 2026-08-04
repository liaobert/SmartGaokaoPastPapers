#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
英语学科知识点体系构建
基于《普通高中英语课程标准》和人教版教材
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '../../database/gaokao.db')


def build_english_knowledge_graph():
    """构建英语学科知识图谱"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM subjects WHERE subject_code = 'english'")
    subject_id = cursor.fetchone()[0]
    
    semesters = [
        {'code': 'compulsory_1', 'name': '必修第一册', 'grade': '高一', 'sort': 1},
        {'code': 'compulsory_2', 'name': '必修第二册', 'grade': '高一', 'sort': 2},
        {'code': 'compulsory_3', 'name': '必修第三册', 'grade': '高一下', 'sort': 3},
        {'code': 'selective_1', 'name': '选择性必修第一册', 'grade': '高二', 'sort': 4},
        {'code': 'selective_2', 'name': '选择性必修第二册', 'grade': '高二', 'sort': 5},
        {'code': 'selective_3', 'name': '选择性必修第三册', 'grade': '高二', 'sort': 6},
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
    
    chapters = [
        {
            'semester': 'compulsory_1', 'code': 'ENG-LISTEN', 'name': '听力理解', 
            'number': '专题一', 'sort': 1,
            'kps': [
                {'id': 'ENG-LIS-001', 'name': '短对话理解', 'level': 1, 'parent': None,
                 'desc': '短对话听力理解', 'importance': 3, 'difficulty': 2},
                {'id': 'ENG-LIS-002', 'name': '长对话理解', 'level': 1, 'parent': None,
                 'desc': '长对话听力理解', 'importance': 3, 'difficulty': 2},
                {'id': 'ENG-LIS-003', 'name': '短文理解', 'level': 1, 'parent': None,
                 'desc': '短文听力理解', 'importance': 3, 'difficulty': 3},
                {'id': 'ENG-LIS-004', 'name': '听力技巧', 'level': 1, 'parent': None,
                 'desc': '听力应试技巧', 'importance': 2, 'difficulty': 2},
            ]
        },
        {
            'semester': 'compulsory_2', 'code': 'ENG-READ', 'name': '阅读理解', 
            'number': '专题二', 'sort': 2,
            'kps': [
                {'id': 'ENG-READ-001', 'name': '细节理解题', 'level': 1, 'parent': None,
                 'desc': '阅读理解细节题', 'importance': 4, 'difficulty': 2},
                {'id': 'ENG-READ-002', 'name': '主旨大意题', 'level': 1, 'parent': None,
                 'desc': '阅读理解主旨题', 'importance': 4, 'difficulty': 3},
                {'id': 'ENG-READ-003', 'name': '推理判断题', 'level': 1, 'parent': None,
                 'desc': '阅读理解推理题', 'importance': 4, 'difficulty': 3},
                {'id': 'ENG-READ-004', 'name': '词义猜测题', 'level': 1, 'parent': None,
                 'desc': '阅读理解词义猜测题', 'importance': 3, 'difficulty': 2},
                {'id': 'ENG-READ-005', 'name': '七选五', 'level': 1, 'parent': None,
                 'desc': '七选五阅读理解', 'importance': 4, 'difficulty': 3},
                # 二级
                {'id': 'ENG-READ-101', 'name': '记叙文阅读', 'level': 2, 'parent': 'ENG-READ-001',
                 'desc': '记叙文阅读理解', 'importance': 3, 'difficulty': 2},
                {'id': 'ENG-READ-102', 'name': '说明文阅读', 'level': 2, 'parent': 'ENG-READ-001',
                 'desc': '说明文阅读理解', 'importance': 4, 'difficulty': 3},
                {'id': 'ENG-READ-103', 'name': '议论文阅读', 'level': 2, 'parent': 'ENG-READ-001',
                 'desc': '议论文阅读理解', 'importance': 4, 'difficulty': 3},
                {'id': 'ENG-READ-104', 'name': '应用文阅读', 'level': 2, 'parent': 'ENG-READ-001',
                 'desc': '应用文阅读理解', 'importance': 3, 'difficulty': 1},
            ]
        },
        {
            'semester': 'compulsory_3', 'code': 'ENG-CLOZE', 'name': '完形填空', 
            'number': '专题三', 'sort': 3,
            'kps': [
                {'id': 'ENG-CLOZE-001', 'name': '完形填空', 'level': 1, 'parent': None,
                 'desc': '完形填空题型与技巧', 'importance': 4, 'difficulty': 3},
                {'id': 'ENG-CLOZE-002', 'name': '词汇辨析', 'level': 1, 'parent': 'ENG-CLOZE-001',
                 'desc': '近义词、形近词辨析', 'importance': 4, 'difficulty': 3},
                {'id': 'ENG-CLOZE-003', 'name': '语境理解', 'level': 1, 'parent': 'ENG-CLOZE-001',
                 'desc': '上下文语境理解', 'importance': 4, 'difficulty': 3},
            ]
        },
        {
            'semester': 'selective_1', 'code': 'ENG-GRAMMAR', 'name': '语法填空', 
            'number': '专题四', 'sort': 4,
            'kps': [
                {'id': 'ENG-GRAM-001', 'name': '名词', 'level': 1, 'parent': None,
                 'desc': '名词的数、格、主谓一致', 'importance': 3, 'difficulty': 2},
                {'id': 'ENG-GRAM-002', 'name': '冠词', 'level': 1, 'parent': None,
                 'desc': '定冠词、不定冠词、零冠词', 'importance': 3, 'difficulty': 2},
                {'id': 'ENG-GRAM-003', 'name': '代词', 'level': 1, 'parent': None,
                 'desc': '人称代词、物主代词、反身代词等', 'importance': 2, 'difficulty': 1},
                {'id': 'ENG-GRAM-004', 'name': '形容词和副词', 'level': 1, 'parent': None,
                 'desc': '形容词、副词的比较级和最高级', 'importance': 3, 'difficulty': 2},
                {'id': 'ENG-GRAM-005', 'name': '动词时态', 'level': 1, 'parent': None,
                 'desc': '各种时态的用法', 'importance': 4, 'difficulty': 3},
                {'id': 'ENG-GRAM-006', 'name': '动词语态', 'level': 1, 'parent': None,
                 'desc': '被动语态的用法', 'importance': 3, 'difficulty': 2},
                {'id': 'ENG-GRAM-007', 'name': '非谓语动词', 'level': 1, 'parent': None,
                 'desc': '不定式、动名词、分词', 'importance': 4, 'difficulty': 3},
                {'id': 'ENG-GRAM-008', 'name': '情态动词', 'level': 1, 'parent': None,
                 'desc': '情态动词的用法', 'importance': 3, 'difficulty': 2},
                {'id': 'ENG-GRAM-009', 'name': '虚拟语气', 'level': 1, 'parent': None,
                 'desc': '虚拟语气的用法', 'importance': 3, 'difficulty': 3},
                {'id': 'ENG-GRAM-010', 'name': '定语从句', 'level': 1, 'parent': None,
                 'desc': '限制性和非限制性定语从句', 'importance': 4, 'difficulty': 3},
                {'id': 'ENG-GRAM-011', 'name': '名词性从句', 'level': 1, 'parent': None,
                 'desc': '主语从句、宾语从句、表语从句、同位语从句', 'importance': 4, 'difficulty': 3},
                {'id': 'ENG-GRAM-012', 'name': '状语从句', 'level': 1, 'parent': None,
                 'desc': '时间、地点、原因、条件、让步等状语从句', 'importance': 4, 'difficulty': 3},
                {'id': 'ENG-GRAM-013', 'name': '倒装句', 'level': 1, 'parent': None,
                 'desc': '完全倒装和部分倒装', 'importance': 2, 'difficulty': 3},
                {'id': 'ENG-GRAM-014', 'name': '强调句', 'level': 1, 'parent': None,
                 'desc': '强调句型的用法', 'importance': 2, 'difficulty': 2},
                {'id': 'ENG-GRAM-015', 'name': '省略句', 'level': 1, 'parent': None,
                 'desc': '省略句的用法', 'importance': 2, 'difficulty': 2},
                {'id': 'ENG-GRAM-016', 'name': '语法填空', 'level': 1, 'parent': None,
                 'desc': '语法填空题型与技巧', 'importance': 4, 'difficulty': 3},
            ]
        },
        {
            'semester': 'selective_2', 'code': 'ENG-WRITING', 'name': '写作', 
            'number': '专题五', 'sort': 5,
            'kps': [
                {'id': 'ENG-WR-001', 'name': '短文改错', 'level': 1, 'parent': None,
                 'desc': '短文改错题型与技巧', 'importance': 3, 'difficulty': 3},
                {'id': 'ENG-WR-002', 'name': '应用文写作', 'level': 1, 'parent': None,
                 'desc': '书信、通知、演讲稿等应用文写作', 'importance': 4, 'difficulty': 2},
                {'id': 'ENG-WR-003', 'name': '读后续写', 'level': 1, 'parent': None,
                 'desc': '读后续写题型与技巧', 'importance': 4, 'difficulty': 4},
                {'id': 'ENG-WR-004', 'name': '概要写作', 'level': 1, 'parent': None,
                 'desc': '概要写作题型与技巧', 'importance': 3, 'difficulty': 3},
                # 二级
                {'id': 'ENG-WR-101', 'name': '书信写作', 'level': 2, 'parent': 'ENG-WR-002',
                 'desc': '建议信、邀请信、感谢信、道歉信等', 'importance': 4, 'difficulty': 2},
                {'id': 'ENG-WR-102', 'name': '通知写作', 'level': 2, 'parent': 'ENG-WR-002',
                 'desc': '通知的写作格式与内容', 'importance': 3, 'difficulty': 2},
                {'id': 'ENG-WR-103', 'name': '演讲稿写作', 'level': 2, 'parent': 'ENG-WR-002',
                 'desc': '演讲稿的写作', 'importance': 3, 'difficulty': 2},
            ]
        },
        {
            'semester': 'selective_3', 'code': 'ENG-VOCAB', 'name': '词汇', 
            'number': '专题六', 'sort': 6,
            'kps': [
                {'id': 'ENG-VOC-001', 'name': '核心词汇', 'level': 1, 'parent': None,
                 'desc': '高考核心词汇3500', 'importance': 4, 'difficulty': 2},
                {'id': 'ENG-VOC-002', 'name': '词法构词', 'level': 1, 'parent': None,
                 'desc': '前缀、后缀、词根', 'importance': 3, 'difficulty': 2},
                {'id': 'ENG-VOC-003', 'name': '短语搭配', 'level': 1, 'parent': None,
                 'desc': '常用短语和固定搭配', 'importance': 4, 'difficulty': 2},
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
    
    for ch in chapters:
        for kp in ch['kps']:
            if kp['parent'] and kp['parent'] in kp_id_map:
                cursor.execute('''
                    UPDATE knowledge_points SET parent_kp_id = ? WHERE kp_id = ?
                ''', (kp_id_map[kp['parent']], kp['id']))
    
    print(f"✅ 英语：{total_kp} 个知识点")
    
    # 考点
    exam_points = [
        ('ENG-READ-001', '阅读理解细节题', '理解文中具体信息', '阅读理解', 2),
        ('ENG-READ-002', '阅读理解主旨题', '归纳主旨大意', '阅读理解', 3),
        ('ENG-READ-003', '阅读理解推理题', '做出推理判断', '阅读理解', 3),
        ('ENG-READ-005', '七选五', '七选五阅读理解', '阅读理解', 3),
        ('ENG-CLOZE-001', '完形填空', '完形填空综合能力', '完形填空', 3),
        ('ENG-GRAM-016', '语法填空', '语法填空综合能力', '语法填空', 3),
        ('ENG-WR-002', '应用文写作', '应用文写作能力', '写作', 2),
        ('ENG-WR-003', '读后续写', '读后续写能力', '写作', 4),
    ]
    
    ep_count = 0
    for kp_id, ep_name, desc, exam_type, difficulty in exam_points:
        if kp_id in kp_id_map:
            ep_id = f"EP-ENG-{ep_count+1:03d}"
            cursor.execute('''
                INSERT OR IGNORE INTO exam_points 
                (ep_id, kp_id, ep_name, description, exam_type, difficulty_level)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (ep_id, kp_id_map[kp_id], ep_name, desc, exam_type, difficulty))
            ep_count += 1
    
    conn.commit()
    conn.close()
    print(f"✅ 英语：{ep_count} 个考点")


if __name__ == '__main__':
    build_english_knowledge_graph()
