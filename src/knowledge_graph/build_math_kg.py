#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数学学科知识点体系构建
基于《普通高中数学课程标准》（2017年版2020年修订）和人教版教材
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '../../database/gaokao.db')


def build_math_knowledge_graph():
    """构建数学学科知识图谱"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取数学学科ID
    cursor.execute("SELECT id FROM subjects WHERE subject_code = 'math'")
    subject_id = cursor.fetchone()[0]
    
    print(f"数学学科ID: {subject_id}")
    
    # ==========================================
    # 学期/模块定义
    # ==========================================
    semesters = [
        # 必修课程
        {'code': 'compulsory_1', 'name': '必修第一册', 'grade': '高一', 'sort': 1},
        {'code': 'compulsory_2', 'name': '必修第二册', 'grade': '高一', 'sort': 2},
        # 选择性必修课程
        {'code': 'selective_1', 'name': '选择性必修第一册', 'grade': '高二', 'sort': 3},
        {'code': 'selective_2', 'name': '选择性必修第二册', 'grade': '高二', 'sort': 4},
        {'code': 'selective_3', 'name': '选择性必修第三册', 'grade': '高二', 'sort': 5},
        # 选考内容
        {'code': 'elective_coord', 'name': '选修4-4 坐标系与参数方程', 'grade': '高三', 'sort': 6},
        {'code': 'elective_ineq', 'name': '选修4-5 不等式选讲', 'grade': '高三', 'sort': 7},
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
    
    print(f"✅ 创建 {len(semesters)} 个学期/模块")
    
    # ==========================================
    # 章节与知识点定义
    # ==========================================
    
    # 必修第一册
    chapters_comp1 = [
        {
            'code': 'CH01', 'name': '集合与常用逻辑用语', 'number': '第一章', 'sort': 1,
            'knowledge_points': [
                # 一级知识点
                {'id': 'MATH-SET-001', 'name': '集合的概念', 'level': 1, 'parent': None,
                 'desc': '集合的定义、元素与集合的关系', 'importance': 3, 'difficulty': 1},
                {'id': 'MATH-SET-002', 'name': '集合间的基本关系', 'level': 1, 'parent': 'MATH-SET-001',
                 'desc': '子集、真子集、集合相等', 'importance': 3, 'difficulty': 1},
                {'id': 'MATH-SET-003', 'name': '集合的基本运算', 'level': 1, 'parent': 'MATH-SET-001',
                 'desc': '并集、交集、补集', 'importance': 4, 'difficulty': 2},
                # 二级知识点
                {'id': 'MATH-SET-101', 'name': '集合的表示方法', 'level': 2, 'parent': 'MATH-SET-001',
                 'desc': '列举法、描述法、图示法', 'importance': 2, 'difficulty': 1},
                {'id': 'MATH-SET-102', 'name': '集合中元素的特性', 'level': 2, 'parent': 'MATH-SET-001',
                 'desc': '确定性、互异性、无序性', 'importance': 2, 'difficulty': 1},
                {'id': 'MATH-SET-103', 'name': 'Venn图及其应用', 'level': 2, 'parent': 'MATH-SET-003',
                 'desc': '用Venn图表示集合关系与运算', 'importance': 3, 'difficulty': 2},
                {'id': 'MATH-LOGIC-001', 'name': '充分条件与必要条件', 'level': 1, 'parent': None,
                 'desc': '充分条件、必要条件、充要条件的判断', 'importance': 3, 'difficulty': 2},
                {'id': 'MATH-LOGIC-002', 'name': '全称量词与存在量词', 'level': 1, 'parent': None,
                 'desc': '全称命题、特称命题及其否定', 'importance': 2, 'difficulty': 2},
            ]
        },
        {
            'code': 'CH02', 'name': '一元二次函数、方程和不等式', 'number': '第二章', 'sort': 2,
            'knowledge_points': [
                {'id': 'MATH-INEQ-001', 'name': '等式性质与不等式性质', 'level': 1, 'parent': None,
                 'desc': '不等式的基本性质', 'importance': 3, 'difficulty': 1},
                {'id': 'MATH-INEQ-002', 'name': '基本不等式', 'level': 1, 'parent': 'MATH-INEQ-001',
                 'desc': '均值不等式及其应用', 'importance': 4, 'difficulty': 3},
                {'id': 'MATH-INEQ-003', 'name': '二次函数与一元二次方程、不等式', 'level': 1, 'parent': None,
                 'desc': '三个二次的关系', 'importance': 4, 'difficulty': 3},
                {'id': 'MATH-INEQ-101', 'name': '一元二次不等式解法', 'level': 2, 'parent': 'MATH-INEQ-003',
                 'desc': '因式分解法、图像法', 'importance': 4, 'difficulty': 2},
                {'id': 'MATH-INEQ-102', 'name': '基本不等式求最值', 'level': 2, 'parent': 'MATH-INEQ-002',
                 'desc': '一正二定三相等', 'importance': 4, 'difficulty': 3},
            ]
        },
        {
            'code': 'CH03', 'name': '函数的概念与性质', 'number': '第三章', 'sort': 3,
            'knowledge_points': [
                {'id': 'MATH-FUNC-001', 'name': '函数的概念', 'level': 1, 'parent': None,
                 'desc': '函数的定义、定义域、值域', 'importance': 4, 'difficulty': 2},
                {'id': 'MATH-FUNC-002', 'name': '函数的表示方法', 'level': 1, 'parent': 'MATH-FUNC-001',
                 'desc': '解析法、列表法、图像法', 'importance': 3, 'difficulty': 2},
                {'id': 'MATH-FUNC-003', 'name': '函数的单调性', 'level': 1, 'parent': None,
                 'desc': '增函数、减函数的定义与判断', 'importance': 4, 'difficulty': 3},
                {'id': 'MATH-FUNC-004', 'name': '函数的奇偶性', 'level': 1, 'parent': None,
                 'desc': '奇函数、偶函数的定义与判断', 'importance': 4, 'difficulty': 2},
                {'id': 'MATH-FUNC-005', 'name': '函数的最值', 'level': 1, 'parent': 'MATH-FUNC-003',
                 'desc': '最大值、最小值的求法', 'importance': 4, 'difficulty': 3},
                {'id': 'MATH-FUNC-006', 'name': '幂函数', 'level': 1, 'parent': None,
                 'desc': '幂函数的定义、图像与性质', 'importance': 3, 'difficulty': 2},
                {'id': 'MATH-FUNC-007', 'name': '函数的应用', 'level': 1, 'parent': None,
                 'desc': '函数模型及其应用', 'importance': 3, 'difficulty': 3},
                # 二级知识点
                {'id': 'MATH-FUNC-101', 'name': '函数定义域求法', 'level': 2, 'parent': 'MATH-FUNC-001',
                 'desc': '分式、根式、对数等定义域', 'importance': 3, 'difficulty': 2},
                {'id': 'MATH-FUNC-102', 'name': '函数值域求法', 'level': 2, 'parent': 'MATH-FUNC-001',
                 'desc': '配方法、换元法、判别式法等', 'importance': 3, 'difficulty': 3},
                {'id': 'MATH-FUNC-103', 'name': '分段函数', 'level': 2, 'parent': 'MATH-FUNC-002',
                 'desc': '分段函数的图像与性质', 'importance': 3, 'difficulty': 2},
                {'id': 'MATH-FUNC-104', 'name': '复合函数', 'level': 2, 'parent': 'MATH-FUNC-003',
                 'desc': '复合函数的单调性（同增异减）', 'importance': 4, 'difficulty': 3},
            ]
        },
        {
            'code': 'CH04', 'name': '指数函数与对数函数', 'number': '第四章', 'sort': 4,
            'knowledge_points': [
                {'id': 'MATH-EXP-001', 'name': '指数', 'level': 1, 'parent': None,
                 'desc': '根式、分数指数幂、有理数指数幂', 'importance': 3, 'difficulty': 2},
                {'id': 'MATH-EXP-002', 'name': '指数函数', 'level': 1, 'parent': 'MATH-EXP-001',
                 'desc': '指数函数的定义、图像与性质', 'importance': 4, 'difficulty': 2},
                {'id': 'MATH-LOG-001', 'name': '对数', 'level': 1, 'parent': None,
                 'desc': '对数的定义、运算性质', 'importance': 3, 'difficulty': 2},
                {'id': 'MATH-LOG-002', 'name': '对数函数', 'level': 1, 'parent': 'MATH-LOG-001',
                 'desc': '对数函数的定义、图像与性质', 'importance': 4, 'difficulty': 2},
                {'id': 'MATH-EXPLOG-001', 'name': '函数的应用（二）', 'level': 1, 'parent': None,
                 'desc': '指数函数、对数函数模型的应用', 'importance': 3, 'difficulty': 3},
                # 二级知识点
                {'id': 'MATH-EXP-101', 'name': '指数运算性质', 'level': 2, 'parent': 'MATH-EXP-001',
                 'desc': '指数幂的运算法则', 'importance': 3, 'difficulty': 1},
                {'id': 'MATH-LOG-101', 'name': '对数运算性质', 'level': 2, 'parent': 'MATH-LOG-001',
                 'desc': '对数的运算法则、换底公式', 'importance': 3, 'difficulty': 2},
                {'id': 'MATH-EXPLOG-101', 'name': '反函数', 'level': 2, 'parent': 'MATH-EXP-002',
                 'desc': '指数函数与对数函数互为反函数', 'importance': 2, 'difficulty': 2},
            ]
        },
        {
            'code': 'CH05', 'name': '三角函数', 'number': '第五章', 'sort': 5,
            'knowledge_points': [
                {'id': 'MATH-TRIG-001', 'name': '任意角和弧度制', 'level': 1, 'parent': None,
                 'desc': '角的概念推广、弧度制', 'importance': 2, 'difficulty': 1},
                {'id': 'MATH-TRIG-002', 'name': '三角函数的概念', 'level': 1, 'parent': 'MATH-TRIG-001',
                 'desc': '正弦、余弦、正切的定义', 'importance': 4, 'difficulty': 2},
                {'id': 'MATH-TRIG-003', 'name': '诱导公式', 'level': 1, 'parent': 'MATH-TRIG-002',
                 'desc': '三角函数的诱导公式', 'importance': 4, 'difficulty': 2},
                {'id': 'MATH-TRIG-004', 'name': '三角函数的图像与性质', 'level': 1, 'parent': None,
                 'desc': '正弦、余弦、正切函数的图像与性质', 'importance': 4, 'difficulty': 3},
                {'id': 'MATH-TRIG-005', 'name': '三角恒等变换', 'level': 1, 'parent': None,
                 'desc': '两角和差公式、二倍角公式', 'importance': 4, 'difficulty': 3},
                {'id': 'MATH-TRIG-006', 'name': '函数y=Asin(ωx+φ)', 'level': 1, 'parent': 'MATH-TRIG-004',
                 'desc': '三角函数图像变换', 'importance': 4, 'difficulty': 3},
                {'id': 'MATH-TRIG-007', 'name': '三角函数的应用', 'level': 1, 'parent': None,
                 'desc': '三角函数模型的简单应用', 'importance': 2, 'difficulty': 3},
                # 二级知识点
                {'id': 'MATH-TRIG-101', 'name': '同角三角函数基本关系', 'level': 2, 'parent': 'MATH-TRIG-002',
                 'desc': 'sin²α+cos²α=1, tanα=sinα/cosα', 'importance': 4, 'difficulty': 2},
                {'id': 'MATH-TRIG-102', 'name': '三角函数的周期性', 'level': 2, 'parent': 'MATH-TRIG-004',
                 'desc': '周期函数的定义、最小正周期', 'importance': 3, 'difficulty': 2},
                {'id': 'MATH-TRIG-103', 'name': '辅助角公式', 'level': 2, 'parent': 'MATH-TRIG-005',
                 'desc': 'asinx+bcosx的化简', 'importance': 4, 'difficulty': 3},
                {'id': 'MATH-TRIG-104', 'name': '三角函数最值问题', 'level': 2, 'parent': 'MATH-TRIG-004',
                 'desc': '三角函数的最值求法', 'importance': 4, 'difficulty': 3},
            ]
        },
    ]
    
    # 必修第二册
    chapters_comp2 = [
        {
            'code': 'CH06', 'name': '平面向量及其应用', 'number': '第六章', 'sort': 6,
            'knowledge_points': [
                {'id': 'MATH-VEC-001', 'name': '平面向量的概念', 'level': 1, 'parent': None,
                 'desc': '向量的定义、模、零向量、单位向量', 'importance': 3, 'difficulty': 1},
                {'id': 'MATH-VEC-002', 'name': '平面向量的运算', 'level': 1, 'parent': 'MATH-VEC-001',
                 'desc': '向量的加法、减法、数乘', 'importance': 4, 'difficulty': 2},
                {'id': 'MATH-VEC-003', 'name': '平面向量基本定理及坐标表示', 'level': 1, 'parent': None,
                 'desc': '平面向量基本定理、坐标运算', 'importance': 4, 'difficulty': 2},
                {'id': 'MATH-VEC-004', 'name': '平面向量的数量积', 'level': 1, 'parent': None,
                 'desc': '向量数量积的定义、性质、运算律', 'importance': 4, 'difficulty': 3},
                {'id': 'MATH-VEC-005', 'name': '平面向量的应用', 'level': 1, 'parent': None,
                 'desc': '向量在几何、物理中的应用', 'importance': 3, 'difficulty': 3},
                # 二级知识点
                {'id': 'MATH-VEC-101', 'name': '向量共线条件', 'level': 2, 'parent': 'MATH-VEC-002',
                 'desc': '向量共线的充要条件', 'importance': 3, 'difficulty': 2},
                {'id': 'MATH-VEC-102', 'name': '向量垂直条件', 'level': 2, 'parent': 'MATH-VEC-004',
                 'desc': '向量垂直的充要条件', 'importance': 4, 'difficulty': 2},
                {'id': 'MATH-VEC-103', 'name': '向量的夹角', 'level': 2, 'parent': 'MATH-VEC-004',
                 'desc': '向量夹角的定义与求法', 'importance': 3, 'difficulty': 2},
                {'id': 'MATH-VEC-104', 'name': '正弦定理', 'level': 2, 'parent': 'MATH-VEC-005',
                 'desc': '正弦定理及其应用', 'importance': 4, 'difficulty': 2},
                {'id': 'MATH-VEC-105', 'name': '余弦定理', 'level': 2, 'parent': 'MATH-VEC-005',
                 'desc': '余弦定理及其应用', 'importance': 4, 'difficulty': 2},
            ]
        },
        {
            'code': 'CH07', 'name': '复数', 'number': '第七章', 'sort': 7,
            'knowledge_points': [
                {'id': 'MATH-COMPLEX-001', 'name': '复数的概念', 'level': 1, 'parent': None,
                 'desc': '复数的定义、实部、虚部、共轭复数', 'importance': 3, 'difficulty': 1},
                {'id': 'MATH-COMPLEX-002', 'name': '复数的四则运算', 'level': 1, 'parent': 'MATH-COMPLEX-001',
                 'desc': '复数的加、减、乘、除运算', 'importance': 4, 'difficulty': 2},
                {'id': 'MATH-COMPLEX-003', 'name': '复数的几何意义', 'level': 1, 'parent': 'MATH-COMPLEX-001',
                 'desc': '复平面、复数的模', 'importance': 2, 'difficulty': 2},
                # 二级知识点
                {'id': 'MATH-COMPLEX-101', 'name': '复数的模', 'level': 2, 'parent': 'MATH-COMPLEX-003',
                 'desc': '复数模的计算与性质', 'importance': 3, 'difficulty': 2},
            ]
        },
        {
            'code': 'CH08', 'name': '立体几何初步', 'number': '第八章', 'sort': 8,
            'knowledge_points': [
                {'id': 'MATH-GEO3D-001', 'name': '基本立体图形', 'level': 1, 'parent': None,
                 'desc': '柱、锥、台、球的结构特征', 'importance': 3, 'difficulty': 1},
                {'id': 'MATH-GEO3D-002', 'name': '立体图形的直观图', 'level': 1, 'parent': 'MATH-GEO3D-001',
                 'desc': '斜二测画法', 'importance': 2, 'difficulty': 2},
                {'id': 'MATH-GEO3D-003', 'name': '简单几何体的表面积与体积', 'level': 1, 'parent': None,
                 'desc': '柱、锥、台、球的表面积与体积', 'importance': 4, 'difficulty': 2},
                {'id': 'MATH-GEO3D-004', 'name': '空间点、直线、平面之间的位置关系', 'level': 1, 'parent': None,
                 'desc': '平面的基本性质、空间中的位置关系', 'importance': 4, 'difficulty': 3},
                {'id': 'MATH-GEO3D-005', 'name': '空间直线、平面的平行', 'level': 1, 'parent': None,
                 'desc': '线面平行、面面平行的判定与性质', 'importance': 4, 'difficulty': 3},
                {'id': 'MATH-GEO3D-006', 'name': '空间直线、平面的垂直', 'level': 1, 'parent': None,
                 'desc': '线面垂直、面面垂直的判定与性质', 'importance': 4, 'difficulty': 3},
                # 二级知识点
                {'id': 'MATH-GEO3D-101', 'name': '三视图', 'level': 2, 'parent': 'MATH-GEO3D-002',
                 'desc': '三视图的识别与还原', 'importance': 3, 'difficulty': 2},
                {'id': 'MATH-GEO3D-102', 'name': '异面直线所成角', 'level': 2, 'parent': 'MATH-GEO3D-004',
                 'desc': '异面直线所成角的求法', 'importance': 3, 'difficulty': 3},
                {'id': 'MATH-GEO3D-103', 'name': '线面角', 'level': 2, 'parent': 'MATH-GEO3D-006',
                 'desc': '直线与平面所成角的求法', 'importance': 3, 'difficulty': 3},
                {'id': 'MATH-GEO3D-104', 'name': '二面角', 'level': 2, 'parent': 'MATH-GEO3D-006',
                 'desc': '二面角的求法', 'importance': 3, 'difficulty': 3},
            ]
        },
        {
            'code': 'CH09', 'name': '统计', 'number': '第九章', 'sort': 9,
            'knowledge_points': [
                {'id': 'MATH-STAT-001', 'name': '随机抽样', 'level': 1, 'parent': None,
                 'desc': '简单随机抽样、分层抽样、系统抽样', 'importance': 3, 'difficulty': 1},
                {'id': 'MATH-STAT-002', 'name': '用样本估计总体', 'level': 1, 'parent': None,
                 'desc': '频率分布直方图、茎叶图、数字特征', 'importance': 4, 'difficulty': 2},
                # 二级知识点
                {'id': 'MATH-STAT-101', 'name': '频率分布直方图', 'level': 2, 'parent': 'MATH-STAT-002',
                 'desc': '频率分布直方图的绘制与应用', 'importance': 4, 'difficulty': 2},
                {'id': 'MATH-STAT-102', 'name': '样本数字特征', 'level': 2, 'parent': 'MATH-STAT-002',
                 'desc': '众数、中位数、平均数、方差、标准差', 'importance': 4, 'difficulty': 2},
            ]
        },
        {
            'code': 'CH10', 'name': '概率', 'number': '第十章', 'sort': 10,
            'knowledge_points': [
                {'id': 'MATH-PROB-001', 'name': '随机事件与概率', 'level': 1, 'parent': None,
                 'desc': '随机事件、频率与概率', 'importance': 3, 'difficulty': 1},
                {'id': 'MATH-PROB-002', 'name': '古典概型', 'level': 1, 'parent': 'MATH-PROB-001',
                 'desc': '古典概型的定义与计算', 'importance': 4, 'difficulty': 2},
                {'id': 'MATH-PROB-003', 'name': '事件的相互独立性', 'level': 1, 'parent': None,
                 'desc': '独立事件的定义与概率计算', 'importance': 3, 'difficulty': 2},
                {'id': 'MATH-PROB-004', 'name': '概率的基本性质', 'level': 1, 'parent': 'MATH-PROB-001',
                 'desc': '互斥事件、对立事件的概率', 'importance': 3, 'difficulty': 2},
                # 二级知识点
                {'id': 'MATH-PROB-101', 'name': '互斥事件与对立事件', 'level': 2, 'parent': 'MATH-PROB-004',
                 'desc': '互斥事件、对立事件的关系与概率', 'importance': 3, 'difficulty': 2},
            ]
        },
    ]
    
    # 选择性必修第一册
    chapters_sel1 = [
        {
            'code': 'CH11', 'name': '空间向量与立体几何', 'number': '第一章', 'sort': 11,
            'knowledge_points': [
                {'id': 'MATH-SVEC-001', 'name': '空间向量及其运算', 'level': 1, 'parent': None,
                 'desc': '空间向量的加减、数乘、数量积', 'importance': 3, 'difficulty': 2},
                {'id': 'MATH-SVEC-002', 'name': '空间向量基本定理', 'level': 1, 'parent': 'MATH-SVEC-001',
                 'desc': '空间向量基本定理、坐标表示', 'importance': 3, 'difficulty': 2},
                {'id': 'MATH-SVEC-003', 'name': '空间向量的应用', 'level': 1, 'parent': None,
                 'desc': '用空间向量证明平行垂直、求角求距离', 'importance': 4, 'difficulty': 4},
                # 二级知识点
                {'id': 'MATH-SVEC-101', 'name': '空间向量法求线面角', 'level': 2, 'parent': 'MATH-SVEC-003',
                 'desc': '用法向量求线面角', 'importance': 4, 'difficulty': 3},
                {'id': 'MATH-SVEC-102', 'name': '空间向量法求二面角', 'level': 2, 'parent': 'MATH-SVEC-003',
                 'desc': '用法向量求二面角', 'importance': 4, 'difficulty': 4},
                {'id': 'MATH-SVEC-103', 'name': '空间向量法求距离', 'level': 2, 'parent': 'MATH-SVEC-003',
                 'desc': '点到平面的距离等', 'importance': 3, 'difficulty': 3},
            ]
        },
        {
            'code': 'CH12', 'name': '直线和圆的方程', 'number': '第二章', 'sort': 12,
            'knowledge_points': [
                {'id': 'MATH-LINE-001', 'name': '直线的倾斜角与斜率', 'level': 1, 'parent': None,
                 'desc': '倾斜角、斜率的定义与计算', 'importance': 3, 'difficulty': 1},
                {'id': 'MATH-LINE-002', 'name': '直线的方程', 'level': 1, 'parent': 'MATH-LINE-001',
                 'desc': '点斜式、斜截式、两点式、一般式', 'importance': 4, 'difficulty': 2},
                {'id': 'MATH-LINE-003', 'name': '直线的交点坐标与距离公式', 'level': 1, 'parent': None,
                 'desc': '两直线交点、点到直线距离、平行线距离', 'importance': 4, 'difficulty': 2},
                {'id': 'MATH-CIRCLE-001', 'name': '圆的方程', 'level': 1, 'parent': None,
                 'desc': '圆的标准方程、一般方程', 'importance': 4, 'difficulty': 2},
                {'id': 'MATH-CIRCLE-002', 'name': '直线与圆、圆与圆的位置关系', 'level': 1, 'parent': None,
                 'desc': '位置关系的判定、切线方程', 'importance': 4, 'difficulty': 3},
                # 二级知识点
                {'id': 'MATH-LINE-101', 'name': '两条直线平行与垂直', 'level': 2, 'parent': 'MATH-LINE-002',
                 'desc': '平行与垂直的条件', 'importance': 4, 'difficulty': 2},
                {'id': 'MATH-CIRCLE-101', 'name': '圆的切线方程', 'level': 2, 'parent': 'MATH-CIRCLE-002',
                 'desc': '圆的切线方程求法', 'importance': 3, 'difficulty': 3},
                {'id': 'MATH-CIRCLE-102', 'name': '直线与圆相交弦长', 'level': 2, 'parent': 'MATH-CIRCLE-002',
                 'desc': '弦长公式', 'importance': 4, 'difficulty': 3},
            ]
        },
        {
            'code': 'CH13', 'name': '圆锥曲线的方程', 'number': '第三章', 'sort': 13,
            'knowledge_points': [
                {'id': 'MATH-CONIC-001', 'name': '椭圆', 'level': 1, 'parent': None,
                 'desc': '椭圆的定义、标准方程、几何性质', 'importance': 4, 'difficulty': 3},
                {'id': 'MATH-CONIC-002', 'name': '双曲线', 'level': 1, 'parent': None,
                 'desc': '双曲线的定义、标准方程、几何性质', 'importance': 4, 'difficulty': 3},
                {'id': 'MATH-CONIC-003', 'name': '抛物线', 'level': 1, 'parent': None,
                 'desc': '抛物线的定义、标准方程、几何性质', 'importance': 4, 'difficulty': 3},
                # 二级知识点
                {'id': 'MATH-CONIC-101', 'name': '圆锥曲线的离心率', 'level': 2, 'parent': 'MATH-CONIC-001',
                 'desc': '离心率的计算与范围', 'importance': 4, 'difficulty': 3},
                {'id': 'MATH-CONIC-102', 'name': '直线与圆锥曲线位置关系', 'level': 2, 'parent': None,
                 'desc': '联立方程、判别式、韦达定理', 'importance': 4, 'difficulty': 4},
                {'id': 'MATH-CONIC-103', 'name': '圆锥曲线弦长问题', 'level': 2, 'parent': 'MATH-CONIC-102',
                 'desc': '弦长公式的应用', 'importance': 4, 'difficulty': 4},
                {'id': 'MATH-CONIC-104', 'name': '圆锥曲线中点弦问题', 'level': 2, 'parent': 'MATH-CONIC-102',
                 'desc': '点差法', 'importance': 3, 'difficulty': 4},
                {'id': 'MATH-CONIC-105', 'name': '圆锥曲线最值与范围问题', 'level': 2, 'parent': 'MATH-CONIC-102',
                 'desc': '函数法、不等式法', 'importance': 4, 'difficulty': 4},
            ]
        },
    ]
    
    # 选择性必修第二册
    chapters_sel2 = [
        {
            'code': 'CH14', 'name': '数列', 'number': '第四章', 'sort': 14,
            'knowledge_points': [
                {'id': 'MATH-SEQ-001', 'name': '数列的概念', 'level': 1, 'parent': None,
                 'desc': '数列的定义、通项公式、递推公式', 'importance': 3, 'difficulty': 1},
                {'id': 'MATH-SEQ-002', 'name': '等差数列', 'level': 1, 'parent': None,
                 'desc': '等差数列的定义、通项公式、前n项和', 'importance': 4, 'difficulty': 2},
                {'id': 'MATH-SEQ-003', 'name': '等比数列', 'level': 1, 'parent': None,
                 'desc': '等比数列的定义、通项公式、前n项和', 'importance': 4, 'difficulty': 2},
                {'id': 'MATH-SEQ-004', 'name': '数列求和', 'level': 1, 'parent': None,
                 'desc': '各种数列求和方法', 'importance': 4, 'difficulty': 3},
                {'id': 'MATH-SEQ-005', 'name': '数列的综合应用', 'level': 1, 'parent': None,
                 'desc': '数列与函数、不等式的综合', 'importance': 4, 'difficulty': 4},
                # 二级知识点
                {'id': 'MATH-SEQ-101', 'name': '等差数列性质', 'level': 2, 'parent': 'MATH-SEQ-002',
                 'desc': '等差中项、下标和性质等', 'importance': 4, 'difficulty': 2},
                {'id': 'MATH-SEQ-102', 'name': '等比数列性质', 'level': 2, 'parent': 'MATH-SEQ-003',
                 'desc': '等比中项、下标积性质等', 'importance': 4, 'difficulty': 2},
                {'id': 'MATH-SEQ-103', 'name': '错位相减法', 'level': 2, 'parent': 'MATH-SEQ-004',
                 'desc': '等差×等比型数列求和', 'importance': 4, 'difficulty': 3},
                {'id': 'MATH-SEQ-104', 'name': '裂项相消法', 'level': 2, 'parent': 'MATH-SEQ-004',
                 'desc': '裂项相消求和', 'importance': 4, 'difficulty': 3},
                {'id': 'MATH-SEQ-105', 'name': '分组求和法', 'level': 2, 'parent': 'MATH-SEQ-004',
                 'desc': '分组转化求和', 'importance': 3, 'difficulty': 2},
            ]
        },
        {
            'code': 'CH15', 'name': '一元函数的导数及其应用', 'number': '第五章', 'sort': 15,
            'knowledge_points': [
                {'id': 'MATH-DERIV-001', 'name': '导数的概念及其意义', 'level': 1, 'parent': None,
                 'desc': '导数的定义、几何意义、物理意义', 'importance': 3, 'difficulty': 2},
                {'id': 'MATH-DERIV-002', 'name': '导数的运算', 'level': 1, 'parent': 'MATH-DERIV-001',
                 'desc': '基本初等函数导数、四则运算、复合函数导数', 'importance': 4, 'difficulty': 2},
                {'id': 'MATH-DERIV-003', 'name': '导数在研究函数中的应用', 'level': 1, 'parent': None,
                 'desc': '单调性、极值、最值', 'importance': 4, 'difficulty': 4},
                {'id': 'MATH-DERIV-004', 'name': '导数的综合应用', 'level': 1, 'parent': None,
                 'desc': '导数与不等式、零点问题', 'importance': 4, 'difficulty': 4},
                # 二级知识点
                {'id': 'MATH-DERIV-101', 'name': '导数与函数单调性', 'level': 2, 'parent': 'MATH-DERIV-003',
                 'desc': '利用导数判断单调性', 'importance': 4, 'difficulty': 3},
                {'id': 'MATH-DERIV-102', 'name': '导数与函数极值', 'level': 2, 'parent': 'MATH-DERIV-003',
                 'desc': '极值的判定与求法', 'importance': 4, 'difficulty': 3},
                {'id': 'MATH-DERIV-103', 'name': '导数与函数最值', 'level': 2, 'parent': 'MATH-DERIV-003',
                 'desc': '闭区间上函数的最值', 'importance': 4, 'difficulty': 3},
                {'id': 'MATH-DERIV-104', 'name': '导数与不等式证明', 'level': 2, 'parent': 'MATH-DERIV-004',
                 'desc': '构造函数证明不等式', 'importance': 4, 'difficulty': 4},
                {'id': 'MATH-DERIV-105', 'name': '导数与函数零点', 'level': 2, 'parent': 'MATH-DERIV-004',
                 'desc': '零点个数、零点范围问题', 'importance': 4, 'difficulty': 4},
                {'id': 'MATH-DERIV-106', 'name': '导数中的恒成立问题', 'level': 2, 'parent': 'MATH-DERIV-004',
                 'desc': '分离参数法、分类讨论法', 'importance': 4, 'difficulty': 4},
            ]
        },
    ]
    
    # 选择性必修第三册
    chapters_sel3 = [
        {
            'code': 'CH16', 'name': '计数原理', 'number': '第六章', 'sort': 16,
            'knowledge_points': [
                {'id': 'MATH-COUNT-001', 'name': '分类加法计数原理与分步乘法计数原理', 'level': 1, 'parent': None,
                 'desc': '两个基本计数原理', 'importance': 4, 'difficulty': 2},
                {'id': 'MATH-COUNT-002', 'name': '排列与组合', 'level': 1, 'parent': None,
                 'desc': '排列数、组合数公式与应用', 'importance': 4, 'difficulty': 3},
                {'id': 'MATH-COUNT-003', 'name': '二项式定理', 'level': 1, 'parent': None,
                 'desc': '二项式定理、二项展开式', 'importance': 3, 'difficulty': 2},
                # 二级知识点
                {'id': 'MATH-COUNT-101', 'name': '排列组合常用方法', 'level': 2, 'parent': 'MATH-COUNT-002',
                 'desc': '捆绑法、插空法、隔板法等', 'importance': 4, 'difficulty': 3},
                {'id': 'MATH-COUNT-102', 'name': '二项式系数性质', 'level': 2, 'parent': 'MATH-COUNT-003',
                 'desc': '二项式系数的性质、杨辉三角', 'importance': 3, 'difficulty': 2},
            ]
        },
        {
            'code': 'CH17', 'name': '随机变量及其分布', 'number': '第七章', 'sort': 17,
            'knowledge_points': [
                {'id': 'MATH-RV-001', 'name': '条件概率与全概率公式', 'level': 1, 'parent': None,
                 'desc': '条件概率、全概率公式、贝叶斯公式', 'importance': 3, 'difficulty': 3},
                {'id': 'MATH-RV-002', 'name': '离散型随机变量及其分布列', 'level': 1, 'parent': None,
                 'desc': '分布列、期望、方差', 'importance': 4, 'difficulty': 3},
                {'id': 'MATH-RV-003', 'name': '二项分布与超几何分布', 'level': 1, 'parent': 'MATH-RV-002',
                 'desc': '二项分布、超几何分布', 'importance': 4, 'difficulty': 3},
                {'id': 'MATH-RV-004', 'name': '正态分布', 'level': 1, 'parent': None,
                 'desc': '正态分布的定义、性质、3σ原则', 'importance': 3, 'difficulty': 2},
                # 二级知识点
                {'id': 'MATH-RV-101', 'name': '离散型随机变量的期望', 'level': 2, 'parent': 'MATH-RV-002',
                 'desc': '期望的计算与性质', 'importance': 4, 'difficulty': 2},
                {'id': 'MATH-RV-102', 'name': '离散型随机变量的方差', 'level': 2, 'parent': 'MATH-RV-002',
                 'desc': '方差的计算与性质', 'importance': 3, 'difficulty': 2},
            ]
        },
        {
            'code': 'CH18', 'name': '成对数据的统计分析', 'number': '第八章', 'sort': 18,
            'knowledge_points': [
                {'id': 'MATH-REG-001', 'name': '成对数据的统计相关性', 'level': 1, 'parent': None,
                 'desc': '相关系数、散点图', 'importance': 2, 'difficulty': 2},
                {'id': 'MATH-REG-002', 'name': '一元线性回归模型', 'level': 1, 'parent': None,
                 'desc': '回归直线方程、最小二乘法', 'importance': 3, 'difficulty': 2},
                {'id': 'MATH-REG-003', 'name': '列联表与独立性检验', 'level': 1, 'parent': None,
                 'desc': '2×2列联表、卡方检验', 'importance': 3, 'difficulty': 2},
            ]
        },
    ]
    
    # 选修4-4 坐标系与参数方程
    chapters_coord = [
        {
            'code': 'CH19', 'name': '坐标系', 'number': '第一讲', 'sort': 19,
            'knowledge_points': [
                {'id': 'MATH-COORD-001', 'name': '平面直角坐标系', 'level': 1, 'parent': None,
                 'desc': '坐标系的伸缩变换', 'importance': 2, 'difficulty': 1},
                {'id': 'MATH-COORD-002', 'name': '极坐标系', 'level': 1, 'parent': None,
                 'desc': '极坐标的概念、极坐标与直角坐标互化', 'importance': 4, 'difficulty': 2},
                {'id': 'MATH-COORD-003', 'name': '简单曲线的极坐标方程', 'level': 1, 'parent': 'MATH-COORD-002',
                 'desc': '圆、直线的极坐标方程', 'importance': 4, 'difficulty': 3},
            ]
        },
        {
            'code': 'CH20', 'name': '参数方程', 'number': '第二讲', 'sort': 20,
            'knowledge_points': [
                {'id': 'MATH-PARAM-001', 'name': '参数方程的概念', 'level': 1, 'parent': None,
                 'desc': '参数方程的定义', 'importance': 2, 'difficulty': 1},
                {'id': 'MATH-PARAM-002', 'name': '常见曲线的参数方程', 'level': 1, 'parent': None,
                 'desc': '直线、圆、椭圆的参数方程', 'importance': 4, 'difficulty': 2},
                {'id': 'MATH-PARAM-003', 'name': '参数方程的应用', 'level': 1, 'parent': 'MATH-PARAM-002',
                 'desc': '参数方程与普通方程互化、参数t的几何意义', 'importance': 4, 'difficulty': 3},
            ]
        },
    ]
    
    # 选修4-5 不等式选讲
    chapters_ineq = [
        {
            'code': 'CH21', 'name': '不等式和绝对值不等式', 'number': '第一讲', 'sort': 21,
            'knowledge_points': [
                {'id': 'MATH-INEQSEL-001', 'name': '不等式', 'level': 1, 'parent': None,
                 'desc': '不等式的基本性质、基本不等式', 'importance': 3, 'difficulty': 2},
                {'id': 'MATH-INEQSEL-002', 'name': '绝对值不等式', 'level': 1, 'parent': None,
                 'desc': '绝对值三角不等式、绝对值不等式解法', 'importance': 4, 'difficulty': 2},
            ]
        },
        {
            'code': 'CH22', 'name': '证明不等式的基本方法', 'number': '第二讲', 'sort': 22,
            'knowledge_points': [
                {'id': 'MATH-INEQSEL-003', 'name': '比较法', 'level': 1, 'parent': None,
                 'desc': '作差比较法、作商比较法', 'importance': 2, 'difficulty': 2},
                {'id': 'MATH-INEQSEL-004', 'name': '综合法与分析法', 'level': 1, 'parent': None,
                 'desc': '综合法、分析法证明不等式', 'importance': 3, 'difficulty': 3},
                {'id': 'MATH-INEQSEL-005', 'name': '反证法与放缩法', 'level': 1, 'parent': None,
                 'desc': '反证法、放缩法证明不等式', 'importance': 2, 'difficulty': 3},
            ]
        },
    ]
    
    # 合并所有章节
    all_chapters = []
    semester_chapter_map = {
        'compulsory_1': chapters_comp1,
        'compulsory_2': chapters_comp2,
        'selective_1': chapters_sel1,
        'selective_2': chapters_sel2,
        'selective_3': chapters_sel3,
        'elective_coord': chapters_coord,
        'elective_ineq': chapters_ineq,
    }
    
    # 先插入所有章节和知识点，建立kp_id到数据库id的映射
    kp_id_map = {}  # kp_id -> db_id
    
    total_kp = 0
    for sem_code, chapters in semester_chapter_map.items():
        sem_id = semester_ids[sem_code]
        for ch in chapters:
            # 插入章节
            cursor.execute('''
                INSERT OR IGNORE INTO chapters 
                (semester_id, chapter_code, chapter_name, chapter_number, sort_order)
                VALUES (?, ?, ?, ?, ?)
            ''', (sem_id, ch['code'], ch['name'], ch['number'], ch['sort']))
            cursor.execute("SELECT id FROM chapters WHERE semester_id = ? AND chapter_code = ?",
                           (sem_id, ch['code']))
            chapter_id = cursor.fetchone()[0]
            
            # 插入知识点（先插入所有一级知识点，再插入二级）
            for kp in ch['knowledge_points']:
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
    
    print(f"✅ 创建 {total_kp} 个知识点")
    
    # 更新父知识点关联
    for sem_code, chapters in semester_chapter_map.items():
        for ch in chapters:
            for kp in ch['knowledge_points']:
                if kp['parent'] and kp['parent'] in kp_id_map:
                    parent_db_id = kp_id_map[kp['parent']]
                    kp_db_id = kp_id_map[kp['id']]
                    cursor.execute('''
                        UPDATE knowledge_points 
                        SET parent_kp_id = ?
                        WHERE id = ?
                    ''', (parent_db_id, kp_db_id))
    
    print("✅ 更新知识点层级关系完成")
    
    # ==========================================
    # 创建知识点关联（知识图谱边）
    # ==========================================
    relations = [
        # 前置依赖关系
        ('MATH-SET-001', 'MATH-FUNC-001', 'prerequisite', '集合是函数概念的基础'),
        ('MATH-INEQ-003', 'MATH-FUNC-003', 'prerequisite', '二次不等式是函数单调性的基础'),
        ('MATH-FUNC-001', 'MATH-EXP-002', 'prerequisite', '函数概念是指数函数的基础'),
        ('MATH-FUNC-001', 'MATH-LOG-002', 'prerequisite', '函数概念是对数函数的基础'),
        ('MATH-FUNC-003', 'MATH-TRIG-004', 'prerequisite', '函数单调性是三角函数性质的基础'),
        ('MATH-TRIG-002', 'MATH-TRIG-005', 'prerequisite', '三角函数概念是恒等变换的基础'),
        ('MATH-VEC-001', 'MATH-SVEC-001', 'extends', '平面向量扩展到空间向量'),
        ('MATH-GEO3D-004', 'MATH-SVEC-003', 'related', '立体几何位置关系可用空间向量解决'),
        ('MATH-LINE-001', 'MATH-CIRCLE-001', 'prerequisite', '直线方程是圆方程的基础'),
        ('MATH-CIRCLE-002', 'MATH-CONIC-001', 'prerequisite', '圆与直线位置关系是圆锥曲线的基础'),
        ('MATH-SEQ-002', 'MATH-SEQ-004', 'prerequisite', '等差数列是数列求和的基础'),
        ('MATH-FUNC-003', 'MATH-DERIV-003', 'related', '导数可用于研究函数单调性'),
        ('MATH-DERIV-003', 'MATH-DERIV-004', 'extends', '导数应用扩展到综合问题'),
        ('MATH-COUNT-002', 'MATH-PROB-002', 'prerequisite', '排列组合是古典概型的基础'),
        ('MATH-PROB-001', 'MATH-RV-002', 'prerequisite', '概率是随机变量分布的基础'),
        ('MATH-COUNT-003', 'MATH-RV-003', 'related', '二项式定理与二项分布相关'),
    ]
    
    for from_kp, to_kp, rel_type, desc in relations:
        if from_kp in kp_id_map and to_kp in kp_id_map:
            cursor.execute('''
                INSERT OR IGNORE INTO kp_relations 
                (from_kp_id, to_kp_id, relation_type, description)
                VALUES (?, ?, ?, ?)
            ''', (kp_id_map[from_kp], kp_id_map[to_kp], rel_type, desc))
    
    print(f"✅ 创建 {len(relations)} 条知识点关联")
    
    # ==========================================
    # 创建考点
    # ==========================================
    exam_points = [
        # 集合与逻辑
        ('MATH-SET-003', '集合的运算', '集合交并补运算，常与不等式结合', '选择题', 2),
        ('MATH-LOGIC-001', '充分必要条件', '充分条件、必要条件的判断', '选择题', 2),
        # 函数
        ('MATH-FUNC-003', '函数的单调性', '函数单调性的判断与应用', '选择题/填空题', 3),
        ('MATH-FUNC-004', '函数的奇偶性', '函数奇偶性的判断与应用', '选择题/填空题', 2),
        ('MATH-EXP-002', '指数函数的图像与性质', '指数函数的图像与性质应用', '选择题', 2),
        ('MATH-LOG-002', '对数函数的图像与性质', '对数函数的图像与性质应用', '选择题', 2),
        # 三角函数
        ('MATH-TRIG-004', '三角函数的图像与性质', '三角函数的周期性、单调性、最值', '选择题/填空题', 3),
        ('MATH-TRIG-005', '三角恒等变换', '两角和差、二倍角公式的应用', '选择题/填空题/解答题', 3),
        ('MATH-TRIG-006', '三角函数图像变换', 'y=Asin(ωx+φ)的图像与性质', '选择题/填空题', 3),
        # 数列
        ('MATH-SEQ-002', '等差数列', '等差数列通项公式、前n项和公式', '选择题/填空题/解答题', 3),
        ('MATH-SEQ-003', '等比数列', '等比数列通项公式、前n项和公式', '选择题/填空题/解答题', 3),
        ('MATH-SEQ-004', '数列求和', '错位相减、裂项相消等求和方法', '解答题', 3),
        # 导数
        ('MATH-DERIV-003', '导数与函数单调性', '利用导数研究函数单调性', '解答题', 4),
        ('MATH-DERIV-004', '导数的综合应用', '导数与不等式、零点问题', '解答题', 4),
        # 立体几何
        ('MATH-GEO3D-005', '空间中的平行关系', '线面平行、面面平行的判定与性质', '选择题/解答题', 3),
        ('MATH-GEO3D-006', '空间中的垂直关系', '线面垂直、面面垂直的判定与性质', '选择题/解答题', 3),
        ('MATH-SVEC-003', '空间向量的应用', '用空间向量求角求距离', '解答题', 4),
        # 解析几何
        ('MATH-CIRCLE-002', '直线与圆的位置关系', '直线与圆相交、相切的判定', '选择题/填空题', 3),
        ('MATH-CONIC-001', '椭圆的标准方程与性质', '椭圆的定义、标准方程、几何性质', '选择题/填空题/解答题', 3),
        ('MATH-CONIC-002', '双曲线的标准方程与性质', '双曲线的定义、标准方程、几何性质', '选择题/填空题', 3),
        ('MATH-CONIC-003', '抛物线的标准方程与性质', '抛物线的定义、标准方程、几何性质', '选择题/填空题', 3),
        ('MATH-CONIC-102', '直线与圆锥曲线位置关系', '联立方程、韦达定理的应用', '解答题', 4),
        # 概率统计
        ('MATH-PROB-002', '古典概型', '古典概型的概率计算', '选择题/填空题', 2),
        ('MATH-RV-002', '离散型随机变量的分布列', '分布列、期望、方差', '解答题', 3),
        ('MATH-RV-003', '二项分布', '二项分布的期望与方差', '选择题/解答题', 3),
        ('MATH-STAT-002', '用样本估计总体', '频率分布直方图、数字特征', '选择题/解答题', 2),
        # 平面向量
        ('MATH-VEC-004', '平面向量的数量积', '向量数量积的定义与运算', '选择题/填空题', 2),
        # 复数
        ('MATH-COMPLEX-002', '复数的四则运算', '复数的加减乘除运算', '选择题', 1),
        # 计数原理
        ('MATH-COUNT-002', '排列组合', '排列组合的应用', '选择题/填空题', 3),
        ('MATH-COUNT-003', '二项式定理', '二项展开式的通项、系数', '选择题/填空题', 2),
        # 选考
        ('MATH-PARAM-003', '参数方程的应用', '参数方程与极坐标的综合应用', '选考题', 3),
        ('MATH-INEQSEL-002', '绝对值不等式', '绝对值不等式的解法与证明', '选考题', 2),
    ]
    
    ep_count = 0
    for kp_id, ep_name, desc, exam_type, difficulty in exam_points:
        if kp_id in kp_id_map:
            ep_id = f"EP-{kp_id}-{ep_count+1:03d}"
            cursor.execute('''
                INSERT OR IGNORE INTO exam_points 
                (ep_id, kp_id, ep_name, description, exam_type, difficulty_level)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (ep_id, kp_id_map[kp_id], ep_name, desc, exam_type, difficulty))
            ep_count += 1
    
    print(f"✅ 创建 {ep_count} 个考点")
    
    conn.commit()
    conn.close()
    print("\n🎉 数学学科知识图谱构建完成！")


if __name__ == '__main__':
    build_math_knowledge_graph()
