"""
DOCX图片提取器核心模块
"""

import os
import os
import zipfile
import logging
import struct
from pathlib import Path
from typing import Dict, Union

try:
    from pypinyin import lazy_pinyin
except ImportError:
    raise ImportError("需要安装 pypinyin 库: pip install pypinyin")

try:
    import olefile
except ImportError:
    raise ImportError("需要安装 olefile 库: pip install olefile")

# 配置日志
logger = logging.getLogger(__name__)


def to_ascii_dirname(name: str) -> str:
    """
    文档名转英文目录（中文转拼音，去除非字母数字，全小写）
    
    Args:
        name: 文档名称
        
    Returns:
        转换后的英文目录名
    """
    if not name:
        return ""
    
    # 特殊处理：如果文件名以点开头（如 .docx），返回空字符串
    if name.startswith('.'):
        return ""
    
    # 获取文件名（不含扩展名）
    stem = Path(name).stem
    if not stem:  # 如果只有扩展名，返回空字符串
        return ""
    
    # 转换为拼音并转小写
    pinyin_name = ''.join(lazy_pinyin(stem)).lower()
    # 只保留字母和数字
    result = ''.join(ch for ch in pinyin_name if ch.isalnum())
    
    return result


def extract_images(doc_path: str, base_image_dir: str = 'images') -> Dict[str, Union[bool, str, int]]:
    """
    提取 docx 或 doc 所有图片到 base_image_dir/文档英文名/ 下
    
    Args:
        doc_path: Word文档的完整路径（支持 .docx 和 .doc）
        base_image_dir: 图片保存的根目录名（默认：'images'）
        
    Returns:
        包含提取结果的字典，格式：
        {
            'success': bool,
            'msg': str,
            'output_dir': str,
            'count': int,
            'skipped': int (可选)
        }
    """
    logger.info(f"开始提取图片: {doc_path}")
    
    # 路径标准化
    doc_path = os.path.abspath(doc_path)
    base_image_dir = os.path.abspath(base_image_dir)
    
    # 验证输入
    if not os.path.exists(doc_path):
        error_msg = f'文档不存在: {doc_path}'
        logger.error(error_msg)
        return {'success': False, 'msg': error_msg, 'output_dir': '', 'count': 0}
    
    file_ext = doc_path.lower()
    if not (file_ext.endswith('.docx') or file_ext.endswith('.doc')):
        error_msg = '只支持.docx和.doc文件'
        logger.error(error_msg)
        return {'success': False, 'msg': error_msg, 'output_dir': '', 'count': 0}
    
    # 创建输出目录
    doc_dir = to_ascii_dirname(doc_path)
    out_dir = os.path.join(base_image_dir, doc_dir)
    logger.info(f"输出目录: {out_dir}")
    
    try:
        os.makedirs(out_dir, exist_ok=True)
    except Exception as e:
        error_msg = f'创建目录失败: {str(e)}'
        logger.error(error_msg)
        return {'success': False, 'msg': error_msg, 'output_dir': out_dir, 'count': 0}
    
    # 根据文件类型选择处理方式
    if file_ext.endswith('.docx'):
        return _extract_from_docx(doc_path, out_dir)
    elif file_ext.endswith('.doc'):
        return _extract_from_doc(doc_path, out_dir)
    else:
        error_msg = '不支持的文件格式'
        logger.error(error_msg)
        return {'success': False, 'msg': error_msg, 'output_dir': out_dir, 'count': 0}


