#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
物理学科知识点体系构建
基于《普通高中物理课程标准》和人教版教材
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '../../database/gaokao.db')


def build_physics_knowledge_graph():
    """构建物理学科知识图谱"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM subjects WHERE subject_code = 'physics'")
    subject_id = cursor.fetchone()[0]
    
    semesters = [
        {'code': 'compulsory_1', 'name': '必修第一册', 'grade': '高一', 'sort': 1},
        {'code': 'compulsory_2', 'name': '必修第二册', 'grade': '高一', 'sort': 2},
        {'code': 'compulsory_3', 'name': '必修第三册', 'grade': '高二', 'sort': 3},
        {'code': 'selective_1', 'name': '选择性必修第一册', 'grade': '高二', 'sort': 4},
        {'code': 'selective_2', 'name': '选择性必修第二册', 'grade': '高二', 'sort': 5},
        {'code': 'selective_3', 'name': '选择性必修第三册', 'grade': '高三', 'sort': 6},
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
        # 必修一：运动的描述、匀变速直线运动、相互作用、牛顿运动定律
        {
            'semester': 'compulsory_1', 'code': 'PHY-KINEMATICS', 'name': '运动的描述', 
            'number': '第一章', 'sort': 1,
            'kps': [
                {'id': 'PHY-KIN-001', 'name': '质点 参考系', 'level': 1, 'parent': None,
                 'desc': '质点、参考系的概念', 'importance': 2, 'difficulty': 1},
                {'id': 'PHY-KIN-002', 'name': '时间 位移', 'level': 1, 'parent': None,
                 'desc': '时间、位移、路程', 'importance': 3, 'difficulty': 1},
                {'id': 'PHY-KIN-003', 'name': '速度', 'level': 1, 'parent': None,
                 'desc': '速度、平均速度、瞬时速度', 'importance': 3, 'difficulty': 2},
                {'id': 'PHY-KIN-004', 'name': '加速度', 'level': 1, 'parent': None,
                 'desc': '加速度的概念与计算', 'importance': 4, 'difficulty': 2},
            ]
        },
        {
            'semester': 'compulsory_1', 'code': 'PHY-UNIFORM', 'name': '匀变速直线运动的研究', 
            'number': '第二章', 'sort': 2,
            'kps': [
                {'id': 'PHY-UNI-001', 'name': '匀变速直线运动的速度与时间的关系', 'level': 1, 'parent': None,
                 'desc': 'v = v0 + at', 'importance': 4, 'difficulty': 2},
                {'id': 'PHY-UNI-002', 'name': '匀变速直线运动的位移与时间的关系', 'level': 1, 'parent': None,
                 'desc': 'x = v0t + ½at²', 'importance': 4, 'difficulty': 2},
                {'id': 'PHY-UNI-003', 'name': '匀变速直线运动的速度与位移的关系', 'level': 1, 'parent': None,
                 'desc': 'v² - v0² = 2ax', 'importance': 4, 'difficulty': 2},
                {'id': 'PHY-UNI-004', 'name': '自由落体运动', 'level': 1, 'parent': 'PHY-UNI-001',
                 'desc': '自由落体运动的规律', 'importance': 3, 'difficulty': 2},
            ]
        },
        {
            'semester': 'compulsory_1', 'code': 'PHY-FORCE', 'name': '相互作用——力', 
            'number': '第三章', 'sort': 3,
            'kps': [
                {'id': 'PHY-FOR-001', 'name': '重力与弹力', 'level': 1, 'parent': None,
                 'desc': '重力、弹力、胡克定律', 'importance': 3, 'difficulty': 2},
                {'id': 'PHY-FOR-002', 'name': '摩擦力', 'level': 1, 'parent': None,
                 'desc': '静摩擦力、滑动摩擦力', 'importance': 4, 'difficulty': 3},
                {'id': 'PHY-FOR-003', 'name': '牛顿第三定律', 'level': 1, 'parent': None,
                 'desc': '作用力与反作用力', 'importance': 3, 'difficulty': 1},
                {'id': 'PHY-FOR-004', 'name': '力的合成与分解', 'level': 1, 'parent': None,
                 'desc': '平行四边形定则、正交分解', 'importance': 4, 'difficulty': 3},
                {'id': 'PHY-FOR-005', 'name': '共点力的平衡', 'level': 1, 'parent': None,
                 'desc': '共点力平衡条件及应用', 'importance': 4, 'difficulty': 3},
            ]
        },
        {
            'semester': 'compulsory_1', 'code': 'PHY-NEWTON', 'name': '运动和力的关系', 
            'number': '第四章', 'sort': 4,
            'kps': [
                {'id': 'PHY-NEW-001', 'name': '牛顿第一定律', 'level': 1, 'parent': None,
                 'desc': '惯性定律', 'importance': 2, 'difficulty': 1},
                {'id': 'PHY-NEW-002', 'name': '牛顿第二定律', 'level': 1, 'parent': None,
                 'desc': 'F = ma', 'importance': 4, 'difficulty': 3},
                {'id': 'PHY-NEW-003', 'name': '牛顿运动定律的应用', 'level': 1, 'parent': None,
                 'desc': '动力学两类基本问题', 'importance': 4, 'difficulty': 4},
                {'id': 'PHY-NEW-004', 'name': '超重和失重', 'level': 1, 'parent': 'PHY-NEW-002',
                 'desc': '超重、失重的概念与判断', 'importance': 3, 'difficulty': 2},
            ]
        },
        # 必修二：曲线运动、万有引力、机械能
        {
            'semester': 'compulsory_2', 'code': 'PHY-CURVE', 'name': '曲线运动', 
            'number': '第五章', 'sort': 5,
            'kps': [
                {'id': 'PHY-CUR-001', 'name': '曲线运动', 'level': 1, 'parent': None,
                 'desc': '曲线运动的条件、速度方向', 'importance': 2, 'difficulty': 1},
                {'id': 'PHY-CUR-002', 'name': '运动的合成与分解', 'level': 1, 'parent': None,
                 'desc': '运动的合成与分解、小船渡河', 'importance': 3, 'difficulty': 3},
                {'id': 'PHY-CUR-003', 'name': '平抛运动', 'level': 1, 'parent': 'PHY-CUR-002',
                 'desc': '平抛运动的规律', 'importance': 4, 'difficulty': 3},
                {'id': 'PHY-CUR-004', 'name': '圆周运动', 'level': 1, 'parent': None,
                 'desc': '线速度、角速度、周期、向心加速度', 'importance': 4, 'difficulty': 3},
                {'id': 'PHY-CUR-005', 'name': '向心力', 'level': 1, 'parent': 'PHY-CUR-004',
                 'desc': '向心力公式与应用', 'importance': 4, 'difficulty': 3},
            ]
        },
        {
            'semester': 'compulsory_2', 'code': 'PHY-GRAVITY', 'name': '万有引力与宇宙航行', 
            'number': '第六章', 'sort': 6,
            'kps': [
                {'id': 'PHY-GRA-001', 'name': '行星的运动', 'level': 1, 'parent': None,
                 'desc': '开普勒行星运动定律', 'importance': 2, 'difficulty': 2},
                {'id': 'PHY-GRA-002', 'name': '万有引力定律', 'level': 1, 'parent': 'PHY-GRA-001',
                 'desc': '万有引力定律的内容与应用', 'importance': 4, 'difficulty': 3},
                {'id': 'PHY-GRA-003', 'name': '万有引力理论的成就', 'level': 1, 'parent': 'PHY-GRA-002',
                 'desc': '天体质量计算、天体运动', 'importance': 4, 'difficulty': 3},
                {'id': 'PHY-GRA-004', 'name': '宇宙航行', 'level': 1, 'parent': 'PHY-GRA-002',
                 'desc': '第一宇宙速度、卫星运动', 'importance': 4, 'difficulty': 3},
            ]
        },
        {
            'semester': 'compulsory_2', 'code': 'PHY-ENERGY', 'name': '机械能守恒定律', 
            'number': '第七章', 'sort': 7,
            'kps': [
                {'id': 'PHY-ENG-001', 'name': '功和功率', 'level': 1, 'parent': None,
                 'desc': '功、功率的计算', 'importance': 4, 'difficulty': 2},
                {'id': 'PHY-ENG-002', 'name': '重力势能', 'level': 1, 'parent': None,
                 'desc': '重力势能、重力做功与重力势能变化的关系', 'importance': 3, 'difficulty': 2},
                {'id': 'PHY-ENG-003', 'name': '动能和动能定理', 'level': 1, 'parent': None,
                 'desc': '动能定理及其应用', 'importance': 4, 'difficulty': 3},
                {'id': 'PHY-ENG-004', 'name': '机械能守恒定律', 'level': 1, 'parent': None,
                 'desc': '机械能守恒定律及其应用', 'importance': 4, 'difficulty': 3},
                {'id': 'PHY-ENG-005', 'name': '功能关系 能量守恒', 'level': 1, 'parent': None,
                 'desc': '功能关系、能量守恒定律', 'importance': 4, 'difficulty': 3},
            ]
        },
        # 必修三：静电场、恒定电流、磁场
        {
            'semester': 'compulsory_3', 'code': 'PHY-ELEC', 'name': '静电场', 
            'number': '第九章', 'sort': 8,
            'kps': [
                {'id': 'PHY-ELE-001', 'name': '电荷 库仑定律', 'level': 1, 'parent': None,
                 'desc': '电荷守恒、库仑定律', 'importance': 3, 'difficulty': 2},
                {'id': 'PHY-ELE-002', 'name': '电场 电场强度', 'level': 1, 'parent': None,
                 'desc': '电场强度、电场线', 'importance': 4, 'difficulty': 3},
                {'id': 'PHY-ELE-003', 'name': '电势能和电势', 'level': 1, 'parent': None,
                 'desc': '电势能、电势、等势面', 'importance': 4, 'difficulty': 3},
                {'id': 'PHY-ELE-004', 'name': '电势差', 'level': 1, 'parent': 'PHY-ELE-003',
                 'desc': '电势差与电场强度的关系', 'importance': 4, 'difficulty': 3},
                {'id': 'PHY-ELE-005', 'name': '电容器的电容', 'level': 1, 'parent': None,
                 'desc': '电容器、电容的定义', 'importance': 3, 'difficulty': 2},
                {'id': 'PHY-ELE-006', 'name': '带电粒子在电场中的运动', 'level': 1, 'parent': None,
                 'desc': '带电粒子的加速和偏转', 'importance': 4, 'difficulty': 4},
            ]
        },
        {
            'semester': 'compulsory_3', 'code': 'PHY-CIRCUIT', 'name': '电路及其应用', 
            'number': '第十一章', 'sort': 9,
            'kps': [
                {'id': 'PHY-CIR-001', 'name': '电流 电压', 'level': 1, 'parent': None,
                 'desc': '电流、电压的概念', 'importance': 2, 'difficulty': 1},
                {'id': 'PHY-CIR-002', 'name': '电阻 电阻定律', 'level': 1, 'parent': None,
                 'desc': '电阻定律、电阻率', 'importance': 3, 'difficulty': 2},
                {'id': 'PHY-CIR-003', 'name': '串并联电路', 'level': 1, 'parent': None,
                 'desc': '串并联电路的特点', 'importance': 4, 'difficulty': 2},
                {'id': 'PHY-CIR-004', 'name': '闭合电路欧姆定律', 'level': 1, 'parent': None,
                 'desc': '闭合电路欧姆定律、路端电压', 'importance': 4, 'difficulty': 3},
            ]
        },
        {
            'semester': 'compulsory_3', 'code': 'PHY-MAG', 'name': '磁场 电磁感应初步', 
            'number': '第十三章', 'sort': 10,
            'kps': [
                {'id': 'PHY-MAG-001', 'name': '磁场 磁感应强度', 'level': 1, 'parent': None,
                 'desc': '磁场、磁感应强度、磁感线', 'importance': 3, 'difficulty': 2},
                {'id': 'PHY-MAG-002', 'name': '安培力', 'level': 1, 'parent': 'PHY-MAG-001',
                 'desc': '安培力的大小与方向', 'importance': 4, 'difficulty': 3},
                {'id': 'PHY-MAG-003', 'name': '洛伦兹力', 'level': 1, 'parent': 'PHY-MAG-001',
                 'desc': '洛伦兹力的大小与方向', 'importance': 4, 'difficulty': 3},
                {'id': 'PHY-MAG-004', 'name': '带电粒子在匀强磁场中的运动', 'level': 1, 'parent': 'PHY-MAG-003',
                 'desc': '匀速圆周运动、半径和周期', 'importance': 4, 'difficulty': 4},
            ]
        },
        # 选择性必修一：动量、机械振动、机械波
        {
            'semester': 'selective_1', 'code': 'PHY-MOMENTUM', 'name': '动量守恒定律', 
            'number': '第一章', 'sort': 11,
            'kps': [
                {'id': 'PHY-MOM-001', 'name': '动量和动量定理', 'level': 1, 'parent': None,
                 'desc': '动量、冲量、动量定理', 'importance': 4, 'difficulty': 3},
                {'id': 'PHY-MOM-002', 'name': '动量守恒定律', 'level': 1, 'parent': None,
                 'desc': '动量守恒定律及其应用', 'importance': 4, 'difficulty': 4},
                {'id': 'PHY-MOM-003', 'name': '碰撞', 'level': 1, 'parent': 'PHY-MOM-002',
                 'desc': '弹性碰撞、非弹性碰撞', 'importance': 4, 'difficulty': 4},
                {'id': 'PHY-MOM-004', 'name': '反冲运动 火箭', 'level': 1, 'parent': 'PHY-MOM-002',
                 'desc': '反冲运动的原理', 'importance': 2, 'difficulty': 2},
            ]
        },
        {
            'semester': 'selective_1', 'code': 'PHY-OSC', 'name': '机械振动', 
            'number': '第二章', 'sort': 12,
            'kps': [
                {'id': 'PHY-OSC-001', 'name': '简谐运动', 'level': 1, 'parent': None,
                 'desc': '简谐运动的特征、回复力', 'importance': 3, 'difficulty': 2},
                {'id': 'PHY-OSC-002', 'name': '简谐运动的描述', 'level': 1, 'parent': 'PHY-OSC-001',
                 'desc': '振幅、周期、频率、相位', 'importance': 3, 'difficulty': 2},
                {'id': 'PHY-OSC-003', 'name': '单摆', 'level': 1, 'parent': 'PHY-OSC-001',
                 'desc': '单摆的周期公式', 'importance': 3, 'difficulty': 2},
                {'id': 'PHY-OSC-004', 'name': '受迫振动 共振', 'level': 1, 'parent': None,
                 'desc': '受迫振动、共振现象', 'importance': 2, 'difficulty': 2},
            ]
        },
        {
            'semester': 'selective_1', 'code': 'PHY-WAVE', 'name': '机械波', 
            'number': '第三章', 'sort': 13,
            'kps': [
                {'id': 'PHY-WAV-001', 'name': '波的形成', 'level': 1, 'parent': None,
                 'desc': '机械波的形成和传播', 'importance': 2, 'difficulty': 2},
                {'id': 'PHY-WAV-002', 'name': '波的描述', 'level': 1, 'parent': 'PHY-WAV-001',
                 'desc': '波长、频率、波速', 'importance': 4, 'difficulty': 2},
                {'id': 'PHY-WAV-003', 'name': '波的干涉和衍射', 'level': 1, 'parent': None,
                 'desc': '波的叠加、干涉、衍射', 'importance': 3, 'difficulty': 3},
                {'id': 'PHY-WAV-004', 'name': '多普勒效应', 'level': 1, 'parent': None,
                 'desc': '多普勒效应的原理', 'importance': 2, 'difficulty': 2},
            ]
        },
        # 选择性必修二：电磁感应、交变电流、传感器
        {
            'semester': 'selective_2', 'code': 'PHY-EMI', 'name': '电磁感应', 
            'number': '第二章', 'sort': 14,
            'kps': [
                {'id': 'PHY-EMI-001', 'name': '楞次定律', 'level': 1, 'parent': None,
                 'desc': '楞次定律及其应用', 'importance': 4, 'difficulty': 3},
                {'id': 'PHY-EMI-002', 'name': '法拉第电磁感应定律', 'level': 1, 'parent': None,
                 'desc': '感应电动势的大小', 'importance': 4, 'difficulty': 3},
                {'id': 'PHY-EMI-003', 'name': '涡流、电磁阻尼和电磁驱动', 'level': 1, 'parent': None,
                 'desc': '涡流现象及其应用', 'importance': 2, 'difficulty': 2},
            ]
        },
        {
            'semester': 'selective_2', 'code': 'PHY-AC', 'name': '交变电流', 
            'number': '第三章', 'sort': 15,
            'kps': [
                {'id': 'PHY-AC-001', 'name': '交变电流', 'level': 1, 'parent': None,
                 'desc': '交变电流的产生、变化规律', 'importance': 3, 'difficulty': 2},
                {'id': 'PHY-AC-002', 'name': '描述交变电流的物理量', 'level': 1, 'parent': 'PHY-AC-001',
                 'desc': '周期、频率、峰值、有效值', 'importance': 4, 'difficulty': 2},
                {'id': 'PHY-AC-003', 'name': '变压器', 'level': 1, 'parent': None,
                 'desc': '变压器的工作原理、电压比', 'importance': 4, 'difficulty': 3},
                {'id': 'PHY-AC-004', 'name': '远距离输电', 'level': 1, 'parent': 'PHY-AC-003',
                 'desc': '远距离输电的功率损耗', 'importance': 3, 'difficulty': 3},
            ]
        },
        # 选择性必修三：热学、光学、原子物理
        {
            'semester': 'selective_3', 'code': 'PHY-THERMO', 'name': '热学', 
            'number': '第一章', 'sort': 16,
            'kps': [
                {'id': 'PHY-THR-001', 'name': '分子动理论', 'level': 1, 'parent': None,
                 'desc': '分子动理论的基本观点', 'importance': 3, 'difficulty': 2},
                {'id': 'PHY-THR-002', 'name': '气体实验定律', 'level': 1, 'parent': None,
                 'desc': '玻意耳定律、查理定律、盖-吕萨克定律', 'importance': 4, 'difficulty': 3},
                {'id': 'PHY-THR-003', 'name': '理想气体状态方程', 'level': 1, 'parent': 'PHY-THR-002',
                 'desc': '理想气体状态方程', 'importance': 4, 'difficulty': 3},
                {'id': 'PHY-THR-004', 'name': '热力学定律', 'level': 1, 'parent': None,
                 'desc': '热力学第一定律、第二定律', 'importance': 4, 'difficulty': 3},
            ]
        },
        {
            'semester': 'selective_3', 'code': 'PHY-OPTICS', 'name': '光学', 
            'number': '第四章', 'sort': 17,
            'kps': [
                {'id': 'PHY-OPT-001', 'name': '光的折射', 'level': 1, 'parent': None,
                 'desc': '折射定律、折射率', 'importance': 4, 'difficulty': 2},
                {'id': 'PHY-OPT-002', 'name': '全反射', 'level': 1, 'parent': 'PHY-OPT-001',
                 'desc': '全反射、临界角', 'importance': 3, 'difficulty': 3},
                {'id': 'PHY-OPT-003', 'name': '光的干涉', 'level': 1, 'parent': None,
                 'desc': '双缝干涉、薄膜干涉', 'importance': 3, 'difficulty': 3},
                {'id': 'PHY-OPT-004', 'name': '光的衍射和偏振', 'level': 1, 'parent': None,
                 'desc': '光的衍射、偏振现象', 'importance': 2, 'difficulty': 2},
            ]
        },
        {
            'semester': 'selective_3', 'code': 'PHY-ATOMIC', 'name': '原子物理', 
            'number': '第五章', 'sort': 18,
            'kps': [
                {'id': 'PHY-ATOM-001', 'name': '原子结构', 'level': 1, 'parent': None,
                 'desc': 'α粒子散射实验、玻尔模型', 'importance': 2, 'difficulty': 2},
                {'id': 'PHY-ATOM-002', 'name': '原子核', 'level': 1, 'parent': None,
                 'desc': '原子核的组成、放射性', 'importance': 2, 'difficulty': 2},
                {'id': 'PHY-ATOM-003', 'name': '核反应', 'level': 1, 'parent': 'PHY-ATOM-002',
                 'desc': '裂变、聚变、质能方程', 'importance': 3, 'difficulty': 2},
                {'id': 'PHY-ATOM-004', 'name': '波粒二象性', 'level': 1, 'parent': None,
                 'desc': '光电效应、光子说、物质波', 'importance': 3, 'difficulty': 3},
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
    
    print(f"✅ 物理：{total_kp} 个知识点")
    
    # 考点
    exam_points = [
        ('PHY-NEW-002', '牛顿第二定律', '牛顿第二定律的应用', '选择题/计算题', 3),
        ('PHY-CUR-003', '平抛运动', '平抛运动的规律', '选择题/实验题', 3),
        ('PHY-CUR-005', '圆周运动向心力', '圆周运动的向心力分析', '选择题/计算题', 3),
        ('PHY-GRA-002', '万有引力定律', '万有引力定律的应用', '选择题', 3),
        ('PHY-ENG-003', '动能定理', '动能定理的应用', '计算题', 4),
        ('PHY-ENG-004', '机械能守恒定律', '机械能守恒定律的应用', '选择题/计算题', 3),
        ('PHY-MOM-002', '动量守恒定律', '动量守恒定律的应用', '计算题', 4),
        ('PHY-ELE-002', '电场强度', '电场强度的计算', '选择题', 3),
        ('PHY-ELE-006', '带电粒子在电场中的运动', '带电粒子的加速和偏转', '计算题', 4),
        ('PHY-CIR-004', '闭合电路欧姆定律', '电路的动态分析', '选择题/实验题', 3),
        ('PHY-MAG-004', '带电粒子在磁场中的运动', '带电粒子在匀强磁场中的圆周运动', '计算题', 4),
        ('PHY-EMI-002', '法拉第电磁感应定律', '电磁感应的综合应用', '计算题', 4),
        ('PHY-THR-003', '理想气体状态方程', '气体实验定律的应用', '选择题/计算题', 3),
        ('PHY-OPT-001', '光的折射', '折射定律的应用', '选择题/计算题', 2),
    ]
    
    ep_count = 0
    for kp_id, ep_name, desc, exam_type, difficulty in exam_points:
        if kp_id in kp_id_map:
            ep_id = f"EP-PHY-{ep_count+1:03d}"
            cursor.execute('''
                INSERT OR IGNORE INTO exam_points 
                (ep_id, kp_id, ep_name, description, exam_type, difficulty_level)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (ep_id, kp_id_map[kp_id], ep_name, desc, exam_type, difficulty))
            ep_count += 1
    
    conn.commit()
    conn.close()
    print(f"✅ 物理：{ep_count} 个考点")


if __name__ == '__main__':
    build_physics_knowledge_graph()
