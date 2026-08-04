#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一构建所有学科知识图谱
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from build_math_kg import build_math_knowledge_graph
from build_chinese_kg import build_chinese_knowledge_graph
from build_english_kg import build_english_knowledge_graph
from build_physics_kg import build_physics_knowledge_graph
from build_chemistry_kg import build_chemistry_knowledge_graph
from build_biology_kg import build_biology_knowledge_graph
from build_politics_kg import build_politics_knowledge_graph
from build_history_kg import build_history_knowledge_graph
from build_geography_kg import build_geography_knowledge_graph


def build_all():
    """构建所有学科知识图谱"""
    print("=" * 60)
    print("开始构建所有学科知识图谱...")
    print("=" * 60)
    
    build_math_knowledge_graph()
    build_chinese_knowledge_graph()
    build_english_knowledge_graph()
    build_physics_knowledge_graph()
    build_chemistry_knowledge_graph()
    build_biology_knowledge_graph()
    build_politics_knowledge_graph()
    build_history_knowledge_graph()
    build_geography_knowledge_graph()
    
    print("=" * 60)
    print("✅ 所有学科知识图谱构建完成！")
    print("=" * 60)


if __name__ == '__main__':
    build_all()
