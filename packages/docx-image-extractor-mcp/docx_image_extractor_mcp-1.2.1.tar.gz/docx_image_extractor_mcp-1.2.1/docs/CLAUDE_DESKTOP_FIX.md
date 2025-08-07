# Claude Desktop 配置修复指南

## 🚨 问题描述

您遇到的错误：
```
C:\Users\16922\AppData\Local\Programs\Python\Python312\python.exe: can't open file 'd:\\BaiduNetdiskDownload\\prompt-test\\docx_image_extractor_mcp.py': [Errno 2] No such file or directory
```

## ✅ 解决方案

### 问题原因
1. **错误的文件路径**：您配置的路径 `docx_image_extractor_mcp.py` 不存在
2. **错误的启动方式**：应该使用模块方式启动，而不是直接运行Python文件

### 正确的配置

请将您的Claude Desktop配置文件 `%APPDATA%\Claude\claude_desktop_config.json` 修改为：

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

### 关键修改点

1. **command**: 从 `"py"` 改为使用模块启动方式
2. **args**: 使用 `["-m", "docx_image_extractor_mcp.main"]` 而不是文件路径
3. **cwd**: 设置为项目根目录

### 步骤说明

1. **找到配置文件**
   ```
   按 Win+R，输入：%APPDATA%\Claude
   找到 claude_desktop_config.json 文件
   ```

2. **编辑配置文件**
   - 用记事本或其他文本编辑器打开
   - 替换为上面的正确配置
   - 保存文件

3. **重启Claude Desktop**
   - 完全关闭Claude Desktop应用
   - 重新启动应用

## 🔍 验证配置

### 手动测试MCP服务器

在命令提示符中运行以下命令验证服务器可以正常启动：

```cmd
cd d:\BaiduNetdiskDownload\prompt-test\docx-image-extractor-mcp
py -m docx_image_extractor_mcp.main
```

如果看到类似以下输出，说明服务器启动成功：
```
2025-08-06 19:33:23,316 - docx_image_extractor_mcp.interfaces.mcp_server - INFO - DOCX图片提取器MCP服务已初始化
```

### 在Claude中测试

重启Claude Desktop后，您可以在对话中测试：

```
请帮我提取这个Word文档中的图片：
C:\path\to\your\document.docx
```

## 🛠️ 故障排除

### 如果仍然出错

1. **检查Python环境**
   ```cmd
   py --version
   ```

2. **检查项目安装**
   ```cmd
   cd d:\BaiduNetdiskDownload\prompt-test\docx-image-extractor-mcp
   py -m pytest tests/ -v
   ```

3. **检查依赖**
   ```cmd
   pip list | findstr mcp
   ```

### 常见错误及解决方案

1. **"py不是内部或外部命令"**
   - 重新安装Python，确保勾选"Add Python to PATH"

2. **"模块找不到"**
   - 确保在正确的目录下运行命令
   - 检查项目结构是否完整

3. **"权限被拒绝"**
   - 以管理员身份运行命令提示符

## 📞 需要帮助？

如果按照以上步骤仍然无法解决问题，请：

1. 检查项目目录结构是否完整
2. 运行测试确保项目功能正常
3. 查看Claude Desktop的错误日志
4. 提供具体的错误信息以便进一步诊断

---

**重要提醒**：配置文件中的路径必须是您实际的项目路径，请根据您的实际情况调整 `cwd` 字段的值。