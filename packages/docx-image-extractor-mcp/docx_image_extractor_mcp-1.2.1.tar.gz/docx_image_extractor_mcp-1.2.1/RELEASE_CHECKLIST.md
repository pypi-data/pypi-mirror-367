# ✅ 发布检查清单

在发布项目到 PyPI 之前，请确保完成以下所有检查项：

## 📋 发布前检查

### 🔧 代码质量
- [ ] 所有测试通过 (`pytest tests/ -v`)
- [ ] 代码格式检查通过 (`black --check src/`)
- [ ] 没有明显的代码问题
- [ ] 所有功能正常工作

### 📝 文档更新
- [ ] 更新版本号 (`setup.py` 中的 `version`)
- [ ] 更新 `CHANGELOG.md`
- [ ] 检查 `README.md` 内容准确性
- [ ] 确认安装说明正确
- [ ] 确认使用示例有效

### 🏗️ 构建测试
- [ ] 清理旧构建文件
- [ ] 成功构建包 (`py -m build`)
- [ ] 包检查通过 (`py -m twine check dist/*`)
- [ ] 本地安装测试成功

### 🔐 发布准备
- [ ] PyPI 账号已注册
- [ ] TestPyPI 账号已注册
- [ ] API Token 已创建
- [ ] `~/.pypirc` 文件已配置

### 📦 包信息
- [ ] 包名称正确且未被占用
- [ ] 作者信息准确
- [ ] 项目描述清晰
- [ ] 许可证信息正确
- [ ] 项目URL正确
- [ ] 依赖关系准确

## 🚀 发布流程

### 1. 测试发布
- [ ] 发布到 TestPyPI
- [ ] 从 TestPyPI 安装测试
- [ ] 功能验证通过

### 2. 正式发布
- [ ] 发布到 PyPI
- [ ] 从 PyPI 安装测试
- [ ] 功能验证通过

### 3. 发布后
- [ ] 检查 PyPI 项目页面
- [ ] 创建 Git 标签
- [ ] 创建 GitHub Release
- [ ] 更新项目文档
- [ ] 通知用户

## 🧪 测试命令

```bash
# 运行测试
pytest tests/ -v

# 检查代码格式
black --check src/

# 清理构建文件
py -c "import shutil; import os; [shutil.rmtree(d) for d in ['build', 'dist', 'src/docx_image_extractor_mcp.egg-info'] if os.path.exists(d)]"

# 构建包
py -m build

# 检查包
py -m twine check dist/*

# 发布到测试环境
py -m twine upload --repository testpypi dist/*

# 发布到正式环境
py -m twine upload dist/*
```

## 📊 发布状态

### 当前版本: 1.2.0

- [x] 代码重构完成
- [x] 测试用例通过
- [x] 文档更新完成
- [x] 构建测试成功
- [ ] 发布到 TestPyPI
- [ ] 发布到 PyPI

### 下一步行动

1. 注册 PyPI 和 TestPyPI 账号
2. 配置 API Token
3. 执行发布流程
4. 验证发布结果

## 🎯 发布目标

让用户能够通过以下方式轻松安装和使用：

```bash
# 安装
pip install docx-image-extractor-mcp

# 使用命令行工具
docx-extract extract document.docx

# 使用 MCP 服务
# 在 Claude Desktop 中配置并使用
```

## 📞 获取帮助

如果在发布过程中遇到问题：

1. 查看 [发布指南](docs/PUBLISHING_GUIDE.md)
2. 查看 [PyPI 官方文档](https://packaging.python.org/)
3. 查看项目 [Issues](https://github.com/docx-image-extractor/docx-image-extractor-mcp/issues)

---

**记住**: 发布是不可逆的操作，请确保所有检查项都已完成！