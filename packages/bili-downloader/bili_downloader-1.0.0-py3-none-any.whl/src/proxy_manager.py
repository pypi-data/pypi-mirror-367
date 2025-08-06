"""
代理检测和管理模块
用于检测和禁用VPN/代理连接，确保B站下载正常运行
"""

import os
import socket
import requests
from typing import Dict, List, Optional, Tuple


class ProxyManager:
    """代理检测和管理器"""
    
    def __init__(self):
        self.original_env_proxies = {}
        self.proxy_disabled = False
        
        # 常见代理环境变量
        self.proxy_env_vars = [
            'HTTP_PROXY', 'HTTPS_PROXY', 'FTP_PROXY', 'SOCKS_PROXY',
            'http_proxy', 'https_proxy', 'ftp_proxy', 'socks_proxy',
            'ALL_PROXY', 'all_proxy'
        ]
        
        # 常见VPN/代理软件的本地端口
        self.common_proxy_ports = [
            1080,  # SOCKS5 (Shadowsocks, V2Ray, etc.)
            1087,  # Shadowsocks
            1088,  # V2Ray
            7890,  # ClashX default port
            7891,  # ClashX mixed port
            8080,  # HTTP proxy
            8888,  # Shadowsocks alternative
            9090,  # ClashX alternative
            10800, # Surge
            10808, # Surge SOCKS5
            11080, # Quantumult
            25378, # Surge alternative
        ]
    
    def detect_system_proxy(self) -> Dict[str, str]:
        """检测系统代理设置"""
        detected_proxies = {}
        
        # 检查环境变量代理
        for var in self.proxy_env_vars:
            value = os.environ.get(var)
            if value:
                detected_proxies[var] = value
        
        # 检查requests库自动检测的代理
        try:
            session_proxies = requests.Session().proxies
            if session_proxies:
                detected_proxies.update(session_proxies)
        except Exception:
            pass
        
        return detected_proxies
    
    def detect_vpn_processes(self) -> List[str]:
        """检测常见VPN/代理软件进程"""
        vpn_processes = [
            'shadowsocks',
            'shadowsocksr',
            'v2ray',
            'clash',
            'clashx',
            'surge',
            'quantumult',
            'proxifier',
            'shadowrocket',
            'trojan',
            'qv2ray',
            'wingy'
        ]
        
        detected_processes = []
        
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    proc_name = proc.info['name'].lower()
                    for vpn_name in vpn_processes:
                        if vpn_name in proc_name:
                            detected_processes.append(proc.info['name'])
                            break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except ImportError:
            # psutil不可用时，使用基本检测
            pass
        
        return detected_processes
    
    def check_proxy_ports(self) -> List[int]:
        """检查常见代理端口是否被占用"""
        active_proxy_ports = []
        
        for port in self.common_proxy_ports:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(0.5)
                    result = sock.connect_ex(('127.0.0.1', port))
                    if result == 0:
                        active_proxy_ports.append(port)
            except Exception:
                continue
        
        return active_proxy_ports
    
    def detect_ip_location(self) -> Optional[Dict]:
        """检测当前IP位置"""
        try:
            # 使用多个IP检测服务
            services = [
                'https://httpbin.org/ip',
                'https://api.ipify.org?format=json',
                'https://ipinfo.io/json'
            ]
            
            for service in services:
                try:
                    response = requests.get(service, timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        
                        # 解析IP信息
                        ip_info = {}
                        if 'origin' in data:
                            ip_info['ip'] = data['origin']
                        elif 'ip' in data:
                            ip_info['ip'] = data['ip']
                        
                        # 获取地理位置信息
                        if 'country' in data:
                            ip_info['country'] = data['country']
                        if 'region' in data:
                            ip_info['region'] = data['region']
                        if 'city' in data:
                            ip_info['city'] = data['city']
                        
                        return ip_info
                        
                except Exception:
                    continue
                    
        except Exception:
            pass
        
        return None
    
    def is_proxy_active(self) -> Tuple[bool, List[str]]:
        """综合检测是否有活跃的代理/VPN连接"""
        issues = []
        
        # 检查环境变量代理
        env_proxies = self.detect_system_proxy()
        if env_proxies:
            issues.append(f"检测到环境变量代理: {list(env_proxies.keys())}")
        
        # 检查VPN进程
        vpn_processes = self.detect_vpn_processes()
        if vpn_processes:
            issues.append(f"检测到VPN/代理进程: {vpn_processes}")
        
        # 检查代理端口
        active_ports = self.check_proxy_ports()
        if active_ports:
            issues.append(f"检测到活跃代理端口: {active_ports}")
        
        return len(issues) > 0, issues
    
    def backup_proxy_settings(self):
        """备份当前代理设置"""
        self.original_env_proxies = {}
        for var in self.proxy_env_vars:
            value = os.environ.get(var)
            if value:
                self.original_env_proxies[var] = value
    
    def disable_proxy(self):
        """禁用代理设置"""
        if self.proxy_disabled:
            return
        
        # 备份原始设置
        self.backup_proxy_settings()
        
        # 清除环境变量代理
        for var in self.proxy_env_vars:
            if var in os.environ:
                del os.environ[var]
        
        # 禁用urllib3的代理
        try:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        except ImportError:
            pass
        
        self.proxy_disabled = True
        print("✓ 已禁用代理设置")
    
    def restore_proxy(self):
        """恢复原始代理设置"""
        if not self.proxy_disabled:
            return
        
        # 恢复环境变量
        for var, value in self.original_env_proxies.items():
            os.environ[var] = value
        
        self.proxy_disabled = False
        print("✓ 已恢复原始代理设置")
    
    def create_no_proxy_session(self) -> requests.Session:
        """创建禁用代理的requests会话"""
        session = requests.Session()
        
        # 清除所有代理设置
        session.proxies = {
            'http': None,
            'https': None,
            'ftp': None,
            'socks4': None,
            'socks5': None
        }
        
        # 设置信任本地环境
        session.trust_env = False
        
        return session
    
    def test_bilibili_connection(self) -> Tuple[bool, str]:
        """测试B站连接"""
        try:
            session = self.create_no_proxy_session()
            response = session.get('https://www.bilibili.com', 
                                 timeout=10, 
                                 headers={'User-Agent': 'Mozilla/5.0 (compatible; BiliDownloader)'})
            
            if response.status_code == 200:
                # 检查是否被重定向到海外版
                if 'global' in response.url or 'intl' in response.url:
                    return False, "连接被重定向到B站海外版，可能使用了海外代理"
                return True, "B站连接正常"
            else:
                return False, f"B站连接失败，状态码: {response.status_code}"
                
        except Exception as e:
            return False, f"B站连接测试失败: {e}"
    
    def show_proxy_status(self):
        """显示代理状态报告"""
        print("\n🔍 代理检测报告")
        print("=" * 50)
        
        # 检测代理状态
        is_active, issues = self.is_proxy_active()
        
        if is_active:
            print("⚠️  检测到可能影响下载的代理/VPN:")
            for issue in issues:
                print(f"  • {issue}")
        else:
            print("✅ 未检测到活跃的代理/VPN")
        
        # 检测IP位置
        ip_info = self.detect_ip_location()
        if ip_info:
            print(f"\n🌍 当前IP信息:")
            print(f"  • IP地址: {ip_info.get('ip', '未知')}")
            if 'country' in ip_info:
                print(f"  • 国家/地区: {ip_info['country']}")
            if 'region' in ip_info:
                print(f"  • 地区: {ip_info['region']}")
        
        # 测试B站连接
        can_connect, message = self.test_bilibili_connection()
        print(f"\n🔗 B站连接测试: {message}")
        
        if is_active and not can_connect:
            print("\n💡 建议:")
            print("  • 暂时关闭VPN/代理软件")
            print("  • 或使用 --disable-proxy 参数强制禁用代理")
            print("  • 或在VPN软件中将bilibili.com设置为直连")
        
        print("=" * 50)
        
        return is_active, can_connect


def apply_proxy_settings_to_session(session: requests.Session, disable_proxy: bool = True):
    """应用代理设置到requests会话"""
    if disable_proxy:
        # 禁用所有代理
        session.proxies = {
            'http': None,
            'https': None,
            'ftp': None,
            'socks4': None,
            'socks5': None
        }
        session.trust_env = False
        
        # 添加B站相关域名到无代理列表
        no_proxy_hosts = [
            'bilibili.com',
            '*.bilibili.com',
            'bilivideo.com', 
            '*.bilivideo.com',
            'hdslb.com',
            '*.hdslb.com'
        ]
        
        # 设置no_proxy环境变量（如果不存在）
        if not os.environ.get('no_proxy') and not os.environ.get('NO_PROXY'):
            os.environ['no_proxy'] = ','.join(no_proxy_hosts)


# 全局代理管理器实例
proxy_manager = ProxyManager()