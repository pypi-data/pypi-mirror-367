"""
CLI界面美化工具模块
提供彩色输出、进度条、ASCII艺术等功能
"""

import time
from typing import Optional, Dict, Any
from rich.console import Console
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn, SpinnerColumn
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
from rich.align import Align


class UIManager:
    """UI管理器类，负责所有界面美化"""
    
    def __init__(self):
        self.console = Console()
        self.current_progress = None
        
    def show_banner(self):
        """显示应用程序横幅"""
        banner_art = """
[bold magenta]
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║                    [cyan]专业的B站视频下载工具[/cyan]                         ║
║                      [dim]版本: v2.0.0 - Enhanced UI[/dim]                  ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
[/bold magenta]
        """
        self.console.print(Align.center(banner_art))
        self.console.print()
    
    def show_info(self, message: str, emoji: str = "[i]"):
        """显示信息消息"""
        self.console.print(f"[bold blue]{emoji} {message}[/bold blue]")
    
    def show_success(self, message: str, emoji: str = "[OK]"):
        """显示成功消息"""
        self.console.print(f"[bold green]{emoji} {message}[/bold green]")
    
    def show_warning(self, message: str, emoji: str = "[!]"):
        """显示警告消息"""
        self.console.print(f"[bold yellow]{emoji} {message}[/bold yellow]")
    
    def show_error(self, message: str, emoji: str = "[X]"):
        """显示错误消息"""
        self.console.print(f"[bold red]{emoji} {message}[/bold red]")
    
    def show_step(self, message: str, step_num: Optional[int] = None):
        """显示步骤消息"""
        if step_num:
            self.console.print(f"[bold cyan]> 步骤 {step_num}: {message}[/bold cyan]")
        else:
            self.console.print(f"[bold cyan]> {message}[/bold cyan]")
    
    def show_video_info(self, video_info: Dict[str, Any]):
        """显示视频信息表格"""
        table = Table(title="视频信息", box=box.ROUNDED)
        table.add_column("属性", style="cyan", no_wrap=True)
        table.add_column("值", style="magenta")
        
        table.add_row("标题", str(video_info.get('title', 'Unknown')))
        table.add_row("BVID", str(video_info.get('bvid', 'Unknown')))
        table.add_row("CID", str(video_info.get('cid', 'Unknown')))
        table.add_row("时长", str(video_info.get('duration', 'Unknown')))
        table.add_row("作者", str(video_info.get('uploader', 'Unknown')))
        
        self.console.print(table)
        self.console.print()
    
    def show_stream_info(self, has_video: bool, has_audio: bool):
        """显示流信息"""
        table = Table(title="流信息", box=box.SIMPLE)
        table.add_column("类型", style="cyan")
        table.add_column("状态", style="green")
        
        video_status = "[OK] 可用" if has_video else "[X] 不可用"
        audio_status = "[OK] 可用" if has_audio else "[X] 不可用"
        
        table.add_row("视频流", video_status)
        table.add_row("音频流", audio_status)
        
        self.console.print(table)
        self.console.print()
    
    def show_download_summary(self, file_path: str, file_size: str):
        """显示下载完成摘要"""
        panel = Panel(
            f"[green][OK] 下载完成！[/green]\n\n"
            f"[cyan]文件位置:[/cyan] {file_path}\n"
            f"[cyan]文件大小:[/cyan] {file_size}",
            title="下载摘要",
            border_style="green"
        )
        self.console.print(panel)
    
    def create_download_progress(self, task_name: str = "下载中") -> Progress:
        """创建下载进度条"""
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=40),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            console=self.console
        )
        
        self.current_progress = progress
        return progress
    
    def show_cookie_prompt(self):
        """显示Cookie输入提示"""
        panel = Panel(
            "[yellow][Cookie] Cookie 导入选项[/yellow]\n\n"
            "导入Cookie可以获取更高质量的视频流（需要B站账号）\n"
            "支持多种Cookie格式：\n"
            "• Netscape格式文件\n"
            "• 浏览器Cookie字符串\n"
            "• 浏览器插件导出",
            title="Cookie设置",
            border_style="yellow"
        )
        self.console.print(panel)
    
    def show_proxy_warning(self):
        """显示代理警告"""
        panel = Panel(
            "[red][!] 网络连接警告[/red]\n\n"
            "检测到代理/VPN可能影响B站连接\n"
            "建议临时关闭代理以获得最佳下载体验",
            title="网络状态",
            border_style="red"
        )
        self.console.print(panel)
    
    def show_login_status(self, is_logged_in: bool, user_id: Optional[str] = None):
        """显示登录状态"""
        if is_logged_in and user_id:
            self.show_success(f"已登录用户: {user_id}", "[USER]")
        else:
            self.show_warning("游客模式：可能无法获取最高质量视频", "[GUEST]")
    
    def show_ffmpeg_warning(self):
        """显示FFmpeg警告"""
        panel = Panel(
            "[red][X] 未找到FFmpeg[/red]\n\n"
            "FFmpeg是视频转换必需的工具\n"
            "请安装FFmpeg: [link]https://ffmpeg.org/download.html[/link]\n\n"
            "安装后重启程序以继续",
            title="依赖检查",
            border_style="red"
        )
        self.console.print(panel)
    
    def input_with_style(self, prompt: str, style: str = "bold cyan") -> str:
        """带样式的输入提示"""
        styled_prompt = f"[{style}]{prompt}[/{style}] "
        self.console.print(styled_prompt, end="")
        return input()
    
    def confirm_with_style(self, prompt: str, default: bool = False) -> bool:
        """带样式的确认提示"""
        default_text = "Y/n" if default else "y/N"
        styled_prompt = f"[bold yellow]{prompt} ({default_text}):[/bold yellow] "
        self.console.print(styled_prompt, end="")
        
        response = input().lower().strip()
        if not response:
            return default
        return response.startswith('y')
    
    def print_separator(self, char: str = "─", length: int = 60):
        """打印分隔符"""
        self.console.print(f"[dim]{char * length}[/dim]")
    
    def show_help_info(self):
        """显示帮助信息"""
        help_text = """
[bold cyan]📖 使用说明[/bold cyan]

[yellow]基本用法:[/yellow]
  bili-dl <B站视频URL>
  
[yellow]常用选项:[/yellow]
  -o, --output      指定下载目录
  --cookies         使用Cookie文件
  --cookie-string   直接粘贴Cookie
  --no-cleanup      保留临时文件
  -v, --verbose     显示详细信息

[yellow]示例:[/yellow]
  bili-dl https://www.bilibili.com/video/BV1234567890
  bili-dl -o ./downloads https://www.bilibili.com/video/BV1234567890
  bili-dl --cookies cookies.txt https://www.bilibili.com/video/BV1234567890
        """
        panel = Panel(help_text, title="帮助", border_style="blue")
        self.console.print(panel)


