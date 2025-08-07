#!/usr/bin/env python3
"""
DOC 支持功能测试脚本
"""

import os
import sys
import tempfile
from pathlib import Path

# 添加项目路径到 Python 路径
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

try:
    from docx_image_extractor_mcp.core.extractor import extract_images, to_ascii_dirname
    print("✅ 成功导入核心模块")
except ImportError as e:
    print(f"❌ 导入核心模块失败: {e}")
    sys.exit(1)

def test_ascii_conversion():
    """测试中文文件名转ASCII功能"""
    print("\n🧪 测试中文文件名转ASCII功能...")
    
    test_cases = [
        ("测试文档.docx", "ceshi-wendang"),
        ("项目报告.doc", "xiangmu-baogao"),
        ("会议纪要 2024.docx", "huiyi-jiyao-2024"),
    ]
    
    for original, expected_prefix in test_cases:
        result = to_ascii_dirname(original)
        print(f"  {original} -> {result}")
        if expected_prefix in result:
            print(f"    ✅ 转换成功")
        else:
            print(f"    ❌ 转换失败，期望包含: {expected_prefix}")

def test_file_extension_validation():
    """测试文件扩展名验证"""
    print("\n🧪 测试文件扩展名验证...")
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # 测试不支持的文件格式
        unsupported_file = temp_path / "test.txt"
        unsupported_file.write_text("test content")
        
        try:
            result = extract_images(str(unsupported_file))
            print(f"    ❌ 应该拒绝不支持的文件格式")
        except Exception as e:
            print(f"    ✅ 正确拒绝不支持的文件格式: {e}")
        
        # 测试不存在的文件
        try:
            result = extract_images("nonexistent.docx")
            print(f"    ❌ 应该拒绝不存在的文件")
        except Exception as e:
            print(f"    ✅ 正确拒绝不存在的文件: {e}")

def test_dependencies():
    """测试依赖项是否正确安装"""
    print("\n🧪 测试依赖项...")
    
    dependencies = [
        ("olefile", "DOC文件支持"),
        ("pypinyin", "中文转拼音"),
        ("zipfile", "DOCX文件支持"),
    ]
    
    for module_name, description in dependencies:
        try:
            if module_name == "zipfile":
                import zipfile
            elif module_name == "olefile":
                import olefile
            elif module_name == "pypinyin":
                import pypinyin
            print(f"    ✅ {description} ({module_name}) 可用")
        except ImportError:
            print(f"    ❌ {description} ({module_name}) 不可用")

def main():
    """主测试函数"""
    print("🚀 开始 DOC/DOCX 图片提取器功能测试")
    print("=" * 50)
    
    test_dependencies()
    test_ascii_conversion()
    test_file_extension_validation()
    
    print("\n" + "=" * 50)
    print("✅ 测试完成！")
    print("\n📝 注意事项:")
    print("  - 要测试实际的图片提取功能，请准备包含图片的DOC/DOCX文件")
    print("  - 使用命令: python -m docx_image_extractor_mcp.interfaces.cli extract your_file.doc")
    print("  - 或者: python -m docx_image_extractor_mcp.interfaces.cli extract your_file.docx")

if __name__ == "__main__":
    main()