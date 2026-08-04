#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本
创建数据库表结构并初始化基础数据
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'gaokao.db')
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schema.sql')

# 9个学科基础数据
SUBJECTS = [
    {'code': 'chinese', 'name': '语文', 'sort': 1},
    {'code': 'math', 'name': '数学', 'sort': 2},
    {'code': 'english', 'name': '英语', 'sort': 3},
    {'code': 'physics', 'name': '物理', 'sort': 4},
    {'code': 'chemistry', 'name': '化学', 'sort': 5},
    {'code': 'biology', 'name': '生物', 'sort': 6},
    {'code': 'politics', 'name': '政治', 'sort': 7},
    {'code': 'history', 'name': '历史', 'sort': 8},
    {'code': 'geography', 'name': '地理', 'sort': 9},
]


def init_database():
    """初始化数据库"""
    # 确保目录存在
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 执行Schema
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
        cursor.executescript(schema_sql)
    
    print("✅ 数据库表结构创建完成")
    
    # 初始化学科数据
    for subj in SUBJECTS:
        cursor.execute('''
            INSERT OR IGNORE INTO subjects (subject_code, subject_name, sort_order)
            VALUES (?, ?, ?)
        ''', (subj['code'], subj['name'], subj['sort']))
    
    print(f"✅ 初始化学科数据完成，共 {len(SUBJECTS)} 个学科")
    
    conn.commit()
    conn.close()
    print(f"✅ 数据库初始化完成: {DB_PATH}")


if __name__ == '__main__':
    init_database()
