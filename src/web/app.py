#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web应用后端API
使用FastAPI构建
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import sqlite3
from typing import List, Optional
from pydantic import BaseModel
import time
from functools import lru_cache

app = FastAPI(title="高考真题库系统")

# 部署子路径（如 /pastpapers）；本地开发保持为空
BASE_PATH = os.environ.get("APP_BASE_PATH", "").rstrip("/")

# 数据库路径
DB_PATH = os.environ.get(
    "GAOKAO_DB",
    os.path.join(os.path.dirname(__file__), '../../database/gaokao.db'),
)

# 静态文件和模板
templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
static_dir = os.path.join(os.path.dirname(__file__), 'static')
templates = Jinja2Templates(directory=templates_dir)
templates.env.globals["base"] = BASE_PATH
app.mount("/static", StaticFiles(directory=static_dir), name="static")


# 简单的内存缓存
class SimpleCache:
    def __init__(self, ttl=300):  # 默认5分钟过期
        self.cache = {}
        self.ttl = ttl
    
    def get(self, key):
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return data
            else:
                del self.cache[key]
        return None
    
    def set(self, key, value):
        self.cache[key] = (value, time.time())
    
    def clear(self):
        self.cache.clear()

# 全局缓存
cache = SimpleCache(ttl=600)  # 10分钟缓存

# 模板过滤器
def get_subject_icon(subject_code):
    """获取学科图标"""
    icons = {
        'chinese': '📖',
        'math': '🔢',
        'english': '🔤',
        'physics': '⚛️',
        'chemistry': '🧪',
        'biology': '🧬',
        'politics': '🏛️',
        'history': '📜',
        'geography': '🌍'
    }
    return icons.get(subject_code, '📚')

# 注册过滤器到Jinja2环境
templates.env.filters['get_subject_icon'] = get_subject_icon

# 题目媒体目录
MEDIA_DIR = os.environ.get(
    "MEDIA_DIR",
    os.path.join(os.path.dirname(__file__), '../../assets/question_media'),
)
os.makedirs(MEDIA_DIR, exist_ok=True)


_media_latex_cache = {"ts": 0.0, "map": {}}


def is_usable_inline_latex(latex: str) -> bool:
    """过滤明显错误的 OCR 结果，避免把垃圾公式塞进 MathJax。"""
    if not latex:
        return False
    s = latex.strip().strip("$").strip()
    if not s or len(s) > 120:
        return False
    if abs(s.count("{") - s.count("}")) > 2:
        return False
    # 多行 array / 显示型公式：行内题干用原图更稳
    if "begin{array}" in s or "begin{align}" in s or "displaystyle" in s:
        return False
    if s.count("\\\\") >= 1:
        return False
    if s.count("mathrm") > 4 or "bullet" in s or "oint" in s:
        return False
    if s.count("hat{") > 3 or s.count("overset") + s.count("underset") > 2:
        return False
    if sum(ch.isalnum() for ch in s) < 2:
        return False
    return True


def load_media_latex_map(force: bool = False) -> dict:
    """加载公式图→LaTeX 映射（进程内缓存）。"""
    now = time.time()
    if not force and _media_latex_cache["map"] and now - _media_latex_cache["ts"] < 300:
        return _media_latex_cache["map"]
    mapping = {}
    try:
        conn = sqlite3.connect(DB_PATH)
        try:
            rows = conn.execute(
                "SELECT media_name, latex FROM media_latex "
                "WHERE latex IS NOT NULL AND TRIM(latex) != ''"
            ).fetchall()
        except sqlite3.OperationalError:
            rows = []
        conn.close()
        for name, latex in rows:
            if not name or not is_usable_inline_latex(latex):
                continue
            mapping[name] = latex.strip().strip("$")
            stem = name.rsplit(".", 1)[0]
            mapping.setdefault(stem + ".png", mapping[name])
    except Exception:
        mapping = _media_latex_cache["map"] or {}
    _media_latex_cache["map"] = mapping
    _media_latex_cache["ts"] = now
    return mapping


