#!/usr/bin/env python3
"""
BiliDownloader 命令行入口点
"""

def main():
    """命令行主入口"""
    import sys
    import os
    import argparse
    from typing import Optional

    # 尝试导入模块，支持多种安装方式
    try:
        # 尝试从包中导入
        from bili_downloader.main_logic import BiliDownloader, ConfigManager
        # 导入UI模块
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
        from ui import UIManager
    except ImportError:
        try:
            # 尝试从开发环境导入
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            if project_root not in sys.path:
                sys.path.insert(0, project_root)
            from main import BiliDownloader, ConfigManager
            # 导入UI模块
            sys.path.insert(0, os.path.join(project_root, 'src'))
            from ui import UIManager
        except ImportError as e:
            print(f"错误: 无法导入必要模块 - {e}")
            print("请重新安装 bili-downloader")
            return 1
    
    # 初始化UI管理器并显示横幅
    ui_manager = UIManager()
    ui_manager.show_banner()

    # 主函数逻辑
    parser = argparse.ArgumentParser(
        description='Bilibili视频下载器 - 类似yt-dlp的B站视频下载工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s https://www.bilibili.com/video/BV1234567890
  %(prog)s -o ./downloads https://www.bilibili.com/video/BV1234567890
  %(prog)s --cookies cookies.txt https://www.bilibili.com/video/BV1234567890
  %(prog)s --cookie-string "SESSDATA=xxx" https://www.bilibili.com/video/BV1234567890
  %(prog)s --ffmpeg-path /usr/local/bin/ffmpeg <URL>

Cookie说明:
  支持Netscape格式的Cookie文件，可通过浏览器插件导出
  也支持直接粘贴Cookie字符串
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

if __name__ == '__main__':
    import sys
    sys.exit(main())