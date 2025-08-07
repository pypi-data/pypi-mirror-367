# 变更日志

本文档记录了项目的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [未发布]

### 计划中
- 支持更多图片格式（WebP、AVIF）
- 批量处理优化
- 图片压缩选项
- 多语言支持

## [1.1.0] - 2024-01-XX

### 新增
- 🎯 智能图片格式检测功能
- 🔧 配置文件支持 (`config.py`, `config.example.json`)
- 🖥️ 命令行界面 (CLI) 工具
- 📊 DOCX 文档结构预览功能
- 🔤 文件名 ASCII 转换功能
- 🐳 Docker 容器化支持
- 🚀 GitHub Actions CI/CD 流水线
- 📝 完整的项目文档和贡献指南
- 🧪 性能测试套件
- 📦 MCP 协议支持增强

### 改进
- ✨ 更好的错误处理和日志记录
- 🎨 代码质量提升（类型提示、格式化）
- 📈 测试覆盖率提升
- 🔧 开发工具配置（Black、flake8、isort）
- 📚 API 文档完善

### 修复
- 🐛 修复空文件处理问题
- 🔧 改进 ZIP 文件错误处理
- 📝 修正文档中的示例代码

### 技术债务
- 🏗️ 代码结构重构
- 📦 依赖管理优化
- 🧹 移除调试代码

## [1.0.0] - 2024-01-XX

### 新增
- 🎉 初始版本发布
- 📄 从 DOCX 文件提取图片的核心功能
- 🔧 基本的 MCP 服务器实现
- 🐍 Python API 支持
- 📝 基础文档

### 功能特性
- 支持从 DOCX 文档中提取嵌入的图片
- 自动创建输出目录
- 基本的错误处理
- 简单的文件命名策略

---

## 版本说明

### 版本号格式
本项目使用语义化版本号：`MAJOR.MINOR.PATCH`

- **MAJOR**: 不兼容的 API 修改
- **MINOR**: 向后兼容的功能性新增
- **PATCH**: 向后兼容的问题修正

### 变更类型
- `新增` - 新功能
- `改进` - 对现有功能的改进
- `修复` - 问题修复
- `移除` - 移除的功能
- `安全` - 安全相关的修复
- `废弃` - 即将移除的功能

### 表情符号说明
- 🎉 重大发布
- ✨ 新功能
- 🐛 Bug 修复
- 📝 文档更新
- 🎨 代码格式/结构改进
- ⚡ 性能优化
- 🔧 配置/工具更新
- 🚀 部署相关
- 🧪 测试相关
- 📦 依赖更新
- 🔒 安全修复
- 🗑️ 移除功能
- 📈 分析/追踪
- 🌐 国际化
- 🎯 功能改进
- 🏗️ 架构变更
- 🧹 代码清理

## 贡献指南

如果您想为变更日志做出贡献：

1. 在每个 Pull Request 中更新相应的变更
2. 遵循现有的格式和分类
3. 使用清晰、简洁的描述
4. 包含相关的 Issue 或 PR 链接
5. 按照重要性排序变更项

## 迁移指南

### 从 1.0.x 升级到 1.1.x

#### 配置变更
```python
# 旧版本
from docx_image_extractor_mcp import extract_images

# 新版本 - 支持配置
from docx_image_extractor_mcp import extract_images, Config

config = Config()
config.set('base_image_dir', 'custom_output')
```

#### CLI 使用
```bash
# 新增的 CLI 工具
docx-extract extract document.docx
docx-extract preview document.docx
docx-extract config show
```

#### Docker 支持
```bash
# 新增的 Docker 支持
docker build -t docx-extractor .
docker run -v $(pwd):/workspace docx-extractor
```

### 破坏性变更
目前没有破坏性变更。所有 1.0.x 的 API 在 1.1.x 中仍然兼容。