def render_rich_text(text: str) -> str:
    """将题干中的 LaTeX / MEDIA 标记转为可展示 HTML。

    若 MEDIA 已在 media_latex 中识别为可用行内公式，则优先渲染 MathJax。
    同时提供图片降级方案，确保公式总能显示。
    """
    import html
    import re as _re
    if not text:
        return ""
    latex_map = load_media_latex_map()
    s = html.escape(text)
    
    # 处理填空题下划线
    s = _re.sub(
        r"_{3,}|＿{3,}",
        lambda m: (
            '<span class="blank-line" style="min-width:%.1fem"></span>'
            % (max(4.5, len(m.group(0)) * 0.55))
        ),
        s,
    )
    
    def _media_sub(m):
        name = m.group(1)
        low = name.lower()
        stem = name.rsplit(".", 1)[0]
        
        # 查找对应的LaTeX公式
        latex = (
            latex_map.get(name)
            or latex_map.get(stem + ".png")
            or latex_map.get(stem + ".jpg")
            or latex_map.get(stem + ".wmf")
            or latex_map.get(stem + ".emf")
        )
        
        # 确定图片路径（WMF/EMF转PNG）
        img_name = name
        if low.endswith((".wmf", ".emf")):
            img_name = stem + ".png"
        src = "%s/media/%s" % (BASE_PATH, img_name)
        
        # 如果有可用的LaTeX公式，优先使用MathJax渲染，同时保留图片作为降级
        if latex and is_usable_inline_latex(latex):
            safe_latex = html.escape(latex.strip().strip("$"))
            # MathJax渲染 + 图片降级（默认隐藏图片，MathJax失败时显示）
            return (
                '<span class="q-latex-wrapper" style="display: inline; position: relative;">'
                '<span class="q-latex">$%s$</span>'
                '<span class="q-latex-fallback" style="display: none;">'
                '<img class="q-media" src="%s" alt="公式" loading="lazy" '
                'onerror="this.style.display=\'inline\';this.onerror=null;" '
                'onload="window.__fitQMedia&&window.__fitQMedia(this)">'
                '</span>'
                '</span>'
            ) % (safe_latex, src)
        
        # 没有LaTeX的，直接使用图片
        return (
            '<img class="q-media" src="%s" alt="公式" loading="lazy" '
            'onerror="this.style.opacity=\'0.3\';this.style.border=\'1px dashed #ccc\';this.onerror=null;" '
            'onload="window.__fitQMedia&&window.__fitQMedia(this)">' % src
        )
    
    # 替换MEDIA标记
    s = _re.sub(r"\{\{MEDIA:([^}]+)\}\}", _media_sub, s)
    
    # 处理换行：保留段落结构
    lines = s.split("\n")
    processed_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped:
            # 如果行首是选项（A. B. C. D. 等），添加选项样式
            if _re.match(r'^[A-Z][\.、．]\s*', stripped):
                processed_lines.append('<div class="option-item" style="margin: 0.3em 0;">' + line + '</div>')
            else:
                processed_lines.append(line)
        else:
            processed_lines.append('')
    
    s = "<br>\n".join(processed_lines)
    
    return s


templates.env.filters['rich'] = render_rich_text


def render_markdown_lite(text: str) -> str:
    """轻量 Markdown→HTML（知识点详细解析：标题/列表/加粗/段落）。"""
    import html
    import re as _re
    if not text:
        return ""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    out = []
    in_ul = in_ol = False

    def close_lists():
        nonlocal in_ul, in_ol
        if in_ul:
            out.append("</ul>")
            in_ul = False
        if in_ol:
            out.append("</ol>")
            in_ol = False

    def inline_fmt(s: str) -> str:
        s = html.escape(s)
        s = _re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        return s

    for raw in lines:
        line = raw.rstrip()
        if not line.strip():
            close_lists()
            continue
        if line.startswith("### "):
            close_lists()
            out.append("<h4>%s</h4>" % inline_fmt(line[4:].strip()))
            continue
        if line.startswith("## "):
            close_lists()
            out.append("<h3>%s</h3>" % inline_fmt(line[3:].strip()))
            continue
        if line.startswith("# "):
            close_lists()
            out.append("<h3>%s</h3>" % inline_fmt(line[2:].strip()))
            continue
        m_ul = _re.match(r"^[-*]\s+(.+)$", line)
        if m_ul:
            if in_ol:
                out.append("</ol>")
                in_ol = False
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            out.append("<li>%s</li>" % inline_fmt(m_ul.group(1)))
            continue
        m_ol = _re.match(r"^(\d+)\.\s+(.+)$", line)
        if m_ol:
            if in_ul:
                out.append("</ul>")
                in_ul = False
            if not in_ol:
                out.append("<ol>")
                in_ol = True
            out.append("<li>%s</li>" % inline_fmt(m_ol.group(2)))
            continue
        close_lists()
        out.append("<p>%s</p>" % inline_fmt(line))
    close_lists()
    return "\n".join(out)


