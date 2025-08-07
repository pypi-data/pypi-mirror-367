"""
接口模块 - 包含CLI和MCP服务器接口
"""

from .cli import main as cli_main
from .mcp_server import DocxImageExtractorMCP

__all__ = [
    "cli_main",
    "DocxImageExtractorMCP",
]