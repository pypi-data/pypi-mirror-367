# 📦 项目发布指南

本指南将帮助您将 DOCX Image Extractor MCP 项目发布到 PyPI，让全世界的用户都能轻松安装和使用。

## 🎯 发布目标

- 发布到 PyPI（Python Package Index）
- 用户可通过 `pip install docx-image-extractor-mcp` 安装
- 支持 Claude Desktop MCP 集成
- 提供命令行工具

## 📋 发布前准备

### 1. 环境检查

确保您的开发环境已安装必要工具：

```bash
# 安装发布工具
py -m pip install build twine wheel setuptools

# 检查工具版本
py -m build --version
py -m twine --version
```

### 2. 代码质量检查

```bash
# 运行测试
pytest tests/ -v

# 检查代码格式
black --check src/
flake8 src/

# 检查类型注解（可选）
mypy src/
```

### 3. 版本管理

更新版本号（遵循语义化版本）：
- `setup.py` 中的 `version` 字段
- `CHANGELOG.md` 中添加新版本记录

## 🚀 发布流程

### 步骤 1: 清理构建目录

```bash
# 删除旧的构建文件
rm -rf build/ dist/ *.egg-info/
```

### 步骤 2: 构建包

```bash
# 构建源码包和wheel包
py -m build
```

这将在 `dist/` 目录下生成：
- `docx-image-extractor-mcp-x.x.x.tar.gz` (源码包)
- `docx_image_extractor_mcp-x.x.x-py3-none-any.whl` (wheel包)

### 步骤 3: 本地测试

```bash
# 在虚拟环境中测试安装
python -m venv test_env
test_env\Scripts\activate  # Windows
# source test_env/bin/activate  # Linux/Mac

# 安装构建的包
pip install dist/docx_image_extractor_mcp-*.whl

# 测试命令行工具
docx-image-extractor-mcp --help
docx-extract --help

# 测试MCP服务
python -m docx_image_extractor_mcp.main

# 退出测试环境
deactivate
```

### 步骤 4: 发布到测试环境（推荐）

```bash
# 注册 TestPyPI 账号（如果还没有）
# 访问: https://test.pypi.org/account/register/

# 发布到测试环境
py -m twine upload --repository testpypi dist/*
```

### 步骤 5: 从测试环境验证

```bash
# 从测试环境安装
pip install --index-url https://test.pypi.org/simple/ docx-image-extractor-mcp

# 测试功能
docx-image-extractor-mcp --version
```

### 步骤 6: 发布到正式环境

```bash
# 注册 PyPI 账号（如果还没有）
# 访问: https://pypi.org/account/register/

# 发布到正式PyPI
py -m twine upload dist/*
```

## 🔐 认证配置

### 方法 1: 使用 API Token（推荐）

1. 在 PyPI 账户设置中创建 API Token
2. 创建 `~/.pypirc` 文件：

```ini
[distutils]
index-servers = pypi testpypi

[pypi]
username = __token__
password = pypi-your-api-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-api-token-here
```

### 方法 2: 交互式输入

发布时会提示输入用户名和密码。

## 📊 发布后验证

### 1. 检查 PyPI 页面

访问 https://pypi.org/project/docx-image-extractor-mcp/ 确认：
- 项目信息正确
- README 显示正常
- 依赖关系正确

### 2. 测试安装

```bash
# 在新环境中测试安装
pip install docx-image-extractor-mcp

# 验证功能
docx-image-extractor-mcp --help
python -c "import docx_image_extractor_mcp; print('Import successful')"
```

### 3. Claude Desktop 集成测试

用户配置示例：

```json
{
  "mcpServers": {
    "docx-image-extractor": {
      "command": "python",
      "args": ["-m", "docx_image_extractor_mcp.main"],
      "env": {}
    }
  }
}
```

## 🔄 自动化发布（GitHub Actions）

创建 `.github/workflows/publish.yml`：

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.8'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    
    - name: Build package
      run: python -m build
    
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

## 📝 发布检查清单

- [ ] 更新版本号
- [ ] 更新 CHANGELOG.md
- [ ] 运行所有测试
- [ ] 检查依赖版本
- [ ] 清理构建目录
- [ ] 构建包
- [ ] 本地测试安装
- [ ] 发布到测试环境
- [ ] 从测试环境验证
- [ ] 发布到正式环境
- [ ] 验证 PyPI 页面
- [ ] 测试最终安装
- [ ] 创建 Git 标签
- [ ] 创建 GitHub Release

## 🛠️ 故障排除

### 常见问题

1. **构建失败**
   - 检查 `setup.py` 配置
   - 确认所有依赖已安装
   - 检查文件路径

2. **上传失败**
   - 检查认证信息
   - 确认包名未被占用
   - 检查网络连接

3. **安装失败**
   - 检查依赖兼容性
   - 确认 Python 版本支持
   - 检查包完整性

### 获取帮助

- PyPI 帮助文档: https://packaging.python.org/
- Twine 文档: https://twine.readthedocs.io/
- 项目 Issues: https://github.com/docx-image-extractor/docx-image-extractor-mcp/issues

## 🎉 发布成功！

恭喜！您的项目现在已经发布到 PyPI，全世界的用户都可以通过以下方式安装：

```bash
pip install docx-image-extractor-mcp
```

记得在项目 README 中更新安装说明，并在社交媒体上分享您的成果！