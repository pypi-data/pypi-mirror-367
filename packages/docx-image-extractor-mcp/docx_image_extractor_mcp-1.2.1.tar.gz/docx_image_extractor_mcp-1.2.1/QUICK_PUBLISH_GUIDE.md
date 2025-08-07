# 🚀 快速发布指南

## 📋 当前状态
✅ **包已构建完成** - dist/ 目录中的文件已准备就绪  
✅ **包质量验证通过** - twine check 成功  
❌ **需要配置 PyPI 认证** - 403 认证错误  

## 🔑 第一步：获取 PyPI API Token

1. 访问 [PyPI.org](https://pypi.org/manage/account/token/)
2. 登录您的 PyPI 账号
3. 点击 "Add API token"
4. 选择 "Entire account" 
5. 输入 Token 名称（如：docx-image-extractor-mcp）
6. 复制生成的完整 token（格式：`pypi-AgEIcHlwaS5vcmcC...`）

## 🛠️ 第二步：配置认证

### 方法 1：创建 .pypirc 文件（推荐）

在您的用户目录创建文件：`C:\Users\您的用户名\.pypirc`

```ini
[distutils]
index-servers = 
    pypi

[pypi]
username = __token__
password = pypi-您的完整API令牌
```

### 方法 2：使用环境变量

```bash
set TWINE_USERNAME=__token__
set TWINE_PASSWORD=pypi-您的完整API令牌
```

## 🚀 第三步：发布

配置完成后，运行：

```bash
cd d:\BaiduNetdiskDownload\prompt-test\docx-image-extractor-mcp
py -m twine upload dist/*
```

## ✅ 验证发布成功

发布成功后，您可以：

1. **访问项目页面**：https://pypi.org/project/docx-image-extractor-mcp/
2. **测试安装**：
   ```bash
   pip install docx-image-extractor-mcp
   ```
3. **验证功能**：
   ```bash
   python -c "import docx_image_extractor_mcp; print('安装成功！')"
   ```

## 🔧 故障排除

### 如果仍然遇到 403 错误：

1. **检查 Token 格式**：确保以 `pypi-` 开头
2. **检查 Token 权限**：确保有上传权限
3. **检查包名**：确保包名没有被占用
4. **重新生成 Token**：删除旧的，创建新的

### 如果包名被占用：

修改 `setup.py` 中的包名，然后重新构建：
```bash
py -m build
py -m twine upload dist/*
```

---

**准备好了吗？** 按照上述步骤配置 API Token，然后运行发布命令！