templates.env.filters['md'] = render_markdown_lite


# 全局数据库连接（线程安全的方式：每个请求使用独立连接，但缓存常用数据）
def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # 优化SQLite性能
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA cache_size=-20000")  # 20MB缓存
    return conn


# ========== 页面路由 ==========

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """首页 - 学科选择"""
    # 尝试从缓存获取
    cache_key = "index_subjects"
    subjects = cache.get(cache_key)
    
    if not subjects:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, subject_code, subject_name FROM subjects ORDER BY id")
        subjects = [dict(row) for row in cursor.fetchall()]
        conn.close()
        cache.set(cache_key, subjects)
    
    return templates.TemplateResponse(request, "index.html", {
        "subjects": subjects
    })


@app.get("/subject/{subject_code}", response_class=HTMLResponse)
async def subject_page(request: Request, subject_code: str):
    """学科页面 - 知识点树"""
    # 尝试从缓存获取
    cache_key = f"subject_tree_{subject_code}"
    cached_data = cache.get(cache_key)
    
    if cached_data:
        subject, semesters, chapters, knowledge_points = cached_data
    else:
        conn = get_db()
        cursor = conn.cursor()
        
        # 获取学科信息
        cursor.execute("SELECT * FROM subjects WHERE subject_code = ?", (subject_code,))
        subject = cursor.fetchone()
        if not subject:
            conn.close()
            raise HTTPException(status_code=404, detail="学科不存在")
        
        subject = dict(subject)
        
        # 一次性获取所有学期、章节、知识点（用JOIN优化）
        cursor.execute('''
            SELECT 
                sem.id as sem_id, sem.semester_code, sem.semester_name, sem.grade_level, sem.sort_order as sem_order,
                ch.id as ch_id, ch.chapter_code, ch.chapter_name, ch.chapter_number, ch.sort_order as ch_order,
                kp.id as kp_db_id, kp.kp_id as kp_code, kp.kp_name, kp.kp_level, kp.parent_kp_id, 
                kp.description, kp.difficulty_level, kp.importance_level, kp.sort_order as kp_order
            FROM semesters sem
            LEFT JOIN chapters ch ON ch.semester_id = sem.id
            LEFT JOIN knowledge_points kp ON kp.chapter_id = ch.id
            WHERE sem.subject_id = ?
            ORDER BY sem.sort_order, ch.sort_order, kp.sort_order
        ''', (subject['id'],))
        
        rows = cursor.fetchall()
        
        # 组织数据
        semesters = []
        chapters = []
        knowledge_points = []
        
        sem_ids = set()
        ch_ids = set()
        
        for row in rows:
            # 学期
            if row['sem_id'] not in sem_ids:
                sem_ids.add(row['sem_id'])
                semesters.append({
                    'id': row['sem_id'],
                    'semester_code': row['semester_code'],
                    'semester_name': row['semester_name'],
                    'grade_level': row['grade_level'],
                    'sort_order': row['sem_order']
                })
            
            # 章节
            if row['ch_id'] and row['ch_id'] not in ch_ids:
                ch_ids.add(row['ch_id'])
                chapters.append({
                    'id': row['ch_id'],
                    'semester_id': row['sem_id'],
                    'chapter_code': row['chapter_code'],
                    'chapter_name': row['chapter_name'],
                    'chapter_number': row['chapter_number'],
                    'sort_order': row['ch_order']
                })
            
            # 知识点（kp_code 为业务 ID，如 MATH-FUNC-001）
            if row['kp_db_id']:
                knowledge_points.append({
                    'id': row['kp_db_id'],
                    'kp_id': row['kp_code'],
                    'chapter_id': row['ch_id'],
                    'kp_name': row['kp_name'],
                    'kp_level': row['kp_level'],
                    'parent_kp_id': row['parent_kp_id'],
                    'description': row['description'],
                    'difficulty_level': row['difficulty_level'],
                    'importance_level': row['importance_level'],
                    'sort_order': row['kp_order']
                })
        
        conn.close()
        
        # 存入缓存
        cache.set(cache_key, (subject, semesters, chapters, knowledge_points))
    
    return templates.TemplateResponse(request, "subject.html", {
        "subject": subject,
        "semesters": semesters,
        "chapters": chapters,
        "knowledge_points": knowledge_points
    })


