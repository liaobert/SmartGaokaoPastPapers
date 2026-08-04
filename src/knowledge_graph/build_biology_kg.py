#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生物学科知识点体系构建
基于《普通高中生物课程标准》和人教版教材
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '../../database/gaokao.db')


def build_biology_knowledge_graph():
    """构建生物学科知识图谱"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM subjects WHERE subject_code = 'biology'")
    subject_id = cursor.fetchone()[0]
    
    semesters = [
        {'code': 'compulsory_1', 'name': '必修1 分子与细胞', 'grade': '高一', 'sort': 1},
        {'code': 'compulsory_2', 'name': '必修2 遗传与进化', 'grade': '高一', 'sort': 2},
        {'code': 'selective_1', 'name': '选择性必修1 稳态与调节', 'grade': '高二', 'sort': 3},
        {'code': 'selective_2', 'name': '选择性必修2 生物与环境', 'grade': '高二', 'sort': 4},
        {'code': 'selective_3', 'name': '选择性必修3 生物技术与工程', 'grade': '高二', 'sort': 5},
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
        # 必修一：分子与细胞
        {
            'semester': 'compulsory_1', 'code': 'BIO-CELL', 'name': '走近细胞', 
            'number': '第1章', 'sort': 1,
            'kps': [
                {'id': 'BIO-CEL-001', 'name': '细胞是生命活动的基本单位', 'level': 1, 'parent': None,
                 'desc': '细胞学说、生命系统的结构层次', 'importance': 2, 'difficulty': 1},
                {'id': 'BIO-CEL-002', 'name': '细胞的多样性和统一性', 'level': 1, 'parent': None,
                 'desc': '原核细胞与真核细胞、显微镜使用', 'importance': 3, 'difficulty': 2},
            ]
        },
        {
            'semester': 'compulsory_1', 'code': 'BIO-MOLECULE', 'name': '组成细胞的分子', 
            'number': '第2章', 'sort': 2,
            'kps': [
                {'id': 'BIO-MOL-001', 'name': '细胞中的元素和化合物', 'level': 1, 'parent': None,
                 'desc': '组成细胞的元素、化合物', 'importance': 2, 'difficulty': 1},
                {'id': 'BIO-MOL-002', 'name': '生命活动的主要承担者——蛋白质', 'level': 1, 'parent': None,
                 'desc': '蛋白质的结构与功能', 'importance': 4, 'difficulty': 2},
                {'id': 'BIO-MOL-003', 'name': '遗传信息的携带者——核酸', 'level': 1, 'parent': None,
                 'desc': '核酸的结构与功能', 'importance': 3, 'difficulty': 2},
                {'id': 'BIO-MOL-004', 'name': '糖类和脂质', 'level': 1, 'parent': None,
                 'desc': '糖类、脂质的种类与作用', 'importance': 3, 'difficulty': 2},
                {'id': 'BIO-MOL-005', 'name': '细胞中的无机物', 'level': 1, 'parent': None,
                 'desc': '水和无机盐的作用', 'importance': 2, 'difficulty': 1},
            ]
        },
        {
            'semester': 'compulsory_1', 'code': 'BIO-CELL-STRUCT', 'name': '细胞的基本结构', 
            'number': '第3章', 'sort': 3,
            'kps': [
                {'id': 'BIO-CST-001', 'name': '细胞膜——系统的边界', 'level': 1, 'parent': None,
                 'desc': '细胞膜的结构与功能', 'importance': 4, 'difficulty': 2},
                {'id': 'BIO-CST-002', 'name': '细胞器——系统内的分工合作', 'level': 1, 'parent': None,
                 'desc': '各种细胞器的结构与功能', 'importance': 4, 'difficulty': 2},
                {'id': 'BIO-CST-003', 'name': '细胞核——系统的控制中心', 'level': 1, 'parent': None,
                 'desc': '细胞核的结构与功能', 'importance': 3, 'difficulty': 2},
            ]
        },
        {
            'semester': 'compulsory_1', 'code': 'BIO-TRANSPORT', 'name': '细胞的物质输入和输出', 
            'number': '第4章', 'sort': 4,
            'kps': [
                {'id': 'BIO-TRA-001', 'name': '物质跨膜运输的实例', 'level': 1, 'parent': None,
                 'desc': '渗透作用、质壁分离', 'importance': 3, 'difficulty': 2},
                {'id': 'BIO-TRA-002', 'name': '生物膜的流动镶嵌模型', 'level': 1, 'parent': None,
                 'desc': '生物膜的结构模型', 'importance': 3, 'difficulty': 2},
                {'id': 'BIO-TRA-003', 'name': '物质跨膜运输的方式', 'level': 1, 'parent': None,
                 'desc': '自由扩散、协助扩散、主动运输', 'importance': 4, 'difficulty': 2},
            ]
        },
        {
            'semester': 'compulsory_1', 'code': 'BIO-ENZYME', 'name': '细胞的能量供应和利用', 
            'number': '第5章', 'sort': 5,
            'kps': [
                {'id': 'BIO-ENZ-001', 'name': '降低化学反应活化能的酶', 'level': 1, 'parent': None,
                 'desc': '酶的作用、本质、特性', 'importance': 4, 'difficulty': 2},
                {'id': 'BIO-ENZ-002', 'name': '细胞的能量"通货"——ATP', 'level': 1, 'parent': None,
                 'desc': 'ATP的结构与功能', 'importance': 3, 'difficulty': 2},
                {'id': 'BIO-ENZ-003', 'name': 'ATP的主要来源——细胞呼吸', 'level': 1, 'parent': None,
                 'desc': '有氧呼吸、无氧呼吸的过程', 'importance': 4, 'difficulty': 3},
                {'id': 'BIO-ENZ-004', 'name': '能量之源——光与光合作用', 'level': 1, 'parent': None,
                 'desc': '光合作用的过程、影响因素', 'importance': 4, 'difficulty': 3},
            ]
        },
        {
            'semester': 'compulsory_1', 'code': 'BIO-CELL-CYCLE', 'name': '细胞的生命历程', 
            'number': '第6章', 'sort': 6,
            'kps': [
                {'id': 'BIO-CCL-001', 'name': '细胞的增殖', 'level': 1, 'parent': None,
                 'desc': '细胞周期、有丝分裂', 'importance': 4, 'difficulty': 3},
                {'id': 'BIO-CCL-002', 'name': '细胞的分化', 'level': 1, 'parent': None,
                 'desc': '细胞分化、细胞全能性', 'importance': 3, 'difficulty': 2},
                {'id': 'BIO-CCL-003', 'name': '细胞的衰老和凋亡', 'level': 1, 'parent': None,
                 'desc': '细胞衰老、细胞凋亡', 'importance': 2, 'difficulty': 2},
                {'id': 'BIO-CCL-004', 'name': '细胞的癌变', 'level': 1, 'parent': None,
                 'desc': '癌细胞的特征、致癌因子', 'importance': 2, 'difficulty': 1},
            ]
        },
        # 必修二：遗传与进化
        {
            'semester': 'compulsory_2', 'code': 'BIO-GENETICS', 'name': '遗传因子的发现', 
            'number': '第1章', 'sort': 7,
            'kps': [
                {'id': 'BIO-GEN-001', 'name': '孟德尔的豌豆杂交实验（一）', 'level': 1, 'parent': None,
                 'desc': '基因的分离定律', 'importance': 4, 'difficulty': 3},
                {'id': 'BIO-GEN-002', 'name': '孟德尔的豌豆杂交实验（二）', 'level': 1, 'parent': None,
                 'desc': '基因的自由组合定律', 'importance': 4, 'difficulty': 3},
            ]
        },
        {
            'semester': 'compulsory_2', 'code': 'BIO-MEIOSIS', 'name': '基因和染色体的关系', 
            'number': '第2章', 'sort': 8,
            'kps': [
                {'id': 'BIO-MEI-001', 'name': '减数分裂和受精作用', 'level': 1, 'parent': None,
                 'desc': '减数分裂的过程、受精作用', 'importance': 4, 'difficulty': 3},
                {'id': 'BIO-MEI-002', 'name': '基因在染色体上', 'level': 1, 'parent': None,
                 'desc': '萨顿假说、摩尔根实验', 'importance': 3, 'difficulty': 2},
                {'id': 'BIO-MEI-003', 'name': '伴性遗传', 'level': 1, 'parent': None,
                 'desc': '伴X遗传、伴Y遗传', 'importance': 4, 'difficulty': 3},
            ]
        },
        {
            'semester': 'compulsory_2', 'code': 'BIO-DNA', 'name': '基因的本质', 
            'number': '第3章', 'sort': 9,
            'kps': [
                {'id': 'BIO-DNA-001', 'name': 'DNA是主要的遗传物质', 'level': 1, 'parent': None,
                 'desc': '肺炎双球菌转化实验、噬菌体侵染细菌实验', 'importance': 4, 'difficulty': 2},
                {'id': 'BIO-DNA-002', 'name': 'DNA的结构', 'level': 1, 'parent': None,
                 'desc': 'DNA双螺旋结构', 'importance': 3, 'difficulty': 2},
                {'id': 'BIO-DNA-003', 'name': 'DNA的复制', 'level': 1, 'parent': 'BIO-DNA-002',
                 'desc': 'DNA半保留复制', 'importance': 4, 'difficulty': 2},
                {'id': 'BIO-DNA-004', 'name': '基因是有遗传效应的DNA片段', 'level': 1, 'parent': None,
                 'desc': '基因的概念、DNA的多样性', 'importance': 2, 'difficulty': 1},
            ]
        },
        {
            'semester': 'compulsory_2', 'code': 'BIO-GENE-EXP', 'name': '基因的表达', 
            'number': '第4章', 'sort': 10,
            'kps': [
                {'id': 'BIO-GEX-001', 'name': '基因指导蛋白质的合成', 'level': 1, 'parent': None,
                 'desc': '转录、翻译的过程', 'importance': 4, 'difficulty': 3},
                {'id': 'BIO-GEX-002', 'name': '基因对性状的控制', 'level': 1, 'parent': None,
                 'desc': '中心法则、基因控制性状的方式', 'importance': 3, 'difficulty': 2},
            ]
        },
        {
            'semester': 'compulsory_2', 'code': 'BIO-MUTATION', 'name': '基因突变及其他变异', 
            'number': '第5章', 'sort': 11,
            'kps': [
                {'id': 'BIO-MUT-001', 'name': '基因突变和基因重组', 'level': 1, 'parent': None,
                 'desc': '基因突变、基因重组', 'importance': 4, 'difficulty': 2},
                {'id': 'BIO-MUT-002', 'name': '染色体变异', 'level': 1, 'parent': None,
                 'desc': '染色体结构变异、数目变异', 'importance': 4, 'difficulty': 3},
                {'id': 'BIO-MUT-003', 'name': '人类遗传病', 'level': 1, 'parent': None,
                 'desc': '遗传病的类型、监测与预防', 'importance': 3, 'difficulty': 2},
            ]
        },
        {
            'semester': 'compulsory_2', 'code': 'BIO-EVOLUTION', 'name': '生物的进化', 
            'number': '第6章', 'sort': 12,
            'kps': [
                {'id': 'BIO-EVO-001', 'name': '现代生物进化理论的由来', 'level': 1, 'parent': None,
                 'desc': '拉马克进化学说、达尔文自然选择学说', 'importance': 2, 'difficulty': 1},
                {'id': 'BIO-EVO-002', 'name': '现代生物进化理论的主要内容', 'level': 1, 'parent': None,
                 'desc': '种群基因频率、物种形成', 'importance': 4, 'difficulty': 3},
            ]
        },
        # 选择性必修一：稳态与调节
        {
            'semester': 'selective_1', 'code': 'BIO-HOMEO', 'name': '人体的内环境与稳态', 
            'number': '第1章', 'sort': 13,
            'kps': [
                {'id': 'BIO-HOM-001', 'name': '细胞生活的环境', 'level': 1, 'parent': None,
                 'desc': '内环境的组成与理化性质', 'importance': 3, 'difficulty': 2},
                {'id': 'BIO-HOM-002', 'name': '内环境稳态的重要性', 'level': 1, 'parent': None,
                 'desc': '稳态的概念、调节机制', 'importance': 3, 'difficulty': 2},
            ]
        },
        {
            'semester': 'selective_1', 'code': 'BIO-NERVE', 'name': '动物和人体生命活动的调节', 
            'number': '第2章', 'sort': 14,
            'kps': [
                {'id': 'BIO-NER-001', 'name': '通过神经系统的调节', 'level': 1, 'parent': None,
                 'desc': '神经调节的结构基础、反射弧、兴奋传导', 'importance': 4, 'difficulty': 3},
                {'id': 'BIO-NER-002', 'name': '通过激素的调节', 'level': 1, 'parent': None,
                 'desc': '激素调节的特点、血糖调节、甲状腺激素分级调节', 'importance': 4, 'difficulty': 3},
                {'id': 'BIO-NER-003', 'name': '神经调节与体液调节的关系', 'level': 1, 'parent': None,
                 'desc': '体温调节、水盐调节', 'importance': 4, 'difficulty': 3},
                {'id': 'BIO-NER-004', 'name': '免疫调节', 'level': 1, 'parent': None,
                 'desc': '免疫系统的组成、特异性免疫', 'importance': 4, 'difficulty': 3},
            ]
        },
        {
            'semester': 'selective_1', 'code': 'BIO-PLANT', 'name': '植物的激素调节', 
            'number': '第3章', 'sort': 15,
            'kps': [
                {'id': 'BIO-PLA-001', 'name': '植物生长素的发现', 'level': 1, 'parent': None,
                 'desc': '生长素的发现过程', 'importance': 2, 'difficulty': 2},
                {'id': 'BIO-PLA-002', 'name': '生长素的生理作用', 'level': 1, 'parent': 'BIO-PLA-001',
                 'desc': '生长素的两重性、顶端优势', 'importance': 4, 'difficulty': 2},
                {'id': 'BIO-PLA-003', 'name': '其他植物激素', 'level': 1, 'parent': None,
                 'desc': '赤霉素、细胞分裂素、脱落酸、乙烯', 'importance': 3, 'difficulty': 2},
            ]
        },
        # 选择性必修二：生物与环境
        {
            'semester': 'selective_2', 'code': 'BIO-ECOLOGY', 'name': '种群和群落', 
            'number': '第4章', 'sort': 16,
            'kps': [
                {'id': 'BIO-ECO-001', 'name': '种群的特征', 'level': 1, 'parent': None,
                 'desc': '种群密度、出生率死亡率、年龄组成', 'importance': 3, 'difficulty': 2},
                {'id': 'BIO-ECO-002', 'name': '种群数量的变化', 'level': 1, 'parent': None,
                 'desc': 'J型曲线、S型曲线', 'importance': 4, 'difficulty': 3},
                {'id': 'BIO-ECO-003', 'name': '群落的结构', 'level': 1, 'parent': None,
                 'desc': '物种组成、种间关系、空间结构', 'importance': 4, 'difficulty': 2},
                {'id': 'BIO-ECO-004', 'name': '群落的演替', 'level': 1, 'parent': None,
                 'desc': '初生演替、次生演替', 'importance': 3, 'difficulty': 2},
            ]
        },
        {
            'semester': 'selective_2', 'code': 'BIO-ECOSYSTEM', 'name': '生态系统及其稳定性', 
            'number': '第5章', 'sort': 17,
            'kps': [
                {'id': 'BIO-ECOS-001', 'name': '生态系统的结构', 'level': 1, 'parent': None,
                 'desc': '生态系统的组成成分、营养结构', 'importance': 3, 'difficulty': 2},
                {'id': 'BIO-ECOS-002', 'name': '生态系统的能量流动', 'level': 1, 'parent': None,
                 'desc': '能量流动的过程、特点', 'importance': 4, 'difficulty': 3},
                {'id': 'BIO-ECOS-003', 'name': '生态系统的物质循环', 'level': 1, 'parent': None,
                 'desc': '碳循环、物质循环与能量流动的关系', 'importance': 4, 'difficulty': 3},
                {'id': 'BIO-ECOS-004', 'name': '生态系统的信息传递', 'level': 1, 'parent': None,
                 'desc': '信息的种类、作用', 'importance': 2, 'difficulty': 1},
                {'id': 'BIO-ECOS-005', 'name': '生态系统的稳定性', 'level': 1, 'parent': None,
                 'desc': '抵抗力稳定性、恢复力稳定性', 'importance': 3, 'difficulty': 2},
            ]
        },
        # 选择性必修三：生物技术与工程
        {
            'semester': 'selective_3', 'code': 'BIO-BIOTECH', 'name': '生物技术与工程', 
            'number': '全书', 'sort': 18,
            'kps': [
                {'id': 'BIO-BIO-001', 'name': '发酵工程', 'level': 1, 'parent': None,
                 'desc': '微生物的培养、发酵工程', 'importance': 3, 'difficulty': 2},
                {'id': 'BIO-BIO-002', 'name': '基因工程', 'level': 1, 'parent': None,
                 'desc': '基因工程的工具、操作步骤', 'importance': 4, 'difficulty': 3},
                {'id': 'BIO-BIO-003', 'name': '细胞工程', 'level': 1, 'parent': None,
                 'desc': '植物细胞工程、动物细胞工程', 'importance': 4, 'difficulty': 3},
                {'id': 'BIO-BIO-004', 'name': '胚胎工程', 'level': 1, 'parent': None,
                 'desc': '胚胎工程的技术', 'importance': 3, 'difficulty': 3},
                {'id': 'BIO-BIO-005', 'name': '生物技术的安全性与伦理问题', 'level': 1, 'parent': None,
                 'desc': '转基因生物安全、生物武器', 'importance': 2, 'difficulty': 1},
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
    
    print(f"✅ 生物：{total_kp} 个知识点")
    
    # 考点
    exam_points = [
        ('BIO-MOL-002', '蛋白质的结构与功能', '蛋白质的结构多样性与功能', '选择题', 2),
        ('BIO-CST-002', '细胞器的结构与功能', '各种细胞器的分工合作', '选择题', 2),
        ('BIO-ENZ-004', '光合作用', '光合作用的过程与影响因素', '选择题/填空题', 3),
        ('BIO-ENZ-003', '细胞呼吸', '有氧呼吸与无氧呼吸的过程', '选择题/填空题', 3),
        ('BIO-CCL-001', '细胞增殖', '有丝分裂的过程', '选择题', 3),
        ('BIO-GEN-001', '基因的分离定律', '分离定律的应用', '选择题/遗传题', 3),
        ('BIO-GEN-002', '基因的自由组合定律', '自由组合定律的应用', '选择题/遗传题', 4),
        ('BIO-MEI-003', '伴性遗传', '伴性遗传的特点与应用', '选择题/遗传题', 3),
        ('BIO-DNA-003', 'DNA的复制', 'DNA半保留复制的计算', '选择题', 2),
        ('BIO-GEX-001', '基因的表达', '转录和翻译的过程', '选择题/填空题', 3),
        ('BIO-MUT-002', '染色体变异', '染色体数目变异与育种', '选择题', 3),
        ('BIO-NER-001', '神经调节', '兴奋在神经纤维上的传导和在突触间的传递', '选择题/填空题', 3),
        ('BIO-NER-004', '免疫调节', '特异性免疫的过程', '选择题/填空题', 3),
        ('BIO-ECOS-002', '生态系统的能量流动', '能量流动的计算', '选择题/填空题', 3),
        ('BIO-BIO-002', '基因工程', '基因工程的工具与操作', '选考题', 3),
    ]
    
    ep_count = 0
    for kp_id, ep_name, desc, exam_type, difficulty in exam_points:
        if kp_id in kp_id_map:
            ep_id = f"EP-BIO-{ep_count+1:03d}"
            cursor.execute('''
                INSERT OR IGNORE INTO exam_points 
                (ep_id, kp_id, ep_name, description, exam_type, difficulty_level)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (ep_id, kp_id_map[kp_id], ep_name, desc, exam_type, difficulty))
            ep_count += 1
    
    conn.commit()
    conn.close()
    print(f"✅ 生物：{ep_count} 个考点")


if __name__ == '__main__':
    build_biology_knowledge_graph()
