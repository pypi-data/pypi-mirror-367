#!/usr/bin/env python3
"""
自动化发布脚本
用于将项目发布到 PyPI
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import argparse


class PublishManager:
    """发布管理器"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.dist_dir = project_root / "dist"
        self.build_dir = project_root / "build"
        
    def run_command(self, cmd: list, check: bool = True) -> subprocess.CompletedProcess:
        """运行命令"""
        print(f"🔧 执行命令: {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, check=check, capture_output=True, text=True, cwd=self.project_root)
            if result.stdout:
                print(f"✅ 输出: {result.stdout}")
            return result
        except subprocess.CalledProcessError as e:
            print(f"❌ 命令执行失败: {e}")
            if e.stderr:
                print(f"错误信息: {e.stderr}")
            raise
    
    def clean_build_dirs(self):
        """清理构建目录"""
        print("🧹 清理构建目录...")
        
        dirs_to_clean = [
            self.dist_dir,
            self.build_dir,
            self.project_root / "src" / "docx_image_extractor_mcp.egg-info"
        ]
        
        for dir_path in dirs_to_clean:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"   删除: {dir_path}")
    
    def run_tests(self):
        """运行测试"""
        print("🧪 运行测试...")
        self.run_command([sys.executable, "-m", "pytest", "tests/", "-v"])
    
    def check_tools(self):
        """检查必要工具"""
        print("🔍 检查发布工具...")
        
        tools = ["build", "twine"]
        for tool in tools:
            try:
                self.run_command([sys.executable, "-m", tool, "--version"])
            except subprocess.CalledProcessError:
                print(f"❌ 工具 {tool} 未安装")
                print(f"请运行: pip install {tool}")
                sys.exit(1)
    
    def build_package(self):
        """构建包"""
        print("📦 构建包...")
        self.run_command([sys.executable, "-m", "build"])
        
        # 检查生成的文件
        if not self.dist_dir.exists():
            raise RuntimeError("构建失败：dist 目录不存在")
        
        files = list(self.dist_dir.glob("*"))
        if not files:
            raise RuntimeError("构建失败：没有生成文件")
        
        print("✅ 构建完成，生成文件:")
        for file in files:
            print(f"   {file.name}")
    
    def test_install(self):
        """测试安装"""
        print("🧪 测试本地安装...")
        
        # 查找wheel文件
        wheel_files = list(self.dist_dir.glob("*.whl"))
        if not wheel_files:
            raise RuntimeError("未找到wheel文件")
        
        wheel_file = wheel_files[0]
        
        # 创建临时虚拟环境进行测试
        test_env = self.project_root / "test_env"
        if test_env.exists():
            shutil.rmtree(test_env)
        
        try:
            # 创建虚拟环境
            self.run_command([sys.executable, "-m", "venv", str(test_env)])
            
            # 获取虚拟环境的python路径
            if os.name == 'nt':  # Windows
                venv_python = test_env / "Scripts" / "python.exe"
            else:  # Unix/Linux/Mac
                venv_python = test_env / "bin" / "python"
            
            # 在虚拟环境中安装包
            self.run_command([str(venv_python), "-m", "pip", "install", str(wheel_file)])
            
            # 测试导入
            self.run_command([str(venv_python), "-c", "import docx_image_extractor_mcp; print('导入成功')"])
            
            # 测试命令行工具
            self.run_command([str(venv_python), "-m", "docx_image_extractor_mcp.main", "--help"])
            
            print("✅ 本地安装测试通过")
            
        finally:
            # 清理测试环境
            if test_env.exists():
                shutil.rmtree(test_env)
    
    def upload_to_testpypi(self):
        """上传到测试PyPI"""
        print("🚀 上传到测试PyPI...")
        self.run_command([
            sys.executable, "-m", "twine", "upload",
            "--repository", "testpypi",
            "dist/*"
        ])
    
    def upload_to_pypi(self):
        """上传到正式PyPI"""
        print("🚀 上传到正式PyPI...")
        
        # 确认操作
        response = input("⚠️  确定要发布到正式PyPI吗？(yes/no): ")
        if response.lower() != 'yes':
            print("❌ 取消发布")
            return
        
        self.run_command([
            sys.executable, "-m", "twine", "upload",
            "dist/*"
        ])
    
    def publish(self, test_only: bool = False, skip_tests: bool = False):
        """完整发布流程"""
        print("🎯 开始发布流程...")
        
        try:
            # 1. 检查工具
            self.check_tools()
            
            # 2. 运行测试
            if not skip_tests:
                self.run_tests()
            
            # 3. 清理构建目录
            self.clean_build_dirs()
            
            # 4. 构建包
            self.build_package()
            
            # 5. 测试安装
            self.test_install()
            
            # 6. 上传
            if test_only:
                self.upload_to_testpypi()
                print("✅ 已发布到测试PyPI")
                print("🔗 查看: https://test.pypi.org/project/docx-image-extractor-mcp/")
            else:
                # 先发布到测试环境
                try:
                    self.upload_to_testpypi()
                    print("✅ 已发布到测试PyPI")
                except subprocess.CalledProcessError as e:
                    if "already exists" in str(e.stderr):
                        print("⚠️  测试PyPI版本已存在，跳过")
                    else:
                        raise
                
                # 再发布到正式环境
                self.upload_to_pypi()
                print("🎉 发布完成！")
                print("🔗 查看: https://pypi.org/project/docx-image-extractor-mcp/")
                print("📦 安装: pip install docx-image-extractor-mcp")
            
        except Exception as e:
            print(f"❌ 发布失败: {e}")
            sys.exit(1)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="自动化发布脚本")
    parser.add_argument("--test-only", action="store_true", help="仅发布到测试PyPI")
    parser.add_argument("--skip-tests", action="store_true", help="跳过测试")
    
    args = parser.parse_args()
    
    # 获取项目根目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # 创建发布管理器
    publisher = PublishManager(project_root)
    
    # 执行发布
    publisher.publish(test_only=args.test_only, skip_tests=args.skip_tests)


if __name__ == "__main__":
    main()