# 高考真题库系统（SmartGaokaoPastPapers）

一个基于知识图谱的高考真题智能学习系统，包含知识图谱、真题库和网页展示三大模块。

## 项目概述

本项目旨在构建一个完整的高考真题智能学习平台，通过知识图谱将知识点系统化，并结合历年高考真题，帮助学生高效学习和复习。

## 功能模块

### 1. 知识图谱系统 ✅
- 覆盖9大学科：语文、数学、英语、物理、化学、生物、政治、历史、地理
- 基于《普通高中课程标准》和人教版教材构建
- 每个知识点有唯一ID，支持层级结构
- 包含考点信息和难度/重要性标注

**统计数据：**
- 知识点总数：538个
- 考点总数：121个
- 学期/模块：51个
- 章节：101个

### 2. 真题库系统 🔄
- 支持4067份高考真题（原卷版+解析版）
- 支持doc/docx/pdf三种格式解析
- 题目自动提取和去重
- 原卷版与解析版智能合并
- 保留公式、图片等完整内容
- 支持题目ID唯一标识

**已完成：**
- ✅ 试卷解析器（docx/pdf/doc）
- ✅ 题目提取模块
- ✅ 题目去重模块
- ✅ 原卷解析合并模块
- ✅ 数据库入库模块
- ✅ 批量处理脚本

**待完成：**
- 🔄 全学科批量处理
- 🔄 题目-知识点自动关联
- 🔄 数据质量校验

### 3. 网页展示系统 🔄
- 学科选择首页
- 知识点树状导航
- 知识点详情页（解析+考点+真题）
- 题目详情页（原题+答案+解析）
- 响应式设计

**已完成：**
- ✅ 后端API（FastAPI）
- ✅ 前端页面（4个核心页面）
- ✅ 知识点树状导航
- ✅ 题目展示功能
- ✅ 美观的UI设计

**待完成：**
- 🔄 搜索功能
- 🔄 题目筛选和排序
- 🔄 学习进度追踪
- 🔄 错题本功能

## 项目结构

```
SmartGaokaoPastPapers/
├── data/
│   └── 10年高考/              # 原始真题数据（9学科×原卷版/解析版）
├── src/
│   ├── knowledge_graph/      # 知识图谱构建模块
│   │   ├── build_math_kg.py
│   │   ├── build_chinese_kg.py
│   │   ├── build_english_kg.py
│   │   ├── build_physics_kg.py
│   │   ├── build_chemistry_kg.py
│   │   ├── build_biology_kg.py
│   │   ├── build_politics_kg.py
│   │   ├── build_history_kg.py
│   │   ├── build_geography_kg.py
│   │   └── build_all_kg.py
│   ├── paper_parser/         # 试卷解析模块
│   │   ├── base_parser.py
│   │   ├── docx_parser.py
│   │   ├── pdf_parser.py
│   │   ├── parser_factory.py
│   │   └── __init__.py
│   ├── question_bank/        # 题库构建模块
│   │   ├── deduplicator.py
│   │   ├── importer.py
│   │   ├── merger.py
│   │   └── __init__.py
│   └── web/                  # 网页展示模块
│       ├── app.py            # FastAPI后端
│       ├── templates/        # HTML模板
│       │   ├── index.html
│       │   ├── subject.html
│       │   ├── knowledge_point.html
│       │   └── question.html
│       └── static/           # 静态资源
│           ├── css/style.css
│           └── js/tree.js
├── database/                 # 数据库目录
│   ├── gaokao.db            # SQLite数据库
│   ├── schema.sql           # 数据库表结构
│   └── init_db.py           # 初始化脚本
├── scripts/                  # 脚本目录
│   └── batch_process_papers.py  # 批量处理脚本
├── output/                   # 输出目录
├── docs/                     # 文档目录
└── assets/                   # 资源目录
    └── images/               # 图片资源
```

## 数据库设计

### 核心表结构
1. **subjects** - 学科表
2. **semesters** - 学期/模块表
3. **chapters** - 章节表
4. **knowledge_points** - 知识点表（核心）
5. **exam_points** - 考点表
6. **kp_relations** - 知识点关联表
7. **papers** - 试卷表
8. **questions** - 题目表（核心）
9. **question_images** - 题目图片表
10. **question_kp_relations** - 题目-知识点关联表
11. **paper_structure** - 试卷结构表

### 知识点ID命名规范
- 格式：`{学科缩写}-{模块缩写}-{序号}`
- 学科缩写：MATH/CHN/ENG/PHY/CHEM/BIO/POL/HIS/GEO
- 示例：MATH-FUNC-001（数学-函数-001号知识点）

### 题目ID命名规范
- 格式：`P-{学科}-{年份}-{地区}-{O/A}-Q{题号}`
- O=原卷版，A=解析版
- 示例：P-MATH-2016-广东-O-Q1

## 技术栈

### 后端
- Python 3.9+
- FastAPI（Web框架）
- SQLite（数据库）
- python-docx（DOCX解析）
- PyMuPDF（PDF解析）
- Jinja2（模板引擎）

### 前端
- HTML5
- CSS3
- JavaScript（原生）
- 响应式设计

## 快速开始

### 1. 初始化数据库
```bash
python3 database/init_db.py
```

### 2. 构建知识图谱
```bash
python3 src/knowledge_graph/build_all_kg.py
```

### 3. 批量处理试卷
```bash
python3 scripts/batch_process_papers.py
```

### 4. 启动Web服务
```bash
cd src/web
python3 app.py
```

访问 http://localhost:8000 查看系统

## 数据来源

- 历年高考真题（2016-2025年）
- 覆盖全国卷、各地方卷
- 包含文/理科分科试卷及新高考卷
- 原卷版 + 解析版

## 学科知识点统计

| 学科 | 知识点 | 考点 |
|------|--------|------|
| 数学 | 143 | 32 |
| 语文 | 47 | 8 |
| 英语 | 42 | 8 |
| 物理 | 76 | 14 |
| 化学 | 55 | 12 |
| 生物 | 60 | 15 |
| 政治 | 34 | 10 |
| 历史 | 49 | 10 |
| 地理 | 32 | 12 |
| **总计** | **538** | **121** |

## 试卷统计

| 学科 | 原卷版 | 解析版 | 合计 |
|------|--------|--------|------|
| 语文 | 167 | 198 | 365 |
| 数学 | 165 | 186 | 351 |
| 英语 | 185 | 211 | 396 |
| 物理 | 245 | 271 | 516 |
| 化学 | 239 | 271 | 510 |
| 生物 | 226 | 260 | 486 |
| 政治 | 217 | 255 | 472 |
| 历史 | 204 | 252 | 456 |
| 地理 | 242 | 273 | 515 |
| **总计** | **1890** | **2177** | **4067** |

## 开发进度

- ✅ 任务1：知识图谱构建（100%）
- 🔄 任务2：真题库构建（70%）
- 🔄 任务3：网页展示系统（60%）

## 后续计划

1. **完善题库**
   - 全学科批量处理
   - 题目-知识点自动关联
   - 数据质量校验

2. **增强Web功能**
   - 搜索功能
   - 题目筛选和排序
   - 学习进度追踪
   - 错题本功能

3. **优化体验**
   - 公式渲染支持
   - 图片懒加载
   - 移动端优化

## 许可证

MIT License