def _extract_from_docx(docx_path: str, out_dir: str) -> Dict[str, Union[bool, str, int]]:
    """
    从 DOCX 文件中提取图片
    
    Args:
        docx_path: DOCX文件路径
        out_dir: 输出目录
        
    Returns:
        提取结果字典
    """
    count = 0
    skipped = 0
    extracted_files = []
    
    try:
        with zipfile.ZipFile(docx_path, 'r') as zip_ref:
            # 查找所有媒体文件
            media_files = [f for f in zip_ref.namelist() 
                          if f.startswith('word/media/') and not f.endswith('/')]
            
            if not media_files:
                msg = '文档中未找到任何图片'
                logger.warning(msg)
                return {
                    'success': False, 
                    'msg': msg,
                    'output_dir': out_dir,
                    'count': 0
                }
            
            logger.info(f"找到 {len(media_files)} 个媒体文件")
            
            for i, media_file in enumerate(media_files):
                ext = os.path.splitext(media_file)[-1].lower()
                # 如果没有扩展名，尝试从文件内容判断
                if not ext:
                    ext = _detect_image_format(zip_ref, media_file)
                
                out_file = os.path.join(out_dir, f'image_{i+1:03d}{ext}')
                
                try:
                    with zip_ref.open(media_file) as src:
                        data = src.read()
                        if data and len(data) > 0:  # 确保有数据才写入
                            with open(out_file, 'wb') as dst:
                                dst.write(data)
                            count += 1
                            extracted_files.append(out_file)
                            logger.debug(f"提取: {media_file} -> {out_file}")
                        else:
                            logger.warning(f"跳过空文件: {media_file}")
                            skipped += 1
                except Exception as e:
                    logger.warning(f"提取 {media_file} 失败: {str(e)}")
                    skipped += 1
                    # 删除可能创建的空文件
                    if os.path.exists(out_file):
                        os.remove(out_file)
                    continue
                    
    except zipfile.BadZipFile:
        error_msg = f'无效的DOCX文件: {docx_path}'
        logger.error(error_msg)
        return {'success': False, 'msg': error_msg, 'output_dir': out_dir, 'count': 0}
    except Exception as e:
        error_msg = f'提取失败: {str(e)}'
        logger.error(error_msg)
        return {'success': False, 'msg': error_msg, 'output_dir': out_dir, 'count': 0}
    
    # 构建结果
    result = {
        'success': count > 0,
        'output_dir': out_dir,
        'count': count
    }
    
    if count > 0:
        msg = f'成功提取 {count} 个图片到: {out_dir}'
        if skipped > 0:
            msg += f'，跳过 {skipped} 个无效文件'
            result['skipped'] = skipped
        logger.info(msg)
        result['msg'] = msg
    else:
        msg = f'未找到任何有效图片，跳过 {skipped} 个无效文件'
        logger.warning(msg)
        result['msg'] = msg
        result['skipped'] = skipped
    
    return result


def _extract_from_doc(doc_path: str, out_dir: str) -> Dict[str, Union[bool, str, int]]:
    """
    从 DOC 文件中提取图片
    
    Args:
        doc_path: DOC文件路径
        out_dir: 输出目录
        
    Returns:
        提取结果字典
    """
    count = 0
    skipped = 0
    
    try:
        # 检查是否为有效的 OLE 文件
        if not olefile.isOleFile(doc_path):
            error_msg = f'无效的DOC文件: {doc_path}'
            logger.error(error_msg)
            return {'success': False, 'msg': error_msg, 'output_dir': out_dir, 'count': 0}
        
        with olefile.OleFileIO(doc_path) as ole:
            # 查找所有流
            streams = ole.listdir()
            logger.info(f"找到 {len(streams)} 个流")
            
            # 查找包含图片数据的流
            image_streams = []
            for stream in streams:
                stream_name = '/'.join(stream)
                # 查找可能包含图片的流
                if any(keyword in stream_name.lower() for keyword in ['data', 'objinfo', 'object', '1table', 'worddocument']):
                    try:
                        data = ole.openfile(stream).read()
                        # 在数据中查找图片标识符
                        images = _find_images_in_data(data)
                        if images:
                            image_streams.extend(images)
                            logger.debug(f"在流 {stream_name} 中找到 {len(images)} 个图片")
                    except Exception as e:
                        logger.debug(f"读取流 {stream_name} 失败: {str(e)}")
                        continue
            
            if not image_streams:
                msg = '文档中未找到任何图片'
                logger.warning(msg)
                return {
                    'success': False, 
                    'msg': msg,
                    'output_dir': out_dir,
                    'count': 0
                }
            
            logger.info(f"找到 {len(image_streams)} 个图片")
            
            # 保存图片
            for i, image_data in enumerate(image_streams):
                try:
                    # 检测图片格式
                    ext = _detect_image_format_from_data(image_data)
                    out_file = os.path.join(out_dir, f'image_{i+1:03d}{ext}')
                    
                    if len(image_data) > 0:  # 确保有数据才写入
                        with open(out_file, 'wb') as f:
                            f.write(image_data)
                        count += 1
                        logger.debug(f"保存图片: {out_file}")
                    else:
                        logger.warning(f"跳过空图片数据")
                        skipped += 1
                except Exception as e:
                    logger.warning(f"保存图片 {i+1} 失败: {str(e)}")
                    skipped += 1
                    continue
                    
    except Exception as e:
        error_msg = f'提取DOC文件失败: {str(e)}'
        logger.error(error_msg)
        return {'success': False, 'msg': error_msg, 'output_dir': out_dir, 'count': 0}
    
    # 构建结果
    result = {
        'success': count > 0,
        'output_dir': out_dir,
        'count': count
    }
    
    if count > 0:
        msg = f'成功提取 {count} 个图片到: {out_dir}'
        if skipped > 0:
            msg += f'，跳过 {skipped} 个无效文件'
            result['skipped'] = skipped
        logger.info(msg)
        result['msg'] = msg
    else:
        msg = f'未找到任何有效图片，跳过 {skipped} 个无效文件'
        logger.warning(msg)
        result['msg'] = msg
        result['skipped'] = skipped
    
    return result


