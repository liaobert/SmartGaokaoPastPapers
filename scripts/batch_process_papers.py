#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量处理试卷脚本
批量解析指定目录下的所有试卷，去重后存入数据库
"""

import os
import sys
import glob
import json
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from paper_parser import parse_paper, get_parser
from question_bank import QuestionDeduplicator, QuestionBankImporter, PaperMerger


class BatchPaperProcessor:
    """批量试卷处理器"""
    
    def __init__(self, data_dir: str, db_path: str, output_dir: str = ""):
        self.data_dir = data_dir
        self.db_path = db_path
        self.output_dir = output_dir
        self.deduplicator = QuestionDeduplicator()
        self.importer = QuestionBankImporter(db_path)
        self.merger = PaperMerger()
        
        # 统计信息
        self.stats = {
            'total_files': 0,
            'success_files': 0,
            'failed_files': 0,
            'total_questions': 0,
            'unique_questions': 0,
            'failed_details': []
        }
    
    def process_subject(self, subject: str, paper_type: str = "原卷版"):
        """处理指定学科的试卷"""
        subject_dir = os.path.join(self.data_dir, subject, paper_type)
        if not os.path.exists(subject_dir):
            print(f"目录不存在: {subject_dir}")
            return
        
        print(f"\n{'='*60}")
        print(f"处理学科: {subject} - {paper_type}")
        print(f"{'='*60}")
        
        # 获取所有试卷文件
        files = []
        for ext in ['*.docx', '*.pdf', '*.doc']:
            files.extend(glob.glob(os.path.join(subject_dir, ext)))
        
        files.sort()
        print(f"找到 {len(files)} 份试卷")
        
        self.stats['total_files'] += len(files)
        
        # 逐个处理
        for i, file_path in enumerate(files):
            filename = os.path.basename(file_path)
            print(f"\n[{i+1}/{len(files)}] 处理: {filename}")
            
            try:
                # 解析试卷
                paper = parse_paper(file_path)
                print(f"  解析成功: {len(paper.questions)} 道题")
                
                # 去重
                unique_questions = self.deduplicator.deduplicate_questions(paper.questions)
                print(f"  去重后: {len(unique_questions)} 道题")
                
                # 存入数据库
                paper_id = self.importer.import_paper(paper, subject)
                print(f"  入库成功: 试卷ID={paper_id}")
                
                self.stats['success_files'] += 1
                self.stats['total_questions'] += len(paper.questions)
                self.stats['unique_questions'] += len(unique_questions)
                
            except Exception as e:
                print(f"  处理失败: {e}")
                self.stats['failed_files'] += 1
                self.stats['failed_details'].append({
                    'file': filename,
                    'error': str(e)
                })
        
        print(f"\n学科 {subject} 处理完成")
        print(f"  成功: {self.stats['success_files']} 份")
        print(f"  失败: {self.stats['failed_files']} 份")
    
    def process_all_subjects(self):
        """处理所有学科"""
        subjects = ['语文', '数学', '英语', '物理', '化学', '生物', '政治', '历史', '地理']
        
        print("="*60)
        print("开始批量处理所有学科试卷")
        print("="*60)
        
        for subject in subjects:
            # 处理原卷版
            self.process_subject(subject, "原卷版")
            
            # 处理解析版
            self.process_subject(subject, "解析版")
        
        self.print_stats()
    
    def print_stats(self):
        """打印统计信息"""
        print("\n" + "="*60)
        print("批量处理统计")
        print("="*60)
        print(f"总文件数: {self.stats['total_files']}")
        print(f"成功: {self.stats['success_files']}")
        print(f"失败: {self.stats['failed_files']}")
        print(f"总题目数: {self.stats['total_questions']}")
        print(f"去重后题目数: {self.stats['unique_questions']}")
        
        if self.stats['failed_details']:
            print(f"\n失败详情:")
            for detail in self.stats['failed_details'][:10]:  # 只显示前10个
                print(f"  {detail['file']}: {detail['error']}")
            if len(self.stats['failed_details']) > 10:
                print(f"  ... 还有 {len(self.stats['failed_details']) - 10} 个失败")
    
    def save_stats(self, output_file: str):
        """保存统计信息到文件"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)
        print(f"统计信息已保存到: {output_file}")


def main():
    """主函数"""
    data_dir = "/Volumes/yingpan/workspace/AiEdu/SmartGaokaoPastPapers/data/10年高考"
    db_path = "/Volumes/yingpan/workspace/AiEdu/SmartGaokaoPastPapers/database/gaokao.db"
    output_dir = "/Volumes/yingpan/workspace/AiEdu/SmartGaokaoPastPapers/output"
    
    processor = BatchPaperProcessor(data_dir, db_path, output_dir)
    
    # 先测试一个学科
    print("先测试数学学科...")
    processor.process_subject('数学', '原卷版')
    
    # 打印统计
    processor.print_stats()


if __name__ == '__main__':
    main()
