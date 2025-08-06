"""
Bilibili视频信息提取模块
负责解析Bilibili页面，提取视频元数据和播放URL
"""

import re
import json
import time
import hashlib
import urllib.parse
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Tuple
from .cookie_manager import CookieManager
from .proxy_manager import ProxyManager, apply_proxy_settings_to_session


class BilibiliExtractor:
    """Bilibili视频信息提取器 - 支持WBI签名认证、Cookie导入和代理管理"""
    
    def __init__(self, cookie_file: str = None, disable_proxy: bool = True):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.bilibili.com/',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate'
        })
        
        # 代理管理
        self.proxy_manager = ProxyManager()
        if disable_proxy:
            apply_proxy_settings_to_session(self.session, disable_proxy=True)
        
        # WBI签名相关
        self._wbi_key_cache = {}
        self._wbi_key_cache_timeout = 30  # 30秒缓存过期
        
        # Cookie管理
        self.cookie_manager = CookieManager()
        if cookie_file:
            self.load_cookies(cookie_file)
    
    def check_proxy_status(self, show_report: bool = True) -> Tuple[bool, bool]:
        """
        检查代理状态
        
        Args:
            show_report: 是否显示详细报告
        
        Returns:
            Tuple[bool, bool]: (有代理活跃, 能连接B站)
        """
        if show_report:
            return self.proxy_manager.show_proxy_status()
        else:
            is_active, _ = self.proxy_manager.is_proxy_active()
            can_connect, _ = self.proxy_manager.test_bilibili_connection()
            return is_active, can_connect
    
    def load_cookies(self, cookie_file: str) -> bool:
        """加载Cookie文件"""
        success = self.cookie_manager.load_netscape_cookies(cookie_file)
        if not success:
            success = self.cookie_manager.load_netscape_cookies_manual(cookie_file)
        
        if success:
            self.cookie_manager.update_session_cookies(self.session)
            return True
        return False
    
    def load_cookies_from_string(self, cookie_string: str) -> bool:
        """从字符串加载Cookie（支持粘贴）"""
        success = self.cookie_manager.parse_cookie_string(cookie_string)
        
        if success:
            # 将Cookie应用到session
            self.cookie_manager.update_session_cookies(self.session)
            return True
        return False
    
    def is_logged_in(self) -> bool:
        """检查是否已登录"""
        return self.cookie_manager.is_logged_in()
    
    def get_user_info(self) -> Dict:
        """获取用户信息"""
        if not self.is_logged_in():
            return {}
        
        user_id = self.cookie_manager.get_user_id()
        return {
            'logged_in': True,
            'user_id': user_id,
            'sessdata': bool(self.cookie_manager.cookies.get('SESSDATA')),
            'bili_jct': bool(self.cookie_manager.cookies.get('bili_jct'))
        }
    
    def _get_wbi_key(self, video_id: str) -> str:
        """获取WBI签名密钥"""
        if time.time() < self._wbi_key_cache.get('ts', 0) + self._wbi_key_cache_timeout:
            return self._wbi_key_cache['key']
        
        try:
            print("正在获取WBI签名密钥...")
            session_data = self.session.get('https://api.bilibili.com/x/web-interface/nav').json()
            
            img_url = session_data['data']['wbi_img']['img_url']
            sub_url = session_data['data']['wbi_img']['sub_url']
            
            # 提取密钥字符
            img_key = img_url.split('/')[-1].split('.')[0]
            sub_key = sub_url.split('/')[-1].split('.')[0]
            lookup = img_key + sub_key
            
            # from getMixinKey() in the vendor js
            mixin_key_enc_tab = [
                46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35, 27, 43, 5, 49,
                33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13, 37, 48, 7, 16, 24, 55, 40,
                61, 26, 17, 0, 1, 60, 51, 30, 4, 22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11,
                36, 20, 34, 44, 52,
            ]
            
            mixin_key = ''.join(lookup[i] for i in mixin_key_enc_tab)[:32]
            
            self._wbi_key_cache.update({
                'key': mixin_key,
                'ts': time.time(),
            })
            
            print(f"WBI密钥获取成功: {mixin_key[:8]}...")
            return mixin_key
            
        except Exception as e:
            print(f"获取WBI密钥失败: {e}")
            return ""
    
    def _sign_wbi(self, params: Dict, video_id: str) -> Dict:
        """WBI签名"""
        params['wts'] = int(time.time())
        
        # 过滤和排序参数
        filtered_params = {}
        for k, v in sorted(params.items()):
            # 过滤特殊字符
            filtered_value = ''.join(filter(lambda char: char not in "!'()*", str(v)))
            filtered_params[k] = filtered_value
        
        # 生成查询字符串
        query = urllib.parse.urlencode(filtered_params)
        
        # 获取密钥并生成签名
        wbi_key = self._get_wbi_key(video_id)
        sign_str = f'{query}{wbi_key}'
        w_rid = hashlib.md5(sign_str.encode()).hexdigest()
        
        params['w_rid'] = w_rid
        return params
    
    def extract_bv_from_url(self, url: str) -> Optional[str]:
        """从URL中提取BV号"""
        patterns = [
            r'BV[a-zA-Z0-9]+',
            r'av(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(0)
        return None
    
    def get_video_info(self, url: str) -> Optional[Dict]:
        """获取视频基本信息"""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 尝试从页面script标签中提取视频信息
            script_tags = soup.find_all('script')
            for script in script_tags:
                if script.string and 'window.__INITIAL_STATE__' in script.string:
                    # 提取JSON数据
                    json_str = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.+?});', script.string)
                    if json_str:
                        data = json.loads(json_str.group(1))
                        return self._parse_video_data(data)
                        
                elif script.string and 'window.__playinfo__' in script.string:
                    # 提取播放信息
                    json_str = re.search(r'window\.__playinfo__\s*=\s*({.+?})</script>', script.string)
                    if json_str:
                        playinfo = json.loads(json_str.group(1))
                        return self._parse_playinfo(playinfo)
            
            return None
        except Exception as e:
            print(f"获取视频信息失败: {e}")
            return None
    
    def _parse_video_data(self, data: Dict) -> Dict:
        """解析视频数据"""
        try:
            video_data = data.get('videoData', {})
            return {
                'title': video_data.get('title', ''),
                'bvid': video_data.get('bvid', ''),
                'aid': video_data.get('aid', ''),
                'cid': video_data.get('cid', ''),
                'duration': video_data.get('duration', 0),
                'pic': video_data.get('pic', ''),
                'desc': video_data.get('desc', ''),
                'owner': video_data.get('owner', {}).get('name', ''),
                'pages': video_data.get('pages', [])
            }
        except Exception as e:
            print(f"解析视频数据失败: {e}")
            return {}
    
    def _parse_playinfo(self, playinfo: Dict) -> Dict:
        """解析播放信息"""
        try:
            data = playinfo.get('data', {})
            dash = data.get('dash', {})
            
            video_streams = []
            audio_streams = []
            
            # 解析视频流
            for video in dash.get('video', []):
                video_streams.append({
                    'id': video.get('id'),
                    'quality': video.get('quality'),
                    'codecs': video.get('codecs'),
                    'width': video.get('width'),
                    'height': video.get('height'),
                    'frame_rate': video.get('frameRate'),
                    'bandwidth': video.get('bandwidth'),
                    'base_url': video.get('baseUrl', ''),
                    'backup_urls': video.get('backupUrl', [])
                })
            
            # 解析音频流
            for audio in dash.get('audio', []):
                audio_streams.append({
                    'id': audio.get('id'),
                    'quality': audio.get('quality'),
                    'codecs': audio.get('codecs'),
                    'bandwidth': audio.get('bandwidth'),
                    'base_url': audio.get('baseUrl', ''),
                    'backup_urls': audio.get('backupUrl', [])
                })
            
            return {
                'duration': data.get('duration', 0),
                'video_streams': video_streams,
                'audio_streams': audio_streams,
                'dash': dash
            }
        except Exception as e:
            print(f"解析播放信息失败: {e}")
            return {}
    
    def get_video_streams(self, bvid: str, cid: str) -> Optional[Dict]:
        """获取视频流信息 - 使用WBI签名认证和Cookie支持"""
        try:
            # 构建参数
            params = {
                'bvid': bvid,
                'cid': cid,
                'fnval': 4048,  # 高质量视频格式
                'fnver': 0,
                'fourk': 1      # 支持4K
            }
            
            # 如果已登录，移除try_look参数
            if self.is_logged_in():
                print("✓ 检测到登录状态，将获取更高质量的视频流")
                # 不需要try_look参数
            else:
                print("⚠ 未登录，使用游客权限（可能无法获取最高质量）")
                params['try_look'] = 1
            
            # WBI签名
            signed_params = self._sign_wbi(params, bvid)
            
            print(f"正在获取视频流信息... (fnval={params['fnval']}, 登录状态: {self.is_logged_in()})")
            
            # 使用WBI API端点
            api_url = "https://api.bilibili.com/x/player/wbi/playurl"
            
            response = self.session.get(api_url, params=signed_params)
            response.raise_for_status()
            
            data = response.json()
            if data.get('code') == 0:
                play_data = data['data']
                result = self._parse_playinfo_dash(play_data)
                print(f"成功获取视频流: {len(result.get('video_streams', []))} 视频流, {len(result.get('audio_streams', []))} 音频流")
                
                # 检查并显示缺失的格式信息
                self._check_missing_formats(play_data, result.get('video_streams', []) + result.get('audio_streams', []))
                
                return result
            else:
                print(f"API返回错误: {data.get('message', '未知错误')}")
                return None
                
        except Exception as e:
            print(f"获取视频流失败: {e}")
            return None
    
    def _check_missing_formats(self, play_data: Dict, formats: List[Dict]):
        """检查缺失的视频格式并提示"""
        try:
            support_formats = play_data.get('support_formats', [])
            if not support_formats:
                return
            
            # 获取当前已解析的质量ID
            parsed_qualities = set()
            for fmt in formats:
                if fmt.get('id'):
                    parsed_qualities.add(fmt['id'])
            
            # 检查缺失的格式
            missing_formats = []
            for support_fmt in support_formats:
                quality = support_fmt.get('quality')
                if quality and quality not in parsed_qualities:
                    desc = support_fmt.get('new_description') or support_fmt.get('display_desc') or f"质量{quality}"
                    missing_formats.append(desc)
            
            if missing_formats and not self.is_logged_in():
                print(f"⚠ 缺失更高质量格式: {', '.join(missing_formats)}")
                print("  提示: 使用--cookies参数导入登录Cookie可获取更高质量视频")
            elif missing_formats and self.is_logged_in():
                print(f"ℹ 需要大会员权限的格式: {', '.join(missing_formats)}")
                
        except Exception as e:
            print(f"检查缺失格式时出错: {e}")
    
    def _parse_playinfo_dash(self, play_data: Dict) -> Dict:
        """解析DASH格式的播放信息"""
        try:
            dash = play_data.get('dash', {})
            
            video_streams = []
            audio_streams = []
            
            # 解析视频流
            for video in dash.get('video', []):
                stream_info = {
                    'id': video.get('id'),
                    'quality': video.get('id'),  # 使用id作为quality
                    'codecs': video.get('codecs'),
                    'width': video.get('width'),
                    'height': video.get('height'),
                    'frame_rate': video.get('frameRate'),
                    'bandwidth': video.get('bandwidth'),
                    'base_url': video.get('baseUrl', ''),
                    'backup_urls': video.get('backup_url', []),
                    'size': video.get('size', 0)
                }
                video_streams.append(stream_info)
                print(f"找到视频流: {stream_info['id']} ({stream_info['width']}x{stream_info['height']}) {stream_info['codecs']}")
            
            # 解析音频流
            for audio in dash.get('audio', []):
                stream_info = {
                    'id': audio.get('id'),
                    'quality': audio.get('id'),  # 使用id作为quality
                    'codecs': audio.get('codecs'),
                    'bandwidth': audio.get('bandwidth'),
                    'base_url': audio.get('baseUrl', ''),
                    'backup_urls': audio.get('backup_url', []),
                    'size': audio.get('size', 0)
                }
                audio_streams.append(stream_info)
                print(f"找到音频流: {stream_info['id']} {stream_info['codecs']}")
            
            # 检查flac音频
            flac = dash.get('flac', {})
            if flac and flac.get('audio'):
                flac_audio = flac['audio']
                stream_info = {
                    'id': flac_audio.get('id'),
                    'quality': flac_audio.get('id'),
                    'codecs': 'flac',
                    'bandwidth': flac_audio.get('bandwidth'),
                    'base_url': flac_audio.get('baseUrl', ''),
                    'backup_urls': flac_audio.get('backup_url', []),
                    'size': flac_audio.get('size', 0)
                }
                audio_streams.append(stream_info)
                print(f"找到FLAC音频流: {stream_info['id']}")
            
            return {
                'duration': play_data.get('timelength', 0) / 1000,  # 转换为秒
                'video_streams': video_streams,
                'audio_streams': audio_streams,
                'dash': dash,
                'support_formats': play_data.get('support_formats', [])
            }
        except Exception as e:
            print(f"解析播放信息失败: {e}")
            return {}
    
    def extract_m4s_urls(self, video_info: Dict) -> Tuple[List[str], List[str]]:
        """提取m4s视频和音频URL"""
        video_urls = []
        audio_urls = []
        
        try:
            # 提取视频流URL
            for stream in video_info.get('video_streams', []):
                base_url = stream.get('base_url', '')
                if base_url and base_url.endswith('.m4s'):
                    video_urls.append(base_url)
                    # 添加备用URL
                    for backup_url in stream.get('backup_urls', []):
                        if backup_url.endswith('.m4s'):
                            video_urls.append(backup_url)
            
            # 提取音频流URL
            for stream in video_info.get('audio_streams', []):
                base_url = stream.get('base_url', '')
                if base_url and base_url.endswith('.m4s'):
                    audio_urls.append(base_url)
                    # 添加备用URL
                    for backup_url in stream.get('backup_urls', []):
                        if backup_url.endswith('.m4s'):
                            audio_urls.append(backup_url)
        
        except Exception as e:
            print(f"提取m4s URL失败: {e}")
        
        return video_urls, audio_urls
    
    def get_best_quality_streams(self, video_info: Dict) -> Tuple[Optional[str], Optional[str]]:
        """获取最佳质量的视频和音频流"""
        try:
            video_streams = video_info.get('video_streams', [])
            audio_streams = video_info.get('audio_streams', [])
            
            print(f"可用视频流数量: {len(video_streams)}")
            print(f"可用音频流数量: {len(audio_streams)}")
            
            # 选择最高质量的视频流 (按带宽或尺寸排序)
            best_video = None
            if video_streams:
                # 优先按带宽排序，然后按分辨率
                best_video = max(video_streams, key=lambda x: (
                    x.get('bandwidth', 0),
                    x.get('width', 0) * x.get('height', 0),
                    x.get('size', 0)
                ))
                print(f"选择最佳视频流: {best_video.get('id')} ({best_video.get('width')}x{best_video.get('height')}) 带宽:{best_video.get('bandwidth')}")
            
            # 选择最高质量的音频流
            best_audio = None
            if audio_streams:
                # 优先选择FLAC，然后按带宽排序
                flac_streams = [s for s in audio_streams if s.get('codecs', '').lower() == 'flac']
                if flac_streams:
                    best_audio = max(flac_streams, key=lambda x: x.get('bandwidth', 0))
                    print(f"选择FLAC音频流: {best_audio.get('id')} 带宽:{best_audio.get('bandwidth')}")
                else:
                    best_audio = max(audio_streams, key=lambda x: (
                        x.get('bandwidth', 0),
                        x.get('size', 0)
                    ))
                    print(f"选择最佳音频流: {best_audio.get('id')} {best_audio.get('codecs')} 带宽:{best_audio.get('bandwidth')}")
            
            return (
                best_video.get('base_url') if best_video else None,
                best_audio.get('base_url') if best_audio else None
            )
            
        except Exception as e:
            print(f"选择最佳质量流失败: {e}")
            return None, None