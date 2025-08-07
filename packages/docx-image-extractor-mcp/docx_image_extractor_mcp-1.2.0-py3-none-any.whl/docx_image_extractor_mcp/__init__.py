"""
DOCX Image Extractor MCP

一个功能强大的DOCX图片提取器，支持MCP协议，可与Claude Desktop等AI工具集成。

主要功能：
- 从Word文档中提取所有图片
- 自动检测图片格式
- 支持中文文档名转拼音
- 提供MCP协议接口
- 支持配置文件自定义
"""

__version__ = "1.1.0"
__author__ = "DOCX Image Extractor Team"
__email__ = "contact@example.com"

from .core.extractor import extract_images, to_ascii_dirname
from .interfaces.mcp_server import DocxImageExtractorMCP
from .core.config import config, Config, load_config

__all__ = [
    "extract_images",
    "to_ascii_dirname", 
    "DocxImageExtractorMCP",
    "config",
    "Config",
    "load_config",
]