-- ============================================
-- SmartGaokaoPastPapers 数据库Schema
-- 高考真题智能题库系统
-- ============================================

-- 启用外键约束
PRAGMA foreign_keys = ON;

-- ============================================
-- 1. 学科表
-- ============================================
CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_code VARCHAR(10) UNIQUE NOT NULL,  -- 学科代码: chinese, math, english, physics, chemistry, biology, politics, history, geography
    subject_name VARCHAR(20) NOT NULL,         -- 学科名称: 语文、数学、英语等
    description TEXT,                          -- 学科描述
    sort_order INTEGER DEFAULT 0,              -- 排序
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 2. 学期/模块表
-- ============================================
CREATE TABLE IF NOT EXISTS semesters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL,
    semester_code VARCHAR(50) NOT NULL,        -- 学期/模块代码: compulsory1, elective1 等
    semester_name VARCHAR(100) NOT NULL,       -- 学期/模块名称: 必修一、选修一等
    grade_level VARCHAR(20),                   -- 年级: 高一、高二、高三
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_id) REFERENCES subjects(id),
    UNIQUE(subject_id, semester_code)
);

-- ============================================
-- 3. 章节表
-- ============================================
CREATE TABLE IF NOT EXISTS chapters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    semester_id INTEGER NOT NULL,
    chapter_code VARCHAR(50) NOT NULL,         -- 章节代码
    chapter_name VARCHAR(200) NOT NULL,        -- 章节名称
    chapter_number VARCHAR(20),                -- 章节序号
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (semester_id) REFERENCES semesters(id),
    UNIQUE(semester_id, chapter_code)
);

-- ============================================
-- 4. 知识点表（核心）
-- ============================================
CREATE TABLE IF NOT EXISTS knowledge_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kp_id VARCHAR(50) UNIQUE NOT NULL,         -- 知识点唯一ID: MATH-ALG-001
    subject_id INTEGER NOT NULL,
    chapter_id INTEGER,
    parent_kp_id INTEGER,                      -- 父知识点ID（用于层级结构）
    kp_name VARCHAR(200) NOT NULL,             -- 知识点名称
    kp_level INTEGER DEFAULT 1,                -- 知识点层级: 1-一级, 2-二级, 3-三级
    description TEXT,                          -- 知识点描述
    content TEXT,                              -- 知识点详细内容/解析
    difficulty_level INTEGER DEFAULT 2,        -- 难度等级: 1-简单, 2-中等, 3-困难
    importance_level INTEGER DEFAULT 2,        -- 重要程度: 1-了解, 2-理解, 3-掌握, 4-应用
    exam_frequency INTEGER DEFAULT 0,          -- 高考考察频率
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_id) REFERENCES subjects(id),
    FOREIGN KEY (chapter_id) REFERENCES chapters(id),
    FOREIGN KEY (parent_kp_id) REFERENCES knowledge_points(id)
);

-- ============================================
-- 5. 考点表
-- ============================================
CREATE TABLE IF NOT EXISTS exam_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ep_id VARCHAR(50) UNIQUE NOT NULL,         -- 考点唯一ID
    kp_id INTEGER NOT NULL,                    -- 关联知识点ID
    ep_name VARCHAR(200) NOT NULL,             -- 考点名称
    description TEXT,                          -- 考点描述
    exam_type VARCHAR(50),                     -- 考察题型: 选择题、填空题、解答题等
    difficulty_level INTEGER DEFAULT 2,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (kp_id) REFERENCES knowledge_points(id)
);

-- ============================================
-- 6. 知识点关联表（知识图谱边）
-- ============================================
CREATE TABLE IF NOT EXISTS kp_relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_kp_id INTEGER NOT NULL,               -- 源知识点
    to_kp_id INTEGER NOT NULL,                 -- 目标知识点
    relation_type VARCHAR(50) NOT NULL,        -- 关系类型: prerequisite(前置), related(相关), extends(扩展), part_of(包含)
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (from_kp_id) REFERENCES knowledge_points(id),
    FOREIGN KEY (to_kp_id) REFERENCES knowledge_points(id),
    UNIQUE(from_kp_id, to_kp_id, relation_type)
);

-- ============================================
-- 7. 试卷表
-- ============================================
CREATE TABLE IF NOT EXISTS papers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paper_id VARCHAR(100) UNIQUE NOT NULL,     -- 试卷唯一ID
    subject_id INTEGER NOT NULL,
    paper_title VARCHAR(500) NOT NULL,         -- 试卷标题
    year INTEGER,                              -- 年份
    region VARCHAR(100),                       -- 地区: 全国卷I、北京、上海等
    paper_type VARCHAR(50),                    -- 试卷类型: 文科、理科、新高考等
    paper_version VARCHAR(50),                 -- 版本: 原卷版、解析版
    total_score INTEGER,                       -- 总分
    total_questions INTEGER,                   -- 题目总数
    duration INTEGER,                          -- 考试时长（分钟）
    source_file VARCHAR(500),                  -- 源文件路径
    file_type VARCHAR(20),                     -- 文件类型: doc, docx, pdf
    parsed_status INTEGER DEFAULT 0,           -- 解析状态: 0-未解析, 1-解析中, 2-已完成, 3-失败
    parsed_at TIMESTAMP,                       -- 解析时间
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_id) REFERENCES subjects(id)
);

