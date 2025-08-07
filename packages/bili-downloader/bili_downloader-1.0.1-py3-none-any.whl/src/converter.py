"""
FFmpeg转换模块
负责将m4s格式转换为mp4格式
"""

import os
import subprocess
from typing import Optional, Dict


class VideoConverter:
    """视频格式转换器"""
    
    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        self.ffmpeg_path = ffmpeg_path
    
    def check_ffmpeg(self) -> bool:
        """检查FFmpeg是否可用"""
        try:
            result = subprocess.run([self.ffmpeg_path, '-version'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def merge_m4s_to_mp4(self, 
                        video_path: str, 
                        audio_path: str, 
                        output_path: str,
                        cleanup_temp: bool = True) -> bool:
        """
        合并视频和音频m4s文件为mp4
        
        Args:
            video_path: 视频m4s文件路径
            audio_path: 音频m4s文件路径
            output_path: 输出mp4文件路径
            cleanup_temp: 是否清理临时文件
        
        Returns:
            bool: 转换是否成功
        """
        if not self.check_ffmpeg():
            print("错误: FFmpeg未安装或不在PATH中")
            print("请安装FFmpeg: https://ffmpeg.org/download.html")
            return False
        
        try:
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 构建FFmpeg命令
            cmd = [
                self.ffmpeg_path,
                '-i', video_path,
                '-i', audio_path,
                '-c', 'copy',  # 直接复制流，不重新编码
                '-y',  # 覆盖输出文件
                output_path
            ]
            
            print(f"开始转换: {os.path.basename(output_path)}")
            print(f"执行命令: {' '.join(cmd)}")
            
            # 执行转换
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"转换成功: {output_path}")
                
                # 清理临时文件
                if cleanup_temp:
                    self._cleanup_files([video_path, audio_path])
                
                return True
            else:
                print(f"转换失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"转换出错: {e}")
            return False
    
    def convert_single_m4s_to_mp4(self, 
                                 input_path: str, 
                                 output_path: str,
                                 cleanup_temp: bool = True) -> bool:
        """
        转换单个m4s文件为mp4
        
        Args:
            input_path: 输入m4s文件路径
            output_path: 输出mp4文件路径
            cleanup_temp: 是否清理临时文件
        
        Returns:
            bool: 转换是否成功
        """
        if not self.check_ffmpeg():
            print("错误: FFmpeg未安装或不在PATH中")
            return False
        
        try:
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 构建FFmpeg命令
            cmd = [
                self.ffmpeg_path,
                '-i', input_path,
                '-c', 'copy',  # 直接复制流
                '-y',  # 覆盖输出文件
                output_path
            ]
            
            print(f"开始转换: {os.path.basename(output_path)}")
            
            # 执行转换
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"转换成功: {output_path}")
                
                # 清理临时文件
                if cleanup_temp:
                    self._cleanup_files([input_path])
                
                return True
            else:
                print(f"转换失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"转换出错: {e}")
            return False
    
    def get_video_info(self, file_path: str) -> Optional[Dict]:
        """
        获取视频文件信息
        
        Args:
            file_path: 视频文件路径
        
        Returns:
            Dict: 视频信息字典
        """
        if not self.check_ffmpeg():
            return None
        
        try:
            cmd = [
                self.ffmpeg_path,
                '-i', file_path,
                '-hide_banner'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # FFmpeg将信息输出到stderr
            info_text = result.stderr
            
            # 简单解析视频信息
            info = {}
            for line in info_text.split('\n'):
                if 'Duration:' in line:
                    duration_match = line.split('Duration: ')[1].split(',')[0]
                    info['duration'] = duration_match.strip()
                elif 'Video:' in line:
                    info['video_codec'] = line.strip()
                elif 'Audio:' in line:
                    info['audio_codec'] = line.strip()
            
            return info
            
        except Exception as e:
            print(f"获取视频信息失败: {e}")
            return None
    
    def _cleanup_files(self, file_paths: list):
        """清理临时文件"""
        for path in file_paths:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                    print(f"已清理临时文件: {os.path.basename(path)}")
                except Exception as e:
                    print(f"清理文件失败 {path}: {e}")
    
    def convert_with_custom_options(self, 
                                   video_path: str, 
                                   audio_path: str, 
                                   output_path: str,
                                   video_codec: str = "copy",
                                   audio_codec: str = "copy",
                                   extra_args: list = None) -> bool:
        """
        使用自定义选项进行转换
        
        Args:
            video_path: 视频文件路径
            audio_path: 音频文件路径  
            output_path: 输出文件路径
            video_codec: 视频编解码器
            audio_codec: 音频编解码器
            extra_args: 额外的FFmpeg参数
        
        Returns:
            bool: 转换是否成功
        """
        if not self.check_ffmpeg():
            return False
        
        try:
            cmd = [self.ffmpeg_path, '-i', video_path, '-i', audio_path]
            
            # 添加编解码器选项
            cmd.extend(['-c:v', video_codec, '-c:a', audio_codec])
            
            # 添加额外参数
            if extra_args:
                cmd.extend(extra_args)
            
            # 添加输出选项
            cmd.extend(['-y', output_path])
            
            print(f"使用自定义选项转换: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"转换成功: {output_path}")
                return True
            else:
                print(f"转换失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"转换出错: {e}")
            return False