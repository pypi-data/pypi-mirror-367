"""
BiliDownloader - Bilibili视频下载器包
"""

__version__ = "1.0.0"
__author__ = "BiliDownloader Team"
__description__ = "Bilibili视频下载器 - 类似yt-dlp的B站视频下载工具"

# 导入主要类
try:
    from .main_logic import BiliDownloader, ConfigManager
except ImportError:
    # 如果导入失败，可能是在开发环境
    pass