#!/usr/bin/env python3
"""
Bilibili视频下载器主程序
模仿yt-dlp等工具，支持下载B站视频并转换为MP4格式
"""

import sys
import os
import argparse
from typing import Optional

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.extractor import BilibiliExtractor
from src.downloader import VideoDownloader
from src.converter import VideoConverter
from src.cookie_manager import CookieManager
from src.utils import (
    sanitize_filename, 
    format_bytes, 
    format_duration,
    is_bilibili_url, 
    extract_video_id_from_url,
    create_download_directory,
    ConfigManager
)
from src.ui import UIManager, EnhancedProgressBar, ui


class BiliDownloader:
    """Bilibili视频下载器主类"""
    
    def __init__(self, config_manager: ConfigManager, cookie_file: str = None, cookie_string: str = None, disable_proxy: bool = None):
        self.ui = UIManager()
        self.config = config_manager
        
        # 确定代理设置
        if disable_proxy is None:
            disable_proxy = config_manager.get('disable_proxy', True)
        
        self.extractor = BilibiliExtractor(
            cookie_file=cookie_file, 
            disable_proxy=disable_proxy
        )
        
        # 如果提供了Cookie字符串，加载它
        if cookie_string:
            self.extractor.load_cookies_from_string(cookie_string)
        
        self.downloader = VideoDownloader(
            chunk_size=config_manager.get('chunk_size', 8192),
            timeout=config_manager.get('timeout', 30),
            disable_proxy=disable_proxy
        )
        self.converter = VideoConverter(
            ffmpeg_path=config_manager.get('ffmpeg_path', 'ffmpeg')
        )
    
    def prompt_for_cookies_if_needed(self) -> bool:
        """如果需要更高质量，提示用户输入Cookie"""
        if not self.extractor.is_logged_in():
            self.ui.show_cookie_prompt()
            
            while True:
                choice = self.ui.input_with_style("是否导入Cookie？(y/N):").lower().strip()
                
                if choice == 'y':
                    return self._handle_cookie_input()
                elif choice in ('n', ''):
                    self.ui.show_info("跳过Cookie导入，使用游客权限", "🔓")
                    return False
                else:
                    self.ui.show_warning("请输入 y 或 n")
        return True
    
    def _handle_cookie_input(self) -> bool:
        """处理Cookie输入"""
        self.ui.show_info("Cookie导入方式:")
        self.ui.console.print("[cyan]1.[/cyan] 从文件导入 (Netscape格式)")
        self.ui.console.print("[cyan]2.[/cyan] 直接粘贴Cookie字符串")
        
        while True:
            method = self.ui.input_with_style("请选择导入方式 (1/2/回车取消):").strip()
            
            if not method:
                self.ui.show_info("取消Cookie导入")
                return False
            elif method == '1':
                return self._handle_cookie_file()
            elif method == '2':
                return self._handle_cookie_paste()
            else:
                self.ui.show_warning("请输入 1、2 或回车")
    
    def _handle_cookie_file(self) -> bool:
        """处理Cookie文件输入"""
        self.ui.console.print("\n[yellow]Cookie文件格式说明:[/yellow]")
        self.ui.console.print("[cyan]1.[/cyan] 支持Netscape格式 (推荐)")
        self.ui.console.print("[cyan]2.[/cyan] 可使用浏览器插件如Cookie-Editor导出")
        self.ui.console.print("[cyan]3.[/cyan] 文件应包含bilibili.com的Cookie")
        
        while True:
            cookie_path = self.ui.input_with_style("请输入Cookie文件路径 (回车返回):").strip()
            
            if not cookie_path:
                return self._handle_cookie_input()
            
            # 尝试加载Cookie
            if self.extractor.load_cookies(cookie_path):
                user_info = self.extractor.get_user_info()
                if user_info.get('logged_in'):
                    self.ui.show_success(f"Cookie加载成功！用户ID: {user_info.get('user_id')}")
                    return True
                else:
                    self.ui.show_warning("Cookie加载成功，但未检测到有效登录状态")
                    return False
            else:
                retry = self.ui.input_with_style("Cookie加载失败，是否重试？(y/N/r返回):", "yellow").lower()
                if retry == 'r':
                    return self._handle_cookie_input()
                elif retry != 'y':
                    return False
    
    def _handle_cookie_paste(self) -> bool:
        """处理Cookie粘贴输入"""
        self.ui.console.print("\n[yellow]Cookie字符串说明:[/yellow]")
        self.ui.console.print("[cyan]1.[/cyan] 支持多种格式：Netscape格式、浏览器Cookie字符串等")
        self.ui.console.print("[cyan]2.[/cyan] 可以从浏览器开发者工具复制Cookie")
        self.ui.console.print("[cyan]3.[/cyan] 输入完成后按回车两次")
        self.ui.console.print("\n[bold]请粘贴Cookie字符串 (多行输入，连续两个回车结束):[/bold]")
        
        lines = []
        empty_count = 0
        
        while True:
            try:
                line = input()
                if not line.strip():
                    empty_count += 1
                    if empty_count >= 2:
                        break
                else:
                    empty_count = 0
                    lines.append(line)
            except (EOFError, KeyboardInterrupt):
                self.ui.show_info("取消输入")
                return self._handle_cookie_input()
        
        if not lines:
            self.ui.show_warning("未输入任何Cookie内容")
            return self._handle_cookie_input()
        
        cookie_string = '\n'.join(lines)
        
        # 尝试解析Cookie
        if self.extractor.load_cookies_from_string(cookie_string):
            user_info = self.extractor.get_user_info()
            if user_info.get('logged_in'):
                print(f"✓ Cookie解析成功！用户ID: {user_info.get('user_id')}")
                return True
            else:
                print("⚠ Cookie解析成功，但未检测到有效登录状态")
                return False
        else:
            retry = input("Cookie解析失败，是否重试？(y/N/r返回): ").lower()
            if retry == 'r':
                return self._handle_cookie_input()
            elif retry == 'y':
                return self._handle_cookie_paste()
            else:
                return False
    
    def download_video(self, url: str, output_dir: str = None, prompt_cookies: bool = True, check_proxy: bool = True) -> bool:
        """
        下载视频
        
        Args:
            url: 视频URL
            output_dir: 输出目录
            prompt_cookies: 是否提示导入Cookie
            check_proxy: 是否检查代理状态
        
        Returns:
            bool: 下载是否成功
        """
        print(f"开始处理视频: {url}")
        
        # 检查代理状态
        if check_proxy and self.config.get('proxy_detection', True):
            print("\n🔍 检查网络连接状态...")
            proxy_active, can_connect = self.extractor.check_proxy_status(
                show_report=self.config.get('proxy_warning', True)
            )
            
            if proxy_active and not can_connect:
                print("⚠ 检测到代理/VPN可能影响B站连接，建议临时关闭代理")
                choice = input("是否继续下载？(y/N): ").lower().strip()
                if choice != 'y':
                    print("取消下载")
                    return False
        
        # 验证URL
        if not is_bilibili_url(url):
            print("错误: 不是有效的Bilibili URL")
            return False
        
        # 提示导入Cookie（如果需要）
        if prompt_cookies and not self.extractor.is_logged_in():
            self.prompt_for_cookies_if_needed()
        
        # 显示登录状态
        self.ui.show_login_status(
            self.extractor.is_logged_in(),
            self.extractor.get_user_info().get('user_id') if self.extractor.is_logged_in() else None
        )
        
        # 提取视频ID
        video_id = extract_video_id_from_url(url)
        if not video_id:
            self.ui.show_error("无法从URL中提取视频ID")
            return False
        
        self.ui.show_info(f"视频ID: {video_id}", "[ID]")
        
        # 获取视频基本信息
        self.ui.show_step("获取视频信息", 3)
        video_info = self.extractor.get_video_info(url)
        if not video_info:
            self.ui.show_error("无法获取视频信息")
            return False
        
        title = video_info.get('title', 'Unknown Title')
        bvid = video_info.get('bvid', '')
        cid = video_info.get('cid', '')
        
        # 显示视频信息表格
        self.ui.show_video_info({
            'title': title,
            'bvid': bvid,
            'cid': str(cid),
            'duration': video_info.get('duration', 'Unknown'),
            'uploader': video_info.get('uploader', 'Unknown')
        })
        
        if not bvid or not cid:
            self.ui.show_error("缺少必要的视频标识符")
            return False
        
        # 获取播放流信息
        self.ui.show_step("获取播放流信息", 4)
        stream_info = self.extractor.get_video_streams(bvid, cid)
        if not stream_info:
            self.ui.show_error("无法获取播放流信息")
            return False
        
        # 获取最佳质量的视频和音频流
        video_url, audio_url = self.extractor.get_best_quality_streams(stream_info)
        
        if not video_url and not audio_url:
            self.ui.show_error("未找到可用的视频流")
            return False
        
        # 显示流信息
        self.ui.show_stream_info(bool(video_url), bool(audio_url))
        
        # 设置下载目录
        if not output_dir:
            output_dir = self.config.get('download_dir', './downloads')
        
        # 创建下载目录
        download_dir = create_download_directory(output_dir, title)
        self.ui.show_info(f"下载目录: {download_dir}", "[DIR]")
        
        # 下载文件
        safe_filename = sanitize_filename(title)
        download_results = self.downloader.download_m4s_streams(
            video_url, audio_url, download_dir, safe_filename
        )
        
        video_path = download_results.get('video_path')
        audio_path = download_results.get('audio_path')
        
        if not video_path and not audio_path:
            self.ui.show_error("下载失败")
            return False
        
        # 转换为MP4
        output_mp4 = os.path.join(download_dir, f"{safe_filename}.mp4")
        
        success = False
        if video_path and audio_path:
            # 合并视频和音频
            self.ui.show_step("合并视频和音频", 5)
            success = self.converter.merge_m4s_to_mp4(
                video_path, audio_path, output_mp4, 
                cleanup_temp=self.config.get('cleanup_temp', True)
            )
        elif video_path:
            # 只有视频流
            self.ui.show_step("转换视频")
            success = self.converter.convert_single_m4s_to_mp4(
                video_path, output_mp4,
                cleanup_temp=self.config.get('cleanup_temp', True)
            )
        elif audio_path:
            # 只有音频流
            self.ui.show_step("转换音频")
            success = self.converter.convert_single_m4s_to_mp4(
                audio_path, output_mp4,
                cleanup_temp=self.config.get('cleanup_temp', True)
            )
        
        if success:
            # 显示文件信息
            file_size_str = "Unknown"
            if os.path.exists(output_mp4):
                file_size = os.path.getsize(output_mp4)
                file_size_str = format_bytes(file_size)
            
            # 显示下载完成摘要
            self.ui.show_download_summary(output_mp4, file_size_str)
        else:
            self.ui.show_error("转换失败")
            return False
        
        return True


