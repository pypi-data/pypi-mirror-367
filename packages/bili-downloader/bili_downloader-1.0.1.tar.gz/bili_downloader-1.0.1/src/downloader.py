"""
视频下载器核心模块
负责下载m4s视频文件，支持分段下载和断点续传，禁用代理功能
"""

import os
import time
import requests
from typing import Optional, Callable, Dict
from .proxy_manager import apply_proxy_settings_to_session
from .ui import EnhancedProgressBar, ui, format_bytes, format_speed


class VideoDownloader:
    """视频下载器"""
    
    def __init__(self, chunk_size: int = 8192, timeout: int = 30, disable_proxy: bool = True):
        self.chunk_size = chunk_size
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.bilibili.com/',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Origin': 'https://www.bilibili.com'
        })
        
        # 应用代理设置
        if disable_proxy:
            apply_proxy_settings_to_session(self.session, disable_proxy=True)
    
    def download_file(self, 
                     url: str, 
                     output_path: str, 
                     progress_callback: Optional[Callable[[int, int], None]] = None) -> bool:
        """
        下载文件
        
        Args:
            url: 下载URL
            output_path: 输出文件路径
            progress_callback: 进度回调函数，参数为(已下载字节, 总字节)
        
        Returns:
            bool: 下载是否成功
        """
        try:
            # 检查是否支持断点续传
            resume_pos = 0
            if os.path.exists(output_path):
                resume_pos = os.path.getsize(output_path)
            
            headers = {}
            if resume_pos > 0:
                headers['Range'] = f'bytes={resume_pos}-'
            
            response = self.session.get(url, headers=headers, stream=True, timeout=self.timeout)
            
            # 检查响应状态
            if response.status_code not in [200, 206]:
                print(f"下载失败，状态码: {response.status_code}")
                return False
            
            # 获取文件总大小
            total_size = resume_pos
            if 'Content-Length' in response.headers:
                total_size += int(response.headers['Content-Length'])
            elif 'Content-Range' in response.headers:
                # 处理206 Partial Content响应
                content_range = response.headers['Content-Range']
                total_size = int(content_range.split('/')[-1])
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 开始下载
            mode = 'ab' if resume_pos > 0 else 'wb'
            downloaded = resume_pos
            
            with open(output_path, mode) as file:
                for chunk in response.iter_content(chunk_size=self.chunk_size):
                    if chunk:
                        file.write(chunk)
                        downloaded += len(chunk)
                        
                        # 调用进度回调
                        if progress_callback:
                            progress_callback(downloaded, total_size)
            
            ui.show_info(f"下载完成: {output_path}", "[FILE]")
            return True
            
        except Exception as e:
            ui.show_error(f"下载失败: {e}")
            return False
    
    def download_m4s_streams(self, 
                           video_url: str, 
                           audio_url: str, 
                           output_dir: str, 
                           filename: str) -> Dict[str, Optional[str]]:
        """
        下载m4s视频和音频流
        
        Args:
            video_url: 视频流URL
            audio_url: 音频流URL
            output_dir: 输出目录
            filename: 文件名（不含扩展名）
        
        Returns:
            Dict: 包含video_path和audio_path的字典
        """
        results = {'video_path': None, 'audio_path': None}
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 下载视频流
        if video_url:
            video_path = os.path.join(output_dir, f"{filename}_video.m4s")
            ui.show_step(f"开始下载视频流")
            
            # 创建增强的进度条
            progress_bar = None
            start_time = time.time()
            
            def video_progress(downloaded, total):
                nonlocal progress_bar
                if total > 0:
                    if progress_bar is None:
                        progress_bar = EnhancedProgressBar(total, "[VIDEO] 视频下载")
                        progress_bar.start()
                    progress_bar.update(downloaded)
            
            if self.download_file(video_url, video_path, video_progress):
                if progress_bar:
                    progress_bar.finish()
                results['video_path'] = video_path
        
        # 下载音频流
        if audio_url:
            audio_path = os.path.join(output_dir, f"{filename}_audio.m4s")
            ui.show_step(f"开始下载音频流")
            
            # 创建增强的进度条
            progress_bar = None
            
            def audio_progress(downloaded, total):
                nonlocal progress_bar
                if total > 0:
                    if progress_bar is None:
                        progress_bar = EnhancedProgressBar(total, "[AUDIO] 音频下载")
                        progress_bar.start()
                    progress_bar.update(downloaded)
            
            if self.download_file(audio_url, audio_path, audio_progress):
                if progress_bar:
                    progress_bar.finish()
                results['audio_path'] = audio_path
        
        return results
    
    def download_with_retry(self, 
                          url: str, 
                          output_path: str, 
                          max_retries: int = 3, 
                          progress_callback: Optional[Callable[[int, int], None]] = None) -> bool:
        """
        带重试的下载功能
        
        Args:
            url: 下载URL
            output_path: 输出文件路径
            max_retries: 最大重试次数
            progress_callback: 进度回调函数
        
        Returns:
            bool: 下载是否成功
        """
        for attempt in range(max_retries):
            try:
                if self.download_file(url, output_path, progress_callback):
                    return True
                else:
                    ui.show_warning(f"第 {attempt + 1} 次尝试失败")
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)  # 指数退避
            except Exception as e:
                ui.show_error(f"第 {attempt + 1} 次尝试出错: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
        
        ui.show_error(f"下载失败，已重试 {max_retries} 次")
        return False
    
    def get_file_info(self, url: str) -> Optional[Dict]:
        """
        获取文件信息
        
        Args:
            url: 文件URL
        
        Returns:
            Dict: 包含文件大小等信息的字典
        """
        try:
            response = self.session.head(url, timeout=self.timeout)
            if response.status_code == 200:
                return {
                    'size': int(response.headers.get('Content-Length', 0)),
                    'supports_range': 'Accept-Ranges' in response.headers,
                    'content_type': response.headers.get('Content-Type', '')
                }
        except Exception as e:
            ui.show_error(f"获取文件信息失败: {e}")
        
        return None
    
    def cleanup_temp_files(self, file_paths: list):
        """清理临时文件"""
        for path in file_paths:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                    ui.show_info(f"已删除临时文件: {path}", "[DEL]")
                except Exception as e:
                    ui.show_warning(f"删除临时文件失败 {path}: {e}")


class ProgressBar:
    """进度条显示类"""
    
    def __init__(self, total: int, prefix: str = "", length: int = 50):
        self.total = total
        self.prefix = prefix
        self.length = length
        self.current = 0
    
    def update(self, current: int):
        """更新进度"""
        self.current = current
        if self.total > 0:
            percent = current / self.total
            filled_length = int(self.length * percent)
            bar = '█' * filled_length + '-' * (self.length - filled_length)
            print(f'\r{self.prefix} |{bar}| {percent:.1%} ({current}/{self.total})', end='')
        else:
            print(f'\r{self.prefix} {current} bytes', end='')
    
    def finish(self):
        """完成进度显示"""
        print()  # 换行