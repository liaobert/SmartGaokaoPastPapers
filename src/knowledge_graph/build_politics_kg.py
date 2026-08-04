#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
政治学科知识点体系构建
基于《普通高中思想政治课程标准》和人教版教材
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '../../database/gaokao.db')


def build_politics_knowledge_graph():
    """构建政治学科知识图谱"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM subjects WHERE subject_code = 'politics'")
    subject_id = cursor.fetchone()[0]
    
    semesters = [
        {'code': 'compulsory_1', 'name': '必修1 中国特色社会主义', 'grade': '高一', 'sort': 1},
        {'code': 'compulsory_2', 'name': '必修2 经济与社会', 'grade': '高一', 'sort': 2},
        {'code': 'compulsory_3', 'name': '必修3 政治与法治', 'grade': '高一下', 'sort': 3},
        {'code': 'compulsory_4', 'name': '必修4 哲学与文化', 'grade': '高二', 'sort': 4},
        {'code': 'selective_1', 'name': '选择性必修1 当代国际政治与经济', 'grade': '高二', 'sort': 5},
        {'code': 'selective_2', 'name': '选择性必修2 法律与生活', 'grade': '高二', 'sort': 6},
        {'code': 'selective_3', 'name': '选择性必修3 逻辑与思维', 'grade': '高三', 'sort': 7},
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
        # 必修一：中国特色社会主义
        {
            'semester': 'compulsory_1', 'code': 'POL-SOCIALISM', 'name': '中国特色社会主义', 
            'number': '全书', 'sort': 1,
            'kps': [
                {'id': 'POL-SOC-001', 'name': '人类社会发展的规律', 'level': 1, 'parent': None,
                 'desc': '社会基本矛盾运动、社会历史发展的总趋势', 'importance': 3, 'difficulty': 2},
                {'id': 'POL-SOC-002', 'name': '社会主义从空想到科学', 'level': 1, 'parent': None,
                 'desc': '空想社会主义、科学社会主义的创立', 'importance': 2, 'difficulty': 2},
                {'id': 'POL-SOC-003', 'name': '只有社会主义才能救中国', 'level': 1, 'parent': None,
                 'desc': '新民主主义革命、社会主义制度的确立', 'importance': 3, 'difficulty': 2},
                {'id': 'POL-SOC-004', 'name': '只有中国特色社会主义才能发展中国', 'level': 1, 'parent': None,
                 'desc': '改革开放、中国特色社会主义的创立与发展', 'importance': 4, 'difficulty': 2},
                {'id': 'POL-SOC-005', 'name': '只有坚持和发展中国特色社会主义才能实现中华民族伟大复兴', 'level': 1, 'parent': None,
                 'desc': '中国特色社会主义新时代、中国梦', 'importance': 4, 'difficulty': 2},
            ]
        },
        # 必修二：经济与社会
        {
            'semester': 'compulsory_2', 'code': 'POL-ECONOMY', 'name': '经济与社会', 
            'number': '全书', 'sort': 2,
            'kps': [
                {'id': 'POL-ECO-001', 'name': '我国的生产资料所有制', 'level': 1, 'parent': None,
                 'desc': '公有制为主体、多种所有制经济共同发展', 'importance': 4, 'difficulty': 2},
                {'id': 'POL-ECO-002', 'name': '我国的社会主义市场经济体制', 'level': 1, 'parent': None,
                 'desc': '市场调节、科学的宏观调控', 'importance': 4, 'difficulty': 3},
                {'id': 'POL-ECO-003', 'name': '我国的经济发展', 'level': 1, 'parent': None,
                 'desc': '新发展理念、高质量发展、现代化经济体系', 'importance': 4, 'difficulty': 3},
                {'id': 'POL-ECO-004', 'name': '我国的个人收入分配与社会保障', 'level': 1, 'parent': None,
                 'desc': '按劳分配为主体、多种分配方式并存、社会保障', 'importance': 4, 'difficulty': 2},
            ]
        },
        # 必修三：政治与法治
        {
            'semester': 'compulsory_3', 'code': 'POL-POLITICS', 'name': '政治与法治', 
            'number': '全书', 'sort': 3,
            'kps': [
                {'id': 'POL-POL-001', 'name': '中国共产党的领导', 'level': 1, 'parent': None,
                 'desc': '党的领导是中国特色社会主义最本质的特征', 'importance': 4, 'difficulty': 2},
                {'id': 'POL-POL-002', 'name': '人民当家作主', 'level': 1, 'parent': None,
                 'desc': '人民代表大会制度、政党制度、民族区域自治、基层群众自治', 'importance': 4, 'difficulty': 3},
                {'id': 'POL-POL-003', 'name': '全面依法治国', 'level': 1, 'parent': None,
                 'desc': '全面依法治国的总目标与原则、法治国家、法治政府、法治社会', 'importance': 4, 'difficulty': 3},
            ]
        },
        # 必修四：哲学与文化
        {
            'semester': 'compulsory_4', 'code': 'POL-PHILOSOPHY', 'name': '哲学与文化', 
            'number': '全书', 'sort': 4,
            'kps': [
                # 哲学部分
                {'id': 'POL-PHI-001', 'name': '哲学的基本问题', 'level': 1, 'parent': None,
                 'desc': '哲学的基本问题、唯物主义和唯心主义', 'importance': 3, 'difficulty': 2},
                {'id': 'POL-PHI-002', 'name': '探究世界的本质', 'level': 1, 'parent': None,
                 'desc': '世界的物质性、运动与规律', 'importance': 4, 'difficulty': 3},
                {'id': 'POL-PHI-003', 'name': '把握世界的规律', 'level': 1, 'parent': None,
                 'desc': '联系观、发展观、矛盾观', 'importance': 4, 'difficulty': 4},
                {'id': 'POL-PHI-004', 'name': '探索认识的奥秘', 'level': 1, 'parent': None,
                 'desc': '认识论、实践与认识、真理', 'importance': 4, 'difficulty': 3},
                {'id': 'POL-PHI-005', 'name': '寻觅社会的真谛', 'level': 1, 'parent': None,
                 'desc': '社会历史观、人民群众是历史的创造者', 'importance': 4, 'difficulty': 3},
                {'id': 'POL-PHI-006', 'name': '实现人生的价值', 'level': 1, 'parent': None,
                 'desc': '价值观、价值判断与价值选择、价值的创造与实现', 'importance': 4, 'difficulty': 3},
                # 文化部分
                {'id': 'POL-CUL-001', 'name': '文化的内涵与功能', 'level': 1, 'parent': None,
                 'desc': '文化的内涵、文化的功能', 'importance': 2, 'difficulty': 2},
                {'id': 'POL-CUL-002', 'name': '认识中华文化', 'level': 1, 'parent': None,
                 'desc': '中华文化的源远流长、博大精深', 'importance': 3, 'difficulty': 2},
                {'id': 'POL-CUL-003', 'name': '弘扬中华优秀传统文化与民族精神', 'level': 1, 'parent': None,
                 'desc': '传统文化的继承与发展、中华民族精神', 'importance': 4, 'difficulty': 2},
                {'id': 'POL-CUL-004', 'name': '发展中国特色社会主义文化', 'level': 1, 'parent': None,
                 'desc': '文化强国、文化自信', 'importance': 4, 'difficulty': 2},
            ]
        },
        # 选择性必修一：当代国际政治与经济
        {
            'semester': 'selective_1', 'code': 'POL-INTL', 'name': '当代国际政治与经济', 
            'number': '全书', 'sort': 5,
            'kps': [
                {'id': 'POL-INT-001', 'name': '各具特色的国家', 'level': 1, 'parent': None,
                 'desc': '国家的本质、国家的政权组织形式、国家结构形式', 'importance': 3, 'difficulty': 2},
                {'id': 'POL-INT-002', 'name': '世界多极化', 'level': 1, 'parent': None,
                 'desc': '世界多极化的发展、国际关系、和平与发展', 'importance': 4, 'difficulty': 2},
                {'id': 'POL-INT-003', 'name': '经济全球化', 'level': 1, 'parent': None,
                 'desc': '经济全球化的表现、影响、应对', 'importance': 4, 'difficulty': 3},
                {'id': 'POL-INT-004', 'name': '国际组织', 'level': 1, 'parent': None,
                 'desc': '国际组织的分类、作用、主要国际组织', 'importance': 3, 'difficulty': 2},
            ]
        },
        # 选择性必修二：法律与生活
        {
            'semester': 'selective_2', 'code': 'POL-LAW', 'name': '法律与生活', 
            'number': '全书', 'sort': 6,
            'kps': [
                {'id': 'POL-LAW-001', 'name': '民事权利与义务', 'level': 1, 'parent': None,
                 'desc': '民事法律关系、人身权、财产权、合同', 'importance': 4, 'difficulty': 3},
                {'id': 'POL-LAW-002', 'name': '家庭与婚姻', 'level': 1, 'parent': None,
                 'desc': '婚姻家庭关系、继承', 'importance': 2, 'difficulty': 2},
                {'id': 'POL-LAW-003', 'name': '就业与创业', 'level': 1, 'parent': None,
                 'desc': '劳动合同、劳动者权益、创业', 'importance': 2, 'difficulty': 2},
                {'id': 'POL-LAW-004', 'name': '社会争议解决', 'level': 1, 'parent': None,
                 'desc': '调解、仲裁、诉讼', 'importance': 3, 'difficulty': 2},
            ]
        },
        # 选择性必修三：逻辑与思维
        {
            'semester': 'selective_3', 'code': 'POL-LOGIC', 'name': '逻辑与思维', 
            'number': '全书', 'sort': 7,
            'kps': [
                {'id': 'POL-LOG-001', 'name': '树立科学思维观念', 'level': 1, 'parent': None,
                 'desc': '思维的含义与特征、科学思维', 'importance': 2, 'difficulty': 2},
                {'id': 'POL-LOG-002', 'name': '遵循逻辑思维规则', 'level': 1, 'parent': None,
                 'desc': '概念、判断、推理', 'importance': 4, 'difficulty': 3},
                {'id': 'POL-LOG-003', 'name': '运用辩证思维方法', 'level': 1, 'parent': None,
                 'desc': '辩证思维的特征、分析与综合、质量互变、辩证否定', 'importance': 3, 'difficulty': 3},
                {'id': 'POL-LOG-004', 'name': '提高创新思维能力', 'level': 1, 'parent': None,
                 'desc': '创新思维、联想思维、发散与聚合思维、逆向思维、超前思维', 'importance': 3, 'difficulty': 2},
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
    
    print(f"✅ 政治：{total_kp} 个知识点")
    
    # 考点
    exam_points = [
        ('POL-ECO-002', '社会主义市场经济体制', '市场调节与宏观调控', '选择题/主观题', 3),
        ('POL-ECO-003', '我国的经济发展', '新发展理念与高质量发展', '主观题', 3),
        ('POL-POL-002', '人民当家作主', '我国的政治制度', '选择题/主观题', 3),
        ('POL-PHI-003', '唯物辩证法', '联系观、发展观、矛盾观', '选择题/主观题', 4),
        ('POL-PHI-004', '认识论', '实践与认识的关系', '选择题/主观题', 3),
        ('POL-PHI-006', '价值观', '价值判断与价值选择', '选择题/主观题', 3),
        ('POL-CUL-003', '民族精神', '中华民族精神的内涵与作用', '选择题/主观题', 2),
        ('POL-INT-002', '世界多极化', '国际关系与时代主题', '选择题/主观题', 3),
        ('POL-INT-003', '经济全球化', '经济全球化的影响与应对', '选择题/主观题', 3),
        ('POL-LAW-001', '民事权利与义务', '民事法律关系与合同', '选择题/主观题', 3),
    ]
    
    ep_count = 0
    for kp_id, ep_name, desc, exam_type, difficulty in exam_points:
        if kp_id in kp_id_map:
            ep_id = f"EP-POL-{ep_count+1:03d}"
            cursor.execute('''
                INSERT OR IGNORE INTO exam_points 
                (ep_id, kp_id, ep_name, description, exam_type, difficulty_level)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (ep_id, kp_id_map[kp_id], ep_name, desc, exam_type, difficulty))
            ep_count += 1
    
    conn.commit()
    conn.close()
    print(f"✅ 政治：{ep_count} 个考点")


if __name__ == '__main__':
    build_politics_knowledge_graph()
