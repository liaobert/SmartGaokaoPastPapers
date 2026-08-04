#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
试卷解析模块
"""

from .base_parser import BasePaperParser, Paper, Question, QuestionImage
from .docx_parser import DocxPaperParser
from .pdf_parser import PdfPaperParser
from .parser_factory import get_parser, parse_paper

__all__ = [
    'BasePaperParser', 'Paper', 'Question', 'QuestionImage',
    'DocxPaperParser', 'PdfPaperParser',
    'get_parser', 'parse_paper'
]