@app.get("/knowledge/{kp_id}", response_class=HTMLResponse)
async def knowledge_point_page(request: Request, kp_id: str, page: int = 1, page_size: int = 20):
    """知识点详情页"""
    conn = get_db()
    cursor = conn.cursor()
    
    # 获取知识点信息
    cursor.execute("SELECT * FROM knowledge_points WHERE kp_id = ?", (kp_id,))
    kp = cursor.fetchone()
    if not kp:
        raise HTTPException(status_code=404, detail="知识点不存在")
    
    kp = dict(kp)
    
    # 获取学科信息
    cursor.execute("SELECT * FROM subjects WHERE id = ?", (kp['subject_id'],))
    subject = dict(cursor.fetchone())
    
    # 获取考点
    cursor.execute("SELECT * FROM exam_points WHERE kp_id = ?", (kp['id'],))
    exam_points = [dict(row) for row in cursor.fetchall()]
    
    # 获取相关题目（通过知识点关联表）
    offset = (page - 1) * page_size
    cursor.execute('''
        SELECT q.*, p.paper_id, p.paper_title, p.year, p.region,
               qkr.relevance_score
        FROM question_kp_relations qkr
        JOIN questions q ON qkr.question_id = q.id
        JOIN papers p ON q.paper_id = p.id
        WHERE qkr.kp_id = ?
        ORDER BY qkr.relevance_score DESC, p.year DESC
        LIMIT ? OFFSET ?
    ''', (kp['id'], page_size, offset))
    questions = [dict(row) for row in cursor.fetchall()]
    
    # 获取总数
    cursor.execute('''
        SELECT COUNT(*) as total
        FROM question_kp_relations qkr
        JOIN questions q ON qkr.question_id = q.id
        WHERE qkr.kp_id = ?
    ''', (kp['id'],))
    total = cursor.fetchone()['total']
    
    total_pages = (total + page_size - 1) // page_size
    
    conn.close()
    
    return templates.TemplateResponse(request, "knowledge_point.html", {
        "subject": subject,
        "kp": kp,
        "exam_points": exam_points,
        "questions": questions,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages
    })


@app.get("/question/{question_id}", response_class=HTMLResponse)
async def question_page(request: Request, question_id: str):
    """题目详情页"""
    conn = get_db()
    cursor = conn.cursor()
    
    # 获取题目信息
    cursor.execute('''
        SELECT q.*, p.paper_id, p.paper_title, p.year, p.region
        FROM questions q
        JOIN papers p ON q.paper_id = p.id
        WHERE q.question_id = ?
    ''', (question_id,))
    question = cursor.fetchone()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    
    question = dict(question)
    
    # 获取学科信息
    cursor.execute("SELECT * FROM subjects WHERE id = ?", (question['subject_id'],))
    subject = dict(cursor.fetchone())
    
    # 获取题目图片
    cursor.execute("SELECT * FROM question_images WHERE question_id = ? ORDER BY COALESCE(position_in_question, 0)", (question["id"],))
    images = [dict(row) for row in cursor.fetchall()]
    for img in images:
        p = img.get("image_path") or ""
        if p.lower().endswith((".wmf", ".emf")):
            img["image_path"] = p.rsplit(".", 1)[0] + ".png"

    # 获取相关知识点
    cursor.execute('''
        SELECT kp.kp_id, kp.kp_name, qkr.relevance_score
        FROM question_kp_relations qkr
        JOIN knowledge_points kp ON qkr.kp_id = kp.id
        WHERE qkr.question_id = ?
        ORDER BY qkr.relevance_score DESC
    ''', (question['id'],))
    related_kps = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return templates.TemplateResponse(request, "question.html", {
        "subject": subject,
        "question": question,
        "images": images,
        "related_kps": related_kps
    })


