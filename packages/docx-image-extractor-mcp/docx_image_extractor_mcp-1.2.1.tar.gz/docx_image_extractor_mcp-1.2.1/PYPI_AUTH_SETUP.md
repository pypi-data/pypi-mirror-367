# 🔑 PyPI 认证配置指南

## 📋 当前状态

✅ **TestPyPI 发布成功** - 项目已成功发布到测试环境  
✅ **包构建成功** - 所有文件已准备就绪  
❌ **PyPI 认证失败** - 需要正确配置 API Token  

## 🚀 下一步：配置 PyPI 认证

### 1. 获取 PyPI API Token

1. 访问 [PyPI.org](https://pypi.org/manage/account/token/)
2. 登录您的账号
3. 点击 "Add API token"
4. 选择 "Entire account" 或 "Specific project"
5. 复制生成的 token（格式：`pypi-AgEIcHlwaS5vcmcC...`）

### 2. 配置认证信息

#### 方法 1: 创建 ~/.pypirc 文件（推荐）

在您的用户目录下创建文件：`C:\Users\您的用户名\.pypirc`

```ini
[distutils]
index-servers = 
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-您的完整API令牌

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-您的测试API令牌
```

#### 方法 2: 使用命令行参数

```bash
py -m twine upload --username __token__ --password pypi-您的API令牌 dist/*
```

### 3. 验证配置

```bash
# 检查配置
py -m twine check dist/*

# 上传到 PyPI
py -m twine upload dist/*
```

## 🔍 故障排除

### 常见错误

1. **403 Forbidden**
   - 检查 API token 是否正确
   - 确认 token 有上传权限
   - 检查包名是否已被占用

2. **包名冲突**
   - 如果包名被占用，需要修改 `setup.py` 中的 `name`
   - 重新构建包：`py -m build`

3. **网络问题**
   - 使用 `--verbose` 参数查看详细信息
   - 检查网络连接

### 检查包名是否可用

访问：https://pypi.org/project/docx-image-extractor-mcp/

如果显示 "404 Not Found"，说明包名可用。

## 📦 发布成功后

一旦发布成功，用户就可以：

```bash
# 安装您的包
pip install docx-image-extractor-mcp

# 使用命令行工具
docx-extract extract document.docx

# 在 Claude Desktop 中配置 MCP 服务
```

## 🎯 项目链接

- **TestPyPI**: https://test.pypi.org/project/docx-image-extractor-mcp/1.2.0/
- **PyPI**: https://pypi.org/project/docx-image-extractor-mcp/ (发布后可用)
- **GitHub**: https://github.com/docx-image-extractor/docx-image-extractor-mcp

## 📞 需要帮助？

如果遇到问题：

1. 检查 API token 是否正确复制
2. 确认网络连接正常
3. 查看 [PyPI 帮助文档](https://pypi.org/help/)
4. 检查项目的 Issues 页面

---

**下一步**: 配置好认证信息后，运行 `py -m twine upload dist/*` 即可发布到 PyPI！