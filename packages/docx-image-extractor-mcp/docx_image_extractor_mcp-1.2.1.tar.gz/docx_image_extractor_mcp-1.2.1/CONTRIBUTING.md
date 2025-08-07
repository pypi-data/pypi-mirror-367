# 贡献指南

感谢您对 `docx-image-extractor-mcp` 项目的关注！我们欢迎各种形式的贡献。

## 🚀 快速开始

### 开发环境设置

1. **Fork 并克隆仓库**
   ```bash
   git clone https://github.com/your-username/docx-image-extractor-mcp.git
   cd docx-image-extractor-mcp
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   venv\Scripts\activate     # Windows
   ```

3. **安装开发依赖**
   ```bash
   make install-dev
   # 或
   pip install -r requirements.txt
   pip install pytest pytest-cov black flake8 isort mypy
   pip install -e .
   ```

## 📝 开发流程

### 1. 创建功能分支
```bash
git checkout -b feature/your-feature-name
```

### 2. 开发和测试
```bash
# 运行测试
make test

# 代码格式化
make format

# 代码检查
make lint

# 运行所有检查
make check
```

### 3. 提交代码
```bash
git add .
git commit -m "feat: 添加新功能描述"
git push origin feature/your-feature-name
```

### 4. 创建 Pull Request
- 在 GitHub 上创建 Pull Request
- 填写详细的描述
- 等待代码审查

## 🧪 测试指南

### 运行测试
```bash
# 运行所有测试
pytest tests/

# 运行特定测试文件
pytest tests/test_extractor.py

# 运行特定测试方法
pytest tests/test_extractor.py::TestExtractor::test_extract_images

# 生成覆盖率报告
pytest tests/ --cov=docx_image_extractor_mcp --cov-report=html
```

### 编写测试
- 为新功能编写单元测试
- 确保测试覆盖率不低于 80%
- 测试文件命名为 `test_*.py`
- 测试类命名为 `Test*`
- 测试方法命名为 `test_*`

## 📋 代码规范

### 代码风格
- 使用 [Black](https://black.readthedocs.io/) 进行代码格式化
- 使用 [isort](https://pycqa.github.io/isort/) 整理导入语句
- 使用 [flake8](https://flake8.pycqa.org/) 进行代码检查
- 行长度限制为 127 字符

### 提交信息规范
使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

类型说明：
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式化（不影响功能）
- `refactor`: 代码重构
- `test`: 添加或修改测试
- `chore`: 构建过程或辅助工具的变动

示例：
```
feat: 添加图片格式自动检测功能

- 支持 PNG、JPEG、GIF 等格式检测
- 根据文件头识别真实格式
- 添加相应的测试用例

Closes #123
```

## 🐛 报告问题

### Bug 报告
请包含以下信息：
- 操作系统和版本
- Python 版本
- 项目版本
- 重现步骤
- 期望行为
- 实际行为
- 错误日志（如有）

### 功能请求
请描述：
- 功能的用途和价值
- 预期的 API 设计
- 可能的实现方案

## 📚 文档贡献

### 文档类型
- README.md：项目介绍和基本使用
- API 文档：函数和类的详细说明
- 教程：使用示例和最佳实践
- 贡献指南：本文档

### 文档规范
- 使用清晰的标题结构
- 提供代码示例
- 包含必要的截图或图表
- 保持内容的时效性

## 🔄 发布流程

### 版本号规范
使用 [语义化版本](https://semver.org/)：
- `MAJOR.MINOR.PATCH`
- `MAJOR`: 不兼容的 API 修改
- `MINOR`: 向后兼容的功能性新增
- `PATCH`: 向后兼容的问题修正

### 发布步骤
1. 更新版本号
2. 更新 CHANGELOG.md
3. 创建 Git 标签
4. GitHub Actions 自动发布到 PyPI

## 🤝 社区准则

### 行为准则
- 尊重所有贡献者
- 保持友好和专业的态度
- 欢迎新手参与
- 提供建设性的反馈

### 沟通渠道
- GitHub Issues：问题报告和功能请求
- GitHub Discussions：一般讨论和问答
- Pull Requests：代码审查和讨论

## 🛠️ 开发工具

### 推荐的 IDE 配置

#### VS Code
```json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.sortImports.args": ["--profile", "black"],
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

#### PyCharm
- 配置 Black 作为代码格式化工具
- 启用 flake8 代码检查
- 配置 isort 整理导入语句

### 有用的命令
```bash
# 查看项目统计
git log --oneline | wc -l  # 提交数量
find . -name "*.py" | xargs wc -l  # 代码行数

# 清理项目
make clean

# 构建项目
make build

# 本地测试发布
make publish-test
```

## 📞 获取帮助

如果您在贡献过程中遇到任何问题，请：

1. 查看现有的 Issues 和 Discussions
2. 阅读项目文档
3. 创建新的 Issue 描述您的问题
4. 在 Pull Request 中请求帮助

感谢您的贡献！🎉