@app.get("/search", response_class=HTMLResponse)
async def search_page(request: Request, q: str = "", subject: str = "", 
                      question_type: str = "", page: int = 1, page_size: int = 20):
    """搜索页面"""
    conn = get_db()
    cursor = conn.cursor()
    
    # 获取所有学科
    cursor.execute("SELECT id, subject_code, subject_name FROM subjects ORDER BY id")
    subjects = [dict(row) for row in cursor.fetchall()]
    
    questions = []
    total = 0
    
    if q:
        # 构建查询
        query = '''
            SELECT q.*, p.paper_id, p.paper_title, p.year, p.region, s.subject_name
            FROM questions q
            JOIN papers p ON q.paper_id = p.id
            JOIN subjects s ON q.subject_id = s.id
            WHERE 1=1
        '''
        params = []
        
        # 关键词搜索
        if q:
            query += " AND q.question_text LIKE ?"
            params.append(f"%{q}%")
        
        # 学科筛选
        if subject:
            query += " AND s.subject_code = ?"
            params.append(subject)
        
        # 题型筛选
        if question_type:
            query += " AND q.question_type = ?"
            params.append(question_type)
        
        # 总数
        count_query = query.replace("SELECT q.*, p.paper_id, p.paper_title, p.year, p.region, s.subject_name", 
                                    "SELECT COUNT(*) as total")
        cursor.execute(count_query, params)
        total = cursor.fetchone()['total']
        
        # 分页查询
        offset = (page - 1) * page_size
        query += " ORDER BY p.year DESC LIMIT ? OFFSET ?"
        params.extend([page_size, offset])
        
        cursor.execute(query, params)
        questions = [dict(row) for row in cursor.fetchall()]
    
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    
    conn.close()
    
    return templates.TemplateResponse(request, "search.html", {
        "subjects": subjects,
        "questions": questions,
        "q": q,
        "subject": subject,
        "question_type": question_type,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages
    })


# ========== API接口 ==========

