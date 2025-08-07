"""
配置模块
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# 默认配置
DEFAULT_CONFIG = {
    "base_image_dir": "images",
    "image_naming": {
        "prefix": "image",
        "padding": 3,
        "format": "{prefix}_{index:0{padding}d}{ext}"
    },
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    },
    "extraction": {
        "skip_empty_files": True,
        "detect_format": True,
        "supported_formats": [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"]
    }
}


class Config:
    """配置管理类"""
    
    def __init__(self, config_path: Optional[str] = None):
        self._config = DEFAULT_CONFIG.copy()
        self._config_path = config_path
        
        if config_path and os.path.exists(config_path):
            self.load_from_file(config_path)
        
        self._setup_logging()
    
    def load_from_file(self, config_path: str) -> None:
        """从文件加载配置"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
            self._merge_config(user_config)
        except Exception as e:
            logging.warning(f"加载配置文件失败: {e}")
    
    def _merge_config(self, user_config: Dict[str, Any]) -> None:
        """合并用户配置"""
        def merge_dict(base: dict, update: dict) -> dict:
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    merge_dict(base[key], value)
                else:
                    base[key] = value
            return base
        
        merge_dict(self._config, user_config)
    
    def _setup_logging(self) -> None:
        """设置日志"""
        log_config = self._config.get("logging", {})
        level = getattr(logging, log_config.get("level", "INFO").upper())
        format_str = log_config.get("format", DEFAULT_CONFIG["logging"]["format"])
        
        logging.basicConfig(level=level, format=format_str)
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """设置配置值"""
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save_to_file(self, config_path: Optional[str] = None) -> None:
        """保存配置到文件"""
        path = config_path or self._config_path
        if not path:
            raise ValueError("未指定配置文件路径")
        
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self._config, f, indent=2, ensure_ascii=False)
    
    @property
    def base_image_dir(self) -> str:
        """获取基础图片目录"""
        return self.get("base_image_dir", "images")
    
    @property
    def image_naming_format(self) -> str:
        """获取图片命名格式"""
        naming = self.get("image_naming", {})
        return naming.get("format", "{prefix}_{index:0{padding}d}{ext}")
    
    @property
    def image_naming_prefix(self) -> str:
        """获取图片命名前缀"""
        return self.get("image_naming.prefix", "image")
    
    @property
    def image_naming_padding(self) -> int:
        """获取图片命名填充位数"""
        return self.get("image_naming.padding", 3)
    
    @property
    def supported_formats(self) -> list:
        """获取支持的图片格式"""
        return self.get("extraction.supported_formats", [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"])


# 全局配置实例
config = Config()


def get_config_path() -> str:
    """获取默认配置文件路径"""
    home_dir = Path.home()
    config_dir = home_dir / ".docx-image-extractor"
    config_dir.mkdir(exist_ok=True)
    return str(config_dir / "config.json")


def load_config(config_path: Optional[str] = None) -> Config:
    """加载配置"""
    if config_path is None:
        config_path = get_config_path()
    
    return Config(config_path)