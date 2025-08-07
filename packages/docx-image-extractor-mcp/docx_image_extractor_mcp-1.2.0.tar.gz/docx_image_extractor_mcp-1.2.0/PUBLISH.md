# MCP服务发布指南

## 🚀 发布方式

### 1. 发布到PyPI（推荐）

#### 准备工作
```bash
# 安装发布工具
pip install build twine

# 注册PyPI账号
# 访问 https://pypi.org/account/register/
```

#### 构建包
```bash
# 在项目根目录执行
python -m build
```

#### 发布到测试环境（可选）
```bash
# 发布到测试PyPI
twine upload --repository testpypi dist/*

# 从测试PyPI安装验证
pip install --index-url https://test.pypi.org/simple/ docx-image-extractor-mcp
```

#### 发布到正式环境
```bash
# 发布到正式PyPI
twine upload dist/*
```

### 2. 发布到GitHub

#### 创建仓库
```bash
# 初始化Git仓库
git init
git add .
git commit -m "Initial commit"

# 添加远程仓库
git remote add origin https://github.com/yourusername/docx-image-extractor-mcp.git
git push -u origin main
```

#### 创建Release
1. 在GitHub仓库页面点击"Releases"
2. 点击"Create a new release"
3. 设置标签版本（如v1.0.0）
4. 填写发布说明
5. 上传构建的包文件

### 3. 本地安装测试

#### 开发模式安装
```bash
# 在项目目录下
pip install -e .
```

#### 测试MCP服务
```bash
# 直接运行
docx-image-extractor-mcp

# 或者
python -m docx_image_extractor_mcp
```

## 📋 发布前检查清单

- [ ] 更新版本号（pyproject.toml）
- [ ] 更新README.md
- [ ] 更新CHANGELOG.md
- [ ] 运行测试
- [ ] 检查依赖版本
- [ ] 构建包并测试安装
- [ ] 检查包内容

## 🔧 Claude Desktop配置

用户安装后的配置方式：

### 从PyPI安装
```json
{
  "mcpServers": {
    "docx-image-extractor": {
      "command": "docx-image-extractor-mcp",
      "args": [],
      "env": {}
    }
  }
}
```

### 从源码安装
```json
{
  "mcpServers": {
    "docx-image-extractor": {
      "command": "python",
      "args": ["/path/to/docx_image_extractor_mcp.py"],
      "env": {}
    }
  }
}
```

## 📈 版本管理

### 语义化版本
- **主版本号**：不兼容的API修改
- **次版本号**：向下兼容的功能性新增
- **修订号**：向下兼容的问题修正

### 发布流程
1. 开发新功能
2. 更新版本号
3. 更新文档
4. 创建Git标签
5. 构建并发布包
6. 创建GitHub Release

## 🛠️ 维护建议

- 定期更新依赖
- 监控用户反馈
- 及时修复bug
- 保持文档更新
- 考虑向后兼容性