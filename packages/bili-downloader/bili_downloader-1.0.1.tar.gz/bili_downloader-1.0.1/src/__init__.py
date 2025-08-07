"""
BiliDownloader - Bilibili视频下载器
一个类似yt-dlp的B站视频下载工具，支持高质量视频下载、Cookie导入、代理管理等功能
"""

__version__ = "1.0.1"
__author__ = "BiliDownloader Team"
__description__ = "Bilibili视频下载器 - 类似yt-dlp的B站视频下载工具"

from .extractor import BilibiliExtractor
from .downloader import VideoDownloader  
from .converter import VideoConverter
from .cookie_manager import CookieManager
from .proxy_manager import ProxyManager
from .utils import (
    sanitize_filename,
    format_bytes,
    format_duration,
    is_bilibili_url,
    extract_video_id_from_url,
    create_download_directory,
    ConfigManager
)

__all__ = [
    'BilibiliExtractor',
    'VideoDownloader', 
    'VideoConverter',
    'CookieManager',
    'ProxyManager',
    'sanitize_filename',
    'format_bytes',
    'format_duration',
    'is_bilibili_url',
    'extract_video_id_from_url',
    'create_download_directory',
    'ConfigManager'
]