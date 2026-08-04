#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
化学学科知识点体系构建
基于《普通高中化学课程标准》和人教版教材
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '../../database/gaokao.db')


def build_chemistry_knowledge_graph():
    """构建化学学科知识图谱"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM subjects WHERE subject_code = 'chemistry'")
    subject_id = cursor.fetchone()[0]
    
    semesters = [
        {'code': 'compulsory_1', 'name': '必修第一册', 'grade': '高一', 'sort': 1},
        {'code': 'compulsory_2', 'name': '必修第二册', 'grade': '高一', 'sort': 2},
        {'code': 'selective_1', 'name': '选择性必修1 化学反应原理', 'grade': '高二', 'sort': 3},
        {'code': 'selective_2', 'name': '选择性必修2 物质结构与性质', 'grade': '高二', 'sort': 4},
        {'code': 'selective_3', 'name': '选择性必修3 有机化学基础', 'grade': '高二', 'sort': 5},
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
        # 必修一：化学基本概念、元素化合物
        {
            'semester': 'compulsory_1', 'code': 'CHEM-BASIC', 'name': '化学物质及其变化', 
            'number': '第一章', 'sort': 1,
            'kps': [
                {'id': 'CHEM-BAS-001', 'name': '物质的分类', 'level': 1, 'parent': None,
                 'desc': '物质的分类方法、分散系', 'importance': 3, 'difficulty': 1},
                {'id': 'CHEM-BAS-002', 'name': '离子反应', 'level': 1, 'parent': None,
                 'desc': '电解质、离子方程式、离子共存', 'importance': 4, 'difficulty': 2},
                {'id': 'CHEM-BAS-003', 'name': '氧化还原反应', 'level': 1, 'parent': None,
                 'desc': '氧化还原反应的概念、配平、计算', 'importance': 4, 'difficulty': 3},
            ]
        },
        {
            'semester': 'compulsory_1', 'code': 'CHEM-METAL', 'name': '金属及其化合物', 
            'number': '第三章', 'sort': 2,
            'kps': [
                {'id': 'CHEM-MET-001', 'name': '钠及其化合物', 'level': 1, 'parent': None,
                 'desc': 'Na、Na₂O、Na₂O₂、NaOH、Na₂CO₃、NaHCO₃', 'importance': 4, 'difficulty': 2},
                {'id': 'CHEM-MET-002', 'name': '铝及其化合物', 'level': 1, 'parent': None,
                 'desc': 'Al、Al₂O₃、Al(OH)₃的两性', 'importance': 4, 'difficulty': 3},
                {'id': 'CHEM-MET-003', 'name': '铁及其化合物', 'level': 1, 'parent': None,
                 'desc': 'Fe、Fe²⁺、Fe³⁺的性质及转化', 'importance': 4, 'difficulty': 3},
                {'id': 'CHEM-MET-004', 'name': '镁铜及其化合物', 'level': 1, 'parent': None,
                 'desc': 'Mg、Cu及其化合物的性质', 'importance': 3, 'difficulty': 2},
            ]
        },
        {
            'semester': 'compulsory_1', 'code': 'CHEM-NONMETAL', 'name': '非金属及其化合物', 
            'number': '第四章', 'sort': 3,
            'kps': [
                {'id': 'CHEM-NON-001', 'name': '硅及其化合物', 'level': 1, 'parent': None,
                 'desc': 'Si、SiO₂、硅酸盐的性质', 'importance': 3, 'difficulty': 2},
                {'id': 'CHEM-NON-002', 'name': '氯及其化合物', 'level': 1, 'parent': None,
                 'desc': 'Cl₂、HClO、漂白粉的性质', 'importance': 4, 'difficulty': 2},
                {'id': 'CHEM-NON-003', 'name': '硫及其化合物', 'level': 1, 'parent': None,
                 'desc': 'S、SO₂、SO₃、H₂SO₄的性质', 'importance': 4, 'difficulty': 3},
                {'id': 'CHEM-NON-004', 'name': '氮及其化合物', 'level': 1, 'parent': None,
                 'desc': 'N₂、NO、NO₂、HNO₃、NH₃的性质', 'importance': 4, 'difficulty': 3},
            ]
        },
        # 必修二：物质结构、化学反应、有机化学初步
        {
            'semester': 'compulsory_2', 'code': 'CHEM-STRUCTURE', 'name': '物质结构 元素周期律', 
            'number': '第一章', 'sort': 4,
            'kps': [
                {'id': 'CHEM-STR-001', 'name': '原子结构', 'level': 1, 'parent': None,
                 'desc': '原子构成、核外电子排布', 'importance': 3, 'difficulty': 2},
                {'id': 'CHEM-STR-002', 'name': '元素周期表', 'level': 1, 'parent': 'CHEM-STR-001',
                 'desc': '元素周期表的结构', 'importance': 3, 'difficulty': 2},
                {'id': 'CHEM-STR-003', 'name': '元素周期律', 'level': 1, 'parent': 'CHEM-STR-002',
                 'desc': '元素性质的周期性变化', 'importance': 4, 'difficulty': 3},
                {'id': 'CHEM-STR-004', 'name': '化学键', 'level': 1, 'parent': None,
                 'desc': '离子键、共价键、金属键', 'importance': 3, 'difficulty': 2},
            ]
        },
        {
            'semester': 'compulsory_2', 'code': 'CHEM-REACTION', 'name': '化学反应与能量', 
            'number': '第二章', 'sort': 5,
            'kps': [
                {'id': 'CHEM-REA-001', 'name': '化学能与热能', 'level': 1, 'parent': None,
                 'desc': '吸热反应、放热反应、反应热', 'importance': 3, 'difficulty': 2},
                {'id': 'CHEM-REA-002', 'name': '化学能与电能', 'level': 1, 'parent': None,
                 'desc': '原电池工作原理', 'importance': 4, 'difficulty': 3},
                {'id': 'CHEM-REA-003', 'name': '化学反应速率', 'level': 1, 'parent': None,
                 'desc': '化学反应速率的概念与计算', 'importance': 3, 'difficulty': 2},
                {'id': 'CHEM-REA-004', 'name': '化学反应的限度', 'level': 1, 'parent': None,
                 'desc': '化学平衡的建立', 'importance': 3, 'difficulty': 3},
            ]
        },
        {
            'semester': 'compulsory_2', 'code': 'CHEM-ORGANIC-BASIC', 'name': '有机化合物', 
            'number': '第三章', 'sort': 6,
            'kps': [
                {'id': 'CHEM-ORGB-001', 'name': '甲烷 烷烃', 'level': 1, 'parent': None,
                 'desc': '甲烷的性质、烷烃的结构与性质', 'importance': 3, 'difficulty': 2},
                {'id': 'CHEM-ORGB-002', 'name': '乙烯 烯烃', 'level': 1, 'parent': None,
                 'desc': '乙烯的性质、加成反应', 'importance': 4, 'difficulty': 2},
                {'id': 'CHEM-ORGB-003', 'name': '苯 芳香烃', 'level': 1, 'parent': None,
                 'desc': '苯的结构与性质', 'importance': 3, 'difficulty': 2},
                {'id': 'CHEM-ORGB-004', 'name': '乙醇 乙酸', 'level': 1, 'parent': None,
                 'desc': '乙醇、乙酸的性质与酯化反应', 'importance': 4, 'difficulty': 2},
                {'id': 'CHEM-ORGB-005', 'name': '基本营养物质', 'level': 1, 'parent': None,
                 'desc': '糖类、油脂、蛋白质', 'importance': 2, 'difficulty': 1},
            ]
        },
        # 选择性必修一：化学反应原理
        {
            'semester': 'selective_1', 'code': 'CHEM-THERMO', 'name': '化学反应的热效应', 
            'number': '第一章', 'sort': 7,
            'kps': [
                {'id': 'CHEM-THM-001', 'name': '反应热 焓变', 'level': 1, 'parent': None,
                 'desc': '反应热、焓变的概念', 'importance': 4, 'difficulty': 2},
                {'id': 'CHEM-THM-002', 'name': '热化学方程式', 'level': 1, 'parent': 'CHEM-THM-001',
                 'desc': '热化学方程式的书写', 'importance': 4, 'difficulty': 2},
                {'id': 'CHEM-THM-003', 'name': '盖斯定律', 'level': 1, 'parent': 'CHEM-THM-001',
                 'desc': '盖斯定律及其应用', 'importance': 4, 'difficulty': 3},
            ]
        },
        {
            'semester': 'selective_1', 'code': 'CHEM-RATE', 'name': '化学反应速率与化学平衡', 
            'number': '第二章', 'sort': 8,
            'kps': [
                {'id': 'CHEM-RAT-001', 'name': '化学反应速率', 'level': 1, 'parent': None,
                 'desc': '反应速率的计算、影响因素', 'importance': 4, 'difficulty': 2},
                {'id': 'CHEM-RAT-002', 'name': '化学平衡', 'level': 1, 'parent': None,
                 'desc': '化学平衡状态、平衡常数', 'importance': 4, 'difficulty': 3},
                {'id': 'CHEM-RAT-003', 'name': '化学平衡移动', 'level': 1, 'parent': 'CHEM-RAT-002',
                 'desc': '勒夏特列原理', 'importance': 4, 'difficulty': 3},
                {'id': 'CHEM-RAT-004', 'name': '化学反应进行的方向', 'level': 1, 'parent': None,
                 'desc': '熵变、焓变与反应方向', 'importance': 2, 'difficulty': 2},
            ]
        },
        {
            'semester': 'selective_1', 'code': 'CHEM-ELECTRO', 'name': '水溶液中的离子反应与平衡', 
            'number': '第三章', 'sort': 9,
            'kps': [
                {'id': 'CHEM-ELE-001', 'name': '弱电解质的电离', 'level': 1, 'parent': None,
                 'desc': '弱电解质的电离平衡', 'importance': 4, 'difficulty': 3},
                {'id': 'CHEM-ELE-002', 'name': '水的电离和溶液的pH', 'level': 1, 'parent': None,
                 'desc': '水的电离、pH计算', 'importance': 4, 'difficulty': 3},
                {'id': 'CHEM-ELE-003', 'name': '盐类的水解', 'level': 1, 'parent': None,
                 'desc': '盐类水解的原理、影响因素', 'importance': 4, 'difficulty': 3},
                {'id': 'CHEM-ELE-004', 'name': '沉淀溶解平衡', 'level': 1, 'parent': None,
                 'desc': '溶度积、沉淀的生成与转化', 'importance': 4, 'difficulty': 3},
            ]
        },
        {
            'semester': 'selective_1', 'code': 'CHEM-ELECTROCHEM', 'name': '化学反应与电能', 
            'number': '第四章', 'sort': 10,
            'kps': [
                {'id': 'CHEM-ELC-001', 'name': '原电池', 'level': 1, 'parent': None,
                 'desc': '原电池工作原理、化学电源', 'importance': 4, 'difficulty': 3},
                {'id': 'CHEM-ELC-002', 'name': '电解池', 'level': 1, 'parent': None,
                 'desc': '电解原理、电解的应用', 'importance': 4, 'difficulty': 3},
                {'id': 'CHEM-ELC-003', 'name': '金属的腐蚀与防护', 'level': 1, 'parent': None,
                 'desc': '金属腐蚀的原理、防护方法', 'importance': 3, 'difficulty': 2},
            ]
        },
        # 选择性必修二：物质结构与性质
        {
            'semester': 'selective_2', 'code': 'CHEM-ATOMIC', 'name': '原子结构与性质', 
            'number': '第一章', 'sort': 11,
            'kps': [
                {'id': 'CHEM-ATM-001', 'name': '原子结构', 'level': 1, 'parent': None,
                 'desc': '能层、能级、电子云、原子轨道', 'importance': 3, 'difficulty': 2},
                {'id': 'CHEM-ATM-002', 'name': '原子核外电子排布', 'level': 1, 'parent': 'CHEM-ATM-001',
                 'desc': '电子排布式、轨道表示式', 'importance': 4, 'difficulty': 2},
                {'id': 'CHEM-ATM-003', 'name': '元素周期律', 'level': 1, 'parent': None,
                 'desc': '电离能、电负性', 'importance': 4, 'difficulty': 3},
            ]
        },
        {
            'semester': 'selective_2', 'code': 'CHEM-MOLECULAR', 'name': '分子结构与性质', 
            'number': '第二章', 'sort': 12,
            'kps': [
                {'id': 'CHEM-MOL-001', 'name': '共价键', 'level': 1, 'parent': None,
                 'desc': 'σ键、π键、键参数', 'importance': 3, 'difficulty': 2},
                {'id': 'CHEM-MOL-002', 'name': '分子的立体构型', 'level': 1, 'parent': None,
                 'desc': '价层电子对互斥理论、杂化轨道理论', 'importance': 4, 'difficulty': 3},
                {'id': 'CHEM-MOL-003', 'name': '分子的性质', 'level': 1, 'parent': None,
                 'desc': '分子的极性、范德华力、氢键', 'importance': 4, 'difficulty': 3},
            ]
        },
        {
            'semester': 'selective_2', 'code': 'CHEM-CRYSTAL', 'name': '晶体结构与性质', 
            'number': '第三章', 'sort': 13,
            'kps': [
                {'id': 'CHEM-CRY-001', 'name': '晶体的常识', 'level': 1, 'parent': None,
                 'desc': '晶体与非晶体、晶胞', 'importance': 3, 'difficulty': 2},
                {'id': 'CHEM-CRY-002', 'name': '分子晶体与原子晶体', 'level': 1, 'parent': None,
                 'desc': '分子晶体、原子晶体的结构与性质', 'importance': 3, 'difficulty': 3},
                {'id': 'CHEM-CRY-003', 'name': '金属晶体', 'level': 1, 'parent': None,
                 'desc': '金属键、金属晶体的堆积方式', 'importance': 2, 'difficulty': 2},
                {'id': 'CHEM-CRY-004', 'name': '离子晶体', 'level': 1, 'parent': None,
                 'desc': '离子晶体的结构与性质、晶格能', 'importance': 3, 'difficulty': 3},
            ]
        },
        # 选择性必修三：有机化学基础
        {
            'semester': 'selective_3', 'code': 'CHEM-ORGANIC', 'name': '有机化学基础', 
            'number': '全书', 'sort': 14,
            'kps': [
                {'id': 'CHEM-ORG-001', 'name': '有机化合物的结构与分类', 'level': 1, 'parent': None,
                 'desc': '有机物的分类、官能团、同分异构体', 'importance': 4, 'difficulty': 3},
                {'id': 'CHEM-ORG-002', 'name': '烃', 'level': 1, 'parent': None,
                 'desc': '烷烃、烯烃、炔烃、芳香烃的性质', 'importance': 4, 'difficulty': 3},
                {'id': 'CHEM-ORG-003', 'name': '烃的衍生物', 'level': 1, 'parent': None,
                 'desc': '卤代烃、醇、酚、醛、羧酸、酯的性质', 'importance': 4, 'difficulty': 3},
                {'id': 'CHEM-ORG-004', 'name': '有机反应类型', 'level': 1, 'parent': None,
                 'desc': '取代、加成、消去、氧化、还原、聚合等', 'importance': 4, 'difficulty': 3},
                {'id': 'CHEM-ORG-005', 'name': '有机合成', 'level': 1, 'parent': None,
                 'desc': '有机合成路线的设计与推断', 'importance': 4, 'difficulty': 4},
                {'id': 'CHEM-ORG-006', 'name': '生命中的基础有机化学物质', 'level': 1, 'parent': None,
                 'desc': '糖类、油脂、蛋白质、核酸', 'importance': 2, 'difficulty': 2},
                {'id': 'CHEM-ORG-007', 'name': '高分子化合物', 'level': 1, 'parent': None,
                 'desc': '加聚反应、缩聚反应', 'importance': 3, 'difficulty': 2},
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
    
    print(f"✅ 化学：{total_kp} 个知识点")
    
    # 考点
    exam_points = [
        ('CHEM-BAS-003', '氧化还原反应', '氧化还原反应的概念与计算', '选择题', 3),
        ('CHEM-BAS-002', '离子反应', '离子方程式书写与离子共存', '选择题', 2),
        ('CHEM-STR-003', '元素周期律', '元素周期律的应用', '选择题', 3),
        ('CHEM-RAT-002', '化学平衡', '化学平衡常数与平衡移动', '选择题/填空题', 3),
        ('CHEM-ELE-003', '盐类的水解', '盐类水解的应用', '选择题/填空题', 3),
        ('CHEM-ELE-004', '沉淀溶解平衡', '溶度积的应用', '选择题/填空题', 3),
        ('CHEM-ELC-001', '原电池', '原电池工作原理', '选择题/填空题', 3),
        ('CHEM-ELC-002', '电解池', '电解原理及应用', '选择题/填空题', 3),
        ('CHEM-ORG-003', '烃的衍生物', '有机物官能团的性质', '选择题/有机推断题', 3),
        ('CHEM-ORG-005', '有机合成', '有机合成与推断', '有机推断题', 4),
        ('CHEM-THM-003', '盖斯定律', '反应热的计算', '选择题/填空题', 2),
        ('CHEM-MOL-002', '分子立体构型', '杂化轨道理论与VSEPR', '物质结构题', 3),
    ]
    
    ep_count = 0
    for kp_id, ep_name, desc, exam_type, difficulty in exam_points:
        if kp_id in kp_id_map:
            ep_id = f"EP-CHEM-{ep_count+1:03d}"
            cursor.execute('''
                INSERT OR IGNORE INTO exam_points 
                (ep_id, kp_id, ep_name, description, exam_type, difficulty_level)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (ep_id, kp_id_map[kp_id], ep_name, desc, exam_type, difficulty))
            ep_count += 1
    
    conn.commit()
    conn.close()
    print(f"✅ 化学：{ep_count} 个考点")


if __name__ == '__main__':
    build_chemistry_knowledge_graph()
