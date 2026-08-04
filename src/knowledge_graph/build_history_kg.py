#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
历史学科知识点体系构建
基于《普通高中历史课程标准》和人教版教材
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '../../database/gaokao.db')


def build_history_knowledge_graph():
    """构建历史学科知识图谱"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM subjects WHERE subject_code = 'history'")
    subject_id = cursor.fetchone()[0]
    
    semesters = [
        {'code': 'compulsory_1', 'name': '必修 中外历史纲要（上）', 'grade': '高一', 'sort': 1},
        {'code': 'compulsory_2', 'name': '必修 中外历史纲要（下）', 'grade': '高一', 'sort': 2},
        {'code': 'selective_1', 'name': '选择性必修1 国家制度与社会治理', 'grade': '高二', 'sort': 3},
        {'code': 'selective_2', 'name': '选择性必修2 经济与社会生活', 'grade': '高二', 'sort': 4},
        {'code': 'selective_3', 'name': '选择性必修3 文化交流与传播', 'grade': '高二', 'sort': 5},
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
        # 必修上：中国古代史、中国近现代史
        {
            'semester': 'compulsory_1', 'code': 'HIS-ANCIENT', 'name': '中国古代史', 
            'number': '第一编', 'sort': 1,
            'kps': [
                {'id': 'HIS-ANC-001', 'name': '从中华文明起源到秦汉统一多民族封建国家的建立与巩固', 'level': 1, 'parent': None,
                 'desc': '先秦时期、秦朝、汉朝', 'importance': 4, 'difficulty': 2},
                {'id': 'HIS-ANC-002', 'name': '三国两晋南北朝的民族交融与隋唐统一多民族封建国家的发展', 'level': 1, 'parent': None,
                 'desc': '三国两晋南北朝、隋唐', 'importance': 3, 'difficulty': 2},
                {'id': 'HIS-ANC-003', 'name': '辽宋夏金多民族政权的并立与元朝的统一', 'level': 1, 'parent': None,
                 'desc': '辽宋夏金元时期', 'importance': 4, 'difficulty': 2},
                {'id': 'HIS-ANC-004', 'name': '明清中国版图的奠定与面临的挑战', 'level': 1, 'parent': None,
                 'desc': '明朝、清朝（鸦片战争前）', 'importance': 4, 'difficulty': 3},
                # 二级知识点
                {'id': 'HIS-ANC-101', 'name': '中央集权制度的形成与发展', 'level': 2, 'parent': 'HIS-ANC-001',
                 'desc': '郡县制、三公九卿制、刺史制度', 'importance': 4, 'difficulty': 2},
                {'id': 'HIS-ANC-102', 'name': '科举制度', 'level': 2, 'parent': 'HIS-ANC-002',
                 'desc': '科举制的创立与发展', 'importance': 3, 'difficulty': 2},
                {'id': 'HIS-ANC-103', 'name': '经济重心南移', 'level': 2, 'parent': 'HIS-ANC-003',
                 'desc': '经济重心南移的过程与影响', 'importance': 3, 'difficulty': 2},
                {'id': 'HIS-ANC-104', 'name': '明清君主专制的加强', 'level': 2, 'parent': 'HIS-ANC-004',
                 'desc': '内阁、军机处', 'importance': 4, 'difficulty': 2},
            ]
        },
        {
            'semester': 'compulsory_1', 'code': 'HIS-MODERN', 'name': '中国近现代史', 
            'number': '第二编', 'sort': 2,
            'kps': [
                {'id': 'HIS-MOD-001', 'name': '晚清时期的内忧外患与救亡图存', 'level': 1, 'parent': None,
                 'desc': '鸦片战争、太平天国、洋务运动、甲午战争、戊戌变法', 'importance': 4, 'difficulty': 3},
                {'id': 'HIS-MOD-002', 'name': '辛亥革命与中华民国的建立', 'level': 1, 'parent': None,
                 'desc': '辛亥革命、北洋军阀统治', 'importance': 4, 'difficulty': 2},
                {'id': 'HIS-MOD-003', 'name': '中国共产党成立与新民主主义革命兴起', 'level': 1, 'parent': None,
                 'desc': '五四运动、中国共产党成立、国民革命、国共十年对峙', 'importance': 4, 'difficulty': 3},
                {'id': 'HIS-MOD-004', 'name': '中华民族的抗日战争和人民解放战争', 'level': 1, 'parent': None,
                 'desc': '抗日战争、解放战争', 'importance': 4, 'difficulty': 3},
                {'id': 'HIS-MOD-005', 'name': '中华人民共和国成立和社会主义革命与建设', 'level': 1, 'parent': None,
                 'desc': '新中国成立、社会主义改造、探索中的曲折', 'importance': 4, 'difficulty': 2},
                {'id': 'HIS-MOD-006', 'name': '改革开放和社会主义现代化建设新时期', 'level': 1, 'parent': None,
                 'desc': '改革开放、中国特色社会主义道路', 'importance': 4, 'difficulty': 2},
                # 二级知识点
                {'id': 'HIS-MOD-101', 'name': '近代中国经济结构的变动', 'level': 2, 'parent': 'HIS-MOD-001',
                 'desc': '自然经济解体、洋务运动、民族资本主义产生', 'importance': 4, 'difficulty': 3},
                {'id': 'HIS-MOD-102', 'name': '新民主主义革命的崛起', 'level': 2, 'parent': 'HIS-MOD-003',
                 'desc': '五四运动、中共一大、国民革命', 'importance': 4, 'difficulty': 2},
                {'id': 'HIS-MOD-103', 'name': '抗日战争的胜利', 'level': 2, 'parent': 'HIS-MOD-004',
                 'desc': '全民族抗战、抗战胜利的意义', 'importance': 4, 'difficulty': 2},
                {'id': 'HIS-MOD-104', 'name': '改革开放的进程', 'level': 2, 'parent': 'HIS-MOD-006',
                 'desc': '农村改革、城市改革、对外开放', 'importance': 4, 'difficulty': 2},
            ]
        },
        # 必修下：世界史
        {
            'semester': 'compulsory_2', 'code': 'HIS-WORLD', 'name': '世界史', 
            'number': '全书', 'sort': 3,
            'kps': [
                {'id': 'HIS-WLD-001', 'name': '古代文明的产生与发展', 'level': 1, 'parent': None,
                 'desc': '古代两河流域、埃及、印度、希腊、罗马', 'importance': 3, 'difficulty': 2},
                {'id': 'HIS-WLD-002', 'name': '中古时期的世界', 'level': 1, 'parent': None,
                 'desc': '中古欧洲、亚洲、非洲、美洲', 'importance': 2, 'difficulty': 2},
                {'id': 'HIS-WLD-003', 'name': '走向整体的世界', 'level': 1, 'parent': None,
                 'desc': '新航路开辟、早期殖民扩张', 'importance': 4, 'difficulty': 2},
                {'id': 'HIS-WLD-004', 'name': '资本主义制度的确立', 'level': 1, 'parent': None,
                 'desc': '文艺复兴、宗教改革、启蒙运动、资产阶级革命', 'importance': 4, 'difficulty': 3},
                {'id': 'HIS-WLD-005', 'name': '工业革命与马克思主义的诞生', 'level': 1, 'parent': None,
                 'desc': '工业革命、马克思主义诞生', 'importance': 4, 'difficulty': 3},
                {'id': 'HIS-WLD-006', 'name': '世界殖民体系与亚非拉民族独立运动', 'level': 1, 'parent': None,
                 'desc': '世界殖民体系形成、民族独立运动', 'importance': 3, 'difficulty': 2},
                {'id': 'HIS-WLD-007', 'name': '两次世界大战、十月革命与国际秩序的演变', 'level': 1, 'parent': None,
                 'desc': '一战、十月革命、二战、战后国际秩序', 'importance': 4, 'difficulty': 3},
                {'id': 'HIS-WLD-008', 'name': '20世纪下半叶世界的新变化', 'level': 1, 'parent': None,
                 'desc': '冷战、资本主义国家的新变化、社会主义国家的发展与变化', 'importance': 4, 'difficulty': 3},
                {'id': 'HIS-WLD-009', 'name': '当代世界发展的特点与主要趋势', 'level': 1, 'parent': None,
                 'desc': '世界多极化、经济全球化、社会信息化、文化多样化', 'importance': 4, 'difficulty': 2},
                # 二级知识点
                {'id': 'HIS-WLD-101', 'name': '新航路开辟的影响', 'level': 2, 'parent': 'HIS-WLD-003',
                 'desc': '商业革命、价格革命、世界市场雏形', 'importance': 4, 'difficulty': 2},
                {'id': 'HIS-WLD-102', 'name': '启蒙运动', 'level': 2, 'parent': 'HIS-WLD-004',
                 'desc': '启蒙思想家的主张、启蒙运动的影响', 'importance': 4, 'difficulty': 3},
                {'id': 'HIS-WLD-103', 'name': '工业革命的影响', 'level': 2, 'parent': 'HIS-WLD-005',
                 'desc': '生产力、社会结构、世界市场', 'importance': 4, 'difficulty': 3},
                {'id': 'HIS-WLD-104', 'name': '罗斯福新政', 'level': 2, 'parent': 'HIS-WLD-008',
                 'desc': '罗斯福新政的内容与影响', 'importance': 4, 'difficulty': 2},
                {'id': 'HIS-WLD-105', 'name': '两极格局的形成', 'level': 2, 'parent': 'HIS-WLD-008',
                 'desc': '美苏冷战、两极格局', 'importance': 4, 'difficulty': 2},
            ]
        },
        # 选择性必修一：国家制度与社会治理
        {
            'semester': 'selective_1', 'code': 'HIS-INSTITUTION', 'name': '国家制度与社会治理', 
            'number': '全书', 'sort': 4,
            'kps': [
                {'id': 'HIS-INS-001', 'name': '政治制度', 'level': 1, 'parent': None,
                 'desc': '中国古代政治制度、近代西方政治制度、中国近代政治制度的探索', 'importance': 4, 'difficulty': 3},
                {'id': 'HIS-INS-002', 'name': '官员的选拔与管理', 'level': 1, 'parent': None,
                 'desc': '中国古代官员选拔、西方文官制度、近代中国官员选拔', 'importance': 3, 'difficulty': 2},
                {'id': 'HIS-INS-003', 'name': '法律与教化', 'level': 1, 'parent': None,
                 'desc': '中国古代法治与教化、近代西方法律制度、当代中国法治建设', 'importance': 3, 'difficulty': 2},
                {'id': 'HIS-INS-004', 'name': '民族关系与国家关系', 'level': 1, 'parent': None,
                 'desc': '中国古代民族关系、近代民族国家、当代中国民族关系与外交', 'importance': 3, 'difficulty': 2},
                {'id': 'HIS-INS-005', 'name': '基层治理与社会保障', 'level': 1, 'parent': None,
                 'desc': '中国古代基层治理、西方基层治理与社会保障、当代中国基层治理与社会保障', 'importance': 3, 'difficulty': 2},
            ]
        },
        # 选择性必修二：经济与社会生活
        {
            'semester': 'selective_2', 'code': 'HIS-ECONOMIC', 'name': '经济与社会生活', 
            'number': '全书', 'sort': 5,
            'kps': [
                {'id': 'HIS-ECO-001', 'name': '食物生产与社会生活', 'level': 1, 'parent': None,
                 'desc': '农业的起源、新航路开辟后的食物物种交流、现代食物的生产', 'importance': 2, 'difficulty': 2},
                {'id': 'HIS-ECO-002', 'name': '生产工具与劳作方式', 'level': 1, 'parent': None,
                 'desc': '古代生产工具、近代工业革命、现代科技革命', 'importance': 3, 'difficulty': 2},
                {'id': 'HIS-ECO-003', 'name': '商业贸易与日常生活', 'level': 1, 'parent': None,
                 'desc': '古代商业贸易、近代世界市场、现代商业贸易', 'importance': 3, 'difficulty': 2},
                {'id': 'HIS-ECO-004', 'name': '村落、城镇与居住环境', 'level': 1, 'parent': None,
                 'desc': '古代村落与城镇、近代城市化、现代居住环境', 'importance': 2, 'difficulty': 2},
                {'id': 'HIS-ECO-005', 'name': '交通与社会变迁', 'level': 1, 'parent': None,
                 'desc': '古代交通、近代交通、现代交通', 'importance': 2, 'difficulty': 2},
                {'id': 'HIS-ECO-006', 'name': '医疗与公共卫生', 'level': 1, 'parent': None,
                 'desc': '古代医疗、近代医疗、现代公共卫生', 'importance': 2, 'difficulty': 2},
            ]
        },
        # 选择性必修三：文化交流与传播
        {
            'semester': 'selective_3', 'code': 'HIS-CULTURE', 'name': '文化交流与传播', 
            'number': '全书', 'sort': 6,
            'kps': [
                {'id': 'HIS-CUL-001', 'name': '源远流长的中华文化', 'level': 1, 'parent': None,
                 'desc': '中华文化的发展历程、中华文化的内涵与特点', 'importance': 3, 'difficulty': 2},
                {'id': 'HIS-CUL-002', 'name': '世界文化的多元传统', 'level': 1, 'parent': None,
                 'desc': '古代西亚、非洲、欧洲、南亚、东亚的文化', 'importance': 3, 'difficulty': 2},
                {'id': 'HIS-CUL-003', 'name': '人口迁徙与文化认同', 'level': 1, 'parent': None,
                 'desc': '古代人口迁徙、近代殖民活动、现代社会的移民', 'importance': 2, 'difficulty': 2},
                {'id': 'HIS-CUL-004', 'name': '商路、贸易与文化交流', 'level': 1, 'parent': None,
                 'desc': '古代商路、近代贸易与文化交流、现代贸易与文化交流', 'importance': 3, 'difficulty': 2},
                {'id': 'HIS-CUL-005', 'name': '战争与文化交锋', 'level': 1, 'parent': None,
                 'desc': '古代战争与文化、近代战争与文化、二战后文化的发展', 'importance': 2, 'difficulty': 2},
                {'id': 'HIS-CUL-006', 'name': '文化的传承与保护', 'level': 1, 'parent': None,
                 'desc': '文化传承的载体、文化遗产的保护', 'importance': 2, 'difficulty': 1},
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
    
    print(f"✅ 历史：{total_kp} 个知识点")
    
    # 考点
    exam_points = [
        ('HIS-ANC-001', '秦汉大一统', '秦朝中央集权制度的形成', '选择题/材料题', 2),
        ('HIS-ANC-004', '明清君主专制加强', '明清君主专制的强化', '选择题/材料题', 2),
        ('HIS-MOD-001', '近代中国的救亡图存', '洋务运动、戊戌变法等', '选择题/材料题', 3),
        ('HIS-MOD-003', '新民主主义革命', '中国共产党领导的革命', '选择题/材料题', 3),
        ('HIS-MOD-006', '改革开放', '改革开放的进程与影响', '选择题/材料题', 2),
        ('HIS-WLD-003', '新航路开辟', '新航路开辟的影响', '选择题/材料题', 2),
        ('HIS-WLD-004', '资本主义制度的确立', '英美法资产阶级革命', '选择题/材料题', 3),
        ('HIS-WLD-005', '工业革命', '两次工业革命的影响', '选择题/材料题', 3),
        ('HIS-WLD-007', '两次世界大战', '一战、二战的影响', '选择题/材料题', 3),
        ('HIS-WLD-008', '冷战与两极格局', '美苏冷战的形成与影响', '选择题/材料题', 3),
    ]
    
    ep_count = 0
    for kp_id, ep_name, desc, exam_type, difficulty in exam_points:
        if kp_id in kp_id_map:
            ep_id = f"EP-HIS-{ep_count+1:03d}"
            cursor.execute('''
                INSERT OR IGNORE INTO exam_points 
                (ep_id, kp_id, ep_name, description, exam_type, difficulty_level)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (ep_id, kp_id_map[kp_id], ep_name, desc, exam_type, difficulty))
            ep_count += 1
    
    conn.commit()
    conn.close()
    print(f"✅ 历史：{ep_count} 个考点")


if __name__ == '__main__':
    build_history_knowledge_graph()