@app.get("/api/subjects")
async def api_subjects():
    """获取所有学科"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, subject_code, subject_name FROM subjects ORDER BY id")
    subjects = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"subjects": subjects}


@app.get("/api/subject/{subject_code}/knowledge-tree")
async def api_knowledge_tree(subject_code: str):
    """获取学科知识树"""
    conn = get_db()
    cursor = conn.cursor()
    
    # 获取学科
    cursor.execute("SELECT id, subject_code, subject_name FROM subjects WHERE subject_code = ?", (subject_code,))
    subject = cursor.fetchone()
    if not subject:
        raise HTTPException(status_code=404, detail="学科不存在")
    
    subject_id = subject['id']
    
    # 获取学期
    cursor.execute('''
        SELECT id, semester_code, semester_name, grade_level, sort_order 
        FROM semesters WHERE subject_id = ? ORDER BY sort_order
    ''', (subject_id,))
    semesters = [dict(row) for row in cursor.fetchall()]
    
    # 获取章节
    semester_ids = [s['id'] for s in semesters]
    chapters_by_semester = {}
    if semester_ids:
        placeholders = ','.join(['?'] * len(semester_ids))
        cursor.execute(f'''
            SELECT id, semester_id, chapter_code, chapter_name, chapter_number, sort_order
            FROM chapters WHERE semester_id IN ({placeholders}) ORDER BY sort_order
        ''', semester_ids)
        for row in cursor.fetchall():
            ch = dict(row)
            sem_id = ch['semester_id']
            if sem_id not in chapters_by_semester:
                chapters_by_semester[sem_id] = []
            chapters_by_semester[sem_id].append(ch)
    
    # 获取知识点
    all_chapter_ids = []
    for sem_chapters in chapters_by_semester.values():
        all_chapter_ids.extend([c['id'] for c in sem_chapters])
    
    kps_by_chapter = {}
    if all_chapter_ids:
        placeholders = ','.join(['?'] * len(all_chapter_ids))
        cursor.execute(f'''
            SELECT id, kp_id, chapter_id, kp_name, kp_level, parent_kp_id, 
                   description, difficulty_level, importance_level
            FROM knowledge_points WHERE chapter_id IN ({placeholders}) ORDER BY sort_order
        ''', all_chapter_ids)
        for row in cursor.fetchall():
            kp = dict(row)
            ch_id = kp['chapter_id']
            if ch_id not in kps_by_chapter:
                kps_by_chapter[ch_id] = []
            kps_by_chapter[ch_id].append(kp)
    
    conn.close()
    
    # 构建树结构
    tree = []
    for sem in semesters:
        sem_node = {
            'id': sem['id'],
            'code': sem['semester_code'],
            'name': sem['semester_name'],
            'type': 'semester',
            'children': []
        }
        
        for ch in chapters_by_semester.get(sem['id'], []):
            ch_node = {
                'id': ch['id'],
                'code': ch['chapter_code'],
                'name': ch['chapter_name'],
                'type': 'chapter',
                'children': []
            }
            
            for kp in kps_by_chapter.get(ch['id'], []):
                kp_node = {
                    'id': kp['kp_id'],
                    'name': kp['kp_name'],
                    'type': 'knowledge_point',
                    'level': kp['kp_level'],
                    'difficulty': kp['difficulty_level'],
                    'importance': kp['importance_level'],
                    'children': []
                }
                ch_node['children'].append(kp_node)
            
            sem_node['children'].append(ch_node)
        
        tree.append(sem_node)
    
    return {
        'subject': dict(subject),
        'tree': tree
    }


@app.get("/api/knowledge/{kp_id}")
async def api_knowledge_point(kp_id: str):
    """获取知识点详情"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM knowledge_points WHERE kp_id = ?", (kp_id,))
    kp = cursor.fetchone()
    if not kp:
        raise HTTPException(status_code=404, detail="知识点不存在")
    
    kp = dict(kp)
    
    # 获取考点
    cursor.execute("SELECT * FROM exam_points WHERE kp_id = ?", (kp['id'],))
    exam_points = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return {
        'knowledge_point': kp,
        'exam_points': exam_points
    }


@app.get("/api/knowledge/{kp_id}/questions")
async def api_kp_questions(kp_id: str, limit: int = 20, offset: int = 0):
    """获取知识点相关题目"""
    conn = get_db()
    cursor = conn.cursor()
    
    # 先获取知识点的subject_id
    cursor.execute("SELECT subject_id FROM knowledge_points WHERE kp_id = ?", (kp_id,))
    kp = cursor.fetchone()
    if not kp:
        raise HTTPException(status_code=404, detail="知识点不存在")
    
    subject_id = kp['subject_id']
    
    # 获取题目（暂时返回该学科所有题目）
    cursor.execute('''
        SELECT q.question_id, q.question_number, q.question_type, q.question_text,
               p.paper_title, p.year, p.region
        FROM questions q
        JOIN papers p ON q.paper_id = p.id
        WHERE q.subject_id = ?
        ORDER BY p.year DESC, CAST(q.question_number AS INTEGER)
        LIMIT ? OFFSET ?
    ''', (subject_id, limit, offset))
    
    questions = [dict(row) for row in cursor.fetchall()]
    
    # 总数
    cursor.execute('''
        SELECT COUNT(*) FROM questions WHERE subject_id = ?
    ''', (subject_id,))
    total = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        'questions': questions,
        'total': total,
        'limit': limit,
        'offset': offset
    }


