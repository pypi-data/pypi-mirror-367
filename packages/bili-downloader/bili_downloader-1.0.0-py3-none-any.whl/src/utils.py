"""
工具函数模块
提供通用的工具函数
"""

import os
import re
import hashlib
from typing import Optional, Dict
from urllib.parse import urlparse


def sanitize_filename(filename: str, max_length: int = 200) -> str:
    """
    清理文件名，移除非法字符
    
    Args:
        filename: 原始文件名
        max_length: 最大长度
    
    Returns:
        str: 清理后的文件名
    """
    # 移除或替换非法字符
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = re.sub(r'\s+', ' ', filename)  # 合并多个空格
    filename = filename.strip()
    
    # 限制长度
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        available_length = max_length - len(ext)
        filename = name[:available_length] + ext
    
    return filename


def format_bytes(bytes_count: int) -> str:
    """
    格式化字节数为人类可读格式
    
    Args:
        bytes_count: 字节数
    
    Returns:
        str: 格式化后的字符串
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_count < 1024.0:
            return f"{bytes_count:.1f} {unit}"
        bytes_count /= 1024.0
    return f"{bytes_count:.1f} PB"


def format_duration(seconds: int) -> str:
    """
    格式化时长为 HH:MM:SS 格式
    
    Args:
        seconds: 秒数
    
    Returns:
        str: 格式化后的时长字符串
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"


def get_file_hash(file_path: str, algorithm: str = 'md5') -> Optional[str]:
    """
    计算文件哈希值
    
    Args:
        file_path: 文件路径
        algorithm: 哈希算法 (md5, sha1, sha256)
    
    Returns:
        str: 文件哈希值
    """
    if not os.path.exists(file_path):
        return None
    
    try:
        hash_algo = hashlib.new(algorithm)
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_algo.update(chunk)
        return hash_algo.hexdigest()
    except Exception as e:
        print(f"计算文件哈希失败: {e}")
        return None


def extract_video_id_from_url(url: str) -> Optional[str]:
    """
    从URL中提取视频ID
    
    Args:
        url: 视频URL
    
    Returns:
        str: 视频ID (BV号或AV号)
    """
    patterns = [
        r'BV[a-zA-Z0-9]{10}',  # BV号
        r'av(\d+)',            # AV号
        r'/video/(BV[a-zA-Z0-9]{10})',
        r'/video/av(\d+)',
        r'bilibili\.com/.*?/(BV[a-zA-Z0-9]{10})',
        r'bilibili\.com/.*?/av(\d+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1) if match.groups() else match.group(0)
    
    return None


def validate_url(url: str) -> bool:
    """
    验证URL是否有效
    
    Args:
        url: 待验证的URL
    
    Returns:
        bool: URL是否有效
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def is_bilibili_url(url: str) -> bool:
    """
    检查是否为B站URL
    
    Args:
        url: 待检查的URL
    
    Returns:
        bool: 是否为B站URL
    """
    bilibili_domains = [
        'bilibili.com',
        'www.bilibili.com',
        'b23.tv',
        'm.bilibili.com'
    ]
    
    try:
        parsed = urlparse(url)
        return any(domain in parsed.netloc for domain in bilibili_domains)
    except Exception:
        return False


def create_download_directory(base_dir: str, video_title: str) -> str:
    """
    创建下载目录
    
    Args:
        base_dir: 基础目录
        video_title: 视频标题
    
    Returns:
        str: 创建的目录路径
    """
    safe_title = sanitize_filename(video_title)
    download_dir = os.path.join(base_dir, safe_title)
    os.makedirs(download_dir, exist_ok=True)
    return download_dir


def get_available_filename(file_path: str) -> str:
    """
    获取可用的文件名，如果文件存在则添加数字后缀
    
    Args:
        file_path: 原始文件路径
    
    Returns:
        str: 可用的文件路径
    """
    if not os.path.exists(file_path):
        return file_path
    
    base, ext = os.path.splitext(file_path)
    counter = 1
    
    while True:
        new_path = f"{base}_{counter}{ext}"
        if not os.path.exists(new_path):
            return new_path
        counter += 1


def parse_quality_desc(quality_id: int) -> str:
    """
    解析质量ID为描述文字
    
    Args:
        quality_id: 质量ID
    
    Returns:
        str: 质量描述
    """
    quality_map = {
        120: "4K超清",
        116: "1080P60高帧率",
        112: "1080P高码率",
        80: "1080P高清",
        74: "720P60高帧率", 
        64: "720P高清",
        32: "480P清晰",
        16: "360P流畅"
    }
    
    return quality_map.get(quality_id, f"未知质量({quality_id})")


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> Dict:
        """加载配置"""
        if os.path.exists(self.config_file):
            try:
                import json
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载配置文件失败: {e}")
        
        return self.get_default_config()
    
    def save_config(self) -> bool:
        """保存配置"""
        try:
            import json
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False
    
    def get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            "download_dir": "./downloads",
            "ffmpeg_path": "ffmpeg", 
            "max_retries": 3,
            "chunk_size": 8192,
            "timeout": 30,
            "cleanup_temp": True,
            "video_quality": 80,  # 1080P
            "disable_proxy": True,  # 默认禁用代理
            "proxy_detection": True,  # 启用代理检测
            "auto_disable_proxy": True,  # 自动禁用代理
            "proxy_warning": True  # 显示代理警告
        }
    
    def get(self, key: str, default=None):
        """获取配置值"""
        return self.config.get(key, default)
    
    def set(self, key: str, value):
        """设置配置值"""
        self.config[key] = value