class EnhancedProgressBar:
    """增强的进度条类"""
    
    def __init__(self, total: int, description: str = "进度", ui_manager: UIManager = None):
        self.total = total
        self.description = description
        self.ui_manager = ui_manager or UIManager()
        self.progress = None
        self.task_id = None
        self.start_time = time.time()
        self.last_update = time.time()
        
    def start(self):
        """启动进度条"""
        self.progress = self.ui_manager.create_download_progress(self.description)
        self.progress.start()
        self.task_id = self.progress.add_task(
            self.description,
            total=self.total
        )
        
    def update(self, completed: int, force_update: bool = False):
        """更新进度"""
        if self.progress and self.task_id is not None:
            # 限制更新频率以提高性能
            current_time = time.time()
            if force_update or current_time - self.last_update >= 0.1:
                self.progress.update(self.task_id, completed=completed)
                self.last_update = current_time
    
    def finish(self):
        """完成进度条"""
        if self.progress:
            self.progress.stop()
            elapsed = time.time() - self.start_time
            self.ui_manager.show_success(f"{self.description}完成 (耗时: {elapsed:.1f}秒)")


# 全局UI管理器实例
ui = UIManager()


def format_bytes(bytes_count: int) -> str:
    """格式化字节数显示"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_count < 1024.0:
            return f"{bytes_count:.1f} {unit}"
        bytes_count /= 1024.0
    return f"{bytes_count:.1f} PB"


def format_speed(bytes_per_second: float) -> str:
    """格式化速度显示"""
    return f"{format_bytes(int(bytes_per_second))}/s"


def format_time(seconds: float) -> str:
    """格式化时间显示"""
    if seconds < 60:
        return f"{seconds:.0f}秒"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:.0f}分{secs:.0f}秒"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours:.0f}小时{minutes:.0f}分"