@app.get("/api/question/{question_id}")
async def api_question(question_id: str):
    """获取题目详情"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT q.*, p.paper_id, p.paper_title, p.year, p.region
        FROM questions q
        JOIN papers p ON q.paper_id = p.id
        WHERE q.question_id = ?
    ''', (question_id,))
    question = cursor.fetchone()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    
    question = dict(question)
    
    # 获取图片
    cursor.execute("SELECT * FROM question_images WHERE question_id = ? ORDER BY COALESCE(position_in_question, 0)", (question["id"],))
    images = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return {
        'question': question,
        'images': images
    }



@app.get("/media/{media_name}")
async def serve_media(media_name: str):
    """提供题目公式/插图（WMF/EMF 按需转 PNG）"""
    from fastapi.responses import FileResponse, Response
    import subprocess
    import shutil

    safe = os.path.basename(media_name)
    path = os.path.join(MEDIA_DIR, safe)
    # 若请求 png 但只有 wmf/emf，尝试转换
    stem, ext = os.path.splitext(safe)
    if not os.path.isfile(path) and ext.lower() == ".png":
        for cand_ext in (".wmf", ".emf"):
            cand = os.path.join(MEDIA_DIR, stem + cand_ext)
            if os.path.isfile(cand):
                path = cand
                break
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="媒体不存在")

    low = path.lower()
    if low.endswith((".wmf", ".emf")):
        png_path = os.path.splitext(path)[0] + ".png"
        # 如果PNG已存在且不是空文件，直接返回
        if os.path.isfile(png_path) and os.path.getsize(png_path) > 100:
            return FileResponse(png_path, media_type="image/png")
        
        # 尝试转换WMF/EMF为PNG
        success = False
        
        # 方法1: 使用libreoffice转换（质量最好，支持EMF）
        if shutil.which("libreoffice"):
            try:
                result = subprocess.run(
                    ["libreoffice", "--headless", "--convert-to", "png", 
                     "--outdir", MEDIA_DIR, path],
                    capture_output=True, timeout=120, check=False,
                )
                if result.returncode == 0 and os.path.isfile(png_path) and os.path.getsize(png_path) > 100:
                    success = True
            except Exception:
                pass
        
        # 方法2: 使用inkscape转换（支持EMF）
        if not success and shutil.which("inkscape"):
            try:
                result = subprocess.run(
                    ["inkscape", path, "--export-type=png", 
                     "--export-filename", png_path, "--export-dpi", "300"],
                    capture_output=True, timeout=120, check=False,
                )
                if result.returncode == 0 and os.path.isfile(png_path) and os.path.getsize(png_path) > 100:
                    success = True
            except Exception:
                pass
        
        # 方法3: 使用ImageMagick的convert命令（备选方案）
        if not success and shutil.which("convert"):
            try:
                # 高分辨率转换，保留更多细节
                # 对于大文件（示意图），使用较低的DPI以避免文件过大
                file_size = os.path.getsize(path)
                if file_size > 1000000:  # 大于1MB的可能是示意图
                    density = 150
                    max_height = 600
                else:  # 小文件可能是公式
                    density = 600
                    max_height = 200
                
                result = subprocess.run(
                    ["convert", 
                     "-density", str(density),  # 根据文件大小调整DPI
                     "-background", "white",  # 白色背景
                     "-alpha", "remove",  # 移除alpha通道
                     "-alpha", "off",  # 关闭alpha
                     "-flatten",  # 扁平化图层
                     path, 
                     "-trim", "+repage",  # 裁剪空白
                     "-resize", f"x{max_height}>",  # 最大高度
                     "-bordercolor", "white", "-border", "8",  # 增加白色边框
                     "-quality", "95",  # 高质量
                     png_path],
                    capture_output=True, timeout=60, check=False,
                )
                if result.returncode == 0 and os.path.isfile(png_path) and os.path.getsize(png_path) > 100:
                    success = True
            except Exception:
                pass
        
        # 如果转换成功，优化图片
        if success and shutil.which("convert"):
            try:
                # 后处理：优化图片，去除多余空白，确保白色背景
                subprocess.run(
                    ["convert", png_path,
                     "-background", "white",
                     "-alpha", "remove",
                     "-alpha", "off",
                     "-flatten",
                     "-trim", "+repage",
                     "-bordercolor", "white", "-border", "4",
                     png_path],
                    capture_output=True, timeout=30, check=False,
                )
            except Exception:
                pass
        
        if os.path.isfile(png_path) and os.path.getsize(png_path) > 100:
            return FileResponse(png_path, media_type="image/png")
        
        # 无法转换时返回原文件（多数浏览器仍无法显示）
        return FileResponse(path)

    return FileResponse(path)


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "ok", "base_path": BASE_PATH or "/"}


if __name__ == '__main__':
    import uvicorn
    host = os.environ.get("BIND_HOST", "0.0.0.0")
    port = int(os.environ.get("BIND_PORT", "8000"))
    uvicorn.run(app, host=host, port=port)
