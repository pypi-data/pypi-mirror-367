# DOCX图片提取器 - Windows配置使用手册

## 📋 目录
- [系统要求](#系统要求)
- [安装指南](#安装指南)
- [配置说明](#配置说明)
- [使用方法](#使用方法)
- [Claude Desktop集成](#claude-desktop集成)
- [常见问题](#常见问题)
- [故障排除](#故障排除)

## 🖥️ 系统要求

### 最低要求
- **操作系统**: Windows 10 或更高版本
- **Python版本**: Python 3.8 或更高版本
- **内存**: 至少 4GB RAM
- **存储空间**: 至少 100MB 可用空间

### 推荐配置
- **操作系统**: Windows 11
- **Python版本**: Python 3.10 或更高版本
- **内存**: 8GB RAM 或更多
- **存储空间**: 1GB 可用空间

## 🚀 安装指南

### 步骤1: 安装Python

1. **下载Python**
   - 访问 [Python官网](https://www.python.org/downloads/windows/)
   - 下载最新的Python 3.x版本

2. **安装Python**
   ```cmd
   # 确保勾选以下选项：
   ☑️ Add Python to PATH
   ☑️ Install pip
   ```

3. **验证安装**
   ```cmd
   # 打开命令提示符(CMD)或PowerShell
   python --version
   pip --version
   ```

### 步骤2: 安装项目依赖

1. **克隆或下载项目**
   ```cmd
   # 如果使用Git
   git clone <项目地址>
   cd docx-image-extractor-mcp
   
   # 或者直接下载ZIP文件并解压
   ```

2. **创建虚拟环境（推荐）**
   ```cmd
   # 创建虚拟环境
   python -m venv venv
   
   # 激活虚拟环境
   venv\Scripts\activate
   ```

3. **安装依赖包**
   ```cmd
   # 安装基础依赖
   pip install -r requirements.txt
   
   # 如果需要MCP功能，安装MCP库
   pip install mcp
   
   # 如果需要性能测试，安装psutil
   pip install psutil
   ```

### 步骤3: 验证安装

```cmd
# 运行测试
python -m pytest tests/ -v

# 测试CLI工具
python -m docx_image_extractor_mcp --help
```

## ⚙️ 配置说明

### 创建配置文件

1. **生成默认配置**
   ```cmd
   python -m docx_image_extractor_mcp config create -o config.json
   ```

2. **配置文件结构**
   ```json
   {
     "base_image_dir": "images",
     "image_naming": {
       "prefix": "image",
       "padding": 3
     },
     "logging": {
       "level": "INFO",
       "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
     }
   }
   ```

### 配置选项说明

| 配置项 | 说明 | 默认值 | 示例 |
|--------|------|--------|------|
| `base_image_dir` | 图片输出根目录 | `"images"` | `"extracted_images"` |
| `image_naming.prefix` | 图片文件名前缀 | `"image"` | `"pic"` |
| `image_naming.padding` | 图片编号位数 | `3` | `4` |
| `logging.level` | 日志级别 | `"INFO"` | `"DEBUG"` |

### 环境变量配置

```cmd
# 设置默认配置文件路径
set DOCX_EXTRACTOR_CONFIG=C:\path\to\config.json

# 设置默认输出目录
set DOCX_EXTRACTOR_OUTPUT=C:\path\to\output
```

## 📖 使用方法

### 命令行工具使用

1. **提取图片**
   ```cmd
   # 提取单个文件
   python -m docx_image_extractor_mcp extract document.docx
   
   # 提取多个文件到指定目录
   python -m docx_image_extractor_mcp extract -o D:\images\ doc1.docx doc2.docx
   
   # 使用自定义配置
   python -m docx_image_extractor_mcp -c config.json extract document.docx
   ```

2. **预览文档结构**
   ```cmd
   # 预览文档内容
   python -m docx_image_extractor_mcp preview document.docx
   
   # 详细预览（显示所有媒体文件）
   python -m docx_image_extractor_mcp -v DEBUG preview document.docx
   ```

3. **文件名转换**
   ```cmd
   # 转换中文文件名为拼音
   python -m docx_image_extractor_mcp convert "测试文档.docx" "项目报告.docx"
   ```

4. **配置管理**
   ```cmd
   # 显示当前配置
   python -m docx_image_extractor_mcp config show
   
   # 创建配置文件
   python -m docx_image_extractor_mcp config create -o my_config.json
   ```

### Python脚本使用

```python
from docx_image_extractor_mcp import extract_images, Config

# 使用默认配置
result = extract_images("document.docx")
print(f"提取了 {result['count']} 张图片")

# 使用自定义配置
config = Config()
config.set("base_image_dir", "my_images")
result = extract_images("document.docx", "my_images")
```

## 🤖 Claude Desktop集成

### 安装Claude Desktop

1. **下载Claude Desktop**
   - 访问 [Claude Desktop官网](https://claude.ai/desktop)
   - 下载Windows版本并安装

### 配置MCP服务器

1. **找到配置文件**
   ```
   配置文件位置：
   %APPDATA%\Claude\claude_desktop_config.json
   ```

2. **编辑配置文件**
   ```json
   {
     "mcpServers": {
       "docx-image-extractor": {
         "command": "py",
         "args": [
           "-m", 
           "docx_image_extractor_mcp.main"
         ],
         "cwd": "d:/BaiduNetdiskDownload/prompt-test/docx-image-extractor-mcp"
       }
     }
   }
   ```

   **重要说明**：
   - `command`: 在Windows上使用 `py` 命令（Python启动器）
   - `args`: 使用 `-m docx_image_extractor_mcp.main` 来启动MCP服务器
   - `cwd`: 设置为项目根目录的绝对路径（请替换为您的实际路径）
   - 路径中使用正斜杠 `/` 或双反斜杠 `\\`

   **针对您的具体情况，正确的配置应该是**：
   ```json
   {
     "mcpServers": {
       "docx-image-extractor": {
         "command": "py",
         "args": [
           "-m", 
           "docx_image_extractor_mcp.main"
         ],
         "cwd": "d:/BaiduNetdiskDownload/prompt-test/docx-image-extractor-mcp"
       }
     }
   }
   ```

3. **重启Claude Desktop**
   - 完全关闭Claude Desktop
   - 重新启动应用程序

### 在Claude中使用

```
你好Claude，请帮我从这个Word文档中提取所有图片：
C:\Documents\report.docx

请将图片保存到：C:\Images\report_images\
```

## ❓ 常见问题

### Q1: Python命令不被识别
**A**: 确保Python已正确安装并添加到PATH环境变量中。

```cmd
# 检查Python路径
where python

# 如果找不到，手动添加到PATH：
# 控制面板 → 系统 → 高级系统设置 → 环境变量
# 在PATH中添加Python安装目录
```

### Q2: 依赖包安装失败
**A**: 尝试使用国内镜像源加速下载。

```cmd
# 使用阿里云镜像
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 或使用清华镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

### Q3: 权限错误
**A**: 以管理员身份运行命令提示符。

```cmd
# 右键点击"命令提示符" → "以管理员身份运行"
```

### Q4: 中文路径问题
**A**: 确保使用UTF-8编码。

```cmd
# 设置控制台编码
chcp 65001
```

### Q5: Claude Desktop无法连接MCP服务器
**A**: 检查配置文件路径和格式。

```json
// 确保路径使用正斜杠或双反斜杠
"cwd": "C:/path/to/project"
// 或
"cwd": "C:\\path\\to\\project"
```

## 🔧 故障排除

### 日志调试

1. **启用详细日志**
   ```cmd
   python -m docx_image_extractor_mcp -v DEBUG extract document.docx
   ```

2. **查看错误详情**
   ```cmd
   # 运行测试查看详细错误
   python -m pytest tests/ -v -s
   ```

### 常见错误解决

1. **ModuleNotFoundError**
   ```cmd
   # 重新安装依赖
   pip install --force-reinstall -r requirements.txt
   ```

2. **PermissionError**
   ```cmd
   # 检查文件权限
   icacls "document.docx"
   
   # 以管理员身份运行
   ```

3. **UnicodeDecodeError**
   ```cmd
   # 设置环境变量
   set PYTHONIOENCODING=utf-8
   ```

### 性能优化

1. **大文件处理**
   ```cmd
   # 增加内存限制
   set PYTHONHASHSEED=0
   
   # 使用64位Python
   python -c "import sys; print(sys.maxsize > 2**32)"
   ```

2. **批量处理**
   ```python
   # 使用脚本批量处理
   import glob
   from docx_image_extractor_mcp import extract_images
   
   for docx_file in glob.glob("*.docx"):
       result = extract_images(docx_file)
       print(f"{docx_file}: {result['count']} 张图片")
   ```

## 📞 技术支持

如果遇到其他问题，请：

1. **查看项目文档**: 阅读README.md和其他文档
2. **运行测试**: `python -m pytest tests/ -v` 检查环境
3. **检查日志**: 使用`-v DEBUG`参数获取详细信息
4. **提交Issue**: 在项目仓库中提交问题报告

---

**版本**: 1.1.0  
**更新日期**: 2024年12月  
**适用系统**: Windows 10/11