def _find_images_in_data(data: bytes) -> list:
    """
    在二进制数据中查找图片
    
    Args:
        data: 二进制数据
        
    Returns:
        图片数据列表
    """
    images = []
    
    # 常见图片格式的文件头
    image_headers = [
        (b'\xff\xd8\xff', b'\xff\xd9'),  # JPEG
        (b'\x89PNG\r\n\x1a\n', b'IEND\xaeB`\x82'),  # PNG
        (b'GIF8', b'\x00;'),  # GIF
        (b'BM', None),  # BMP (没有固定结尾)
        (b'RIFF', b'WEBP'),  # WEBP
    ]
    
    for start_marker, end_marker in image_headers:
        pos = 0
        while True:
            # 查找开始标记
            start_pos = data.find(start_marker, pos)
            if start_pos == -1:
                break
                
            if end_marker:
                # 查找结束标记
                end_pos = data.find(end_marker, start_pos + len(start_marker))
                if end_pos != -1:
                    end_pos += len(end_marker)
                    image_data = data[start_pos:end_pos]
                    if len(image_data) > 100:  # 过滤太小的数据
                        images.append(image_data)
                    pos = end_pos
                else:
                    break
            else:
                # BMP 格式特殊处理
                if start_marker == b'BM':
                    try:
                        # BMP 文件头包含文件大小信息
                        if start_pos + 6 < len(data):
                            file_size = struct.unpack('<I', data[start_pos+2:start_pos+6])[0]
                            if start_pos + file_size <= len(data) and file_size > 100:
                                image_data = data[start_pos:start_pos+file_size]
                                images.append(image_data)
                        pos = start_pos + 1
                    except:
                        pos = start_pos + 1
                else:
                    pos = start_pos + 1
    
    return images


def _detect_image_format_from_data(data: bytes) -> str:
    """
    通过数据头检测图片格式
    
    Args:
        data: 图片二进制数据
        
    Returns:
        文件扩展名
    """
    if len(data) < 8:
        return '.png'
        
    # 检测常见图片格式
    if data.startswith(b'\x89PNG'):
        return '.png'
    elif data.startswith(b'\xff\xd8\xff'):
        return '.jpg'
    elif data.startswith(b'GIF8'):
        return '.gif'
    elif data.startswith(b'BM'):
        return '.bmp'
    elif data.startswith(b'RIFF') and b'WEBP' in data[:12]:
        return '.webp'
    else:
        return '.png'  # 默认使用PNG


def _detect_image_format(zip_ref: zipfile.ZipFile, media_file: str) -> str:
    """
    通过文件头检测图片格式
    
    Args:
        zip_ref: ZIP文件引用
        media_file: 媒体文件路径
        
    Returns:
        文件扩展名
    """
    try:
        with zip_ref.open(media_file) as f:
            header = f.read(8)
            
        # 检测常见图片格式
        if header.startswith(b'\x89PNG'):
            return '.png'
        elif header.startswith(b'\xff\xd8\xff'):
            return '.jpg'
        elif header.startswith(b'GIF8'):
            return '.gif'
        elif header.startswith(b'BM'):
            return '.bmp'
        elif header.startswith(b'RIFF') and b'WEBP' in header:
            return '.webp'
        else:
            return '.png'  # 默认使用PNG
    except Exception:
        return '.png'  # 出错时默认使用PNG