"""
Cookie处理模块
支持Netscape格式Cookie文件的解析和导入
"""

import os
import re
import time
from typing import Dict, Optional
from http.cookiejar import MozillaCookieJar, Cookie


class CookieManager:
    """Cookie管理器，支持Netscape格式Cookie文件"""
    
    def __init__(self):
        self.cookies = {}
        self.cookie_jar = None
    
    def load_netscape_cookies(self, cookie_file_path: str) -> bool:
        """
        加载Netscape格式的Cookie文件
        
        Args:
            cookie_file_path: Cookie文件路径
            
        Returns:
            bool: 是否成功加载
        """
        if not os.path.exists(cookie_file_path):
            print(f"Cookie文件不存在: {cookie_file_path}")
            return False
        
        try:
            # 使用MozillaCookieJar来解析Netscape格式
            self.cookie_jar = MozillaCookieJar(cookie_file_path)
            self.cookie_jar.load(ignore_discard=True, ignore_expires=False)
            
            # 转换为字典格式便于使用
            self.cookies = {}
            current_time = time.time()
            
            for cookie in self.cookie_jar:
                # 检查cookie是否过期
                if cookie.expires is not None and cookie.expires < current_time:
                    continue
                    
                # 只保留bilibili相关的cookie
                if 'bilibili.com' in cookie.domain:
                    self.cookies[cookie.name] = cookie.value
            
            print(f"成功加载Cookie文件: {len(self.cookies)} 个有效Cookie")
            
            # 显示重要的认证Cookie
            important_cookies = ['SESSDATA', 'bili_jct', 'DedeUserID', 'buvid3']
            found_important = [name for name in important_cookies if name in self.cookies]
            if found_important:
                print(f"找到重要认证Cookie: {', '.join(found_important)}")
            else:
                print("警告: 未找到重要的认证Cookie (SESSDATA等)")
            
            return True
            
        except Exception as e:
            print(f"加载Cookie文件失败: {e}")
            return False
    
    def load_netscape_cookies_manual(self, cookie_file_path: str) -> bool:
        """
        手动解析Netscape格式的Cookie文件
        作为MozillaCookieJar的备用方案
        
        Args:
            cookie_file_path: Cookie文件路径
            
        Returns:
            bool: 是否成功加载
        """
        if not os.path.exists(cookie_file_path):
            print(f"Cookie文件不存在: {cookie_file_path}")
            return False
        
        try:
            self.cookies = {}
            current_time = time.time()
            
            with open(cookie_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    
                    # 跳过注释和空行
                    if not line or line.startswith('#'):
                        continue
                    
                    # 解析Cookie行格式：
                    # domain	flag	path	secure	expiration	name	value
                    parts = line.split('\t')
                    if len(parts) != 7:
                        continue
                    
                    domain, flag, path, secure, expiration, name, value = parts
                    
                    # 检查是否为bilibili域名
                    if 'bilibili.com' not in domain:
                        continue
                    
                    # 检查是否过期
                    try:
                        exp_time = int(expiration)
                        if exp_time != 0 and exp_time < current_time:
                            continue
                    except (ValueError, TypeError):
                        pass
                    
                    self.cookies[name] = value
            
            print(f"手动解析成功: {len(self.cookies)} 个有效Cookie")
            
            # 显示重要的认证Cookie
            important_cookies = ['SESSDATA', 'bili_jct', 'DedeUserID', 'buvid3']
            found_important = [name for name in important_cookies if name in self.cookies]
            if found_important:
                print(f"找到重要认证Cookie: {', '.join(found_important)}")
                
            return len(self.cookies) > 0
            
        except Exception as e:
            print(f"手动解析Cookie文件失败: {e}")
            return False
    
    def parse_cookie_string(self, cookie_string: str) -> bool:
        """
        直接解析Cookie字符串内容（支持粘贴）
        支持多种格式：
        1. Netscape格式（每行一个cookie）
        2. 浏览器Cookie字符串格式（name=value; name=value）
        3. 混合格式
        
        Args:
            cookie_string: Cookie字符串内容
            
        Returns:
            bool: 是否成功解析
        """
        try:
            self.cookies = {}
            current_time = time.time()
            
            # 按行分割
            lines = cookie_string.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                
                # 跳过注释和空行
                if not line or line.startswith('#'):
                    continue
                
                # 尝试解析不同格式
                if self._parse_netscape_line(line, current_time):
                    continue
                elif self._parse_browser_cookie_line(line):
                    continue
            
            print(f"解析成功: {len(self.cookies)} 个有效Cookie")
            
            # 显示重要的认证Cookie
            important_cookies = ['SESSDATA', 'bili_jct', 'DedeUserID', 'buvid3']
            found_important = [name for name in important_cookies if name in self.cookies]
            if found_important:
                print(f"找到重要认证Cookie: {', '.join(found_important)}")
            else:
                print("警告: 未找到重要的认证Cookie (SESSDATA等)")
            
            return len(self.cookies) > 0
            
        except Exception as e:
            print(f"解析Cookie字符串失败: {e}")
            return False
    
    def _parse_netscape_line(self, line: str, current_time: float) -> bool:
        """解析Netscape格式的Cookie行"""
        try:
            # 解析Cookie行格式：
            # domain	flag	path	secure	expiration	name	value
            parts = line.split('\t')
            if len(parts) != 7:
                return False
            
            domain, flag, path, secure, expiration, name, value = parts
            
            # 检查是否为bilibili域名
            if 'bilibili.com' not in domain:
                return False
            
            # 检查是否过期
            try:
                exp_time = int(expiration)
                if exp_time != 0 and exp_time < current_time:
                    return False
            except (ValueError, TypeError):
                pass
            
            self.cookies[name] = value
            return True
            
        except Exception:
            return False
    
    def _parse_browser_cookie_line(self, line: str) -> bool:
        """解析浏览器Cookie字符串格式"""
        try:
            # 处理形如 "name=value; name=value" 的格式
            if '=' in line:
                # 可能是browser cookie格式或单个cookie
                cookie_pairs = line.split(';')
                parsed_any = False
                
                for pair in cookie_pairs:
                    pair = pair.strip()
                    if '=' in pair:
                        name, value = pair.split('=', 1)
                        name = name.strip()
                        value = value.strip()
                        
                        # 简单验证：只保留看起来像bilibili cookie的
                        if any(keyword in name.lower() for keyword in ['sess', 'bili', 'buvid', 'dede', 'jct']):
                            self.cookies[name] = value
                            parsed_any = True
                
                return parsed_any
            
            return False
            
        except Exception:
            return False
    
    def get_cookie_dict(self) -> Dict[str, str]:
        """获取Cookie字典"""
        return self.cookies.copy()
    
    def get_cookie_header(self) -> str:
        """获取Cookie请求头字符串"""
        if not self.cookies:
            return ""
        
        cookie_pairs = [f"{name}={value}" for name, value in self.cookies.items()]
        return "; ".join(cookie_pairs)
    
    def is_logged_in(self) -> bool:
        """检查是否已登录（通过SESSDATA判断）"""
        return bool(self.cookies.get('SESSDATA'))
    
    def get_user_id(self) -> Optional[str]:
        """获取用户ID"""
        return self.cookies.get('DedeUserID')
    
    def update_session_cookies(self, session):
        """将Cookie更新到requests session中"""
        if self.cookie_jar:
            session.cookies.update(self.cookie_jar)
        else:
            # 手动添加cookie
            for name, value in self.cookies.items():
                session.cookies.set(name, value, domain='.bilibili.com')
        
        print(f"已将{len(self.cookies)}个Cookie添加到session中")
    
    def save_cookies(self, file_path: str) -> bool:
        """
        保存Cookie到Netscape格式文件
        
        Args:
            file_path: 保存路径
            
        Returns:
            bool: 是否成功保存
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("# Netscape HTTP Cookie File\n")
                f.write("# http://curl.haxx.se/rfc/cookie_spec.html\n")
                f.write("# This file was generated by BiliDownloader\n\n")
                
                for name, value in self.cookies.items():
                    # 简化格式：domain	flag	path	secure	expiration	name	value
                    f.write(f".bilibili.com\tTRUE\t/\tFALSE\t0\t{name}\t{value}\n")
            
            print(f"Cookie已保存到: {file_path}")
            return True
            
        except Exception as e:
            print(f"保存Cookie文件失败: {e}")
            return False
    
    def prompt_for_cookies(self) -> bool:
        """
        提示用户输入Cookie文件路径
        
        Returns:
            bool: 是否成功加载Cookie
        """
        print("\n需要Cookie文件来访问高质量视频流")
        print("请提供Netscape格式的Cookie文件路径")
        print("您可以使用浏览器插件如Cookie-Editor导出Cookie")
        print("格式示例: cookies.txt")
        
        while True:
            cookie_path = input("请输入Cookie文件路径 (回车跳过): ").strip()
            
            if not cookie_path:
                print("跳过Cookie导入，使用游客权限")
                return False
            
            # 尝试解析Cookie文件
            success = self.load_netscape_cookies(cookie_path)
            if not success:
                success = self.load_netscape_cookies_manual(cookie_path)
            
            if success:
                return True
            else:
                retry = input("是否重试? (y/N): ").lower()
                if retry != 'y':
                    print("跳过Cookie导入")
                    return False


def create_sample_cookie_file(file_path: str = "sample_cookies.txt"):
    """
    创建示例Cookie文件
    
    Args:
        file_path: 示例文件路径
    """
    sample_content = """# Netscape HTTP Cookie File
# http://curl.haxx.se/rfc/cookie_spec.html
# This file was generated by Cookie-Editor
.bilibili.com	TRUE	/	FALSE	1780905961	buvid_fp_plain	undefined
.bilibili.com	TRUE	/	FALSE	1780905960	fingerprint	a31a20948581601e693817967921ffa4
.bilibili.com	TRUE	/	FALSE	1784086095	CURRENT_QUALITY	80
.bilibili.com	TRUE	/	FALSE	1754542780	b_lsid	B9E10C4BD_1987D881D20
.bilibili.com	TRUE	/	FALSE	1785988628	theme-tip-show	SHOWED
.bilibili.com	TRUE	/	FALSE	1781617193	enable_feed_channel	ENABLE
.bilibili.com	TRUE	/	FALSE	1785983325	home_feed_column	5
.bilibili.com	TRUE	/	FALSE	1784640336	LIVE_BUVID	AUTO4117500803363336
.bilibili.com	TRUE	/	FALSE	1789008584	buvid4	BF3EB5F7-F7B3-7B4D-4C8B-12887666F2E474242-025030900-sa1nA8ZgZNjQ4IQF7na0DQ%3D%3D
.bilibili.com	TRUE	/	FALSE	1785988627	CURRENT_FNVAL	4048
.bilibili.com	TRUE	/	FALSE	1784172336	header_theme_version	OPEN
.bilibili.com	TRUE	/	FALSE	1773014473	buvid3	5095DF82-D0A7-BAB7-046C-2FE6A88D269173626infoc
.bilibili.com	TRUE	/	FALSE	1754542780	sid	7qg1rxi0
.bilibili.com	TRUE	/	FALSE	1757044723	bp_t_offset_1446964797	1097855157674180608
#HttpOnly_.bilibili.com	TRUE	/	TRUE	1757636940	SESSDATA	d004fa58%2C1757636940%2Cc5ded%2A32CjBxsZUbgYLbULCNFIQOOThDX45H3TlyCEb_pPYMqz4md0rS2PmxD2eQJ4vVOQcOH_YSVnFKUE5WVnVsYkJLbEQ0eFBBQ0thaVhHV3JhVmZNMWJlN3h5bjh6QVdRUHR2VHZZRG1rVlpxbUlGY1g3OHhLZi00WTF4Si1Yck00NHNVMUlaTmVfcmFnIIEC
.bilibili.com	TRUE	/	FALSE	1783208650	theme-avatar-tip-show	SHOWED
#HttpOnly_.bilibili.com	TRUE	/	TRUE	1754542780	timeMachine	0
.bilibili.com	TRUE	/	FALSE	1773014473	b_nut	1741478473
.bilibili.com	TRUE	/	FALSE	1773014473	_uuid	3E17E4C7-B3C7-108DC-E925-CE9C1CAC3571073824infoc
.bilibili.com	TRUE	/	FALSE	1757636940	bili_jct	bcdd5c8c6ce677f620447a39bafe7839
.bilibili.com	TRUE	/	FALSE	1754706525	bili_ticket	eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTQ3MDY1MjUsImlhdCI6MTc1NDQ0NzI2NSwicGx0IjotMX0.urLfPhGtmso7gqb-oK9oHSXgiK_5swTVZPXNncDQPLs
.bilibili.com	TRUE	/	FALSE	1754706525	bili_ticket_expires	1754706465
www.bilibili.com	FALSE	/	FALSE	1754542780	bmg_af_switch	1
www.bilibili.com	FALSE	/	FALSE	1754542780	bmg_src_def_domain	i0.hdslb.com
.bilibili.com	TRUE	/	FALSE	1785983325	browser_resolution	1862-936
.bilibili.com	TRUE	/	FALSE	1783929961	buvid_fp	f1ce5934455c4014d501d95c5c46735f
.bilibili.com	TRUE	/	FALSE	1757636940	DedeUserID	1446964797
.bilibili.com	TRUE	/	FALSE	1757636940	DedeUserID__ckMd5	be81c1d555bf7fd3
.bilibili.com	TRUE	/	FALSE	1785983325	enable_web_push	DISABLE
.bilibili.com	TRUE	/	FALSE	1774657667	hit-dyn-v2	1
.bilibili.com	TRUE	/	FALSE	1784643420	PVID	16
.bilibili.com	TRUE	/	FALSE	1776038477	rpdid	|(u)~l|R|kl~0J'u~RuR~)R~~
www.bilibili.com	FALSE	/video/BV1rN8HzWEjt	TRUE	1754542780	testcookie	1"""
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(sample_content)
        print(f"示例Cookie文件已创建: {file_path}")
        return True
    except Exception as e:
        print(f"创建示例文件失败: {e}")
        return False