# DOC/DOCX Image Extractor MCP

一个功能强大的DOC/DOCX文档图片提取工具，支持MCP协议、命令行和Python API。具备智能图片格式检测、中文文档名转拼音、可配置选项等高级功能。

## ✨ 功能特性

- 🖼️ **智能图片提取**: 从DOC/DOCX文档中提取所有图片，支持多种格式
- 📄 **双格式支持**: 同时支持传统DOC格式和现代DOCX格式
- 🔍 **格式自动检测**: 根据文件头自动识别图片格式（PNG、JPEG、GIF等）
- 🔤 **中文支持**: 中文文档名自动转换为拼音目录名
- 📁 **智能目录管理**: 自动创建规范的目录结构
- 🔧 **MCP协议支持**: 与Claude Desktop等AI工具无缝集成
- ⚙️ **灵活配置**: 支持JSON配置文件，可自定义各种参数
- 🐍 **多种接口**: 提供Python API、命令行工具和MCP服务
- 📊 **详细预览**: 支持DOC/DOCX文档结构预览
- 🚀 **高性能**: 优化的处理流程，支持大文件处理
- 📝 **完整日志**: 详细的日志记录和错误处理

## 🚀 快速开始

### 安装

#### 方法 1: 从 PyPI 安装（推荐）

```bash
pip install docx-image-extractor-mcp
```

#### 方法 2: 从源码安装

```bash
git clone https://github.com/docx-image-extractor/docx-image-extractor-mcp.git
cd docx-image-extractor-mcp
pip install -e .
```

#### 验证安装

```bash
# 检查命令行工具
docx-image-extractor-mcp --help
docx-extract --help

# 检查Python模块
python -c "import docx_image_extractor_mcp; print('安装成功！')"
```

### 基本使用

```bash
# 命令行提取图片
docx-extract extract document.docx
docx-extract extract document.doc

# 预览文档结构
docx-extract preview document.docx
docx-extract preview document.doc

# 转换文件名为ASCII
docx-extract convert "测试文档.docx"
```

## 📖 使用方法

### 1. 命令行工具

```bash
# 提取单个文件的图片
docx-extract extract document.docx
docx-extract extract document.doc

# 提取多个文件到指定目录
docx-extract extract -o images/ doc1.docx doc2.doc

# 预览文档结构
docx-extract preview document.docx
docx-extract preview document.doc

# 转换文件名为ASCII
docx-extract convert "测试文档.docx" "另一个文档.doc"

# 显示配置
docx-extract config show

# 创建配置文件
docx-extract config create -o my-config.json
```

### 2. Python API

```python
from docx_image_extractor_mcp import extract_images, Config

# 基本使用 - 支持 DOC 和 DOCX
result = extract_images("document.docx")
print(f"提取了 {result['count']} 张图片到: {result['output_dir']}")

result = extract_images("document.doc")
print(f"提取了 {result['count']} 张图片到: {result['output_dir']}")

# 使用自定义配置
config = Config()
config.base_image_dir = "my_images"
config.image_naming_prefix = "pic"

result = extract_images("document.docx", config=config)
```

### 3. MCP服务

#### 从 PyPI 安装后的配置

在Claude Desktop配置文件中添加：

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

#### Windows 用户注意事项

如果使用 `py` 命令：

```json
{
  "mcpServers": {
    "docx-image-extractor": {
      "command": "py",
      "args": ["-m", "docx_image_extractor_mcp.main"],
      "env": {}
    }
  }
}
```

> 📖 详细配置指南请参考：[Windows 配置手册](docs/WINDOWS_SETUP_GUIDE.md) 和 [Claude Desktop 修复指南](docs/CLAUDE_DESKTOP_FIX.md)

可用的MCP工具：
- `extract_docx_images`: 提取DOC/DOCX文档中的图片
- `preview_docx_structure`: 预览DOCX文档结构（仅支持DOCX）
- `convert_filename_to_ascii`: 转换文件名为ASCII

## ⚙️ 配置选项

创建 `config.json` 文件来自定义行为：

```json
{
  "base_image_dir": "extracted_images",
  "image_naming": {
    "prefix": "image",
    "padding": 3
  },
  "logging": {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  },
  "extraction": {
    "skip_empty_files": true,
    "detect_format": true,
    "supported_formats": [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp"]
  }
}
```

