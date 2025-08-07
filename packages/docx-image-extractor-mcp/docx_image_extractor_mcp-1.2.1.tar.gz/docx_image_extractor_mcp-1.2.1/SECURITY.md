# 安全策略

## 支持的版本

我们为以下版本提供安全更新：

| 版本 | 支持状态 |
| --- | --- |
| 1.1.x | ✅ |
| 1.0.x | ⚠️ 有限支持 |
| < 1.0 | ❌ |

## 报告安全漏洞

我们非常重视安全问题。如果您发现了安全漏洞，请**不要**通过公开的 Issue 报告。

### 报告方式

1. **私密报告**：通过 GitHub 的私密安全报告功能
2. **邮件报告**：发送邮件至 [security@example.com]
3. **加密通信**：使用我们的 PGP 公钥加密敏感信息

### 报告内容

请在报告中包含以下信息：

- 漏洞的详细描述
- 重现步骤
- 影响范围和严重程度
- 可能的修复建议
- 您的联系方式

### 响应时间

- **确认收到**：24 小时内
- **初步评估**：72 小时内
- **详细分析**：1 周内
- **修复发布**：根据严重程度，1-4 周内

## 安全最佳实践

### 对于用户

1. **及时更新**
   ```bash
   pip install --upgrade docx-image-extractor-mcp
   ```

2. **验证文件来源**
   - 只处理来自可信来源的 DOCX 文件
   - 对未知文件进行病毒扫描

3. **限制输出目录权限**
   ```python
   # 使用受限的输出目录
   extract_images('document.docx', output_dir='/safe/output/path')
   ```

4. **监控资源使用**
   - 处理大文件时监控内存和磁盘使用
   - 设置合理的超时时间

### 对于开发者

1. **输入验证**
   ```python
   # 验证文件路径
   import os
   if not os.path.exists(docx_path):
       raise FileNotFoundError("文件不存在")
   
   # 验证文件类型
   if not docx_path.endswith('.docx'):
       raise ValueError("不支持的文件类型")
   ```

2. **路径遍历防护**
   ```python
   import os.path
   
   # 防止路径遍历攻击
   safe_path = os.path.normpath(output_path)
   if not safe_path.startswith(base_dir):
       raise ValueError("不安全的输出路径")
   ```

3. **资源限制**
   ```python
   # 限制处理的文件大小
   MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
   if os.path.getsize(docx_path) > MAX_FILE_SIZE:
       raise ValueError("文件过大")
   ```

## 已知安全考虑

### 文件处理安全

1. **ZIP 炸弹防护**
   - 限制解压缩后的文件大小
   - 监控解压缩过程中的资源使用

2. **恶意文件检测**
   - 验证 DOCX 文件结构
   - 检查异常的文件内容

3. **路径安全**
   - 防止路径遍历攻击
   - 验证输出路径的安全性

### 依赖安全

我们定期审查和更新依赖项：

```bash
# 检查已知漏洞
pip-audit

# 更新依赖
pip install --upgrade -r requirements.txt
```

### 容器安全

Docker 镜像安全措施：

1. **最小权限原则**
   ```dockerfile
   # 使用非 root 用户
   USER app
   ```

2. **最小化攻击面**
   ```dockerfile
   # 使用 slim 基础镜像
   FROM python:3.10-slim
   ```

3. **定期更新**
   - 基础镜像定期更新
   - 安全补丁及时应用

## 安全配置

### 生产环境配置

```json
{
  "security": {
    "max_file_size": 104857600,
    "allowed_extensions": [".docx"],
    "output_path_validation": true,
    "resource_limits": {
      "memory_mb": 512,
      "timeout_seconds": 300
    }
  }
}
```

### 日志安全

```python
import logging

# 配置安全日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('security.log'),
        logging.StreamHandler()
    ]
)

# 记录安全事件
logger = logging.getLogger('security')
logger.info(f"文件处理: {filename}")
```

## 安全更新

### 自动更新检查

```python
import requests

def check_for_updates():
    """检查是否有安全更新"""
    try:
        response = requests.get(
            'https://api.github.com/repos/owner/docx-image-extractor-mcp/releases/latest',
            timeout=5
        )
        latest_version = response.json()['tag_name']
        # 比较版本并提示更新
    except Exception:
        pass  # 静默失败
```

### 安全补丁策略

- **关键漏洞**：24 小时内发布补丁
- **高危漏洞**：72 小时内发布补丁
- **中危漏洞**：1 周内发布补丁
- **低危漏洞**：下个版本中修复

## 安全审计

### 代码审计

我们使用以下工具进行安全审计：

```bash
# 静态代码分析
bandit -r docx_image_extractor_mcp/

# 依赖漏洞扫描
safety check

# 代码质量检查
sonarqube-scanner
```

### 第三方审计

- 定期进行第三方安全审计
- 参与负责任的漏洞披露计划
- 与安全研究社区合作

## 联系信息

- **安全团队邮箱**：security@example.com
- **PGP 公钥**：[链接到公钥]
- **安全公告**：[GitHub Security Advisories]

## 致谢

感谢以下安全研究人员的贡献：

- [研究人员姓名] - 发现并报告了 [漏洞描述]

---

**注意**：本文档会定期更新。请关注最新版本以获取最新的安全信息。