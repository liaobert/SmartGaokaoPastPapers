#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
地理学科知识点体系构建
基于《普通高中地理课程标准》和人教版教材
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '../../database/gaokao.db')


def build_geography_knowledge_graph():
    """构建地理学科知识图谱"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM subjects WHERE subject_code = 'geography'")
    subject_id = cursor.fetchone()[0]
    
    semesters = [
        {'code': 'compulsory_1', 'name': '必修第一册', 'grade': '高一', 'sort': 1},
        {'code': 'compulsory_2', 'name': '必修第二册', 'grade': '高一', 'sort': 2},
        {'code': 'selective_1', 'name': '选择性必修1 自然地理基础', 'grade': '高二', 'sort': 3},
        {'code': 'selective_2', 'name': '选择性必修2 区域发展', 'grade': '高二', 'sort': 4},
        {'code': 'selective_3', 'name': '选择性必修3 资源、环境与国家安全', 'grade': '高二', 'sort': 5},
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
        # 必修一：自然地理
        {
            'semester': 'compulsory_1', 'code': 'GEO-PHYSICAL', 'name': '自然地理', 
            'number': '全书', 'sort': 1,
            'kps': [
                {'id': 'GEO-PHY-001', 'name': '宇宙中的地球', 'level': 1, 'parent': None,
                 'desc': '地球的宇宙环境、太阳对地球的影响、地球的历史、地球的圈层结构', 'importance': 3, 'difficulty': 2},
                {'id': 'GEO-PHY-002', 'name': '地球上的大气', 'level': 1, 'parent': None,
                 'desc': '大气的组成与垂直分层、大气受热过程、大气运动、常见天气系统', 'importance': 4, 'difficulty': 3},
                {'id': 'GEO-PHY-003', 'name': '地球上的水', 'level': 1, 'parent': None,
                 'desc': '水循环、海水的性质、海水的运动', 'importance': 4, 'difficulty': 3},
                {'id': 'GEO-PHY-004', 'name': '地貌', 'level': 1, 'parent': None,
                 'desc': '常见地貌类型、地貌的观察', 'importance': 3, 'difficulty': 2},
                {'id': 'GEO-PHY-005', 'name': '植被与土壤', 'level': 1, 'parent': None,
                 'desc': '植被、土壤', 'importance': 3, 'difficulty': 2},
                {'id': 'GEO-PHY-006', 'name': '自然灾害', 'level': 1, 'parent': None,
                 'desc': '气象灾害、地质灾害、防灾减灾、地理信息技术在防灾减灾中的应用', 'importance': 3, 'difficulty': 2},
                # 二级知识点
                {'id': 'GEO-PHY-101', 'name': '地球运动', 'level': 2, 'parent': 'GEO-PHY-001',
                 'desc': '地球自转、公转的地理意义', 'importance': 4, 'difficulty': 4},
                {'id': 'GEO-PHY-102', 'name': '大气环流', 'level': 2, 'parent': 'GEO-PHY-002',
                 'desc': '气压带风带、季风环流', 'importance': 4, 'difficulty': 3},
                {'id': 'GEO-PHY-103', 'name': '天气系统', 'level': 2, 'parent': 'GEO-PHY-002',
                 'desc': '锋面、气旋、反气旋', 'importance': 4, 'difficulty': 3},
                {'id': 'GEO-PHY-104', 'name': '洋流', 'level': 2, 'parent': 'GEO-PHY-003',
                 'desc': '世界洋流分布规律、洋流对地理环境的影响', 'importance': 4, 'difficulty': 3},
            ]
        },
        # 必修二：人文地理
        {
            'semester': 'compulsory_2', 'code': 'GEO-HUMAN', 'name': '人文地理', 
            'number': '全书', 'sort': 2,
            'kps': [
                {'id': 'GEO-HUM-001', 'name': '人口', 'level': 1, 'parent': None,
                 'desc': '人口分布、人口迁移、人口容量', 'importance': 3, 'difficulty': 2},
                {'id': 'GEO-HUM-002', 'name': '乡村与城镇', 'level': 1, 'parent': None,
                 'desc': '城乡空间结构、城镇化、地域文化与城乡景观', 'importance': 4, 'difficulty': 2},
                {'id': 'GEO-HUM-003', 'name': '产业区位因素', 'level': 1, 'parent': None,
                 'desc': '农业区位因素、工业区位因素、服务业区位因素', 'importance': 4, 'difficulty': 3},
                {'id': 'GEO-HUM-004', 'name': '交通运输布局与区域发展', 'level': 1, 'parent': None,
                 'desc': '区域发展对交通运输布局的影响、交通运输布局对区域发展的影响', 'importance': 3, 'difficulty': 2},
                {'id': 'GEO-HUM-005', 'name': '环境与发展', 'level': 1, 'parent': None,
                 'desc': '人类面临的主要环境问题、走向人地协调——可持续发展、中国国家发展战略', 'importance': 4, 'difficulty': 2},
                # 二级知识点
                {'id': 'GEO-HUM-101', 'name': '人口增长模式', 'level': 2, 'parent': 'GEO-HUM-001',
                 'desc': '人口增长模式的转变', 'importance': 3, 'difficulty': 2},
                {'id': 'GEO-HUM-102', 'name': '城市化', 'level': 2, 'parent': 'GEO-HUM-002',
                 'desc': '城市化的进程、城市化对地理环境的影响', 'importance': 4, 'difficulty': 2},
                {'id': 'GEO-HUM-103', 'name': '农业地域类型', 'level': 2, 'parent': 'GEO-HUM-003',
                 'desc': '主要农业地域类型', 'importance': 4, 'difficulty': 3},
                {'id': 'GEO-HUM-104', 'name': '工业地域', 'level': 2, 'parent': 'GEO-HUM-003',
                 'desc': '工业集聚与工业地域、传统工业区与新工业区', 'importance': 4, 'difficulty': 3},
            ]
        },
        # 选择性必修一：自然地理基础
        {
            'semester': 'selective_1', 'code': 'GEO-PHYSICAL-ADV', 'name': '自然地理基础', 
            'number': '全书', 'sort': 3,
            'kps': [
                {'id': 'GEO-PADV-001', 'name': '地球的运动', 'level': 1, 'parent': None,
                 'desc': '自转和公转、地球运动的地理意义', 'importance': 4, 'difficulty': 4},
                {'id': 'GEO-PADV-002', 'name': '岩石圈与地表形态', 'level': 1, 'parent': None,
                 'desc': '岩石圈的组成、内力作用与地表形态、外力作用与地表形态', 'importance': 4, 'difficulty': 3},
                {'id': 'GEO-PADV-003', 'name': '大气运动与天气气候', 'level': 1, 'parent': None,
                 'desc': '常见的天气系统、气压带和风带、气候的形成及其对自然地理景观的影响', 'importance': 4, 'difficulty': 4},
                {'id': 'GEO-PADV-004', 'name': '水体运动的影响', 'level': 1, 'parent': None,
                 'desc': '陆地水体及其相互关系、洋流及其影响、海—气相互作用', 'importance': 4, 'difficulty': 3},
                {'id': 'GEO-PADV-005', 'name': '自然环境的整体性与差异性', 'level': 1, 'parent': None,
                 'desc': '自然环境的整体性、自然环境的地域差异性', 'importance': 4, 'difficulty': 3},
            ]
        },
        # 选择性必修二：区域发展
        {
            'semester': 'selective_2', 'code': 'GEO-REGIONAL', 'name': '区域发展', 
            'number': '全书', 'sort': 4,
            'kps': [
                {'id': 'GEO-REG-001', 'name': '区域与区域发展', 'level': 1, 'parent': None,
                 'desc': '多种多样的区域、区域整体性和关联性、区域协调发展', 'importance': 4, 'difficulty': 2},
                {'id': 'GEO-REG-002', 'name': '资源、环境与区域发展', 'level': 1, 'parent': None,
                 'desc': '区域发展的自然环境基础、生态脆弱区的综合治理、资源枯竭型城市的转型发展', 'importance': 4, 'difficulty': 3},
                {'id': 'GEO-REG-003', 'name': '城市、产业与区域发展', 'level': 1, 'parent': None,
                 'desc': '城市的辐射功能、地区产业结构变化', 'importance': 4, 'difficulty': 3},
                {'id': 'GEO-REG-004', 'name': '区际联系与区域协调发展', 'level': 1, 'parent': None,
                 'desc': '流域内协调发展、资源跨区域调配、产业转移、国际合作', 'importance': 4, 'difficulty': 3},
            ]
        },
        # 选择性必修三：资源、环境与国家安全
        {
            'semester': 'selective_3', 'code': 'GEO-RESOURCE', 'name': '资源、环境与国家安全', 
            'number': '全书', 'sort': 5,
            'kps': [
                {'id': 'GEO-RES-001', 'name': '自然环境与人类社会', 'level': 1, 'parent': None,
                 'desc': '自然环境的服务功能、自然资源及其利用、环境问题及其危害', 'importance': 3, 'difficulty': 2},
                {'id': 'GEO-RES-002', 'name': '资源安全与国家安全', 'level': 1, 'parent': None,
                 'desc': '资源安全对国家安全的影响、中国的能源安全、中国的耕地资源与粮食安全、海洋空间资源开发与国家安全', 'importance': 4, 'difficulty': 3},
                {'id': 'GEO-RES-003', 'name': '环境安全与国家安全', 'level': 1, 'parent': None,
                 'desc': '环境安全对国家安全的影响、环境污染与国家安全、生态保护与国家安全、全球气候变化与国家安全', 'importance': 4, 'difficulty': 3},
                {'id': 'GEO-RES-004', 'name': '保障国家安全的资源、环境战略与行动', 'level': 1, 'parent': None,
                 'desc': '走向生态文明、国家战略与政策、国际合作', 'importance': 3, 'difficulty': 2},
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
    
    print(f"✅ 地理：{total_kp} 个知识点")
    
    # 考点
    exam_points = [
        ('GEO-PHY-101', '地球运动的地理意义', '自转和公转的地理意义', '选择题/综合题', 4),
        ('GEO-PHY-102', '大气环流', '气压带风带与气候', '选择题/综合题', 4),
        ('GEO-PHY-103', '天气系统', '锋面、气旋与天气', '选择题', 3),
        ('GEO-PHY-104', '洋流', '洋流分布及其影响', '选择题', 3),
        ('GEO-PADV-002', '地表形态的塑造', '内力作用与外力作用', '选择题/综合题', 3),
        ('GEO-PADV-005', '自然环境的整体性与差异性', '地理环境的地域分异规律', '选择题/综合题', 3),
        ('GEO-HUM-003', '产业区位因素', '农业、工业区位因素分析', '选择题/综合题', 4),
        ('GEO-HUM-002', '城镇化', '城市化进程与问题', '选择题/综合题', 3),
        ('GEO-REG-002', '资源环境与区域发展', '区域可持续发展', '综合题', 3),
        ('GEO-REG-004', '区际联系与区域协调发展', '产业转移、资源跨区域调配', '综合题', 3),
        ('GEO-RES-002', '资源安全', '能源安全、粮食安全', '选择题/综合题', 3),
        ('GEO-RES-003', '环境安全', '生态保护与国家安全', '选择题/综合题', 3),
    ]
    
    ep_count = 0
    for kp_id, ep_name, desc, exam_type, difficulty in exam_points:
        if kp_id in kp_id_map:
            ep_id = f"EP-GEO-{ep_count+1:03d}"
            cursor.execute('''
                INSERT OR IGNORE INTO exam_points 
                (ep_id, kp_id, ep_name, description, exam_type, difficulty_level)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (ep_id, kp_id_map[kp_id], ep_name, desc, exam_type, difficulty))
            ep_count += 1
    
    conn.commit()
    conn.close()
    print(f"✅ 地理：{ep_count} 个考点")


if __name__ == '__main__':
    build_geography_knowledge_graph()
