#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
试卷解析器工厂
根据文件格式选择合适的解析器
"""

import os
from .base_parser import BasePaperParser, Paper
from .docx_parser import DocxPaperParser
from .pdf_parser import PdfPaperParser


def get_parser(file_path: str, output_dir: str = "") -> BasePaperParser:
    """根据文件扩展名获取对应的解析器"""
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == '.docx':
        return DocxPaperParser(file_path, output_dir)
    elif ext == '.pdf':
        return PdfPaperParser(file_path, output_dir)
    elif ext == '.doc':
        # .doc文件需要先转换为.docx
        return DocPaperParser(file_path, output_dir)
    else:
        raise ValueError(f"不支持的文件格式: {ext}")


class DocPaperParser(BasePaperParser):
    """DOC格式试卷解析器（先转换为docx再解析）"""
    
    def __init__(self, file_path: str, output_dir: str = ""):
        super().__init__(file_path, output_dir)
        self._docx_path = None
    
    def _convert_to_docx(self) -> str:
        """将doc转换为docx（优先 LibreOffice，其次 macOS textutil）"""
        import shutil
        import subprocess
        import tempfile

        temp_dir = tempfile.mkdtemp()
        base = os.path.splitext(os.path.basename(self.file_path))[0]
        output_path = os.path.join(temp_dir, base + '.docx')

        soffice = shutil.which('soffice') or shutil.which('libreoffice')
        errors = []
        if soffice:
            try:
                result = subprocess.run(
                    [soffice, '--headless', '--convert-to', 'docx', '--outdir', temp_dir, self.file_path],
                    capture_output=True, text=True, timeout=120,
                )
                # LibreOffice 输出文件名基于原名
                candidates = [
                    output_path,
                    os.path.join(temp_dir, base + '.docx'),
                ]
                for c in os.listdir(temp_dir):
                    if c.lower().endswith('.docx'):
                        candidates.append(os.path.join(temp_dir, c))
                for c in candidates:
                    if os.path.exists(c) and os.path.getsize(c) > 0:
                        self._docx_path = c
                        return c
                errors.append(f"soffice: {result.stderr or result.stdout}")
            except Exception as e:
                errors.append(f"soffice: {e}")

        if shutil.which('textutil'):
            try:
                result = subprocess.run(
                    ['textutil', '-convert', 'docx', self.file_path, '-output', output_path],
                    capture_output=True, text=True, timeout=60,
                )
                if result.returncode == 0 and os.path.exists(output_path):
                    self._docx_path = output_path
                    return output_path
                errors.append(f"textutil: {result.stderr}")
            except Exception as e:
                errors.append(f"textutil: {e}")

        raise Exception("doc转docx失败: " + "; ".join(errors) if errors else "无可用转换工具")
    
    def parse(self) -> Paper:
        """解析doc试卷（先转docx再解析）"""
        docx_path = self._convert_to_docx()
        parser = DocxPaperParser(docx_path, self.output_dir)
        paper = parser.parse()
        
        # 修正文件名等信息
        paper.paper_name = self.paper.paper_name
        paper.year = self.paper.year
        paper.region = self.paper.region
        paper.paper_type = self.paper.paper_type
        
        return paper
    
    def extract_images_to_dir(self, output_dir: str) -> dict:
        """提取图片"""
        docx_path = self._convert_to_docx()
        parser = DocxPaperParser(docx_path, output_dir)
        return parser.extract_images_to_dir(output_dir)


def parse_paper(file_path: str, output_dir: str = "") -> Paper:
    """便捷函数：解析试卷文件"""
    parser = get_parser(file_path, output_dir)
    return parser.parse()
