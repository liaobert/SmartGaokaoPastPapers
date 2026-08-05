-- ???? ? LaTeX ??????
CREATE TABLE IF NOT EXISTS media_latex (
    media_name VARCHAR(200) PRIMARY KEY,
    latex TEXT NOT NULL,
    method VARCHAR(40) DEFAULT 'pix2tex',
    confidence REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_media_latex_updated ON media_latex(updated_at);
