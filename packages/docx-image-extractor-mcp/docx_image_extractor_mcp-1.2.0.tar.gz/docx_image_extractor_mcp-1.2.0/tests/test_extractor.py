"""
测试图片提取器模块
"""

import os
import tempfile
import unittest
import zipfile
from pathlib import Path

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from docx_image_extractor_mcp.core.extractor import to_ascii_dirname, extract_images, _detect_image_format
from docx_image_extractor_mcp.core.config import Config, DEFAULT_CONFIG


class TestExtractor(unittest.TestCase):
    """测试图片提取器"""
    
    def test_to_ascii_dirname(self):
        """测试文档名转换"""
        # 测试中文转拼音
        self.assertEqual(to_ascii_dirname("测试文档.docx"), "ceshiwendang")
        
        # 测试英文
        self.assertEqual(to_ascii_dirname("test_document.docx"), "testdocument")
        
        # 测试混合
        self.assertEqual(to_ascii_dirname("Test测试123.docx"), "testceshi123")
        
        # 测试特殊字符
        self.assertEqual(to_ascii_dirname("文档-名称_test.docx"), "wendangmingchengtest")
        
        # 测试空字符串
        self.assertEqual(to_ascii_dirname(""), "")
        
        # 测试只有扩展名
        self.assertEqual(to_ascii_dirname(".docx"), "")
    
    def test_extract_images_file_not_exists(self):
        """测试文件不存在的情况"""
        result = extract_images("nonexistent.docx")
        self.assertFalse(result['success'])
        self.assertIn("文档不存在", result['msg'])
        self.assertEqual(result['count'], 0)
    
    def test_extract_images_wrong_extension(self):
        """测试错误的文件扩展名"""
        with tempfile.NamedTemporaryFile(suffix=".txt") as tmp:
            result = extract_images(tmp.name)
            self.assertFalse(result['success'])
            self.assertIn("只支持.docx文件", result['msg'])
            self.assertEqual(result['count'], 0)
    
    def test_extract_images_invalid_zip(self):
        """测试无效的ZIP文件"""
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
            tmp.write(b"invalid zip content")
            tmp.flush()
            tmp_name = tmp.name
            
        try:
            result = extract_images(tmp_name)
            self.assertFalse(result['success'])
            self.assertIn("无效的DOCX文件", result['msg'])
        finally:
            try:
                os.unlink(tmp_name)
            except (OSError, PermissionError):
                pass  # 忽略删除失败
    
    def test_detect_image_format(self):
        """测试图片格式检测"""
        # 创建一个临时ZIP文件用于测试
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp_zip:
            tmp_zip_name = tmp_zip.name
            
        try:
            with zipfile.ZipFile(tmp_zip_name, 'w') as zf:
                # 添加PNG文件头
                zf.writestr("test.png", b'\x89PNG\r\n\x1a\n' + b'fake png data')
                # 添加JPEG文件头
                zf.writestr("test.jpg", b'\xff\xd8\xff\xe0' + b'fake jpg data')
                # 添加未知格式
                zf.writestr("test.unknown", b'unknown format')
            
            with zipfile.ZipFile(tmp_zip_name, 'r') as zf:
                # 测试PNG检测
                self.assertEqual(_detect_image_format(zf, "test.png"), ".png")
                # 测试JPEG检测
                self.assertEqual(_detect_image_format(zf, "test.jpg"), ".jpg")
                # 测试未知格式（应该返回默认的.png）
                self.assertEqual(_detect_image_format(zf, "test.unknown"), ".png")
        finally:
            try:
                os.unlink(tmp_zip_name)
            except (OSError, PermissionError):
                pass  # 忽略删除失败


class TestConfig(unittest.TestCase):
    """测试配置模块"""
    
    def test_default_config(self):
        """测试默认配置"""
        config = Config()
        self.assertEqual(config.base_image_dir, DEFAULT_CONFIG["base_image_dir"])
        self.assertEqual(config.image_naming_prefix, DEFAULT_CONFIG["image_naming"]["prefix"])
        self.assertEqual(config.image_naming_padding, DEFAULT_CONFIG["image_naming"]["padding"])
    
    def test_config_get_set(self):
        """测试配置的获取和设置"""
        config = Config()
        
        # 测试设置和获取
        config.set("test.key", "test_value")
        self.assertEqual(config.get("test.key"), "test_value")
        
        # 测试默认值
        self.assertEqual(config.get("nonexistent.key", "default"), "default")
    
    def test_config_from_dict(self):
        """测试从字典加载配置"""
        config = Config()
        user_config = {
            "base_image_dir": "custom_images",
            "image_naming": {
                "prefix": "pic"
            }
        }
        
        config._merge_config(user_config)
        self.assertEqual(config.base_image_dir, "custom_images")
        self.assertEqual(config.image_naming_prefix, "pic")
        # 确保其他配置保持默认值
        self.assertEqual(config.image_naming_padding, DEFAULT_CONFIG["image_naming"]["padding"])


if __name__ == "__main__":
    unittest.main()