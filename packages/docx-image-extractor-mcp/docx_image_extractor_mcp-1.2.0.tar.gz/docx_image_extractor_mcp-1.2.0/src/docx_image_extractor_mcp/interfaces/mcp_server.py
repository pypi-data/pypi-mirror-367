"""
MCP服务器模块
"""

import json
import logging
from typing import List, Dict, Any

from ..core.extractor import extract_images, to_ascii_dirname
from ..core.config import config

logger = logging.getLogger(__name__)


class DocxImageExtractorMCP:
    """DOCX图片提取器MCP服务"""
    
    def __init__(self):
        try:
            from mcp.server import Server
            from mcp.server.models import InitializationOptions
            from mcp.server import NotificationOptions
            from mcp.types import Tool, TextContent
        except ImportError:
            raise ImportError("需要安装 mcp 库: pip install mcp")
            
        self.server = Server("docx-image-extractor")
        self.Tool = Tool
        self.TextContent = TextContent
        self.InitializationOptions = InitializationOptions
        self.NotificationOptions = NotificationOptions
        self.setup_tools()
        
        logger.info("DOCX图片提取器MCP服务已初始化")

    def setup_tools(self):
        """设置MCP工具"""
        
        @self.server.list_tools()
        async def handle_list_tools():
            return [
                self.Tool(
                    name="extract_docx_images",
                    description="从Word文档(.docx)中提取所有图片到指定目录，支持自动命名和格式检测",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "docx_path": {
                                "type": "string",
                                "description": "Word文档的完整路径"
                            },
                            "base_image_dir": {
                                "type": "string",
                                "description": "存放图片的根目录名（如 images、assets、pictures等）",
                                "default": config.base_image_dir
                            }
                        },
                        "required": ["docx_path"]
                    }
                ),
                self.Tool(
                    name="preview_docx_structure",
                    description="预览Word文档的内部结构，包括媒体文件信息",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "docx_path": {
                                "type": "string",
                                "description": "Word文档的完整路径"
                            }
                        },
                        "required": ["docx_path"]
                    }
                ),
                self.Tool(
                    name="convert_filename_to_ascii",
                    description="将中文文件名转换为ASCII字符（拼音），用于目录命名",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "要转换的文件名"
                            }
                        },
                        "required": ["filename"]
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict):
            try:
                if name == "extract_docx_images":
                    return await self._handle_extract_images(arguments)
                elif name == "preview_docx_structure":
                    return await self._handle_preview_structure(arguments)
                elif name == "convert_filename_to_ascii":
                    return await self._handle_convert_filename(arguments)
                else:
                    return [self.TextContent(type="text", text=f"未知工具: {name}")]
            except Exception as e:
                logger.error(f"工具调用失败 {name}: {e}")
                return [self.TextContent(type="text", text=f"工具执行失败: {str(e)}")]
    
    async def _handle_extract_images(self, arguments: dict) -> List:
        """处理图片提取"""
        docx_path = arguments["docx_path"]
        base_image_dir = arguments.get("base_image_dir", config.base_image_dir)
        
        logger.info(f"开始提取图片: {docx_path}")
        result = extract_images(docx_path, base_image_dir)
        
        # 构建详细的响应消息
        if result['success']:
            response = {
                "status": "success",
                "message": result['msg'],
                "details": {
                    "extracted_count": result['count'],
                    "output_directory": result['output_dir'],
                    "skipped_count": result.get('skipped', 0)
                }
            }
        else:
            response = {
                "status": "error",
                "message": result['msg'],
                "details": {
                    "extracted_count": result.get('count', 0),
                    "output_directory": result.get('output_dir', ''),
                    "skipped_count": result.get('skipped', 0)
                }
            }
        
        return [self.TextContent(type="text", text=json.dumps(response, ensure_ascii=False, indent=2))]
    
    async def _handle_preview_structure(self, arguments: dict) -> List:
        """处理文档结构预览"""
        import zipfile
        import os
        
        docx_path = arguments["docx_path"]
        
        if not os.path.exists(docx_path):
            return [self.TextContent(type="text", text=f"文档不存在: {docx_path}")]
        
        if not docx_path.lower().endswith('.docx'):
            return [self.TextContent(type="text", text="只支持.docx文件")]
        
        try:
            with zipfile.ZipFile(docx_path, 'r') as zip_ref:
                all_files = zip_ref.namelist()
                media_files = [f for f in all_files if f.startswith('word/media/') and not f.endswith('/')]
                
                structure = {
                    "document_path": docx_path,
                    "total_files": len(all_files),
                    "media_files_count": len(media_files),
                    "media_files": []
                }
                
                for media_file in media_files:
                    try:
                        file_info = zip_ref.getinfo(media_file)
                        structure["media_files"].append({
                            "path": media_file,
                            "size": file_info.file_size,
                            "compressed_size": file_info.compress_size
                        })
                    except Exception as e:
                        logger.warning(f"获取文件信息失败 {media_file}: {e}")
                
                return [self.TextContent(type="text", text=json.dumps(structure, ensure_ascii=False, indent=2))]
                
        except Exception as e:
            return [self.TextContent(type="text", text=f"预览文档结构失败: {str(e)}")]
    
    async def _handle_convert_filename(self, arguments: dict) -> List:
        """处理文件名转换"""
        filename = arguments["filename"]
        converted = to_ascii_dirname(filename)
        
        result = {
            "original": filename,
            "converted": converted,
            "message": f"文件名 '{filename}' 转换为 '{converted}'"
        }
        
        return [self.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

    async def run(self):
        """运行MCP服务器"""
        try:
            from mcp.server.stdio import stdio_server
        except ImportError:
            raise ImportError("需要安装 mcp 库: pip install mcp")
            
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.InitializationOptions(
                    server_name="docx-image-extractor",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=self.NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )