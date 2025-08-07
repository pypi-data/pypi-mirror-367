"""
主入口模块
"""

import asyncio
import sys
from .interfaces.mcp_server import DocxImageExtractorMCP


async def main():
    """主函数"""
    try:
        mcp_service = DocxImageExtractorMCP()
        await mcp_service.run()
    except KeyboardInterrupt:
        print("\n服务已停止")
        sys.exit(0)
    except Exception as e:
        print(f"启动服务失败: {e}")
        sys.exit(1)


def cli_main():
    """命令行入口点"""
    asyncio.run(main())


if __name__ == "__main__":
    cli_main()