def main():
    """主函数"""
    # 初始化UI管理器并显示横幅
    ui_manager = UIManager()
    ui_manager.show_banner()
    
    parser = argparse.ArgumentParser(
        description='Bilibili视频下载器 - 类似yt-dlp的B站视频下载工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s https://www.bilibili.com/video/BV1234567890
  %(prog)s -o ./downloads https://www.bilibili.com/video/BV1234567890
  %(prog)s --cookies cookies.txt https://www.bilibili.com/video/BV1234567890
  %(prog)s --ffmpeg-path /usr/local/bin/ffmpeg <URL>

Cookie说明:
  支持Netscape格式的Cookie文件，可通过浏览器插件导出
  Cookie文件示例格式：
  .bilibili.com	TRUE	/	FALSE	0	SESSDATA	your_sessdata_here
        """
    )
    
    parser.add_argument('url', help='Bilibili视频URL')
    parser.add_argument('-o', '--output', help='输出目录 (默认: ./downloads)')
    parser.add_argument('--cookies', help='Cookie文件路径 (Netscape格式)')
    parser.add_argument('--cookie-string', help='直接粘贴Cookie字符串（替代文件）')
    parser.add_argument('--ffmpeg-path', help='FFmpeg可执行文件路径')
    parser.add_argument('--no-cleanup', action='store_true', help='不清理临时文件')
    parser.add_argument('--no-cookie-prompt', action='store_true', help='不提示输入Cookie')
    parser.add_argument('--chunk-size', type=int, default=8192, help='下载块大小')
    parser.add_argument('--timeout', type=int, default=30, help='请求超时时间')
    parser.add_argument('--retries', type=int, default=3, help='最大重试次数')
    parser.add_argument('--no-proxy-check', action='store_true', help='跳过代理检测')
    parser.add_argument('--enable-proxy', action='store_true', help='允许使用代理（默认禁用）')
    parser.add_argument('-v', '--verbose', action='store_true', help='显示详细信息')
    
    args = parser.parse_args()
    
    # 加载配置
    config_manager = ConfigManager()
    
    # 应用命令行参数
    if args.output:
        config_manager.set('download_dir', args.output)
    if args.ffmpeg_path:
        config_manager.set('ffmpeg_path', args.ffmpeg_path)
    if args.no_cleanup:
        config_manager.set('cleanup_temp', False)
    if args.chunk_size:
        config_manager.set('chunk_size', args.chunk_size)
    if args.timeout:
        config_manager.set('timeout', args.timeout)
    if args.retries:
        config_manager.set('max_retries', args.retries)
    if args.no_proxy_check:
        config_manager.set('proxy_detection', False)
    if args.enable_proxy:
        config_manager.set('disable_proxy', False)
    
    # 创建下载器实例
    downloader = BiliDownloader(
        config_manager, 
        cookie_file=args.cookies,
        cookie_string=args.cookie_string,
        disable_proxy=not args.enable_proxy if args.enable_proxy else None
    )
    
    # 检查FFmpeg
    if not downloader.converter.check_ffmpeg():
        ui_manager.show_ffmpeg_warning()
        return 1
    
    # 显示Cookie状态
    if args.cookies or args.cookie_string:
        if downloader.extractor.is_logged_in():
            user_info = downloader.extractor.get_user_info()
            ui_manager.show_success(f"Cookie加载成功，用户ID: {user_info.get('user_id')}")
        else:
            ui_manager.show_warning("Cookie加载但未检测到有效登录状态")
    
    # 开始下载
    try:
        success = downloader.download_video(
            args.url, 
            args.output, 
            prompt_cookies=not args.no_cookie_prompt and not args.cookies and not args.cookie_string,
            check_proxy=not args.no_proxy_check
        )
        return 0 if success else 1
    except KeyboardInterrupt:
        ui_manager.show_warning("用户取消下载", "[STOP]")
        return 1
    except Exception as e:
        ui_manager.show_error(f"下载过程中出现错误: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())