### 配置参数说明

- `base_image_dir`: 图片输出基础目录
- `image_naming.prefix`: 图片文件名前缀
- `image_naming.padding`: 图片编号填充位数
- `logging.level`: 日志级别（DEBUG、INFO、WARNING、ERROR）
- `extraction.skip_empty_files`: 是否跳过空图片文件
- `extraction.detect_format`: 是否自动检测图片格式
- `extraction.supported_formats`: 支持的图片格式列表

## 📊 API参考

### extract_images(doc_path, base_image_dir=None, config=None)

提取DOC/DOCX文档中的图片。

**参数:**
- `doc_path` (str): DOC/DOCX文档路径
- `base_image_dir` (str, 可选): 图片输出基础目录
- `config` (Config, 可选): 配置对象

**返回值:**
```python
{
    "success": True,                    # 是否成功
    "count": 5,                        # 提取的图片数量
    "output_dir": "path/to/output",    # 输出目录路径
    "msg": "成功提取5张图片",            # 状态消息
    "images": [                        # 图片列表
        {
            "filename": "image_001.png",
            "path": "full/path/to/image_001.png",
            "size": 12345,
            "format": "PNG"
        }
    ]
}
```

### to_ascii_dirname(filename)

将文件名转换为ASCII目录名。

**参数:**
- `filename` (str): 原始文件名

**返回值:**
- `str`: 转换后的ASCII目录名

## 🏗️ 项目结构

```
docx-image-extractor-mcp/
├── src/
│   └── docx_image_extractor_mcp/
│       ├── __init__.py                 # 主包入口
│       ├── __main__.py                 # 模块执行入口
│       ├── main.py                     # MCP服务器启动
│       ├── core/                       # 核心功能模块
│       │   ├── __init__.py
│       │   ├── extractor.py           # 图片提取核心逻辑
│       │   └── config.py              # 配置管理
│       └── interfaces/                 # 接口模块
│           ├── __init__.py
│           ├── cli.py                 # 命令行接口
│           └── mcp_server.py          # MCP服务器接口
├── tests/                             # 测试模块
│   ├── test_extractor.py             # 核心功能测试
│   └── test_performance.py           # 性能测试
├── docs/                              # 文档目录
│   ├── WINDOWS_SETUP_GUIDE.md        # Windows配置手册
│   └── CODE_STRUCTURE_OPTIMIZATION.md # 结构优化说明
├── requirements.txt                   # 依赖管理
├── pyproject.toml                    # 项目配置
├── .gitignore                        # Git忽略规则
└── README.md                         # 项目说明
```

## 🧪 测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行功能测试
python -m pytest tests/test_extractor.py

# 运行性能测试
python -m pytest tests/test_performance.py

# 运行特定测试
python -m pytest tests/test_extractor.py::TestExtractor::test_extract_images_file_not_exists
```

## 📈 性能特性

- **内存优化**: 流式处理大文件，避免内存溢出
- **格式检测**: 智能识别图片格式，避免错误扩展名
- **并发处理**: 支持批量文件处理
- **错误恢复**: 完善的错误处理和恢复机制

## 🔧 依赖项

- Python >= 3.8
- mcp >= 0.1.0
- pypinyin >= 0.44.0
- python-docx >= 0.8.11
- olefile >= 0.46 (用于DOC文件支持)
- python-docx2txt >= 0.8 (用于DOC文件支持)

## 📝 更新日志

### v1.2.0
- ✨ 新增DOC文件格式支持
- ✨ 新增DOC文件结构预览功能
- 🔧 更新所有接口以支持DOC/DOCX双格式
- 📚 更新文档和示例以反映DOC支持
- 🐛 改进错误处理和兼容性

### v1.1.0
- ✨ 新增智能图片格式检测
- ✨ 新增配置文件支持
- ✨ 新增命令行工具
- ✨ 新增DOCX结构预览功能
- 🐛 改进错误处理和日志记录
- 🚀 性能优化和内存管理改进
- 📚 完善文档和测试用例

### v1.0.0
- 🎉 初始版本发布
- 基本的图片提取功能
- MCP协议支持
- 中文文档名转拼音

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License