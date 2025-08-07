"""
性能测试模块
"""

import os
import sys
import time
import tempfile
import zipfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from docx_image_extractor_mcp.core.extractor import extract_images


class TestPerformance(unittest.TestCase):
    """性能测试"""
    
    def create_test_docx(self, image_count: int = 10, image_size: int = 1024) -> str:
        """创建测试用的DOCX文件"""
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
            tmp_name = tmp.name
            
        with zipfile.ZipFile(tmp_name, 'w') as zf:
            # 创建基本的DOCX结构
            zf.writestr("[Content_Types].xml", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
    <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
    <Default Extension="xml" ContentType="application/xml"/>
    <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>""")
            
            zf.writestr("_rels/.rels", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>""")
            
            zf.writestr("word/document.xml", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
    <w:body>
        <w:p><w:r><w:t>Test document</w:t></w:r></w:p>
    </w:body>
</w:document>""")
            
            # 添加测试图片
            fake_image_data = b'\x89PNG\r\n\x1a\n' + b'0' * image_size
            for i in range(image_count):
                zf.writestr(f"word/media/image{i+1}.png", fake_image_data)
        
        return tmp_name
    
    def test_small_file_performance(self):
        """测试小文件性能（10张图片）"""
        docx_path = self.create_test_docx(10, 1024)
        
        try:
            start_time = time.time()
            result = extract_images(docx_path)
            end_time = time.time()
            
            self.assertTrue(result['success'])
            self.assertEqual(result['count'], 10)
            
            processing_time = end_time - start_time
            print(f"小文件处理时间: {processing_time:.3f}秒")
            
            # 小文件应该在1秒内完成
            self.assertLess(processing_time, 1.0)
            
        finally:
            Path(docx_path).unlink(missing_ok=True)
    
    def test_medium_file_performance(self):
        """测试中等文件性能（50张图片）"""
        docx_path = self.create_test_docx(50, 2048)
        
        try:
            start_time = time.time()
            result = extract_images(docx_path)
            end_time = time.time()
            
            self.assertTrue(result['success'])
            self.assertEqual(result['count'], 50)
            
            processing_time = end_time - start_time
            print(f"中等文件处理时间: {processing_time:.3f}秒")
            
            # 中等文件应该在3秒内完成
            self.assertLess(processing_time, 3.0)
            
        finally:
            Path(docx_path).unlink(missing_ok=True)
    
    def test_large_file_performance(self):
        """测试大文件性能（100张图片）"""
        docx_path = self.create_test_docx(100, 4096)
        
        try:
            start_time = time.time()
            result = extract_images(docx_path)
            end_time = time.time()
            
            self.assertTrue(result['success'])
            self.assertEqual(result['count'], 100)
            
            processing_time = end_time - start_time
            print(f"大文件处理时间: {processing_time:.3f}秒")
            
            # 大文件应该在10秒内完成
            self.assertLess(processing_time, 10.0)
            
        finally:
            Path(docx_path).unlink(missing_ok=True)
    
    def test_memory_usage(self):
        """测试内存使用情况"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 处理多个文件
        for i in range(5):
            docx_path = self.create_test_docx(20, 2048)
            try:
                result = extract_images(docx_path)
                self.assertTrue(result['success'])
            finally:
                Path(docx_path).unlink(missing_ok=True)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"内存使用: 初始 {initial_memory:.1f}MB, 最终 {final_memory:.1f}MB, 增加 {memory_increase:.1f}MB")
        
        # 内存增长应该控制在合理范围内（小于100MB）
        self.assertLess(memory_increase, 100)


if __name__ == "__main__":
    # 只有在安装了psutil的情况下才运行内存测试
    try:
        import psutil
        unittest.main()
    except ImportError:
        print("警告: 未安装psutil，跳过内存测试")
        # 运行除内存测试外的其他测试
        suite = unittest.TestLoader().loadTestsFromTestCase(TestPerformance)
        filtered_suite = unittest.TestSuite()
        for test in suite:
            if "memory" not in test._testMethodName:
                filtered_suite.addTest(test)
        unittest.TextTestRunner().run(filtered_suite)