-- ============================================
-- 8. 题目表（核心）
-- ============================================
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id VARCHAR(100) UNIQUE NOT NULL,  -- 题目唯一ID
    subject_id INTEGER NOT NULL,
    paper_id INTEGER,                          -- 所属试卷ID
    question_number VARCHAR(50),               -- 题目编号
    question_type VARCHAR(50),                 -- 题型: 选择题、填空题、解答题、阅读理解等
    question_section VARCHAR(100),             -- 题目所在大题: 第Ⅰ卷、第二大题等
    difficulty_level INTEGER DEFAULT 2,        -- 难度等级
    score_value FLOAT,                         -- 分值
    question_text TEXT NOT NULL,               -- 题干文本（含图片引用标记）
    options_json TEXT,                         -- 选项JSON（选择题用）
    answer_text TEXT,                          -- 答案文本
    analysis_text TEXT,                        -- 解析文本
    has_image INTEGER DEFAULT 0,               -- 是否包含图片
    has_formula INTEGER DEFAULT 0,             -- 是否包含公式
    content_hash VARCHAR(64),                  -- 内容哈希（用于去重）
    source_type VARCHAR(20) DEFAULT 'original',-- 来源类型: original(原卷), analysis(解析), merged(合并)
    merged_question_id INTEGER,                -- 合并后的题目ID
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_id) REFERENCES subjects(id),
    FOREIGN KEY (paper_id) REFERENCES papers(id)
);

-- ============================================
-- 9. 题目图片表
-- ============================================
CREATE TABLE IF NOT EXISTS question_images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_id VARCHAR(100) UNIQUE NOT NULL,     -- 图片唯一ID: IMG-xxxxxx
    question_id INTEGER NOT NULL,              -- 所属题目ID
    image_type VARCHAR(50),                    -- 图片类型: question(题干), option(选项), answer(答案), analysis(解析), formula(公式), diagram(图形)
    image_format VARCHAR(20),                  -- 图片格式: png, jpg, gif等
    image_path VARCHAR(500),                   -- 图片存储路径
    image_width INTEGER,                       -- 图片宽度
    image_height INTEGER,                      -- 图片高度
    description TEXT,                          -- 图片描述/alt文本
    position_in_question INTEGER,              -- 在题目中的位置序号
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (question_id) REFERENCES questions(id)
);

-- ============================================
-- 10. 题目-知识点关联表
-- ============================================
CREATE TABLE IF NOT EXISTS question_kp_relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER NOT NULL,
    kp_id INTEGER NOT NULL,
    relation_type VARCHAR(50) DEFAULT 'main',  -- 关系类型: main(主要考点), related(相关知识点)
    relevance_score FLOAT DEFAULT 1.0,         -- 关联度分数
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (question_id) REFERENCES questions(id),
    FOREIGN KEY (kp_id) REFERENCES knowledge_points(id),
    UNIQUE(question_id, kp_id, relation_type)
);

-- ============================================
-- 11. 试卷结构表（大题/小题结构）
-- ============================================
CREATE TABLE IF NOT EXISTS paper_structure (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paper_id INTEGER NOT NULL,
    section_title VARCHAR(200),                -- 大题标题
    section_type VARCHAR(50),                  -- 题型分类
    section_number VARCHAR(20),                -- 大题序号
    question_count INTEGER,                    -- 题目数量
    total_score FLOAT,                         -- 总分
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (paper_id) REFERENCES papers(id)
);

-- ============================================
-- 索引
-- ============================================
CREATE INDEX IF NOT EXISTS idx_kp_subject ON knowledge_points(subject_id);
CREATE INDEX IF NOT EXISTS idx_kp_chapter ON knowledge_points(chapter_id);
CREATE INDEX IF NOT EXISTS idx_kp_parent ON knowledge_points(parent_kp_id);
CREATE INDEX IF NOT EXISTS idx_kp_level ON knowledge_points(kp_level);
CREATE INDEX IF NOT EXISTS idx_questions_subject ON questions(subject_id);
CREATE INDEX IF NOT EXISTS idx_questions_paper ON questions(paper_id);
CREATE INDEX IF NOT EXISTS idx_questions_type ON questions(question_type);
CREATE INDEX IF NOT EXISTS idx_questions_hash ON questions(content_hash);
CREATE INDEX IF NOT EXISTS idx_question_img_qid ON question_images(question_id);
CREATE INDEX IF NOT EXISTS idx_qkp_kp ON question_kp_relations(kp_id);
CREATE INDEX IF NOT EXISTS idx_qkp_question ON question_kp_relations(question_id);
CREATE INDEX IF NOT EXISTS idx_papers_subject ON papers(subject_id);
CREATE INDEX IF NOT EXISTS idx_papers_year ON papers(year);
CREATE INDEX IF NOT EXISTS idx_papers_region ON papers(region);
CREATE INDEX IF NOT EXISTS idx_exam_points_kp ON exam_points(kp_id);
CREATE INDEX IF NOT EXISTS idx_kp_relations_from ON kp_relations(from_kp_id);
CREATE INDEX IF NOT EXISTS idx_kp_relations_to ON kp_relations(to_kp_id);

-- ============================================
-- 视图：知识点题目统计视图
-- ============================================
CREATE VIEW IF NOT EXISTS v_kp_question_stats AS
SELECT 
    kp.id as kp_id,
    kp.kp_name,
    kp.subject_id,
    COUNT(DISTINCT qkr.question_id) as question_count,
    COUNT(DISTINCT CASE WHEN q.question_type = '选择题' THEN qkr.question_id END) as choice_count,
    COUNT(DISTINCT CASE WHEN q.question_type = '填空题' THEN qkr.question_id END) as fill_count,
    COUNT(DISTINCT CASE WHEN q.question_type = '解答题' THEN qkr.question_id END) as answer_count
FROM knowledge_points kp
LEFT JOIN question_kp_relations qkr ON kp.id = qkr.kp_id
LEFT JOIN questions q ON qkr.question_id = q.id
GROUP BY kp.id;
