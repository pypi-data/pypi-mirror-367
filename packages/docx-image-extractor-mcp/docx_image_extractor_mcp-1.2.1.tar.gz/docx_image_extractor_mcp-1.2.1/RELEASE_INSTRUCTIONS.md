# 🚀 快速发布指南

## 📦 一键发布到 PyPI

您的项目已经准备好发布！按照以下步骤即可让全世界的用户使用您的工具。

### 🎯 发布目标

发布后，用户可以通过以下方式安装：
```bash
pip install docx-image-extractor-mcp
```

### 📋 发布前准备

1. **注册 PyPI 账号**
   - 访问 https://pypi.org/account/register/ 注册账号
   - 访问 https://test.pypi.org/account/register/ 注册测试账号

2. **创建 API Token**
   - 在 PyPI 账户设置中创建 API Token
   - 在 TestPyPI 账户设置中创建 API Token

### 🚀 发布步骤

#### 方法 1: 使用自动化脚本（推荐）

```bash
# 仅发布到测试环境
py scripts/publish.py --test-only

# 发布到正式环境（会先发布到测试环境）
py scripts/publish.py
```

#### 方法 2: 手动发布

```bash
# 1. 清理旧文件
py -c "import shutil; import os; [shutil.rmtree(d) for d in ['build', 'dist', 'src/docx_image_extractor_mcp.egg-info'] if os.path.exists(d)]"

# 2. 构建包
py -m build

# 3. 检查包质量
py -m twine check dist/*

# 4. 发布到测试环境
py -m twine upload --repository testpypi dist/*

# 5. 发布到正式环境
py -m twine upload dist/*
```

### 🔐 认证配置

创建 `~/.pypirc` 文件：

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

### ✅ 发布验证

发布成功后：

1. **检查 PyPI 页面**
   - https://pypi.org/project/docx-image-extractor-mcp/

2. **测试安装**
   ```bash
   pip install docx-image-extractor-mcp
   docx-image-extractor-mcp --help
   ```

3. **Claude Desktop 配置**
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

### 🎉 发布成功！

恭喜！您的项目现在已经可以被全世界的用户使用了！

### 📚 更多信息

- 详细发布指南: `docs/PUBLISHING_GUIDE.md`
- 项目配置: `docs/WINDOWS_SETUP_GUIDE.md`
- Claude Desktop 修复: `docs/CLAUDE_DESKTOP_FIX.md`